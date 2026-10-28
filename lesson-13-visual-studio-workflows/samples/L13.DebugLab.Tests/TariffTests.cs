namespace L13.DebugLab.Tests;

public class TariffTests
{
    #region TestsWorkedExample
    // Test Explorer groups by trait: Trait > Category > Tariff. The CLI filter is the same string.
    [Fact, Trait("Category", "Tariff")]
    public void Worked_example_prices_to_the_curriculum_total()
    {
        var request = new QuoteRequest(
            new Vehicle("Make0", "Model0", 2024, 1500, VehicleUse.Private, Money.Thb(550_000)),
            new Driver(new DateOnly(2002, 6, 15), 4, 0), CoverageClass.Class1, QuoteBatch.StartDate);

        var premium = QuoteCalculator.Price(request);

        Assert.Equal(8316.00m, premium.Net.Amount);
        Assert.Equal(33.26m, premium.StampDuty.Amount);
        Assert.Equal(584.45m, premium.Vat.Amount);
        Assert.Equal(8933.71m, premium.Total.Amount);
    }
    #endregion

    [Theory, Trait("Category", "Tariff")]
    [InlineData(0, 0.0)]
    [InlineData(1, 0.20)]
    [InlineData(2, 0.25)]
    [InlineData(3, 0.30)]
    [InlineData(4, 0.40)]
    [InlineData(5, 0.50)]
    [InlineData(12, 0.50)]
    public void No_claim_discount_follows_the_schedule(int claimFreeYears, double expected)
    {
        var driver = new Driver(new DateOnly(1990, 1, 1), claimFreeYears, 0);
        Assert.Equal((decimal)expected, Tariff.NoClaimDiscount(driver));
    }

    [Theory, Trait("Category", "Tariff")]
    [InlineData(0, 0.0)]
    [InlineData(1, 0.10)]
    [InlineData(2, 0.25)]
    public void Claims_loading_follows_the_schedule(int claims, double expected) =>
        Assert.Equal((decimal)expected, Tariff.ClaimsLoading(claims));

    [Fact, Trait("Category", "Tariff")]
    public void Three_claims_decline_the_quote()
    {
        var ex = Assert.Throws<QuoteDeclinedException>(() => Tariff.ClaimsLoading(3));
        Assert.Equal("3+ claims in 5 years", ex.Message);
    }

    [Fact, Trait("Category", "Tariff")]
    public void Commercial_loading_is_higher_above_3000_cc()
    {
        Vehicle Van(int cc) => new("Make1", "Van", 2022, cc, VehicleUse.Commercial, Money.Thb(400_000));
        Assert.Equal(0.25m, Tariff.CommercialLoading(Van(3000)));
        Assert.Equal(0.35m, Tariff.CommercialLoading(Van(3001)));
    }

    [Fact, Trait("Category", "Tariff")]
    public void Satang_rounds_a_midpoint_away_from_zero() =>
        Assert.Equal(0.02m, Tariff.Satang(0.015m));
}
