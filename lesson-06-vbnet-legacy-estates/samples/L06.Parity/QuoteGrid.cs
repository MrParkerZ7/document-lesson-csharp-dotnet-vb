using L06.ModernRating;

namespace L06.Parity;

#region grid
// Every combination of these values is one parity case.
public static class QuoteGrid
{
    public static readonly string[] CoverCodes =
        ["CLASS1", "Class1", "CLASS2PLUS", "class2plus",
         "CLASS3PLUS", "Class3", "CLASS4"];
    public static readonly decimal[] SumsInsured =
        [205_000m, 250_000m, 287_500m, 312_500m,
         450_000m, 487_500m, 612_500m, 800_000m];
    public static readonly DateOnly[] BirthDates =
        [new(2001, 12, 31), new(2002, 1, 1), new(2002, 6, 15), new(1990, 3, 10)];
    public static readonly DateOnly[] StartDates = [new(2026, 1, 1), new(2026, 7, 1)];
    public static readonly int[] LicenceMonths = [6, 17, 18, 30, 42];
    public static readonly int[] ClaimFreeYears = [0, 1, 2, 3, 4, 5, 7];
    public static readonly int[] Claims = [0, 1, 2];
    public static readonly bool[] Commercial = [false, true];

    public static IEnumerable<QuoteRequest> All() =>
        from code in CoverCodes
        from sum in SumsInsured
        from dob in BirthDates
        from start in StartDates
        from months in LicenceMonths
        from free in ClaimFreeYears
        from claims in Claims
        from commercial in Commercial
        select new QuoteRequest(code, sum, dob, start, months, free, claims, commercial);
}
#endregion
