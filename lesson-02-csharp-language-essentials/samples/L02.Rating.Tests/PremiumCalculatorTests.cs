using System.Globalization;

namespace L02.Rating.Tests;

public class PremiumCalculatorTests
{
    #region worked-example
    [Fact]
    public void Calculate_matches_the_worked_example()
    {
        Premium p = PremiumCalculator.Calculate(Examples.YoungDriver());

        Assert.Equal(11_550.00m, p.Base);       // 550,000 x 2.1%
        Assert.Equal(2_310.00m, p.Loadings);    // age 23 -> +20%
        Assert.Equal(4_158.00m, p.Discount);    // 4 claim-free years -> 30%
        Assert.Equal(9_702.00m, p.Net);
        Assert.Equal(38.81m, p.StampDuty);      // 38.808 rounded
        Assert.Equal(681.86m, p.Vat);           // 681.8567 rounded
        Assert.Equal(10_422.67m, p.Total);
    }
    #endregion

    [Fact]
    public void Calculate_adds_the_commercial_loading()
    {
        var privateUse = PremiumCalculator.Calculate(Examples.YoungDriver());
        var commercial = PremiumCalculator.Calculate(Examples.YoungDriver(use: VehicleUse.Commercial));
        Assert.True(commercial.Total > privateUse.Total);
    }

    [Fact]
    public void TryCalculate_reports_why_a_quote_was_declined()
    {
        bool ok = PremiumCalculator.TryCalculate(Examples.YoungDriver(claims: 3), out var premium, out var reason);

        Assert.False(ok);
        Assert.Null(premium);
        Assert.Equal("3+ claims in 5 years", reason);   // no ! needed: [NotNullWhen(false)]
    }

    // DateOnly is not an attribute argument either: pass ISO text, parse it with the invariant culture
    [Theory]
    [InlineData("2001-10-01", 25)]
    [InlineData("2001-10-02", 24)]
    public void AgeOn_counts_age_on_the_policy_start_date(string dateOfBirth, int expectedAge)
    {
        var dob = DateOnly.ParseExact(dateOfBirth, "yyyy-MM-dd", CultureInfo.InvariantCulture);
        Assert.Equal(expectedAge, new Driver(dob, 5, 0).AgeOn(Examples.StartDate));
    }
}
