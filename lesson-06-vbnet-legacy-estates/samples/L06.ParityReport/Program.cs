using System.Globalization;
using L06.ModernRating;
using L06.Parity;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;

#region report
var faithful = ParityRunner.Compare(PremiumCalculator.Calculate);
Console.WriteLine($"Parity grid        {faithful.Cases:N0} quote requests");
Console.WriteLine($"Faithful C# port   {faithful.Mismatches} mismatches");
Console.WriteLine("Port variants, one change at a time:");
foreach (var change in Enum.GetValues<PortChange>().Skip(1))
{
    var r = ParityRunner.Compare(q => NaivePort.Calculate(q, change));
    Console.WriteLine(
        $"  {change,-19}{r.Mismatches,7:N0}  {100.0 * r.Mismatches / r.Cases,5:0.0}%");
}
#endregion

// The curriculum's worked example: Class 1, 550,000 THB, private use, aged 23
// with 4 claim-free licence years, no claims.
var example = new QuoteRequest("CLASS1", 550_000m, new(2002, 6, 15), new(2026, 1, 1), 48, 0);
Console.WriteLine($"Worked example  {ParityRunner.Describe(example)}");
Console.WriteLine($"  VB legacy {LegacyAdapter.Quote(example, out _)}  C# port {PremiumCalculator.Calculate(example)}  canonical {CanonicalTariff.Total(example)}");
var probe = new QuoteRequest("class1", 287_500m, new(2001, 12, 31), new(2026, 1, 1), 18, 0);
Console.WriteLine($"Sample  {ParityRunner.Describe(probe)}");
Console.WriteLine($"  VB legacy {LegacyAdapter.Quote(probe, out _)}  C# port {PremiumCalculator.Calculate(probe)}");
foreach (var change in new[] { PortChange.HalfUpRounding, PortChange.DecimalRates })
{
    Console.WriteLine($"First {change} mismatch");
    Console.WriteLine("  " + ParityRunner.Compare(q => NaivePort.Calculate(q, change)).FirstMismatch);
}
