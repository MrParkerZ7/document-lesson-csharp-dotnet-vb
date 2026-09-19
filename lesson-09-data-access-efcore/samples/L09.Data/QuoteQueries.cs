using Microsoft.EntityFrameworkCore;

namespace L09.Data;

public sealed record QuoteSummary(string Reference, string Make, decimal Total, int Lines);

public static class QuoteQueries
{
    #region projection
    // Reads only the named columns; never tracked.
    // q.Lines.Count becomes a COUNT(*) subquery.
    public static IQueryable<QuoteSummary> Summaries(
        this MotorQuoteDbContext db, CoverageClass coverage) =>
        db.Quotes
            .Where(q => q.Coverage == coverage)
            .OrderBy(q => q.Reference)
            .Select(q => new QuoteSummary(
                q.Reference,
                q.Vehicle.Make,
                q.Total.Amount,
                q.Lines.Count));
    #endregion

    #region bulk-expire
    // One UPDATE; nothing loaded or tracked. The
    // token is NOT checked, so rotate it yourself.
    public static Task<int> ExpireStaleAsync(
        this MotorQuoteDbContext db, DateOnly today)
    {
        var stamp = Guid.NewGuid();
        return db.Quotes
            .Where(q => q.Status == QuoteStatus.Quoted
                     && q.ValidUntil < today)
            .ExecuteUpdateAsync(s => s
                .SetProperty(q => q.Status, QuoteStatus.Expired)
                .SetProperty(q => q.Version, stamp));
    }
    #endregion

    #region from-sql
    // FromSql takes a FormattableString: {make} is sent as a parameter,
    // never spliced into the SQL text.
    public static IQueryable<Vehicle> VehiclesByMake(
        this MotorQuoteDbContext db, string make) =>
        db.Vehicles.FromSql($"SELECT * FROM Vehicles WHERE Make = {make}");
    #endregion
}
