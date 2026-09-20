using L06.ModernRating;

namespace L06.Parity;

#region canonical
// The track's canonical illustrative tariff (curriculum, "Canonical
// tariff") in decimal, rounded to the satang. The legacy rule prices in
// whole baht; this is the reference its numbers are checked against.
public static class CanonicalTariff
{
    public static decimal? Total(QuoteRequest r)
    {
        decimal rate = r.CoverCode.Trim().ToUpperInvariant() switch
        {
            "CLASS1" => 0.021m,
            "CLASS2PLUS" => 0.012m,
            "CLASS3PLUS" => 0.009m,
            "CLASS3" => 0.004m,
            _ => 0m,
        };
        if (rate == 0m || r.Claims >= 3) return null;      // declined

        int age = r.StartDate.Year - r.DateOfBirth.Year
            - (r.StartDate < r.DateOfBirth.AddYears(
                r.StartDate.Year - r.DateOfBirth.Year) ? 1 : 0);
        decimal loadings = (age < 25 ? 0.20m : 0m)
            + r.Claims switch { 1 => 0.10m, 2 => 0.25m, _ => 0m }
            + (r.Commercial ? (r.EngineCc > 3_000 ? 0.35m : 0.25m) : 0m);
        int claimFree = r.Claims == 0 ? r.LicenceMonths / 12 : 0;
        decimal discount = claimFree switch
        {
            0 => 0m, 1 => 0.20m, 2 => 0.25m, 3 => 0.30m, 4 => 0.40m,
            _ => 0.50m,
        };

        decimal net = Satang(r.SumInsured * rate * (1 + loadings)
                             * (1 - discount));
        decimal duty = Satang(net * 0.004m);
        decimal vat = Satang((net + duty) * 0.07m);
        return net + duty + vat;
    }

    static decimal Satang(decimal amount) =>
        Math.Round(amount, 2, MidpointRounding.AwayFromZero);
}
#endregion
