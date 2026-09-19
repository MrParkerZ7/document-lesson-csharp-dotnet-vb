using Reqnroll;

namespace L10.Pricing.Specs.Steps;

// Step definitions bind one Gherkin phrase to one method. {int} and {decimal}
// are Cucumber expressions, not regular expressions.
[Binding]
public sealed class PremiumSteps
{
    private static readonly DateOnly Start = new(2026, 10, 1);
    private Money _sumInsured;
    private DateOnly _dateOfBirth;
    private int _claimFreeYears;
    private int _claims;
    private Premium? _premium;

    #region steps
    [Given("a private car insured for {decimal} THB, Class 1")]
    public void GivenACar(decimal sumInsured) =>
        _sumInsured = new Money(sumInsured, "THB");

    [Given("a driver aged {int} with {int} claim-free years")]
    public void GivenADriver(int age, int years) =>
        (_dateOfBirth, _claimFreeYears) =
            (Start.AddYears(-age), years);

    [Given("the driver made {int} claim(s) in the last 5 years")]
    public void GivenClaims(int claims) => _claims = claims;

    [When("the premium is calculated")]
    public void WhenCalculated() =>
        _premium = new PremiumCalculator().Calculate(Request());

    [Then("the net premium is {decimal} THB")]
    public void ThenNet(decimal net) =>
        Assert.Equal(net, _premium!.Net.Amount);
    #endregion

    private QuoteRequest Request() =>
        new(new Vehicle("Toyota", "Yaris", 2023, 1200,
                VehicleUse.Private, _sumInsured),
            new Driver(_dateOfBirth, _claimFreeYears, _claims),
            CoverageClass.Class1, Start);
}
