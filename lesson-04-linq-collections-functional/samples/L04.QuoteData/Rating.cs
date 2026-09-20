namespace L04.QuoteData;

public sealed record RatingInput(
    CoverageClass Coverage,
    decimal SumInsured,
    int DriverAge,
    int Claims,
    int LicenceYears,
    VehicleUse Use,
    int EngineCc);

/// <summary>The track's one illustrative tariff (_curriculum.md, "Canonical tariff"), not a real one.
/// Every member is a pure function.</summary>
public static class Rating
{
    /// <summary>3 or more claims in 5 years: a decision, not a price. The quote is never rated.</summary>
    public const string DeclineReason = "3+ claims in 5 years";

    public static bool IsDeclined(RatingInput r) => r.Claims >= 3;

    #region rules-as-functions
    // a rule is a value: it reads the quote and returns the loading it adds to the base premium
    public delegate decimal Loading(RatingInput input);

    public static readonly IReadOnlyList<(string Name, Loading Rate)> Rules =
    [
        ("young driver", r => r.DriverAge < 25 ? 0.20m : 0m),
        ("claims", r => r.Claims switch
        {
            0 => 0m, 1 => 0.10m, 2 => 0.25m,
            _ => throw new InvalidOperationException(DeclineReason), // 3+ is declined, not loaded
        }),
        ("commercial use", r => r.Use is not VehicleUse.Commercial ? 0m
                                : r.EngineCc > 3_000 ? 0.35m : 0.25m),
    ];

    // fold the rules into one loading, then apply it and the no-claim discount to the base premium
    public static decimal Net(RatingInput r) =>
        Round(Base(r) * (1m + Rules.Aggregate(0m, (loading, rule) => loading + rule.Rate(r)))
                      * (1m - NoClaimDiscount(r)));

    // claim-free years earn the ladder; a single claim resets it to zero
    static decimal NoClaimDiscount(RatingInput r) =>
        (r.Claims == 0 ? r.LicenceYears : 0) switch
        {
            0 => 0m, 1 => 0.20m, 2 => 0.25m, 3 => 0.30m, 4 => 0.40m, _ => 0.50m,
        };
    #endregion

    public static decimal Base(RatingInput r) => r.Coverage switch
    {
        CoverageClass.Class1 => r.SumInsured * 0.021m,
        CoverageClass.Class2Plus => r.SumInsured * 0.012m,
        CoverageClass.Class3Plus => r.SumInsured * 0.009m,
        CoverageClass.Class3 => r.SumInsured * 0.004m, // third-party only: a rate, never a flat amount
        _ => throw new ArgumentOutOfRangeException(nameof(r)),
    };

    public static Money Total(RatingInput r)
    {
        var net = Net(r);
        var duty = Round(net * 0.004m);        // stamp duty 0.4% of the net premium
        var vat = Round((net + duty) * 0.07m); // VAT 7% on net + stamp duty
        return new Money(net + duty + vat);
    }

    // the satang: two decimal places, halves away from zero
    static decimal Round(decimal amount) => decimal.Round(amount, 2, MidpointRounding.AwayFromZero);

    public static int AgeOn(DateOnly dateOfBirth, DateOnly asOf)
    {
        var age = asOf.Year - dateOfBirth.Year;
        return asOf < dateOfBirth.AddYears(age) ? age - 1 : age;
    }
}
