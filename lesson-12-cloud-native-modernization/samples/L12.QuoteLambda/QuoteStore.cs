using System.Collections.Concurrent;
using L12.RatingVb;

namespace L12.QuoteLambda;

public sealed record QuoteRequest(
    string Coverage, decimal SumInsured, int DriverAge,
    int ClaimsLast5Years, bool Commercial);

public sealed record StoredQuote(
    string QuoteId, decimal NetPremium, decimal StampDuty,
    decimal Vat, decimal Total, string Currency);

public interface IQuoteStore
{
    StoredQuote Save(PremiumBreakdown premium);
    StoredQuote? Find(string quoteId);
}

/// <summary>
/// Lives as long as ONE execution environment. Lambda runs many environments in parallel and
/// recycles them, so a production store is DynamoDB — this one exists for the sample and tests.
/// </summary>
public sealed class InMemoryQuoteStore : IQuoteStore
{
    readonly ConcurrentDictionary<string, StoredQuote> quotes = new();

    public StoredQuote Save(PremiumBreakdown premium)
    {
        var quote = new StoredQuote(Guid.NewGuid().ToString("N"), premium.Net,
            premium.StampDuty, premium.Vat, premium.Total, "THB");
        quotes[quote.QuoteId] = quote;
        return quote;
    }

    public StoredQuote? Find(string quoteId) => quotes.GetValueOrDefault(quoteId);
}
