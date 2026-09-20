using Microsoft.Extensions.Time.Testing;

namespace L10.Pricing.WeakTests;

/// <summary>
/// Executes every line and branch of L10.Pricing and asserts almost nothing.
/// Do not copy this: it exists to show that 100% coverage is not 100% tested.
/// </summary>
public class WeakSuite
{
    #region weak
    [Fact]
    public void Every_rating_rule_runs()
    {
        for (var years = -1; years <= 5; years++)
            Swallow(() => NoClaimBonus.DiscountFor(years));
        for (var claims = 0; claims <= 3; claims++)
            Swallow(() => PremiumCalculator.ClaimsLoading(claims));
        foreach (var coverage in Enum.GetValues<CoverageClass>())
            PremiumCalculator.BaseRate(coverage);
        Swallow(() => PremiumCalculator.BaseRate((CoverageClass)99));
        PremiumCalculator.AgeAt(new DateOnly(2001, 10, 2), Requests.Start);

        var calculator = new PremiumCalculator();
        Swallow(() => calculator.Calculate(null!));
        Assert.NotNull(calculator.Calculate(Requests.Standard()));
        Assert.NotNull(calculator.Calculate(Requests.Standard(
            age: 23, claims: 1, use: VehicleUse.Commercial)));
        Assert.NotNull(calculator.Calculate(Requests.Standard(
            claims: 2, use: VehicleUse.Commercial, engineCc: 3_500)));
    }
    #endregion

    [Fact]
    public async Task Every_quote_path_runs()
    {
        var ct = TestContext.Current.CancellationToken;
        var time = new FakeTimeProvider();
        var repo = new InMemoryQuoteRepository();
        var service = new QuoteService(repo, new PremiumCalculator(), time);

        var first = await service.CreateAsync(Requests.Standard(), ct);
        await service.AcceptAsync(first.Id, ct);
        await SwallowAsync(() => service.AcceptAsync(first.Id, ct));
        await SwallowAsync(() => service.AcceptAsync(Guid.NewGuid(), ct));

        var second = await service.CreateAsync(Requests.Standard(), ct);
        time.Advance(TimeSpan.FromDays(31));
        Assert.NotNull(await service.AcceptAsync(second.Id, ct));
    }

    private static void Swallow(Action action)
    {
        try { action(); } catch (Exception) { /* weak on purpose */ }
    }

    private static async Task SwallowAsync(Func<Task> action)
    {
        try { await action(); } catch (Exception) { /* weak on purpose */ }
    }
}
