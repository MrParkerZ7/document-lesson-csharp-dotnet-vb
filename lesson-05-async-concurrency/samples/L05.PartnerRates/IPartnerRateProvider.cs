namespace L05.PartnerRates;

/// <summary>An external rating partner. Some are slow, some fail, some never answer.</summary>
public interface IPartnerRateProvider
{
    string PartnerId { get; }

    #region contract
    // Task<T> is the promise; CancellationToken is how the caller says "stop".
    Task<Money> GetRateAsync(QuoteRequest request, CancellationToken ct);
    #endregion
}

/// <summary>What one partner call produced — the fan-out never throws for a partner problem.</summary>
public abstract record PartnerOutcome(string PartnerId, TimeSpan Elapsed);

public sealed record Quoted(string PartnerId, TimeSpan Elapsed, Money Premium)
    : PartnerOutcome(PartnerId, Elapsed);

public sealed record TimedOut(string PartnerId, TimeSpan Elapsed)
    : PartnerOutcome(PartnerId, Elapsed);

public sealed record Failed(string PartnerId, TimeSpan Elapsed, string Reason)
    : PartnerOutcome(PartnerId, Elapsed);
