using System.Diagnostics;

namespace L13.DebugLab;

#region BatchResult
// The debugger shows BatchResultView instead of the raw fields: the summary first, the
// declined indexes one click away. Nothing in the production API changes.
[DebuggerTypeProxy(typeof(BatchResultView))]
[DebuggerDisplay("{Quoted} quoted, {Declined.Count} declined")]
public sealed class BatchResult(int quoted, decimal gross, List<int> declined)
{
    public int Quoted { get; } = quoted;
    public decimal Gross { get; } = gross;
    public List<int> Declined { get; } = declined;
}

internal sealed class BatchResultView(BatchResult result)
{
    public string Summary => $"{result.Quoted} quoted, gross {result.Gross}";
    public int FirstDeclinedIndex => result.Declined.Count == 0 ? -1 : result.Declined[0];
    [DebuggerBrowsable(DebuggerBrowsableState.RootHidden)]
    public int[] DeclinedIndexes => [.. result.Declined];
}
#endregion

public static class QuoteBatch
{
    public static readonly DateOnly StartDate = new(2026, 1, 1);

    #region Generator
    // Deterministic: no Random, no clock. Quote i is always the same quote.
    public static QuoteRequest Request(int i)
    {
        var age = 19 + (i * 7) % 41;
        var claims = i % 61 == 47 ? 3 : i % 4 == 1 ? 1 : i % 9 == 4 ? 2 : 0;
        var vehicle = new Vehicle($"Make{i % 5}", $"Model{i % 7}", 2016 + i % 10, 1200 + i * 130 % 3400,
                                  i % 6 == 3 ? VehicleUse.Commercial : VehicleUse.Private,
                                  Money.Thb(250_000 + i % 37 * 15_000));
        var driver = new Driver(StartDate.AddYears(-age).AddDays(-(i % 300)),
                                Math.Min(age - 18, i * 3 % 12), claims);
        return new QuoteRequest(vehicle, driver, (CoverageClass)(i % 4), StartDate);
    }
    #endregion

    #region BatchLoop
    public static BatchResult Run(int count)
    {
        var gross = 0m;
        var quoted = 0;
        var declined = new List<int>();
        for (var i = 0; i < count; i++)
        {
            var request = Request(i);
            try
            {
                // Break on this line, after request is assigned: "i == 137", or a hit count of 138.
                gross += QuoteCalculator.Price(request).Total.Amount;
                quoted++;
            }
            catch (QuoteDeclinedException)
            {
                declined.Add(i);
            }
        }
        return new BatchResult(quoted, gross, declined);
    }
    #endregion
}
