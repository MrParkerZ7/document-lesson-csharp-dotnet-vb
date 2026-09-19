using System.Collections.Concurrent;

namespace L11.SecureQuoteApi.Quotes;

public enum QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }

public readonly record struct Money(decimal Amount, string Currency = "THB");

public sealed record Quote(string QuoteId, string OwnerId, Money Total, QuoteStatus Status);

public sealed record QuoteRequest(string Make, int Year, decimal SumInsured);

/// <summary>In-memory quotes. Every premium here is illustrative, not a real tariff.</summary>
public sealed class QuoteStore
{
    private readonly ConcurrentDictionary<string, Quote> _quotes = new();
    private int _lastId = 1000;

    public QuoteStore()
    {
        Add("cust-a", 850_000m);   // Q-1001 — owned by the "owner" caller in the tests
        Add("cust-b", 420_000m);   // Q-1002
    }

    public Quote Add(string ownerId, decimal sumInsured)
    {
        var net = decimal.Round(sumInsured * 0.021m, 2);          // illustrative class-1 rate
        var duty = decimal.Round(net * 0.004m, 2);                 // stamp duty 0.4%
        var vat = decimal.Round((net + duty) * 0.07m, 2);          // VAT 7% on net + duty
        var id = $"Q-{Interlocked.Increment(ref _lastId)}";
        var quote = new Quote(id, ownerId, new Money(net + duty + vat), QuoteStatus.Quoted);
        _quotes[id] = quote;
        return quote;
    }

    public Quote? Find(string id) => _quotes.GetValueOrDefault(id);

    public Quote Accept(Quote quote) =>
        _quotes[quote.QuoteId] = quote with { Status = QuoteStatus.Accepted };

    public IReadOnlyList<Quote> Referrals() =>
        _quotes.Values.Where(q => q.Total.Amount > 15_000m).OrderBy(q => q.QuoteId).ToList();
}
