using System.Collections.Concurrent;
using System.Runtime.CompilerServices;

namespace L05.PartnerRates;

/// <summary>
/// Asks every partner for a rate at once, with a timeout per partner. Library code: every await
/// uses ConfigureAwait(false) so the class behaves the same in ASP.NET Core, a UI app or a test runner.
/// </summary>
public sealed class RateFanOut(
    IReadOnlyList<IPartnerRateProvider> partners, TimeProvider time, TimeSpan perPartnerTimeout)
{
    public TimeSpan PerPartnerTimeout => perPartnerTimeout;

    #region per-partner-timeout
    private async Task<PartnerOutcome> QueryOneAsync(
        IPartnerRateProvider partner, QuoteRequest request, CancellationToken ct)
    {
        long started = time.GetTimestamp();
        // this partner's own deadline, on the injected clock (tests move it by hand)
        using var deadline = new CancellationTokenSource(perPartnerTimeout, time);
        // cancelled when EITHER the caller gives up OR this partner's deadline passes
        using var linked = CancellationTokenSource.CreateLinkedTokenSource(ct, deadline.Token);
        try
        {
            var premium = await partner.GetRateAsync(request, linked.Token).ConfigureAwait(false);
            return new Quoted(partner.PartnerId, time.GetElapsedTime(started), premium);
        }
        catch (OperationCanceledException) when (!ct.IsCancellationRequested)
        {
            // our deadline fired, not the caller's token: a partner problem, not the caller's
            return new TimedOut(partner.PartnerId, time.GetElapsedTime(started));
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            return new Failed(partner.PartnerId, time.GetElapsedTime(started), ex.Message);
        }
    }
    #endregion

    #region fan-out
    public async Task<IReadOnlyList<PartnerOutcome>>
        QueryAllAsync(QuoteRequest request,
                      CancellationToken ct = default)
    {
        // start all 30 calls first: no await inside the Select
        Task<PartnerOutcome>[] calls = [.. partners
            .Select(p => QueryOneAsync(p, request, ct))];
        // then wait for every one of them, together
        return await Task.WhenAll(calls).ConfigureAwait(false);
    }

    public static Quoted? Best(IEnumerable<PartnerOutcome> all) =>
        all.OfType<Quoted>().MinBy(q => q.Premium.Amount);
    #endregion

    #region when-each
    public async IAsyncEnumerable<PartnerOutcome> StreamAsync(
        QuoteRequest request, [EnumeratorCancellation] CancellationToken ct = default)
    {
        Task<PartnerOutcome>[] calls = [.. partners.Select(p => QueryOneAsync(p, request, ct))];
        // .NET 9: hands back each task as it completes — no WhenAny loop re-scanning the list
        var inCompletionOrder = Task.WhenEach(calls).WithCancellation(ct).ConfigureAwait(false);
        await foreach (Task<PartnerOutcome> done in inCompletionOrder)
            yield return await done.ConfigureAwait(false);   // already complete: no wait
    }
    #endregion

    #region first-good-enough
    public async Task<Quoted?> FirstAtOrBelowAsync(
        QuoteRequest request, decimal targetPremium, CancellationToken ct = default)
    {
        using var stop = CancellationTokenSource.CreateLinkedTokenSource(ct);
        await foreach (var outcome in StreamAsync(request, stop.Token).ConfigureAwait(false))
        {
            if (outcome is Quoted q && q.Premium.Amount <= targetPremium)
            {
                await stop.CancelAsync().ConfigureAwait(false);   // tell every other partner to stop
                return q;
            }
        }
        return null;
    }
    #endregion

    #region throttle
    public async Task<IReadOnlyList<PartnerOutcome>> QueryAllThrottledAsync(
        QuoteRequest request, int maxConcurrent, CancellationToken ct = default)
    {
        var results = new ConcurrentBag<PartnerOutcome>();
        var options = new ParallelOptions
        {
            MaxDegreeOfParallelism = maxConcurrent,   // e.g. a shared outbound connection budget
            CancellationToken = ct,
        };
        // at most maxConcurrent partner calls in flight at any moment
        await Parallel.ForEachAsync(partners, options, async (partner, token) =>
            results.Add(await QueryOneAsync(partner, request, token).ConfigureAwait(false)))
            .ConfigureAwait(false);
        return [.. results.OrderBy(r => r.PartnerId)];
    }
    #endregion
}
