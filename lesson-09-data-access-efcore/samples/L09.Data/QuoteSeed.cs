namespace L09.Data;

/// <summary>
/// Deterministic MotorQuote data for the samples, priced with the one tariff the whole track uses
/// ("Canonical tariff" in the curriculum). Every rate is ILLUSTRATIVE, not a real tariff:
/// base premium = sum insured x rate for the coverage class (Class1 2.1%, Class2Plus 1.2%,
/// Class3Plus 0.9%, Class3 0.4%); the young-driver, claims and commercial-use loadings are added
/// together and applied to the base; then the no-claim discount for claim-free licence years;
/// stamp duty 0.4% of the net premium and VAT 7% on (net + duty); rounding is 2 decimals away from
/// zero. Three or more claims in five years is a decline, not a price: the quote is stored with
/// QuoteStatus.Declined, a zero total and one "declined" line.
/// </summary>
public static class QuoteSeed
{
    public static readonly DateOnly Today = new(2026, 9, 1);

    private static readonly (string Make, string Model, int Cc, decimal Sum)[] Cars =
    [
        ("Toyota", "Yaris Ativ", 1200, 520_000m),
        ("Honda", "City", 1000, 580_000m),
        ("Toyota", "Hilux Revo", 2400, 890_000m),
        ("Mazda", "CX-30", 2000, 1_050_000m),
        ("Isuzu", "D-Max", 1900, 760_000m),
    ];

    // indexed by CoverageClass: Class1, Class2Plus, Class3Plus, Class3
    private static readonly decimal[] BaseRate = [0.021m, 0.012m, 0.009m, 0.004m];

    // claims in the last five years -> loading; 3 or more declines the quote
    private static readonly decimal[] ClaimsLoading = [0m, 0.10m, 0.25m];

    // claim-free licence years (capped at 5) -> no-claim discount
    private static readonly decimal[] NoClaimDiscount = [0m, 0.20m, 0.25m, 0.30m, 0.40m, 0.50m];

    public static List<Quote> Build(int count)
    {
        var vehicles = Cars.Select((c, i) => new Vehicle
        {
            Make = c.Make,
            Model = c.Model,
            Year = 2020 + i,
            EngineCc = c.Cc,
            Use = i == 4 ? VehicleUse.Commercial : VehicleUse.Private,
            SumInsured = Money.Thb(c.Sum),
        }).ToArray();

        return Enumerable.Range(0, count)
            .Select(i => BuildQuote(i, vehicles[i % vehicles.Length]))
            .ToList();
    }

    /// <summary>
    /// Prices one quote with the canonical tariff. Public so a test can check the track's worked
    /// example: Class 1, 550,000 THB sum insured, private use, a driver aged 23 with four
    /// claim-free licence years — base 11,550.00, young driver +20%, no-claim −40%, net 8,316.00,
    /// stamp duty 33.26, VAT 584.45, total 8,933.71 THB.
    /// </summary>
    public static Quote Price(string reference, Vehicle vehicle, Driver driver,
        CoverageClass coverage, DateOnly start)
    {
        var quote = new Quote
        {
            Reference = reference,
            Vehicle = vehicle,
            Driver = driver,
            Coverage = coverage,
            Status = QuoteStatus.Quoted,
            ValidUntil = start.AddDays(30),
        };

        // 3+ claims in five years: a domain outcome, not a crash and not a price.
        if (driver.ClaimsLast5Years >= ClaimsLoading.Length)
        {
            quote.Status = QuoteStatus.Declined;
            quote.Lines.Add(Line("declined", 0m));
            quote.Total = Money.Thb(0m);
            return quote;
        }

        var basePremium = Round(vehicle.SumInsured.Amount * BaseRate[(int)coverage]);
        quote.Lines.Add(Line("base", basePremium));

        var loading = 0m;
        if (AgeOn(start, driver.DateOfBirth) < 25)
            loading += Loading(quote, "young-driver", basePremium, 0.20m);
        if (driver.ClaimsLast5Years > 0)
            loading += Loading(quote, "claims", basePremium, ClaimsLoading[driver.ClaimsLast5Years]);
        if (vehicle.Use == VehicleUse.Commercial)
            loading += Loading(quote, "commercial", basePremium,
                vehicle.EngineCc > 3_000 ? 0.35m : 0.25m);

        var loaded = basePremium * (1 + loading);
        var claimFreeYears = driver.ClaimsLast5Years == 0 ? driver.LicenceYears : 0;
        var discount = NoClaimDiscount[Math.Min(claimFreeYears, NoClaimDiscount.Length - 1)];
        if (discount > 0)
            quote.Lines.Add(Line("no-claim", -Round(loaded * discount)));

        var net = Round(loaded * (1 - discount));
        var duty = Round(net * 0.004m);
        var vat = Round((net + duty) * 0.07m);
        quote.Lines.Add(Line("stamp-duty", duty));
        quote.Lines.Add(Line("vat", vat));
        quote.Total = Money.Thb(net + duty + vat);
        return quote;
    }

    private static Quote BuildQuote(int i, Vehicle vehicle)
    {
        var driver = new Driver(
            DateOfBirth: new DateOnly(1978 + (i * 7) % 28, 1 + i % 12, 1 + i % 28),
            LicenceYears: (i * 3) % 15,
            ClaimsLast5Years: i % 7 == 6 ? 3 : i % 5 == 4 ? 2 : i % 3 == 0 ? 1 : 0);

        var quote = Price($"Q-{i + 1:0000}", vehicle, driver, (CoverageClass)(i % 4), Today);
        quote.ValidUntil = Today.AddDays(i % 2 == 0 ? -3 : 20);
        if (quote.Status == QuoteStatus.Quoted && i % 6 == 5)
            quote.Status = QuoteStatus.Accepted;
        return quote;
    }

    private static decimal Loading(Quote quote, string kind, decimal basePremium, decimal percent)
    {
        quote.Lines.Add(Line(kind, Round(basePremium * percent)));
        return percent;
    }

    private static PremiumLine Line(string kind, decimal amount) =>
        new() { Kind = kind, Amount = Money.Thb(amount) };

    private static int AgeOn(DateOnly day, DateOnly birth)
    {
        var age = day.Year - birth.Year;
        return day < birth.AddYears(age) ? age - 1 : age;
    }

    private static decimal Round(decimal value) => Math.Round(value, 2, MidpointRounding.AwayFromZero);
}
