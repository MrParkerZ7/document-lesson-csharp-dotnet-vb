namespace L02.Rating;

/// <summary>The MotorQuote rating rules. ILLUSTRATIVE rates, not a real tariff.</summary>
public static class RatingRules
{
    #region constants
    // const: a compile-time literal, copied INTO every assembly that uses it
    public const decimal StampDutyRate = 0.004m;
    public const decimal VatRate = 0.07m;

    // static readonly: computed once at run time, read from this assembly
    public static readonly DateOnly TariffEffective = new(2026, 1, 1);
    #endregion

    #region base-rate
    public static decimal BaseRate(CoverageClass coverage,
                                   Money insured) =>
        coverage switch
        {
            CoverageClass.Class1 => insured.Amount * 0.021m,
            CoverageClass.Class2Plus => insured.Amount * 0.012m,
            CoverageClass.Class3Plus => insured.Amount * 0.009m,
            CoverageClass.Class3 => 2_400m,
            // an enum is an int: (CoverageClass)7 lands here
            _ => throw new ArgumentOutOfRangeException(
                nameof(coverage)),
        };
    #endregion

    #region age-loading
    public static decimal AgeLoading(int age) => age switch
    {
        < 18 => throw new NotSupportedException("under 18"),
        < 25 => 0.20m,
        < 30 => 0.10m,
        >= 70 => 0.15m,
        _ => 0m,
    };
    #endregion

    #region rules
    public static decimal ClaimsLoading(int claims)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(claims);
        return claims switch
        {
            0 => 0m,
            1 => 0.10m,
            2 => 0.25m,
            _ => throw new QuoteDeclinedException("3+ claims in 5 years"),
        };
    }

    // property patterns: test a record's properties, first match wins
    public static decimal NoClaimBonus(Driver driver) => driver switch
    {
        { ClaimsLast5Years: > 0 } => 0m,
        { LicenceYears: >= 5 } => 0.40m,
        { LicenceYears: 3 or 4 } => 0.30m,
        { LicenceYears: 2 } => 0.20m,
        _ => 0m,
    };

    // a tuple pattern: switch on two values at once
    public static decimal UseLoading(Vehicle vehicle) => (vehicle.Use, vehicle.EngineCc) switch
    {
        (VehicleUse.Commercial, > 3_000) => 0.35m,
        (VehicleUse.Commercial, _) => 0.25m,
        _ => 0m,
    };
    #endregion

    #region round
    // Math.Round defaults to banker's rounding (ToEven):
    //   Math.Round(2.345m, 2) -> 2.34
    // A premium rounds half away from zero:
    //   Round(2.345m)         -> 2.35
    public static decimal Round(decimal amount) =>
        Math.Round(amount, 2, MidpointRounding.AwayFromZero);
    #endregion
}
