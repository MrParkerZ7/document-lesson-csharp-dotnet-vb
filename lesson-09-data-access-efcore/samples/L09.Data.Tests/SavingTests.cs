using Dapper;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;

namespace L09.Data.Tests;

public class SavingTests
{
    [Fact]
    public async Task Accepting_a_quote_writes_the_update_and_the_insert_together()
    {
        using var sqlite = new SqliteDb().Seed(3);
        await using (var db = sqlite.NewContext())
        {
            var policy = await QuoteWorkflow.AcceptAsync(db, "Q-0001", QuoteSeed.Today);
            Assert.Equal("P-0001", policy.PolicyNumber);
        }

        await using var check = sqlite.NewContext();
        var quote = await check.Quotes.SingleAsync(q => q.Reference == "Q-0001");
        Assert.Equal(QuoteStatus.Accepted, quote.Status);
        Assert.True(await check.Policies.AnyAsync(p => p.QuoteId == quote.Id));
    }

    #region no-auto-flush
    [Fact]
    public async Task A_query_reads_the_database_not_unsaved_changes()
    {
        using var sqlite = new SqliteDb().Seed(3);
        await using var db = sqlite.NewContext();
        var quote = await db.Quotes.SingleAsync(q => q.Reference == "Q-0001");

        quote.Status = QuoteStatus.Declined;       // tracked, not saved
        var declined = await db.Quotes
            .CountAsync(q => q.Status == QuoteStatus.Declined);
        var again = await db.Quotes.SingleAsync(q => q.Id == quote.Id);

        Assert.Equal(0, declined);                 // no flush before a query
        Assert.Same(quote, again);                 // identity resolution
        Assert.Equal(QuoteStatus.Declined, again.Status);
    }
    #endregion

    #region concurrency-conflict
    [Fact]
    public async Task The_second_writer_gets_a_concurrency_exception()
    {
        using var sqlite = new SqliteDb().Seed(1);
        await using var underwriter = sqlite.NewContext();
        await using var broker = sqlite.NewContext();
        var mine = await underwriter.Quotes.SingleAsync();
        var theirs = await broker.Quotes.SingleAsync();  // same row

        mine.Status = QuoteStatus.Accepted;
        await underwriter.SaveChangesAsync();   // new Version stamped

        theirs.Status = QuoteStatus.Declined;   // based on stale Version
        await Assert.ThrowsAsync<DbUpdateConcurrencyException>(
            () => broker.SaveChangesAsync());
    }
    #endregion

    #region transaction-tests
    [Fact]
    public async Task One_transaction_covers_ExecuteUpdate_and_SaveChanges()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using (var db = sqlite.NewContext())
            await QuoteWorkflow.AcceptAndDeclineRivalsAsync(db, "Q-0001", QuoteSeed.Today);

        await using var check = sqlite.NewContext();
        Assert.Equal(QuoteStatus.Accepted, await StatusOf(check, "Q-0001"));
        Assert.Equal(QuoteStatus.Declined, await StatusOf(check, "Q-0011"));   // rivals on the
        Assert.Equal(QuoteStatus.Declined, await StatusOf(check, "Q-0016"));   // same vehicle
        Assert.Equal(QuoteStatus.Accepted, await StatusOf(check, "Q-0006"));  // already accepted
    }

    [Fact]
    public async Task A_failed_SaveChanges_rolls_back_the_ExecuteUpdate_too()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using (var setup = sqlite.NewContext())
        {
            var rival = await setup.Quotes.SingleAsync(q => q.Reference == "Q-0011");
            setup.Policies.Add(new Policy      // takes the number Q-0001 would get
            {
                PolicyNumber = "P-0001", QuoteId = rival.Id,
                Inception = QuoteSeed.Today, Expiry = QuoteSeed.Today.AddYears(1),
            });
            await setup.SaveChangesAsync();
        }

        await using (var db = sqlite.NewContext())
            await Assert.ThrowsAsync<DbUpdateException>(
                () => QuoteWorkflow.AcceptAndDeclineRivalsAsync(db, "Q-0001", QuoteSeed.Today));

        await using var check = sqlite.NewContext();
        Assert.Equal(QuoteStatus.Quoted, await StatusOf(check, "Q-0001"));
        Assert.Equal(QuoteStatus.Quoted, await StatusOf(check, "Q-0011"));   // the UPDATE was undone
        Assert.Equal(QuoteStatus.Quoted, await StatusOf(check, "Q-0016"));
    }

    [Fact]
    public async Task Dapper_joins_the_transaction_of_an_EF_Core_context()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using var db = sqlite.NewContext();
        await using (var tx = await db.Database.BeginTransactionAsync())
        {
            await db.Database.GetDbConnection().ExecuteAsync(
                "UPDATE Quotes SET Status = 'Declined' WHERE Reference = 'Q-0001'",
                transaction: tx.GetDbTransaction());
            Assert.Equal(QuoteStatus.Declined, await StatusOf(db, "Q-0001"));   // seen inside tx
        }   // disposed without CommitAsync: rolled back

        await using var check = sqlite.NewContext();
        Assert.Equal(QuoteStatus.Quoted, await StatusOf(check, "Q-0001"));
    }

    private static async Task<QuoteStatus> StatusOf(MotorQuoteDbContext db, string reference) =>
        (await db.Quotes.AsNoTracking().SingleAsync(q => q.Reference == reference)).Status;
    #endregion

    [Fact]
    public async Task ExecuteUpdate_is_one_command_and_skips_the_change_tracker()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using var db = sqlite.NewContext();
        var tracked = await db.Quotes.SingleAsync(q => q.Reference == "Q-0001");
        sqlite.Log.Reset();

        var expired = await db.ExpireStaleAsync(QuoteSeed.Today);

        Assert.Equal(10, expired);
        Assert.Equal(1, sqlite.Log.Count);
        Assert.Equal(QuoteStatus.Quoted, tracked.Status);     // stale copy
        await db.Entry(tracked).ReloadAsync();
        Assert.Equal(QuoteStatus.Expired, tracked.Status);
    }

    [Fact]
    public async Task Tracked_bulk_change_costs_a_select_plus_the_updates()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using var db = sqlite.NewContext();

        var stale = await db.Quotes
            .Where(q => q.Status == QuoteStatus.Quoted && q.ValidUntil < QuoteSeed.Today)
            .ToListAsync();
        foreach (var q in stale)
            q.Status = QuoteStatus.Expired;
        var written = await db.SaveChangesAsync();

        Assert.Equal(10, written);
        Assert.Equal(11, sqlite.Log.Count);   // measured on SQLite: 1 SELECT + 10 UPDATEs
    }
}
