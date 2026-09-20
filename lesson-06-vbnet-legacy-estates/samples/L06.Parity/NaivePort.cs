using L06.ModernRating;

namespace L06.Parity;

#region port-changes
// One change to the faithful port, injected on its own: six realistic
// translation mistakes, and the decimal fix the team wants to make.
public enum PortChange
{
    None,
    TruncatingCasts,     // CInt(x) written as (int)x
    HalfUpRounding,      // MidpointRounding.AwayFromZero, as Java HALF_UP
    IntegerDivision,     // months / 12 on ints truncates
    BirthdayAge,         // a correct age instead of DateDiff year parts
    CaseSensitiveCodes,  // == instead of Option Compare Text
    FiveElementTable,    // Dim ncb(5) read as five elements
    DecimalRates,        // the planned fix: decimal rates instead of Double
}
#endregion

public static class NaivePort
{
    public static decimal? Calculate(QuoteRequest r, PortChange m)
    {
        int ToInt(double v) => m switch
        {
            PortChange.TruncatingCasts => (int)v,
            PortChange.HalfUpRounding => (int)Math.Round(v, MidpointRounding.AwayFromZero),
            _ => VbCompat.CInt(v),
        };
        int ToIntM(decimal v) => m switch
        {
            PortChange.TruncatingCasts => (int)v,
            PortChange.HalfUpRounding => (int)Math.Round(v, MidpointRounding.AwayFromZero),
            _ => VbCompat.CInt(v),
        };

        string code = r.CoverCode.Trim();
        bool Is(string expected) => m == PortChange.CaseSensitiveCodes
            ? code == expected
            : VbCompat.TextEquals(code, expected);

        double rate;
        if (Is("CLASS1")) rate = 0.021;
        else if (Is("CLASS2PLUS")) rate = 0.012;
        else if (Is("CLASS3PLUS")) rate = 0.009;
        else if (Is("CLASS3")) rate = 0.004;
        else return null;

        bool dec = m == PortChange.DecimalRates;
        int @base = dec ? ToIntM(r.SumInsured * (decimal)rate)
                        : ToInt((double)r.SumInsured * rate);
        int Scale(int amount, double share) => dec
            ? ToIntM(amount * (decimal)share)
            : ToInt(amount * share);

        int age = m == PortChange.BirthdayAge
            ? AgeOnDate(r.DateOfBirth, r.StartDate)
            : VbCompat.DateDiffYears(r.DateOfBirth, r.StartDate);
        int licenceYears = m == PortChange.IntegerDivision
            ? r.LicenceMonths / 12
            : ToInt(r.LicenceMonths / 12.0);

        int loading = 0;
        if (age < 25) loading += Scale(@base, 0.2);
        switch (r.Claims)
        {
            case 0: break;
            case 1: loading += Scale(@base, 0.1); break;
            case 2: loading += Scale(@base, 0.25); break;
            default: return null;
        }
        if (r.Commercial) loading += Scale(@base, r.EngineCc > 3000 ? 0.35 : 0.25);

        decimal[] ncb = m == PortChange.FiveElementTable
            ? [0m, 0.2m, 0.25m, 0.3m, 0.4m]
            : [0m, 0.2m, 0.25m, 0.3m, 0.4m, 0.5m];
        int claimFree = r.Claims == 0 ? licenceYears : 0;
        int discount = ToIntM((@base + loading) * ncb[Math.Min(claimFree, 5)]);

        int net = @base + loading - discount;
        int duty = Scale(net, 0.004);
        decimal vat = Math.Round((net + duty) * 0.07m,
            m == PortChange.HalfUpRounding ? MidpointRounding.AwayFromZero : MidpointRounding.ToEven);
        return net + duty + vat;
    }

    static int AgeOnDate(DateOnly born, DateOnly on)
    {
        int age = on.Year - born.Year;
        return born.AddYears(age) > on ? age - 1 : age;
    }
}
