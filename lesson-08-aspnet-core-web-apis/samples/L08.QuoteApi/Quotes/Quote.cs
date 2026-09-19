using System.Collections.Concurrent;
using MotorQuote.Rating;

namespace L08.QuoteApi.Quotes;

public enum QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }

public enum AcceptOutcome { Accepted, NotFound, AlreadyAccepted, Expired }

/// <summary>A priced quote. The in-memory store shares instances across requests, so state changes lock.</summary>
public sealed class Quote(Guid id, QuoteRequest request, PremiumBreakdown premium, DateTimeOffset validUntil)
{
    private readonly Lock _gate = new();

    public Guid Id { get; } = id;
    public QuoteRequest Request { get; } = request;
    public PremiumBreakdown Premium { get; } = premium;
    public DateTimeOffset ValidUntil { get; } = validUntil;
    public QuoteStatus Status { get; private set; } = QuoteStatus.Quoted;
    public string? PolicyNumber { get; private set; }

    public AcceptOutcome Accept(DateTimeOffset now, Func<string> nextPolicyNumber)
    {
        lock (_gate)
        {
            if (Status == QuoteStatus.Accepted) return AcceptOutcome.AlreadyAccepted;
            if (now > ValidUntil)
            {
                Status = QuoteStatus.Expired;
                return AcceptOutcome.Expired;
            }
            Status = QuoteStatus.Accepted;
            PolicyNumber = nextPolicyNumber();
            return AcceptOutcome.Accepted;
        }
    }
}

public interface IQuoteStore
{
    void Add(Quote quote);
    Quote? Find(Guid id);
}

/// <summary>Singleton: one dictionary for the whole process (lesson 09 replaces it with EF Core).</summary>
public sealed class InMemoryQuoteStore : IQuoteStore
{
    private readonly ConcurrentDictionary<Guid, Quote> _quotes = new();

    public void Add(Quote quote) => _quotes[quote.Id] = quote;

    public Quote? Find(Guid id) => _quotes.GetValueOrDefault(id);
}

/// <summary>Singleton: policy numbers must be unique across requests.</summary>
public sealed class PolicyNumbers
{
    private int _last;

    public string Next() => $"MQ-{Interlocked.Increment(ref _last):D6}";
}
