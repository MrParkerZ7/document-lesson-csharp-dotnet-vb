using L05.PartnerRates;
using Microsoft.Extensions.Time.Testing;

namespace L05.PartnerRates.Tests;

/// <summary>
/// Every test runs on virtual time: FakeTimeProvider fires timers only when Advance is called,
/// so a 250 ms timeout takes microseconds and never flakes on a slow build agent.
/// </summary>
public class FanOutTests
{
    private static readonly QuoteRequest Request =
        new("Toyota", 2022, CoverageClass.Class1, new Money(650_000m));

    private static readonly TimeSpan Timeout = TimeSpan.FromMilliseconds(250);

    #region fake-time
    [Fact]
    public async Task Fan_out_ends_at_the_timeout_not_the_sum_of_latencies()
    {
        var time = new FakeTimeProvider();
        var fanOut = new RateFanOut(PartnerCatalog.Create(time), time, Timeout);

        var call = fanOut.QueryAllAsync(Request);   // all 30 timers registered here
        time.Advance(TimeSpan.FromMilliseconds(249));
        Assert.False(call.IsCompleted);             // slow partners still out

        time.Advance(TimeSpan.FromMilliseconds(1)); // deadlines fire now
        var outcomes = await call;                  // no real time has passed

        Assert.Equal(19, outcomes.OfType<Quoted>().Count());
        Assert.Equal(8, outcomes.OfType<TimedOut>().Count());
        Assert.Equal(3, outcomes.OfType<Failed>().Count());
    }
    #endregion

    [Fact]
    public async Task Best_is_the_cheapest_quote_that_arrived_in_time()
    {
        var time = new FakeTimeProvider();
        var partners = PartnerCatalog.Create(time);
        var fanOut = new RateFanOut(partners, time, Timeout);

        var call = fanOut.QueryAllAsync(Request);
        time.Advance(Timeout);
        var best = RateFanOut.Best(await call);

        var expected = partners
            .Where(p => p.Behaviour == PartnerBehaviour.Quotes && p.Latency < Timeout)
            .MinBy(p => p.RateBps)!;
        Assert.NotNull(best);
        Assert.Equal(expected.PartnerId, best.PartnerId);
    }

    [Fact]
    public async Task A_failing_partner_is_an_outcome_not_an_exception()
    {
        var time = new FakeTimeProvider();
        var fanOut = new RateFanOut(PartnerCatalog.Create(time), time, Timeout);

        var call = fanOut.QueryAllAsync(Request);
        time.Advance(Timeout);
        var failed = (await call).OfType<Failed>().Select(f => f.PartnerId);

        Assert.Equal(["P04", "P17", "P26"], failed);
    }

    [Fact]
    public async Task Caller_cancellation_propagates_instead_of_becoming_timeouts()
    {
        var time = new FakeTimeProvider();
        var fanOut = new RateFanOut(PartnerCatalog.Create(time), time, Timeout);
        using var caller = new CancellationTokenSource();

        var call = fanOut.QueryAllAsync(Request, caller.Token);
        time.Advance(TimeSpan.FromMilliseconds(100));
        await caller.CancelAsync();

        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => call);
    }

    [Fact]
    public async Task WhenEach_hands_back_each_outcome_the_moment_it_completes()
    {
        var time = new FakeTimeProvider();
        var partners = PartnerCatalog.Create(time);
        var fanOut = new RateFanOut(partners, time, Timeout);
        var answerOrder = partners
            .Where(p => p.Behaviour != PartnerBehaviour.Hangs && p.Latency < Timeout)
            .OrderBy(p => p.Latency)
            .ToList();

        await using var stream = fanOut.StreamAsync(Request).GetAsyncEnumerator();
        var next = stream.MoveNextAsync();          // starts all 30 calls
        var now = TimeSpan.Zero;
        foreach (var partner in answerOrder)
        {
            time.Advance(partner.Latency - now);    // move the clock to this partner's answer...
            now = partner.Latency;
            Assert.True(await next);                // ...and exactly that outcome comes out
            Assert.Equal(partner.PartnerId, stream.Current.PartnerId);
            next = stream.MoveNextAsync();
        }

        time.Advance(Timeout - now);                // the rest hit their deadline together
        var rest = new List<PartnerOutcome>();
        while (await next)
        {
            rest.Add(stream.Current);
            next = stream.MoveNextAsync();
        }
        Assert.Equal(PartnerCatalog.PartnerCount - answerOrder.Count, rest.Count);
        Assert.All(rest, o => Assert.IsType<TimedOut>(o));
    }

    [Fact]
    public async Task First_good_enough_quote_cancels_every_partner_still_working()
    {
        var time = new FakeTimeProvider();
        var partners = PartnerCatalog.Create(time);
        var fanOut = new RateFanOut(partners, time, Timeout);
        const decimal target = 12_500m;
        var winner = partners
            .Where(p => p.Behaviour == PartnerBehaviour.Quotes && Premium(p) <= target)
            .MinBy(p => p.Latency)!;

        var call = fanOut.FirstAtOrBelowAsync(Request, target);
        time.Advance(winner.Latency);               // exactly when the winner answers
        var first = await call;

        Assert.Equal(winner.PartnerId, first?.PartnerId);
        var stillWorking = partners.Count(p => p.Behaviour == PartnerBehaviour.Hangs || p.Latency > winner.Latency);
        // cancellation callbacks may finish on another thread: wait for the counters, not for time
        Assert.True(SpinWait.SpinUntil(
            () => partners.Sum(p => p.CancelledCalls) == stillWorking, TimeSpan.FromSeconds(5)));
    }

    #region wait-async
    [Fact]
    public async Task WaitAsync_stops_waiting_but_does_not_stop_the_call()
    {
        var time = new FakeTimeProvider();
        var stubborn = new SimulatedPartner("P99", TimeSpan.FromSeconds(2), 200m,
            PartnerBehaviour.IgnoresCancellation, time);

        var call = stubborn.GetRateAsync(Request, CancellationToken.None);
        var waiting = call.WaitAsync(Timeout, time);
        time.Advance(Timeout);

        await Assert.ThrowsAsync<TimeoutException>(() => waiting);
        Assert.False(call.IsCompleted);             // we gave up; the partner did not

        time.Advance(TimeSpan.FromSeconds(2));
        Assert.Equal(13_000m, (await call).Amount); // it finished anyway, unobserved
    }
    #endregion

    [Fact]
    public async Task Throttled_fan_out_never_exceeds_the_concurrency_budget()
    {
        var time = new FakeTimeProvider();
        var probe = new ConcurrencyProbe();
        var partners = PartnerCatalog.Create(time).Select(p => probe.Wrap(p)).ToList();
        var fanOut = new RateFanOut(partners, time, Timeout);

        var call = fanOut.QueryAllThrottledAsync(Request, maxConcurrent: 4);
        // Parallel.ForEachAsync starts calls on pool threads: keep moving virtual time until done
        for (var step = 0; step < 100_000 && !call.IsCompleted; step++)
        {
            time.Advance(TimeSpan.FromMilliseconds(5));
            await Task.Yield();
        }
        var outcomes = await call;

        // which partner lands in which bucket can shift by a step here (pool threads start calls
        // while time moves), so this test asserts the budget, not the quote counts
        Assert.Equal(PartnerCatalog.PartnerCount, outcomes.Count);
        Assert.InRange(probe.MaxInFlight, 1, 4);
    }

    private static decimal Premium(SimulatedPartner p) =>
        decimal.Round(Request.SumInsured.Amount * p.RateBps / 10_000m, 2);

    private sealed class ConcurrencyProbe
    {
        private int _inFlight, _max;
        public int MaxInFlight => Volatile.Read(ref _max);

        public IPartnerRateProvider Wrap(IPartnerRateProvider inner) => new Probed(inner, this);

        private sealed class Probed(IPartnerRateProvider inner, ConcurrencyProbe probe) : IPartnerRateProvider
        {
            public string PartnerId => inner.PartnerId;

            public async Task<Money> GetRateAsync(QuoteRequest request, CancellationToken ct)
            {
                var now = Interlocked.Increment(ref probe._inFlight);
                int seen;
                while (now > (seen = Volatile.Read(ref probe._max)) &&
                       Interlocked.CompareExchange(ref probe._max, now, seen) != seen)
                {
                }
                try
                {
                    return await inner.GetRateAsync(request, ct);
                }
                finally
                {
                    Interlocked.Decrement(ref probe._inFlight);
                }
            }
        }
    }
}
