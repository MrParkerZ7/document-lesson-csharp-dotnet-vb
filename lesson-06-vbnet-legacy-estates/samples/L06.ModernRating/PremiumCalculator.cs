namespace L06.ModernRating;

// The faithful port: the same numbers as LegacyPremium.CalcPremium.
// Fixing the legacy quirks is a later, separately signed-off change.
public static class PremiumCalculator
{
    #region port-cover
    public static decimal? Calculate(QuoteRequest r)
    {
        string code = r.CoverCode.Trim();
        double rate;
        if (VbCompat.TextEquals(code, "CLASS1")) rate = 0.0185;
        else if (VbCompat.TextEquals(code, "CLASS2PLUS")) rate = 0.012;
        else if (VbCompat.TextEquals(code, "CLASS3PLUS")) rate = 0.0095;
        else if (VbCompat.TextEquals(code, "CLASS3")) rate = 0.0065;
        else return null;                     // was: Return -1

        int @base = VbCompat.CInt((double)r.SumInsured * rate);
        #endregion

        #region port-loadings
        int age = VbCompat.DateDiffYears(
            r.DateOfBirth, r.StartDate);      // calendar years
        int licenceYears = VbCompat.CInt(r.LicenceMonths / 12.0);

        int loading = 0;
        if (age < 25) loading += VbCompat.CInt(@base * 0.25);
        if (licenceYears < 2) loading += VbCompat.CInt(@base * 0.1);
        loading += VbCompat.CInt(@base * 0.2 * r.Claims);
        if (r.Commercial) loading += VbCompat.CInt(@base * 0.3);
        #endregion

        #region port-discount-total
        // six slots, as Dim ncb(5)
        decimal[] ncb = [0m, 0.2m, 0.25m, 0.3m, 0.4m, 0.5m];
        int claimFree = Math.Min(r.ClaimFreeYears, 5);
        int discount = VbCompat.CInt(
            (@base + loading) * ncb[claimFree]);

        int net = Math.Max(@base + loading - discount, 1000);
        int duty = VbCompat.CInt(net * 0.004);
        decimal vat = Math.Round(
            (net + duty) * 0.07m, MidpointRounding.ToEven);
        return net + duty + vat;
        #endregion
    }
}
