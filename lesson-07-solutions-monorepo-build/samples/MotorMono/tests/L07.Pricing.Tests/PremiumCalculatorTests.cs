using L07.Core;
using L07.Pricing.Vb;

namespace L07.Pricing.Tests;

public class PremiumCalculatorTests
{
    private static QuoteRequest Request(
        int age = 40, int claimFree = 0, int claims = 0, VehicleUse use = VehicleUse.Private,
        int engineCc = 1_600) =>
        new(CoverageClass.Class1, new Money(550_000m), age, claimFree, claims, use, engineCc);

    #region internals-test
    [Fact]
    public void Internal_base_rates_are_visible_here()
    {
        // BaseRates is internal to the L07.Pricing
        // assembly. Directory.Build.targets gave it
        // [InternalsVisibleTo("L07.Pricing.Tests")].
        Assert.Equal(0.021m, BaseRates.For(CoverageClass.Class1));
        Assert.Equal(0.004m, BaseRates.For(CoverageClass.Class3));
    }
    #endregion

    [Fact]
    public void The_worked_example_of_the_tariff_matches_the_cli()
    {
        IRatingRule[] rules = [new YoungDriverLoading(), new ClaimsLoading(), new NoClaimBonusVb()];

        var premium = new PremiumCalculator(rules).Calculate(Request(age: 23, claimFree: 4));

        Assert.Equal(11_550.00m, premium.Base.Amount);
        Assert.Equal(8_316.00m, premium.Net.Amount);
        Assert.Equal(33.26m, premium.StampDuty.Amount);
        Assert.Equal(584.45m, premium.Vat.Amount);
        Assert.Equal(8_933.71m, premium.Total.Amount);
    }

    [Theory]
    [InlineData(VehicleUse.Private, 1_600, 0)]
    [InlineData(VehicleUse.Commercial, 1_600, 288_750)]
    [InlineData(VehicleUse.Commercial, 3_200, 404_250)]
    public void Commercial_use_loads_the_base_premium(VehicleUse use, int engineCc, int expectedSatang)
    {
        var premium = new PremiumCalculator([new CommercialUseLoading()])
            .Calculate(Request(use: use, engineCc: engineCc));

        Assert.Equal(expectedSatang / 100m, premium.Net.Amount - premium.Base.Amount);
    }

    [Fact]
    public void Three_claims_in_five_years_declines_the_quote()
    {
        var calculator = new PremiumCalculator([new ClaimsLoading()]);

        var declined = Assert.Throws<QuoteDeclinedException>(() => calculator.Calculate(Request(claims: 3)));

        Assert.Equal(QuoteDeclinedException.ThreeOrMoreClaims, declined.Message);
    }

    #region parity-test
    [Theory]
    [InlineData(0, 0)]
    [InlineData(1, 0)]
    [InlineData(3, 0)]
    [InlineData(5, 0)]
    [InlineData(9, 0)]
    [InlineData(4, 1)]
    public void Csharp_port_and_vb_original_agree(int claimFreeYears, int claims)
    {
        var request = Request(claimFree: claimFreeYears, claims: claims);

        Assert.Equal(new NoClaimBonusVb().Factor(request), new NoClaimBonus().Factor(request));
    }
    #endregion

    [Fact]
    public void Each_line_names_the_module_its_rule_was_compiled_into()
    {
        string[] expected = ["L07.Pricing", "L07.Pricing.Vb"];

        var premium = new PremiumCalculator([new YoungDriverLoading(), new NoClaimBonusVb()])
            .Calculate(Request(age: 23, claimFree: 2));

        Assert.Equal(expected, premium.Adjustments.Select(line => line.Module));
    }

    [Fact]
    public void Money_refuses_to_add_different_currencies()
    {
        var thb = new Money(100m);

        Assert.Throws<InvalidOperationException>(() => thb.Plus(new Money(1m, "USD")));
    }
}
