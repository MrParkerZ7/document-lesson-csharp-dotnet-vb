using Microsoft.Identity.Abstractions;

namespace L11.SecureQuoteApi.Partners;

public sealed record PartnerRate(string PartnerId, string QuoteId, decimal NetPremium);

/// <summary>
/// Calls a rating partner's API that trusts the same Entra tenant. Compiled, not run by the tests:
/// acquiring a token needs a real tenant.
/// </summary>
public sealed class PartnerRatesClient(IDownstreamApi api)
{
    #region downstream
    // On behalf of the caller: the incoming token is exchanged (OBO) for a
    // partner token that still names the customer. Scopes: DownstreamApis:PartnerRates
    public Task<PartnerRate?> RateForCustomerAsync(string quoteId, CancellationToken ct) =>
        api.GetForUserAsync<PartnerRate>("PartnerRates",
            o => o.RelativePath = $"rates/{quoteId}",
            cancellationToken: ct);

    // As the API itself (client credentials): no user in the token, app roles only
    public Task<PartnerRate?> RateForBatchAsync(string quoteId, CancellationToken ct) =>
        api.GetForAppAsync<PartnerRate>("PartnerRates", o =>
        {
            o.RelativePath = $"batch-rates/{quoteId}";
            o.Scopes = ["api://l11-partner-api/.default"];   // app tokens: .default only
        }, ct);
    #endregion
}
