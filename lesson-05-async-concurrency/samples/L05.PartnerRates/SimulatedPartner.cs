namespace L05.PartnerRates;

public enum PartnerBehaviour { Quotes, Fails, Hangs, IgnoresCancellation }

/// <summary>
/// A partner that answers after <see cref="Latency"/>. The "network call" is a TimeProvider timer,
/// so a test can move time forward instead of sleeping. This is library code, so every await uses
/// ConfigureAwait(false): it must behave the same under any SynchronizationContext.
/// </summary>
public sealed class SimulatedPartner(
    string partnerId, TimeSpan latency, decimal rateBps, PartnerBehaviour behaviour, TimeProvider time)
    : IPartnerRateProvider
{
    private int _finished, _cancelled;

    public string PartnerId => partnerId;
    public TimeSpan Latency => latency;
    public decimal RateBps => rateBps;
    public PartnerBehaviour Behaviour => behaviour;

    /// <summary>Calls whose simulated network wait ran to the end.</summary>
    public int FinishedCalls => Volatile.Read(ref _finished);

    /// <summary>Calls that observed cancellation before the partner answered.</summary>
    public int CancelledCalls => Volatile.Read(ref _cancelled);

    #region partner-call
    public async Task<Money> GetRateAsync(
        QuoteRequest request, CancellationToken ct)
    {
        // the "HTTP call" is a timer: no thread waits for it
        await NetworkAsync(ct).ConfigureAwait(false);

        if (behaviour == PartnerBehaviour.Fails)
            throw new HttpRequestException($"{partnerId}: 503");

        var premium = request.SumInsured.Amount * rateBps;
        return new Money(decimal.Round(premium / 10_000m, 2));
    }
    #endregion

    private async Task NetworkAsync(CancellationToken ct)
    {
        var wait = behaviour == PartnerBehaviour.Hangs ? Timeout.InfiniteTimeSpan : latency;
        // a partner that ignores the token keeps running after its caller gives up
        var token = behaviour == PartnerBehaviour.IgnoresCancellation ? CancellationToken.None : ct;
        try
        {
            await Task.Delay(wait, time, token).ConfigureAwait(false);
            Interlocked.Increment(ref _finished);
        }
        catch (OperationCanceledException)
        {
            Interlocked.Increment(ref _cancelled);
            throw;
        }
    }
}

public static class PartnerCatalog
{
    public const int PartnerCount = 30;

    /// <summary>
    /// 30 partners P01..P30. Fast ones answer in 60–189 ms, every fifth one takes 320 ms or more,
    /// three return errors and two never answer. Rates are basis points of the sum insured and are
    /// illustrative, not a real tariff.
    /// </summary>
    public static IReadOnlyList<SimulatedPartner> Create(TimeProvider time)
    {
        var partners = new List<SimulatedPartner>(PartnerCount);
        for (var i = 1; i <= PartnerCount; i++)
        {
            var slow = i % 5 == 0;
            var latency = TimeSpan.FromMilliseconds(slow ? 300 + i * 4 : 60 + i * 37 % 130);
            var rateBps = 180m + i * 53 % 90;
            var behaviour = i switch
            {
                4 or 17 or 26 => PartnerBehaviour.Fails,
                11 or 23 => PartnerBehaviour.Hangs,
                _ => PartnerBehaviour.Quotes,
            };
            partners.Add(new SimulatedPartner($"P{i:00}", latency, rateBps, behaviour, time));
        }
        return partners;
    }
}
