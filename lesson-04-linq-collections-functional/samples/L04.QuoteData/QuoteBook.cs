namespace L04.QuoteData;

/// <summary>A deterministic quote dataset: the same quotes on every machine and every run.</summary>
public static class QuoteBook
{
    public static readonly DateOnly AsOf = new(2026, 9, 1);

    private static readonly (string Make, string Model, int Cc)[] Models =
    [
        ("Toyota", "Yaris Ativ", 1200), ("Toyota", "Hilux Revo", 2400), ("Honda", "City", 1000),
        ("Honda", "HR-V", 1500), ("Isuzu", "D-Max", 1900), ("Mazda", "CX-30", 2000),
        ("Nissan", "Almera", 1000), ("Ford", "Ranger", 2000), ("MG", "MG4", 0), ("BYD", "Atto 3", 0),
    ];

    public static IReadOnlyList<Quote> Generate(int count = 240) =>
        Enumerable.Range(0, count).Select(Create).ToArray();

    /// <summary>Policies for accepted quotes; every sixth accepted quote is still pending issuance.</summary>
    public static IReadOnlyList<Policy> IssuePolicies(IEnumerable<Quote> quotes) =>
        quotes
            .Where(q => q.IsAccepted)
            .Where((q, index) => index % 6 != 5)
            .Select((q, n) => new Policy($"P-{n + 1:D5}", q.QuoteId, q.StartDate, q.StartDate.AddYears(1)))
            .ToList();

    private static Quote Create(int i)
    {
        var (make, model, cc) = Models[(i * 7 + i / 5) % Models.Length];
        var coverage = (CoverageClass)((i * 3 + i / 4) % 4);
        var use = i % 9 == 4 ? VehicleUse.Commercial : VehicleUse.Private;
        var sumInsured = coverage == CoverageClass.Class3 ? 0m : 250_000m + (i * 13 % 16) * 50_000m;
        var driver = new Driver(
            DateOfBirth: new DateOnly(1962 + (i * 17) % 42, 1 + i % 12, 1 + (i * 3) % 28),
            LicenceYears: (i * 11) % 15,
            ClaimsLast5Years: (i * 7 % 10) switch { < 6 => 0, < 9 => 1, _ => 2 });
        var input = new RatingInput(coverage, sumInsured, Rating.AgeOn(driver.DateOfBirth, AsOf),
            driver.ClaimsLast5Years, driver.LicenceYears, use);
        var vehicle = new Vehicle(make, model, 2014 + (i * 5) % 12, cc, use, new Money(sumInsured));
        return new Quote($"Q-{i + 1:D4}", vehicle, driver, coverage,
            AsOf.AddDays(i % 30), Rating.Total(input), StatusOf(i, coverage));
    }

    private static QuoteStatus StatusOf(int i, CoverageClass coverage)
    {
        var roll = (int)((uint)(i + 1) * 2654435761u % 100);
        var acceptBelow = coverage switch
        {
            CoverageClass.Class1 => 42,
            CoverageClass.Class2Plus => 55,
            CoverageClass.Class3Plus => 61,
            _ => 70,
        };
        if (roll < acceptBelow) return QuoteStatus.Accepted;
        return (roll % 3) switch { 0 => QuoteStatus.Expired, 1 => QuoteStatus.Declined, _ => QuoteStatus.Quoted };
    }
}
