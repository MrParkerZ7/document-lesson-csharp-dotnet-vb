using Microsoft.EntityFrameworkCore;

namespace L09.Data;

public static class QuoteWorkflow
{
    #region unit-of-work
    public static async Task<Policy> AcceptAsync(
        MotorQuoteDbContext db, string reference, DateOnly today)
    {
        var quote = await db.Quotes.SingleAsync(q => q.Reference == reference);
        if (quote.Status != QuoteStatus.Quoted)
            throw new InvalidOperationException($"{reference} is {quote.Status}");

        quote.Status = QuoteStatus.Accepted;       // tracked change -> UPDATE
        var policy = new Policy
        {
            PolicyNumber = "P-" + reference[2..],
            QuoteId = quote.Id,
            Inception = today,
            Expiry = today.AddYears(1),
        };
        db.Policies.Add(policy);                    // new entity -> INSERT

        await db.SaveChangesAsync();   // both statements, one transaction
        return policy;
    }
    #endregion

    #region explicit-transaction
    // Accepting one quote declines the other open quotes on the same vehicle.
    // ExecuteUpdate and SaveChanges are separate commands, so one explicit
    // transaction makes them succeed or fail together.
    public static async Task AcceptAndDeclineRivalsAsync(
        MotorQuoteDbContext db, string reference, DateOnly today)
    {
        await using var tx = await db.Database.BeginTransactionAsync();

        var quote = await db.Quotes.SingleAsync(q => q.Reference == reference);
        await db.Quotes
            .Where(q => q.VehicleId == quote.VehicleId && q.Id != quote.Id
                     && q.Status == QuoteStatus.Quoted)
            .ExecuteUpdateAsync(s => s
                .SetProperty(q => q.Status, QuoteStatus.Declined)
                .SetProperty(q => q.Version, Guid.NewGuid()));

        await AcceptAsync(db, reference, today);   // its SaveChanges joins tx
        await tx.CommitAsync();                    // no commit = rollback on dispose
    }
    #endregion
}
