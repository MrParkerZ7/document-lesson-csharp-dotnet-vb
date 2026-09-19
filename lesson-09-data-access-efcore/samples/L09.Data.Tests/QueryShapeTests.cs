using Microsoft.EntityFrameworkCore;

namespace L09.Data.Tests;

public class QueryShapeTests
{
    #region command-counts
    [Theory]
    [InlineData(1)]
    [InlineData(5)]
    [InlineData(20)]
    public async Task Loading_lines_per_quote_costs_one_command_each(int n)
    {
        using var sqlite = new SqliteDb().Seed(n);
        await using var db = sqlite.NewContext();

        foreach (var quote in await db.Quotes.ToListAsync())
            await db.Entry(quote).Collection(q => q.Lines).LoadAsync();

        Assert.Equal(n + 1, sqlite.Log.Count);          // the N+1
    }

    [Theory]
    [InlineData(1)]
    [InlineData(20)]
    public async Task Include_loads_the_same_graph_in_one_command(int n)
    {
        using var sqlite = new SqliteDb().Seed(n);
        await using var db = sqlite.NewContext();

        var quotes = await db.Quotes.Include(q => q.Lines).ToListAsync();

        Assert.Equal(1, sqlite.Log.Count);
        Assert.All(quotes, q => Assert.NotEmpty(q.Lines));
    }
    #endregion

    [Fact]
    public async Task AsSplitQuery_uses_one_command_per_collection_level()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using var db = sqlite.NewContext();

        var quotes = await db.Quotes.Include(q => q.Lines).AsSplitQuery().ToListAsync();

        Assert.Equal(2, sqlite.Log.Count);
        Assert.All(quotes, q => Assert.NotEmpty(q.Lines));
    }

    #region missing-include
    [Fact]
    public async Task Missing_Include_leaves_Lines_empty()
    {
        using var sqlite = new SqliteDb().Seed(3);
        await using var db = sqlite.NewContext();

        var quote = await db.Quotes.FirstAsync();

        // No proxy, no exception: just an empty list.
        Assert.Empty(quote.Lines);
        Assert.Equal(1, sqlite.Log.Count);
    }
    #endregion

    [Fact]
    public void An_IEnumerable_filter_reads_and_tracks_every_row()
    {
        using var sqlite = new SqliteDb().Seed(20);
        using var db = sqlite.NewContext();
        IEnumerable<Quote> quotes = db.Quotes;

        var class1 = quotes.Count(q => q.Coverage == CoverageClass.Class1);

        Assert.Equal(5, class1);
        Assert.DoesNotContain("WHERE", Assert.Single(sqlite.Log.Sql));
        Assert.Equal(20, db.ChangeTracker.Entries<Quote>().Count());
    }

    [Fact]
    public void An_IQueryable_filter_becomes_a_SQL_COUNT()
    {
        using var sqlite = new SqliteDb().Seed(20);
        using var db = sqlite.NewContext();
        IQueryable<Quote> quotes = db.Quotes;

        var class1 = quotes.Count(q => q.Coverage == CoverageClass.Class1);

        Assert.Equal(5, class1);
        var sql = Assert.Single(sqlite.Log.Sql);
        Assert.Contains("COUNT(*)", sql);
        Assert.Contains("WHERE", sql);
        Assert.Empty(db.ChangeTracker.Entries());
    }

    [Fact]
    public void A_projection_selects_only_the_named_columns()
    {
        using var sqlite = new SqliteDb();
        using var db = sqlite.NewContext();

        var sql = db.Summaries(CoverageClass.Class1).ToQueryString();

        Assert.Contains("Total_Amount", sql);
        Assert.DoesNotContain("Driver_", sql);
    }
}
