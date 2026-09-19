namespace L10.Pricing.Tests;

public class NoClaimBonusTests
{
    #region first-test
    [Fact]
    public void No_claim_free_years_means_no_discount()
    {
        var discount = NoClaimBonus.DiscountFor(claimFreeYears: 0);

        Assert.Equal(0.00m, discount);
    }
    #endregion

    #region theory
    public static TheoryData<int, decimal> Table => new()
    {
        { 1, 0.20m }, { 2, 0.25m }, { 3, 0.30m },
        { 4, 0.40m }, { 5, 0.50m }, { 9, 0.50m },
    };

    [Theory]
    [MemberData(nameof(Table))]
    public void Discount_grows_with_claim_free_years(
        int years, decimal expected)
    {
        var discount = NoClaimBonus.DiscountFor(years);

        Assert.Equal(expected, discount);
    }
    #endregion

    #region throws
    [Fact]
    public void Negative_years_are_rejected()
    {
        var ex = Assert.Throws<ArgumentOutOfRangeException>(
            () => NoClaimBonus.DiscountFor(-1));

        Assert.Equal("claimFreeYears", ex.ParamName);
    }
    #endregion
}
