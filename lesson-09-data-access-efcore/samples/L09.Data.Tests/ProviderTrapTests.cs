using Microsoft.EntityFrameworkCore;

namespace L09.Data.Tests;

public class ProviderTrapTests
{
    #region in-memory-trap
    [Fact]
    public async Task The_InMemory_provider_cannot_run_ExecuteUpdate()
    {
        var options = new DbContextOptionsBuilder<MotorQuoteDbContext>()
            .UseInMemoryDatabase("trap")
            .Options;
        await using var db = new MotorQuoteDbContext(options);

        // Compiles, and runs on every relational provider (SQLite here):
        // on InMemory it throws.
        var ex = await Assert.ThrowsAsync<InvalidOperationException>(
            () => db.ExpireStaleAsync(QuoteSeed.Today));
        Assert.Contains("ExecuteUpdate", ex.Message);
    }
    #endregion

    [Fact]
    public async Task FromSql_sends_interpolated_values_as_parameters()
    {
        using var sqlite = new SqliteDb().Seed(5);
        await using var db = sqlite.NewContext();

        var rows = await db.VehiclesByMake("Toyota' OR '1'='1").ToListAsync();

        Assert.Empty(rows);
        var sql = Assert.Single(sqlite.Log.Sql);
        Assert.DoesNotContain("OR '1'", sql);
        Assert.Equal(2, (await db.VehiclesByMake("Toyota").ToListAsync()).Count);
    }

    [Fact]
    public async Task Dapper_and_EF_Core_agree_on_the_coverage_report()
    {
        using var sqlite = new SqliteDb().Seed(20);
        await using var db = sqlite.NewContext();

        var linq = await db.Quotes
            .Where(q => q.Status == QuoteStatus.Quoted)
            .GroupBy(q => q.Coverage)
            .Select(g => new { Coverage = g.Key.ToString(), Quotes = (long)g.Count() })
            .ToListAsync();
        var dapper = await CoverageReport.ByCoverageAsync(sqlite.Connection, "Quoted");

        Assert.Equal(
            linq.OrderBy(r => r.Coverage, StringComparer.Ordinal).Select(r => (r.Coverage, r.Quotes)),
            dapper.Select(r => (r.Coverage, r.Quotes)));
    }
}
