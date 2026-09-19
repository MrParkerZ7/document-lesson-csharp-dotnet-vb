using System.Collections.Concurrent;

namespace L10.Pricing;

/// <summary>A real, in-memory implementation — a fake you can hand to tests and to the API.</summary>
public sealed class InMemoryQuoteRepository : IQuoteRepository
{
    private readonly ConcurrentDictionary<Guid, Quote> _quotes = new();

    public Task SaveAsync(Quote quote, CancellationToken ct = default)
    {
        _quotes[quote.Id] = quote;
        return Task.CompletedTask;
    }

    public Task<Quote?> FindAsync(Guid id, CancellationToken ct = default) =>
        Task.FromResult(_quotes.TryGetValue(id, out var quote) ? quote : null);
}
