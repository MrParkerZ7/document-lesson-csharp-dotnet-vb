using System.Globalization;
using L13.DebugLab;
using L13.PerfLab;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;

// The quotes the batch prices (the declined ones are left out), built once, outside every measurement.
var requests = Enumerable.Range(0, 240).Select(QuoteBatch.Request)
    .Where(r => r.Driver.ClaimsLast5Years < 3).ToArray();

Console.WriteLine($"L13.PerfLab — {requests.Length} quotes, one report routine three ways");
Console.WriteLine($"{"version",-26}{"calls to Price",16}{"allocated bytes",18}{"bytes per quote",18}");

#region Measure
// GC.GetAllocatedBytesForCurrentThread counts bytes, not time, so the figure is repeatable:
// the same code on the same runtime allocates the same amount on every run.
static (string Text, int Calls, long Bytes) Measure(
    Func<IReadOnlyList<QuoteRequest>, string> version, IReadOnlyList<QuoteRequest> input)
{
    version(input);                                  // warm-up: static setup and first-call costs
    Report.PriceCalls = 0;
    var before = GC.GetAllocatedBytesForCurrentThread();
    var text = version(input);
    var bytes = GC.GetAllocatedBytesForCurrentThread() - before;
    return (text, Report.PriceCalls, bytes);
}
#endregion

var floor = Measure(Report.PricingOnly, requests);
var heavy = Measure(Report.Heavy, requests);
var builder = Measure(Report.Builder, requests);
var presized = Measure(Report.Presized, requests);

foreach (var (name, r) in new[] { ("pricing only (floor)", floor), ("LINQ + string.Format", heavy), ("StringBuilder", builder),
                                  ("StringBuilder, pre-sized", presized) })
    Console.WriteLine($"{name,-26}{r.Calls,16}{r.Bytes,18:N0}{r.Bytes / requests.Length,18:N0}");

var same = heavy.Text == builder.Text && builder.Text == presized.Text;
Console.WriteLine($"all three reports are identical: {same} ({heavy.Text.Length} characters)");
return same ? 0 : 1;
