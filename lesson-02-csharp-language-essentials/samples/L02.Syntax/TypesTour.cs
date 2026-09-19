namespace L02.Syntax;   // file-scoped namespace (C# 10): applies to the whole file

static class TypesTour
{
    public static void Run()
    {
        Console.WriteLine();
        Console.WriteLine("[types]");

        #region numbers
        int engineCc = 1_200;               // int is an alias of System.Int32
        Int32 sameType = engineCc;          // the same struct: no wrapper, no boxing
        var year = 2024;                    // var: inferred at compile time, still static
        const int MaxClaims = 2;            // const: a compile-time literal
        Console.WriteLine($"{typeof(int).FullName} {sameType} {year} {MaxClaims}");

        #region overflow
        int big = int.MaxValue;
        Console.WriteLine(big + 1);      // unchecked: wraps
        // the constant int.MaxValue + 1: compile error CS0220
        try
        {
            Console.WriteLine(checked(big + 1));
        }
        catch (OverflowException)
        {
            Console.WriteLine("checked: OverflowException");
        }
        #endregion
        #endregion

        #region money
        decimal sumInsured = 550_000m;       // m suffix = decimal
        decimal rate = 0.021m;
        decimal basePremium = sumInsured * rate;

        double d = 0;
        decimal m = 0;
        for (var i = 0; i < 10; i++)
        {
            d += 0.1;
            m += 0.1m;
        }
        Console.WriteLine(d);                // 0.9999999999999999
        Console.WriteLine(m);                // 1.0

        // no implicit double -> decimal: say it
        decimal vat = basePremium * (decimal)0.07;
        Console.WriteLine($"{basePremium} {vat}");
        #endregion
    }
}
