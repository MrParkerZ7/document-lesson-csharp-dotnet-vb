using System.Diagnostics;

namespace L13.DebugLab;

/// <summary>The canonical MotorQuote tariff — illustrative, not a real tariff.</summary>
public static class Tariff
{
    #region ClassRate
    public static decimal Rate(CoverageClass coverage) => coverage switch
    {
        CoverageClass.Class1 => 0.021m,
        CoverageClass.Class2Plus => 0.012m,
        CoverageClass.Class3Plus => 0.009m,
        CoverageClass.Class3 => 0.004m,
        _ => throw new ArgumentOutOfRangeException(nameof(coverage)),
    };
    #endregion

    #region ClaimsLoading
    // Set Debug > Windows > Exception Settings > "L13.DebugLab.QuoteDeclinedException" and
    // the debugger stops on the throw line, even though the batch loop catches it.
    public static decimal ClaimsLoading(int claims) => claims switch
    {
        < 0 => throw new ArgumentOutOfRangeException(nameof(claims)),
        0 => 0m,
        1 => 0.10m,
        2 => 0.25m,
        _ => throw new QuoteDeclinedException("3+ claims in 5 years"),
    };
    #endregion

    public static decimal YoungDriverLoading(Driver driver, DateOnly start) =>
        AgeOn(driver.DateOfBirth, start) < 25 ? 0.20m : 0m;

    public static decimal CommercialLoading(Vehicle vehicle) =>
        vehicle.Use == VehicleUse.Private ? 0m : vehicle.EngineCc > 3000 ? 0.35m : 0.25m;

    #region NoClaimDiscount
    public static decimal NoClaimDiscount(Driver driver)
    {
        var claimFreeYears = driver.ClaimsLast5Years == 0 ? driver.LicenceYears : 0;
        return claimFreeYears switch
        {
            0 => 0m, 1 => 0.20m, 2 => 0.25m, 3 => 0.30m, 4 => 0.40m, _ => 0.50m,
        };
    }
    #endregion

    public static int AgeOn(DateOnly dateOfBirth, DateOnly day)
    {
        var age = day.Year - dateOfBirth.Year;
        return dateOfBirth.AddYears(age) > day ? age - 1 : age;
    }

    #region StepThrough
    // F11 (Step Into) skips this method: it is plumbing, the debugger has nothing to teach here.
    [DebuggerStepThrough]
    public static decimal Satang(decimal value) =>
        Math.Round(value, 2, MidpointRounding.AwayFromZero);
    #endregion
}
