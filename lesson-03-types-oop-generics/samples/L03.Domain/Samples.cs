namespace L03.Domain;

/// <summary>
/// Deterministic MotorQuote data shared by the lesson-03 samples and tests.
/// Rates and premiums come from the curriculum's canonical tariff: illustrative, not a real tariff.
/// </summary>
public static class Samples
{
    public static readonly DateOnly StartDate = new(2026, 10, 1);

    public static QuoteRequest YoungDriver() => new(
        new Vehicle("Toyota", "Yaris", 2024, 1200, VehicleUse.Private, Money.Thb(450_000m)),
        new Driver(new DateOnly(2003, 5, 10), LicenceYears: 3, ClaimsLast5Years: 0),
        CoverageClass.Class1,
        StartDate);

    public static QuoteRequest CommercialPickup() => new(
        new Vehicle("Isuzu", "D-Max", 2021, 1900, VehicleUse.Commercial, Money.Thb(620_000m)),
        new Driver(new DateOnly(1985, 11, 2), LicenceYears: 18, ClaimsLast5Years: 1),
        CoverageClass.Class2Plus,
        StartDate);

    /// <summary>Three claims in five years: the tariff declines this one.</summary>
    public static QuoteRequest ThreeClaims()
    {
        var request = CommercialPickup();
        return request with { Driver = request.Driver with { ClaimsLast5Years = 3 } };
    }

    public static PremiumCalculator Calculator() => new(
        new StandardRateTable(),
        [new YoungDriverLoading(), new ClaimsLoading(), new NoClaimBonus(), new CommercialUseLoading()]);

    #region object-initializer
    // leave out a required member and this does not compile
    public static Quote Quote(int number, QuoteRequest req) =>
        new Quote
        {
            Id = new QuoteId(number),
            Request = req,
            Premium = Calculator().Calculate(req),
            ValidUntil = req.StartDate, // init, but optional
        };
    #endregion
}
