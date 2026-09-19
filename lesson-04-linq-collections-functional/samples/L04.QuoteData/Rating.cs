namespace L04.QuoteData;

public sealed record RatingInput(
    CoverageClass Coverage,
    decimal SumInsured,
    int DriverAge,
    int Claims,
    int LicenceYears,
    VehicleUse Use);

/// <summary>Illustrative rates only, not a real tariff. Every member is a pure function.</summary>
public static class Rating
{
    #region rules-as-functions
    // a rule is a value: takes the input and the running premium, returns a new premium
    public delegate decimal Adjustment(RatingInput input, decimal premium);

    public static readonly IReadOnlyList<(string Name, Adjustment Apply)> Rules =
    [
        ("young driver", (r, p) => r.DriverAge < 25 ? p * 1.20m : p),
        ("claims loading", (r, p) => p * (1m + 0.15m * r.Claims)),
        // licence years stand in for claim-free years in this illustrative rule
        ("no-claim bonus", (r, p) => r.Claims == 0 ? p * NoClaimFactor(r.LicenceYears) : p),
        ("commercial use", (r, p) => r.Use == VehicleUse.Commercial ? p * 1.25m : p),
    ];

    // fold the rules over the base premium: no mutable state, same input -> same output
    public static decimal Net(RatingInput r) =>
        Rules.Aggregate(Base(r), (premium, rule) => rule.Apply(r, premium));

    static decimal NoClaimFactor(int years) => 1m - 0.05m * Math.Min(years, 5);
    #endregion

    public static decimal Base(RatingInput r) => r.Coverage switch
    {
        CoverageClass.Class1 => r.SumInsured * 0.022m,
        CoverageClass.Class2Plus => r.SumInsured * 0.016m,
        CoverageClass.Class3Plus => r.SumInsured * 0.012m,
        _ => 1_800m, // Class 3: third-party only, flat
    };

    public static Money Total(RatingInput r)
    {
        var net = Net(r);
        var duty = net * 0.004m;        // stamp duty 0.4% of net (illustrative)
        var vat = (net + duty) * 0.07m; // VAT 7% on net + duty (illustrative)
        return new Money(decimal.Round(net + duty + vat, 2, MidpointRounding.AwayFromZero));
    }

    public static int AgeOn(DateOnly dateOfBirth, DateOnly asOf)
    {
        var age = asOf.Year - dateOfBirth.Year;
        return asOf < dateOfBirth.AddYears(age) ? age - 1 : age;
    }
}
