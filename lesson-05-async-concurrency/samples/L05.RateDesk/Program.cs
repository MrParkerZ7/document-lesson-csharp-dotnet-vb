using System.Diagnostics;
using L05.PartnerRates;

// A rating desk: ask 30 simulated partners for a motor premium on the real clock.
// Premiums are illustrative, not a real tariff.
var request = new QuoteRequest("Toyota", 2022, CoverageClass.Class1, new Money(650_000m));
var partners = PartnerCatalog.Create(TimeProvider.System);
var timeout = TimeSpan.FromMilliseconds(250);
Console.WriteLine($"C#  {partners.Count} partners, timeout {timeout.TotalMilliseconds} ms");

#region program
var fanOut = new RateFanOut(partners, TimeProvider.System,
                            timeout);
var clock = Stopwatch.StartNew();
var outcomes = await fanOut.QueryAllAsync(request);
clock.Stop();

var stats = new RateStats();
foreach (var outcome in outcomes) stats.Record(outcome);

Console.WriteLine($"  quoted {stats.QuotedCount}"
    + $", timed out {stats.TimedOutCount}"
    + $", failed {stats.FailedCount}");
Console.WriteLine($"  best   {stats.Best?.PartnerId}"
    + $" {stats.Best?.Premium}");
#endregion

var sequential = partners.Sum(p => p.Behaviour == PartnerBehaviour.Hangs || p.Latency > timeout
    ? timeout.TotalMilliseconds
    : p.Latency.TotalMilliseconds);
Console.WriteLine($"  wall   {clock.ElapsedMilliseconds} ms concurrently,"
                  + $" {sequential:N0} ms one after another");
Console.WriteLine($"  pool   {ThreadPool.ThreadCount} thread-pool threads");
Console.WriteLine("  first answers, in completion order:");

#region stream
// the first 5 answers, as they arrive (Take: .NET 10 ships
// LINQ for IAsyncEnumerable, no System.Linq.Async package)
using var enough = new CancellationTokenSource();
var answers = fanOut.StreamAsync(request, enough.Token);
await foreach (var outcome in answers.Take(5))
{
    Console.WriteLine("    " + Describe(outcome));
}
// leaving the loop does NOT stop the calls it started
await enough.CancelAsync();
#endregion
Console.WriteLine("  cancelled the partners still working");

static string Describe(PartnerOutcome outcome) => outcome switch
{
    Quoted q => $"{q.PartnerId} quoted {q.Premium}",
    TimedOut t => $"{t.PartnerId} timed out",
    Failed f => $"{f.PartnerId} failed ({f.Reason})",
    _ => outcome.PartnerId,
};
