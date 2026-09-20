namespace L10.Pricing.Tests;

public class PremiumCalculatorTests
{
    private readonly PremiumCalculator _calculator = new();

    #region rating-sheet
    // Expected totals are worked by hand from the canonical tariff (the curriculum's
    // "Canonical tariff" section), before the code exists — that is what makes this
    // a test, not a snapshot. Illustrative rates, not a real tariff.
    public static TheoryData<string, decimal> Sheet => new()
    {
        { "standard: 36, 10 claim-free years, Class 1", 6_767.96m },
        { "young: 23, one claim, Class 1", 17_596.71m },
        { "commercial: two claims, Class 3", 2_578.27m },
        { "heavy: 3,500 cc commercial, Class 3", 1_160.22m },
        // added after Stryker showed `< 25` -> `<= 25` survived
        { "boundary: turns 25 on the start date", 6_767.96m },
        // added after Stryker showed `> 3_000` -> `>= 3_000` survived
        { "engine: exactly 3,000 cc commercial, Class 3", 1_074.28m },
        // the curriculum's worked example, priced by every lesson in the track
        { "track: 23, four claim-free years, 550,000", 8_933.71m },
    };

    [Theory]
    [MemberData(nameof(Sheet))]
    public void Total_matches_the_rating_sheet(string scenario, decimal total)
    {
        var premium = _calculator.Calculate(Scenario(scenario));

        Assert.Equal(total, premium.Total.Amount);
    }
    #endregion

    [Fact]
    public void Standard_premium_breaks_down_into_net_duty_and_vat()
    {
        var premium = _calculator.Calculate(Requests.Standard());

        Assert.Equal(new Money(6_300.00m, "THB"), premium.Net);
        Assert.Equal(new Money(25.20m, "THB"), premium.StampDuty);
        Assert.Equal(new Money(442.76m, "THB"), premium.Vat);
    }

    [Theory]
    [InlineData(CoverageClass.Class1, 0.021)]
    [InlineData(CoverageClass.Class2Plus, 0.012)]
    [InlineData(CoverageClass.Class3Plus, 0.009)]
    [InlineData(CoverageClass.Class3, 0.004)]
    public void Base_rate_depends_on_the_coverage_class(CoverageClass coverage, double rate) =>
        Assert.Equal((decimal)rate, PremiumCalculator.BaseRate(coverage));

    #region enum-trap
    [Fact]
    public void An_undefined_coverage_class_is_rejected()
    {
        var bogus = (CoverageClass)99; // compiles: C# enums are open

        Assert.Throws<ArgumentOutOfRangeException>(
            () => PremiumCalculator.BaseRate(bogus));
    }
    #endregion

    #region decline
    [Theory]
    [InlineData(3)] // the boundary the tariff declines at
    [InlineData(9)]
    public void Three_or_more_claims_is_declined_rather_than_priced(int claims)
    {
        var request = Requests.Standard(claims: claims);

        var ex = Assert.Throws<QuoteDeclinedException>(
            () => _calculator.Calculate(request));

        Assert.Equal("3+ claims in 5 years", ex.Message);
    }
    #endregion

    [Theory]
    [InlineData("2001-10-01", 25)] // birthday on the start date
    [InlineData("2001-10-02", 24)] // birthday the day after
    public void Age_is_counted_in_whole_years_at_the_start_date(string dateOfBirth, int age) =>
        Assert.Equal(age, PremiumCalculator.AgeAt(DateOnly.Parse(dateOfBirth), Requests.Start));

    [Fact]
    public void A_null_request_is_rejected() =>
        Assert.Throws<ArgumentNullException>(() => _calculator.Calculate(null!));

    private static QuoteRequest Scenario(string name) => name.Split(':')[0] switch
    {
        "standard" => Requests.Standard(),
        "young" => Requests.Standard(age: 23, licenceYears: 3, claims: 1),
        "boundary" => Requests.Standard(age: 25, licenceYears: 5),
        "track" => Requests.Standard(sumInsured: 550_000m, age: 23, licenceYears: 4),
        "commercial" => Requests.Standard(CoverageClass.Class3, 400_000m, age: 45,
            licenceYears: 20, claims: 2, use: VehicleUse.Commercial),
        "heavy" => Requests.Standard(CoverageClass.Class3, 400_000m, age: 45,
            licenceYears: 20, use: VehicleUse.Commercial, engineCc: 3_500),
        "engine" => Requests.Standard(CoverageClass.Class3, 400_000m, age: 45,
            licenceYears: 20, use: VehicleUse.Commercial, engineCc: 3_000),
        _ => throw new ArgumentException($"unknown scenario {name}", nameof(name)),
    };
}
