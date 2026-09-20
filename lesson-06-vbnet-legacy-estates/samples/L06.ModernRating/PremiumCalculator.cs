namespace L06.ModernRating;

// The faithful port: the same numbers as LegacyPremium.CalcPremium, on
// the canonical illustrative tariff. Fixing the legacy quirks (whole-baht
// rounding included) is a later, separately signed-off change.
public static class PremiumCalculator
{
    #region port-cover
    public static decimal? Calculate(QuoteRequest r)
    {
        string code = r.CoverCode.Trim();
        double rate;
        if (VbCompat.TextEquals(code, "CLASS1")) rate = 0.021;
        else if (VbCompat.TextEquals(code, "CLASS2PLUS")) rate = 0.012;
        else if (VbCompat.TextEquals(code, "CLASS3PLUS")) rate = 0.009;
        else if (VbCompat.TextEquals(code, "CLASS3")) rate = 0.004;
        else return null;                     // was: Return -1

        int @base = VbCompat.CInt((double)r.SumInsured * rate);
        #endregion

        #region port-loadings
        int age = VbCompat.DateDiffYears(
            r.DateOfBirth, r.StartDate);      // calendar years
        int licenceYears = VbCompat.CInt(r.LicenceMonths / 12.0);

        int loading = 0;
        if (age < 25) loading += VbCompat.CInt(@base * 0.2);
        switch (r.Claims)
        {
            case 0: break;
            case 1: loading += VbCompat.CInt(@base * 0.1); break;
            case 2: loading += VbCompat.CInt(@base * 0.25); break;
            default: return null;             // 3+ claims: declined
        }
        if (r.Commercial)
            loading += VbCompat.CInt(
                @base * (r.EngineCc > 3000 ? 0.35 : 0.25));
        #endregion

        #region port-discount-total
        int claimFree = r.Claims == 0 ? licenceYears : 0;
        // six slots, as Dim ncb(5)
        decimal[] ncb = [0m, 0.2m, 0.25m, 0.3m, 0.4m, 0.5m];
        int discount = VbCompat.CInt(
            (@base + loading) * ncb[Math.Min(claimFree, 5)]);

        int net = @base + loading - discount;
        int duty = VbCompat.CInt(net * 0.004);
        decimal vat = Math.Round(
            (net + duty) * 0.07m, MidpointRounding.ToEven);
        return net + duty + vat;
        #endregion
    }
}
