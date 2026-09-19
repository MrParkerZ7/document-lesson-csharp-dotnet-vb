namespace L02.Rating;

/// <summary>The worked example every lesson-02 sample prints: one young private driver.</summary>
public static class Examples
{
    public static readonly DateOnly StartDate = new(2026, 10, 1);

    public static QuoteRequest YoungDriver(int claims = 0, VehicleUse use = VehicleUse.Private) =>
        new(new Vehicle("Toyota", "Yaris Ativ", 2024, 1_200, use, new Money(550_000m)),
            new Driver(new DateOnly(2003, 3, 15), LicenceYears: 4, ClaimsLast5Years: claims),
            CoverageClass.Class1,
            StartDate);
}
