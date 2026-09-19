namespace L09.Data;

/// <summary>
/// Deterministic MotorQuote data for the samples. Every rate here is ILLUSTRATIVE, not a real tariff:
/// base rate by coverage class x sum insured, young-driver loading (under 25), claims loading,
/// commercial-use loading, stamp duty 0.4% of net premium and VAT 7% on (net + duty).
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
    private static readonly decimal[] BaseRate = [0.020m, 0.012m, 0.009m, 0.004m];

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

    private static Quote BuildQuote(int i, Vehicle vehicle)
    {
        var coverage = (CoverageClass)(i % 4);
        var driver = new Driver(
            DateOfBirth: new DateOnly(1978 + (i * 7) % 28, 1 + i % 12, 1 + i % 28),
            LicenceYears: (i * 3) % 15,
            ClaimsLast5Years: i % 5 == 4 ? 2 : i % 3 == 0 ? 1 : 0);

        var quote = new Quote
        {
            Reference = $"Q-{i + 1:0000}",
            Vehicle = vehicle,
            Driver = driver,
            Coverage = coverage,
            Status = i % 6 == 5 ? QuoteStatus.Accepted : QuoteStatus.Quoted,
            ValidUntil = Today.AddDays(i % 2 == 0 ? -3 : 20),
        };

        var basePremium = Round(vehicle.SumInsured.Amount * BaseRate[(int)coverage]);
        var net = basePremium;
        AddLine("base", basePremium);

        if (AgeOn(Today, driver.DateOfBirth) < 25)
            net += AddLine("young-driver", Round(basePremium * 0.20m));
        if (driver.ClaimsLast5Years > 0)
            net += AddLine("claims", Round(basePremium * 0.10m * driver.ClaimsLast5Years));
        if (vehicle.Use == VehicleUse.Commercial)
            net += AddLine("commercial", Round(basePremium * 0.15m));

        var duty = AddLine("stamp-duty", Round(net * 0.004m));
        var vat = AddLine("vat", Round((net + duty) * 0.07m));
        quote.Total = Money.Thb(net + duty + vat);
        return quote;

        decimal AddLine(string kind, decimal amount)
        {
            quote.Lines.Add(new PremiumLine { Kind = kind, Amount = Money.Thb(amount) });
            return amount;
        }
    }

    private static int AgeOn(DateOnly day, DateOnly birth)
    {
        var age = day.Year - birth.Year;
        return day < birth.AddYears(age) ? age - 1 : age;
    }

    private static decimal Round(decimal value) => Math.Round(value, 2, MidpointRounding.AwayFromZero);
}
