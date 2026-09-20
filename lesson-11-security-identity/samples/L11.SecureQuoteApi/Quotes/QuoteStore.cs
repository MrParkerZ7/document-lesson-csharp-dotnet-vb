using System.Collections.Concurrent;

namespace L11.SecureQuoteApi.Quotes;

public enum QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }

public readonly record struct Money(decimal Amount, string Currency = "THB");

public sealed record Quote(string QuoteId, string OwnerId, Money Total, QuoteStatus Status);

public sealed record QuoteRequest(string Make, int Year, decimal SumInsured);

/// <summary>
/// In-memory quotes. Every premium here is illustrative, not a real tariff: the MotorQuote tariff
/// shared by every lesson of the track, reduced to what a bare sum insured allows - Class 1, private
/// use, no loadings and no no-claim discount, because the request carries no driver or claims data.
/// </summary>
public sealed class QuoteStore
{
    private readonly ConcurrentDictionary<string, Quote> _quotes = new();
    private int _lastId = 1000;

    private const decimal Class1Rate = 0.021m;

    // money rounds half away from zero, to the satang - the default (half to even) can lose one
    private static decimal Round(decimal amount) =>
        decimal.Round(amount, 2, MidpointRounding.AwayFromZero);

    public QuoteStore()
    {
        Add("cust-a", 850_000m);   // Q-1001 — owned by the "owner" caller in the tests
        Add("cust-b", 420_000m);   // Q-1002
    }

    public Quote Add(string ownerId, decimal sumInsured)
    {
        var net = Round(sumInsured * Class1Rate);            // base x (1 + no loadings) x (1 - 0%)
        var duty = Round(net * 0.004m);                     // stamp duty 0.4% of net
        var vat = Round((net + duty) * 0.07m);              // VAT 7% on net + duty
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
