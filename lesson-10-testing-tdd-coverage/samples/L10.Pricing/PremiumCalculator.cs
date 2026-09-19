namespace L10.Pricing;

/// <summary>Rating rules for a motor quote. Illustrative rates, not a real tariff.</summary>
public sealed class PremiumCalculator
{
    #region base-rate
    public static decimal BaseRate(CoverageClass coverage) => coverage switch
    {
        CoverageClass.Class1 => 0.020m,
        CoverageClass.Class2Plus => 0.012m,
        CoverageClass.Class3Plus => 0.009m,
        CoverageClass.Class3 => 0.005m,
        // enums are open: (CoverageClass)99 compiles, so this arm is reachable
        _ => throw new ArgumentOutOfRangeException(nameof(coverage), coverage, "unknown class"),
    };
    #endregion

    #region calculate
    public Premium Calculate(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        var (vehicle, driver) = (request.Vehicle, request.Driver);

        var loading = 1.00m;
        if (AgeAt(driver.DateOfBirth, request.StartDate) < 25)
            loading += 0.20m;                                   // young driver
        loading += 0.10m * Math.Min(driver.ClaimsLast5Years, 3); // claims
        if (vehicle.Use == VehicleUse.Commercial)
            loading += 0.25m;                                   // commercial use

        var claimFreeYears = driver.ClaimsLast5Years == 0 ? driver.LicenceYears : 0;
        var gross = vehicle.SumInsured.Amount * BaseRate(request.Coverage) * loading;
        var net = Round(gross * (1 - NoClaimBonus.DiscountFor(claimFreeYears)));

        var duty = Math.Ceiling(net * 0.004m);                  // stamp duty 0.4%, whole baht
        var vat = Round((net + duty) * 0.07m);                  // VAT 7% on net + duty
        return new Premium(Thb(net), Thb(duty), Thb(vat), Thb(net + duty + vat));
    }
    #endregion

    #region age
    public static int AgeAt(DateOnly dateOfBirth, DateOnly on)
    {
        var age = on.Year - dateOfBirth.Year;
        return dateOfBirth > on.AddYears(-age) ? age - 1 : age;
    }
    #endregion

    private static decimal Round(decimal value) =>
        Math.Round(value, 2, MidpointRounding.AwayFromZero);

    private static Money Thb(decimal amount) => new(amount, "THB");
}
