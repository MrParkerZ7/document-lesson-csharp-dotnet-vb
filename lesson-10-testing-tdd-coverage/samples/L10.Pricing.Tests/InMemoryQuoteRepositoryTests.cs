using Microsoft.Extensions.Time.Testing;

namespace L10.Pricing.Tests;

public class InMemoryQuoteRepositoryTests
{
    #region fake-not-mock
    [Fact]
    public async Task A_saved_quote_can_be_found_and_accepted()
    {
        var ct = TestContext.Current.CancellationToken;
        var repo = new InMemoryQuoteRepository();   // a fake: real behaviour, no network
        var service = new QuoteService(repo, new PremiumCalculator(), new FakeTimeProvider());

        var quote = await service.CreateAsync(Requests.Standard(), ct);
        await service.AcceptAsync(quote.Id, ct);

        var stored = await repo.FindAsync(quote.Id, ct);
        Assert.Equal(QuoteStatus.Accepted, stored?.Status);
    }
    #endregion

    [Fact]
    public async Task An_unknown_id_is_not_found()
    {
        var repo = new InMemoryQuoteRepository();

        var found = await repo.FindAsync(Guid.NewGuid(), TestContext.Current.CancellationToken);

        Assert.Null(found);
    }
}
