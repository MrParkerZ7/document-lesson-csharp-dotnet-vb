namespace L09.Data.Tests;

// The seed data prices with the one tariff the whole track uses, so these two facts keep this
// lesson's numbers equal to every other lesson's. They touch no database.
public class TariffTests
{
    [Fact]
    public void The_seed_prices_the_tracks_worked_example()
    {
        var vehicle = new Vehicle
        {
            Make = "Toyota", Model = "Corolla Cross", Year = 2024, EngineCc = 1800,
            Use = VehicleUse.Private, SumInsured = Money.Thb(550_000m),
        };
        var driver = new Driver(
            DateOfBirth: QuoteSeed.Today.AddYears(-23), LicenceYears: 4, ClaimsLast5Years: 0);

        var quote = QuoteSeed.Price("Q-9001", vehicle, driver, CoverageClass.Class1, QuoteSeed.Today);

        // base 11,550.00 · young driver +20% -> 13,860.00 · no-claim -40% -> net 8,316.00
        // stamp duty 33.26 · VAT 584.45
        Assert.Equal(8_933.71m, quote.Total.Amount);
        Assert.Equal(QuoteStatus.Quoted, quote.Status);
        Assert.Equal(
            ["base", "young-driver", "no-claim", "stamp-duty", "vat"],
            quote.Lines.Select(l => l.Kind));
    }

    [Fact]
    public void Three_claims_in_five_years_is_a_decline_not_a_price()
    {
        var vehicle = new Vehicle
        {
            Make = "Honda", Model = "City", Year = 2023, EngineCc = 1000,
            Use = VehicleUse.Private, SumInsured = Money.Thb(580_000m),
        };
        var driver = new Driver(
            DateOfBirth: new DateOnly(1988, 4, 2), LicenceYears: 12, ClaimsLast5Years: 3);

        var quote = QuoteSeed.Price("Q-9002", vehicle, driver, CoverageClass.Class1, QuoteSeed.Today);

        // A domain outcome, stored as data: no exception, no premium.
        Assert.Equal(QuoteStatus.Declined, quote.Status);
        Assert.Equal(0m, quote.Total.Amount);
        Assert.Equal("declined", Assert.Single(quote.Lines).Kind);
    }
}
