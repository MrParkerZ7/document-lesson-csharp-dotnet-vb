namespace L02.Syntax;

delegate bool TryParse<T>(string text, out T result);

static class MethodsTour
{
    #region declarations
    // optional parameters, expression-bodied member.
    // roundUp is a parameter demo: the tariff rounds half away
    // from zero through RatingRules.Round (3.2), never up.
    static decimal Discount(decimal amount, decimal rate = 0.40m,
                            bool roundUp = false) =>
        roundUp ? Math.Ceiling(amount * rate) : amount * rate;

    // params collection (C# 13): a span, not an array
    static decimal Sum(params ReadOnlySpan<decimal> parts)
    {
        decimal total = 0;
        foreach (var part in parts) total += part;
        return total;
    }

    // a value tuple with named elements
    static (decimal Bonus, string Reason) Bonus(Driver d) =>
        d.ClaimsLast5Years == 0
            ? (RatingRules.NoClaimBonus(d), "claim-free")
            : (0m, "has claims");

    // ref: writes back to the caller's variable
    // in:  passed by reference, read-only
    static void Load(ref decimal premium, in decimal rate) =>
        premium += premium * rate;
    #endregion

    public static void Run()
    {
        Console.WriteLine();
        Console.WriteLine("[methods]");

        #region calls
        // named arguments: skip optional ones, any order
        decimal d1 = Discount(13_860m, roundUp: true);
        decimal d2 = Discount(rate: 0.20m, amount: 13_860m);

        decimal total = Sum(8_316m, 33.26m, 584.45m);       // params span: no array allocated

        var driver = Examples.YoungDriver().Driver;
        var (bonus, reason) = Bonus(driver);                // deconstruct the tuple

        decimal premium = 11_550m;
        Load(ref premium, 0.20m);                           // ref must be repeated at the call site

        if (int.TryParse("2", out var claims))              // out var: declared inline
            Console.WriteLine($"claims {claims}");

        // a static local function: cannot capture locals by accident
        static string Fmt(decimal x) => x.ToString("N2", CultureInfo.InvariantCulture);
        Console.WriteLine($"{Fmt(d1)} {Fmt(d2)} {Fmt(total)} {bonus} {reason} {Fmt(premium)}");

        // lambdas (lesson 04): C# 14 allows `out` on an untyped lambda parameter
        TryParse<decimal> parsePercent = (text, out result) =>
            decimal.TryParse(text, CultureInfo.InvariantCulture, out result);
        Console.WriteLine(parsePercent("2.1", out var pct) ? $"parsed {pct}" : "no");
        #endregion
    }
}
