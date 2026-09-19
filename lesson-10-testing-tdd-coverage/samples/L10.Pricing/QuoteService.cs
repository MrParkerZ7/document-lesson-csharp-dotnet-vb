namespace L10.Pricing;

public interface IQuoteRepository
{
    Task SaveAsync(Quote quote, CancellationToken ct = default);

    Task<Quote?> FindAsync(Guid id, CancellationToken ct = default);
}

/// <summary>Creates and accepts quotes. Time comes from TimeProvider, never DateTime.UtcNow.</summary>
public sealed class QuoteService(
    IQuoteRepository repository, PremiumCalculator calculator, TimeProvider time)
{
    public static readonly TimeSpan Validity = TimeSpan.FromDays(30);

    #region create
    public async Task<Quote> CreateAsync(QuoteRequest request, CancellationToken ct = default)
    {
        var now = time.GetUtcNow();
        var quote = new Quote(Guid.CreateVersion7(now), request,
            calculator.Calculate(request), now + Validity, QuoteStatus.Quoted);
        await repository.SaveAsync(quote, ct);
        return quote;
    }
    #endregion

    #region accept
    public async Task<Quote> AcceptAsync(Guid id, CancellationToken ct = default)
    {
        var quote = await repository.FindAsync(id, ct)
            ?? throw new KeyNotFoundException($"quote {id} not found");
        if (quote.Status != QuoteStatus.Quoted)
            throw new InvalidOperationException($"quote {id} is already {quote.Status}");

        var status = time.GetUtcNow() > quote.ValidUntil
            ? QuoteStatus.Expired
            : QuoteStatus.Accepted;
        var updated = quote with { Status = status };
        await repository.SaveAsync(updated, ct);
        return updated;
    }
    #endregion
}
