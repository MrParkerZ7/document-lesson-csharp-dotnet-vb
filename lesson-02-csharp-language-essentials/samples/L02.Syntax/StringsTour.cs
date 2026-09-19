namespace L02.Syntax;

static class StringsTour
{
    public static void Run()
    {
        Console.WriteLine();
        Console.WriteLine("[strings]");

        #region strings
        var make = "Toyota";
        decimal total = 10_422.67m;
        var de = CultureInfo.GetCultureInfo("de-DE");

        // interpolation + format specifiers; the CURRENT culture picks the separators
        Console.WriteLine($"{make} total {total:N2} THB");
        Console.WriteLine(string.Create(de, $"{make} total {total:N2} THB"));

        // verbatim string: backslashes are literal
        var path = @"C:\quotes\2026\Q-0001.json";

        // raw string literal (C# 11): no escaping; $$ means holes are {{ }}
        var json = $$"""
            { "make": "{{make}}", "total": {{total}} }
            """;
        Console.WriteLine(path);
        Console.WriteLine(json);
        #endregion

        #region comparison
        var tr = CultureInfo.GetCultureInfo("tr-TR");
        var th = CultureInfo.GetCultureInfo("th-TH");

        // culture-aware casing: Turkish upper-cases i to a dotted capital I
        Console.WriteLine("file".ToUpper(tr));                           // FİLE
        Console.WriteLine("file".ToUpperInvariant() == "FILE");          // True

        // IndexOf(string) is linguistic by default and skips ignorable characters
        char softHyphen = (char)0xAD;
        string partnerCode = "MQ" + softHyphen + "TH";
        Console.WriteLine(partnerCode.IndexOf("MQTH"));                  // 0
        Console.WriteLine(partnerCode.IndexOf("MQTH", StringComparison.Ordinal)); // -1

        // identifiers: compare ordinally, and say so
        Console.WriteLine(string.Equals("mq-th", "MQ-TH", StringComparison.OrdinalIgnoreCase));

        // th-TH formats dates in the Thai Buddhist calendar
        var start = new DateOnly(2026, 10, 1);
        Console.WriteLine(start.ToString("d/M/yyyy", th));                 // 1/10/2569
        Console.WriteLine(start.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture));
        #endregion
    }
}
