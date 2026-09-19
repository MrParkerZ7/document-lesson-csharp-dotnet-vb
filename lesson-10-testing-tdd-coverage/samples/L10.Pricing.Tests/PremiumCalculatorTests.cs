namespace L10.Pricing.Tests;

public class PremiumCalculatorTests
{
    private readonly PremiumCalculator _calculator = new();

    #region rating-sheet
    // Expected totals are worked by hand from the (illustrative) rating sheet,
    // before the code exists — that is what makes this a test, not a snapshot.
    public static TheoryData<string, decimal> Sheet => new()
    {
        { "standard: 36, 10 claim-free years, Class 1", 6_445.68m },
        { "young: 23, one claim, Class 1", 16_759.41m },
        { "commercial: four claims, Class 3", 3_330.91m },
        // added after Stryker showed `< 25` -> `<= 25` survived
        { "boundary: turns 25 on the start date", 6_445.68m },
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

        Assert.Equal(new Money(6_000.00m, "THB"), premium.Net);
        Assert.Equal(new Money(24m, "THB"), premium.StampDuty);
        Assert.Equal(new Money(421.68m, "THB"), premium.Vat);
    }

    [Theory]
    [InlineData(CoverageClass.Class1, 0.020)]
    [InlineData(CoverageClass.Class2Plus, 0.012)]
    [InlineData(CoverageClass.Class3Plus, 0.009)]
    [InlineData(CoverageClass.Class3, 0.005)]
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
        "commercial" => Requests.Standard(CoverageClass.Class3, 400_000m, age: 45,
            licenceYears: 20, claims: 4, use: VehicleUse.Commercial),
        _ => throw new ArgumentException($"unknown scenario {name}", nameof(name)),
    };
}
