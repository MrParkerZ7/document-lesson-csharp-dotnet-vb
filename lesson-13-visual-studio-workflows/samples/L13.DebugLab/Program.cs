using System.Globalization;
using L13.DebugLab;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;

const int BatchSize = 240;
Console.WriteLine("MotorQuote DebugLab — illustrative tariff, not a real one");

#region WorkedExample
// The curriculum's worked example: Class 1, 550,000 THB, private use, a 23-year-old with
// 4 claim-free licence years.
var example = new QuoteRequest(
    new Vehicle("Make0", "Model0", 2024, 1500, VehicleUse.Private, Money.Thb(550_000)),
    new Driver(new DateOnly(2002, 6, 15), 4, 0), CoverageClass.Class1, QuoteBatch.StartDate);
var premium = QuoteCalculator.Price(example);
Console.WriteLine($"worked example: net {premium.Net.Amount:F2} · stamp duty {premium.StampDuty.Amount:F2}" +
                  $" · VAT {premium.Vat.Amount:F2} · total {premium.Total.Amount:F2} THB");
#endregion

if (args is ["--show", var index] && int.TryParse(index, out var i))
{
    Show(i);
    return;
}

var result = QuoteBatch.Run(BatchSize);
Console.WriteLine($"batch of {BatchSize} quotes: {result.Quoted} quoted, {result.Declined.Count} declined");
Console.WriteLine($"declined at index: {string.Join(", ", result.Declined)}");
Console.WriteLine($"gross premium of the quoted policies: {result.Gross:F2} THB");

static void Show(int i)
{
    var request = QuoteBatch.Request(i);
    try
    {
        var p = QuoteCalculator.Price(request);
        Console.WriteLine($"quote #{i}: {request.Coverage}, sum insured {request.Vehicle.SumInsured.Amount:F2}, " +
                          $"loadings {p.LoadingRate * 100:F0}%, no-claim {p.DiscountRate * 100:F0}%");
        Console.WriteLine($"quote #{i}: net {p.Net.Amount:F2} · total {p.Total.Amount:F2} THB");
    }
    catch (QuoteDeclinedException ex)
    {
        Console.WriteLine($"quote #{i}: declined in {ex.TargetSite?.Name} — {ex.Message}");
    }
}
