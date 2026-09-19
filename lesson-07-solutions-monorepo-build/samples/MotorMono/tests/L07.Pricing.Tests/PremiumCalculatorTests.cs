using L07.Core;
using L07.Pricing.Vb;

namespace L07.Pricing.Tests;

public class PremiumCalculatorTests
{
    private static QuoteRequest Request(
        int age = 40, int claimFree = 0, int claims = 0, VehicleUse use = VehicleUse.Private) =>
        new(CoverageClass.Class1, new Money(850_000m), age, claimFree, claims, use);

    #region internals-test
    [Fact]
    public void Internal_base_rates_are_visible_here()
    {
        // BaseRates is internal to the L07.Pricing
        // assembly. Directory.Build.targets gave it
        // [InternalsVisibleTo("L07.Pricing.Tests")].
        Assert.Equal(0.018m, BaseRates.For(CoverageClass.Class1));
        Assert.Equal(0.004m, BaseRates.For(CoverageClass.Class3));
    }
    #endregion

    [Fact]
    public void Young_driver_with_three_claim_free_years_matches_the_cli()
    {
        IRatingRule[] rules = [new YoungDriverLoading(), new ClaimsLoading(), new NoClaimBonusVb()];

        var premium = new PremiumCalculator(rules).Calculate(Request(age: 23, claimFree: 3));

        Assert.Equal(15_300.00m, premium.Base.Amount);
        Assert.Equal(14_535.00m, premium.Net.Amount);
        Assert.Equal(58.14m, premium.StampDuty.Amount);
        Assert.Equal(1_021.52m, premium.Vat.Amount);
        Assert.Equal(15_614.66m, premium.Total.Amount);
    }

    [Theory]
    [InlineData(VehicleUse.Private, 0)]
    [InlineData(VehicleUse.Commercial, 229_500)]
    public void Commercial_use_adds_fifteen_percent(VehicleUse use, int expectedSatang)
    {
        var premium = new PremiumCalculator([new CommercialUseLoading()]).Calculate(Request(use: use));

        Assert.Equal(expectedSatang / 100m, premium.Net.Amount - premium.Base.Amount);
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
