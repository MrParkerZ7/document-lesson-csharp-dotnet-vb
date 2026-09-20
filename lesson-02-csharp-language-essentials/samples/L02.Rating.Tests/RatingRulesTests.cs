namespace L02.Rating.Tests;

public class RatingRulesTests
{
    // Every TheoryData row sits on its own line: the lesson PDF counts them at build time.
    public static TheoryData<CoverageClass, decimal> BaseRates => new()
    {
        { CoverageClass.Class1, 11_550m },
        { CoverageClass.Class2Plus, 6_600m },
        { CoverageClass.Class3Plus, 4_950m },
        { CoverageClass.Class3, 2_200m },
    };

    [Theory]
    [MemberData(nameof(BaseRates))]
    public void BaseRate_depends_on_coverage_class(CoverageClass coverage, decimal expected) =>
        Assert.Equal(expected, RatingRules.BaseRate(coverage, new Money(550_000m)));

    [Fact]
    public void BaseRate_rejects_an_undefined_enum_value() =>
        Assert.Throws<ArgumentOutOfRangeException>(
            () => RatingRules.BaseRate((CoverageClass)7, new Money(1m)));

    #region theory
    // decimal is not a valid attribute argument (error CS0182), so
    // [InlineData(24, 0.20m)] does not compile. TheoryData<,> does.
    public static TheoryData<int, decimal> AgeBands => new()
    {
        { 18, 0.20m },
        { 24, 0.20m },
        { 25, 0m },
        { 70, 0m },
    };

    [Theory]
    [MemberData(nameof(AgeBands))]
    public void AgeLoading_follows_the_age_bands(int age, decimal expected) =>
        Assert.Equal(expected, RatingRules.AgeLoading(age));
    #endregion

    [Fact]
    public void AgeLoading_refuses_drivers_under_18() =>
        Assert.Throws<NotSupportedException>(() => RatingRules.AgeLoading(17));

    public static TheoryData<int, decimal> ClaimBands => new()
    {
        { 0, 0m },
        { 1, 0.10m },
        { 2, 0.25m },
    };

    [Theory]
    [MemberData(nameof(ClaimBands))]
    public void ClaimsLoading_follows_the_claim_count(int claims, decimal expected) =>
        Assert.Equal(expected, RatingRules.ClaimsLoading(claims));

    [Fact]
    public void ClaimsLoading_declines_three_claims()
    {
        var e = Assert.Throws<QuoteDeclinedException>(() => RatingRules.ClaimsLoading(3));
        Assert.Equal("3+ claims in 5 years", e.Reason);
    }

    // ints and enums ARE valid attribute arguments: express the percentage as an int
    [Theory]
    [InlineData(0, 0, 0)]
    [InlineData(1, 0, 20)]
    [InlineData(2, 0, 25)]
    [InlineData(3, 0, 30)]
    [InlineData(4, 0, 40)]
    [InlineData(5, 0, 50)]
    [InlineData(9, 0, 50)]
    [InlineData(9, 1, 0)]
    public void NoClaimBonus_grows_with_claim_free_licence_years(int licenceYears, int claims, int percent) =>
        Assert.Equal(percent / 100m,
            RatingRules.NoClaimBonus(new Driver(new DateOnly(1990, 1, 1), licenceYears, claims)));

    [Theory]
    [InlineData(VehicleUse.Private, 3_500, 0)]
    [InlineData(VehicleUse.Commercial, 3_000, 25)]
    [InlineData(VehicleUse.Commercial, 3_001, 35)]
    public void UseLoading_charges_commercial_vehicles(VehicleUse use, int engineCc, int percent) =>
        Assert.Equal(percent / 100m,
            RatingRules.UseLoading(new Vehicle("Isuzu", "D-Max", 2023, engineCc, use, new Money(900_000m))));

    [Fact]
    public void Round_is_half_away_from_zero_not_bankers()
    {
        Assert.Equal(2.34m, Math.Round(2.345m, 2));        // the default: to even
        Assert.Equal(2.35m, RatingRules.Round(2.345m));    // the premium rule
    }
}
