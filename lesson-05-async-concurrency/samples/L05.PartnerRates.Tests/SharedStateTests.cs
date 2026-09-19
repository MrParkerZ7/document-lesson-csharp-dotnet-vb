using L05.PartnerRates;
using Microsoft.Extensions.Time.Testing;

namespace L05.PartnerRates.Tests;

/// <summary>Real threads, deterministic results: the counts only come out exact if the code is safe.</summary>
public class SharedStateTests
{
    [Fact]
    public void RateStats_counts_exactly_under_parallel_writers()
    {
        var stats = new RateStats();
        Parallel.For(0, 30_000, i =>
        {
            PartnerOutcome outcome = (i % 3) switch
            {
                0 => new Quoted($"P{i % 30:00}", TimeSpan.Zero, new Money(10_000m + i)),
                1 => new TimedOut($"P{i % 30:00}", TimeSpan.Zero),
                _ => new Failed($"P{i % 30:00}", TimeSpan.Zero, "503"),
            };
            stats.Record(outcome);
        });

        Assert.Equal(10_000, stats.QuotedCount);
        Assert.Equal(10_000, stats.TimedOutCount);
        Assert.Equal(10_000, stats.FailedCount);
        Assert.Equal(10_000m, stats.Best?.Premium.Amount);
    }

    [Fact]
    public async Task SingleFlight_makes_one_call_for_fifty_concurrent_callers()
    {
        var flight = new SingleFlight<string, Money>();
        var partnerAnswer = new TaskCompletionSource<Money>();
        var calls = 0;

        var callers = Enumerable.Range(0, 50)
            .Select(_ => Task.Run(() => flight.RunAsync("TOYOTA-2022-CLASS1", _ =>
            {
                Interlocked.Increment(ref calls);
                return partnerAnswer.Task;
            })))
            .ToArray();
        partnerAnswer.SetResult(new Money(12_345m));
        var premiums = await Task.WhenAll(callers);

        Assert.Equal(1, calls);
        Assert.All(premiums, p => Assert.Equal(12_345m, p.Amount));
    }

    [Fact]
    public async Task PartnerToken_is_fetched_once_for_fifty_callers_and_again_after_it_expires()
    {
        var time = new FakeTimeProvider();
        var reply = new TaskCompletionSource<string>(TaskCreationOptions.RunContinuationsAsynchronously);
        var fetches = 0;
        var token = new PartnerToken(time, _ =>
        {
            var n = Interlocked.Increment(ref fetches);
            return n == 1 ? reply.Task : Task.FromResult($"token-{n}");
        }, TimeSpan.FromMinutes(10));

        var callers = Enumerable.Range(0, 50).Select(_ => token.GetAsync()).ToArray();
        reply.SetResult("token-1");                       // the one fetch answers all fifty
        Assert.All(await Task.WhenAll(callers), t => Assert.Equal("token-1", t));
        Assert.Equal(1, fetches);

        Assert.Equal("token-1", await token.GetAsync());   // still fresh: no new fetch
        time.Advance(TimeSpan.FromMinutes(11));
        Assert.Equal("token-2", await token.GetAsync());   // expired: exactly one more
        Assert.Equal(2, fetches);
    }
}
