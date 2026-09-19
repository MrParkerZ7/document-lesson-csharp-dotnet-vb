using System.Globalization;

namespace L06.ModernRating;

#region vb-compat
// Legacy VB semantics, named so a reviewer can see them.
public static class VbCompat
{
    // CInt, and implicit Double -> Integer: banker's rounding
    public static int CInt(double value) => checked(
        (int)Math.Round(value, MidpointRounding.ToEven));

    public static int CInt(decimal value) => checked(
        (int)Math.Round(value, MidpointRounding.ToEven));

    // DateDiff(DateInterval.Year, d1, d2): year parts only
    public static int DateDiffYears(
        DateOnly d1, DateOnly d2) => d2.Year - d1.Year;

    // Option Compare Text: current culture, ignoring case,
    // width and kana type
    const CompareOptions Text = CompareOptions.IgnoreCase
        | CompareOptions.IgnoreWidth
        | CompareOptions.IgnoreKanaType;

    public static bool TextEquals(string a, string b) =>
        CultureInfo.CurrentCulture.CompareInfo
            .Compare(a, b, Text) == 0;
}
#endregion
