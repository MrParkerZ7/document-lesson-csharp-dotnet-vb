using Microsoft.Extensions.Time.Testing;
using NSubstitute;

namespace L10.Pricing.Tests;

public class QuoteServiceTests
{
    #region fixture
    // xUnit creates a new instance of this class for every test:
    // the constructor is @BeforeEach, and nothing leaks between tests.
    private static readonly DateTimeOffset Nine =
        new(2026, 10, 1, 9, 0, 0, TimeSpan.Zero);

    private readonly FakeTimeProvider _time = new(Nine);
    private readonly IQuoteRepository _repo =
        Substitute.For<IQuoteRepository>();
    private readonly QuoteService _service;

    public QuoteServiceTests() =>
        _service = new(_repo, new PremiumCalculator(), _time);
    #endregion

    #region nsubstitute
    [Fact]
    public async Task Create_saves_a_quote_valid_for_30_days()
    {
        var ct = TestContext.Current.CancellationToken;
        var request = Requests.Standard();

        var quote = await _service.CreateAsync(request, ct);

        Assert.Equal(Nine.AddDays(30), quote.ValidUntil);
        await _repo.Received(1).SaveAsync(
            Arg.Is<Quote>(q => q.Status == QuoteStatus.Quoted),
            ct);
    }
    #endregion

    #region fake-time
    [Fact]
    public async Task Accepting_after_30_days_expires_the_quote()
    {
        var ct = TestContext.Current.CancellationToken;
        var quote = await _service.CreateAsync(
            Requests.Standard(), ct);
        _repo.FindAsync(quote.Id, ct).Returns(quote);

        _time.Advance(QuoteService.Validity); // still valid
        _time.Advance(TimeSpan.FromTicks(1)); // one tick late
        var result = await _service.AcceptAsync(quote.Id, ct);

        Assert.Equal(QuoteStatus.Expired, result.Status);
    }
    #endregion

    [Fact]
    public async Task Accepting_within_30_days_accepts_the_quote()
    {
        var ct = TestContext.Current.CancellationToken;
        var quote = await _service.CreateAsync(Requests.Standard(), ct);
        _repo.FindAsync(quote.Id, ct).Returns(quote);

        _time.Advance(TimeSpan.FromDays(30));
        var result = await _service.AcceptAsync(quote.Id, ct);

        Assert.Equal(QuoteStatus.Accepted, result.Status);
        await _repo.Received(1).SaveAsync(result, ct);
    }

    [Fact]
    public async Task Accepting_an_unknown_quote_throws()
    {
        var ct = TestContext.Current.CancellationToken;
        _repo.FindAsync(Arg.Any<Guid>(), ct).Returns((Quote?)null);

        await Assert.ThrowsAsync<KeyNotFoundException>(
            () => _service.AcceptAsync(Guid.NewGuid(), ct));
    }

    [Fact]
    public async Task A_quote_cannot_be_accepted_twice()
    {
        var ct = TestContext.Current.CancellationToken;
        var quote = await _service.CreateAsync(Requests.Standard(), ct);
        _repo.FindAsync(quote.Id, ct).Returns(quote with { Status = QuoteStatus.Accepted });

        await Assert.ThrowsAsync<InvalidOperationException>(
            () => _service.AcceptAsync(quote.Id, ct));
    }
}
