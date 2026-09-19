namespace L02.Syntax;

static class ErrorsTour
{
    public static void Run()
    {
        Console.WriteLine();
        Console.WriteLine("[errors]");
        Resources();
        FilterOrder();
        Console.WriteLine(Percent("2.1"));
    }

    static void Resources()
    {
        #region resources
        using var audit = new AuditScope("audit");  // declaration
        using var trace = new AuditScope("trace");  // disposed first

        var request = Examples.YoungDriver(claims: 3);
        try
        {
            var premium = PremiumCalculator.Calculate(request);
            Console.WriteLine(premium.Total);
        }
        catch (QuoteDeclinedException e)
            when (e.Reason.Contains("claims"))  // filter
        {
            Console.WriteLine($"declined: {e.Reason}");
        }
        // end of scope: trace, then audit, are disposed
        #endregion
    }

    static void FilterOrder()
    {
        #region filter-order
        try
        {
            Rate();
        }
        catch (Exception e) when (Log(e))              // 1st: the filter runs BEFORE unwinding
        {
            Console.WriteLine("catch block");         // 3rd
        }

        static void Rate()
        {
            try { throw new QuoteDeclinedException("3+ claims in 5 years"); }
            finally { Console.WriteLine("inner finally"); }   // 2nd
        }

        static bool Log(Exception e)
        {
            Console.WriteLine($"filter sees {e.GetType().Name}");
            return true;                               // false = keep searching up the stack
        }
        #endregion
    }

    #region throw-expressions
    static decimal Percent(string text) =>
        decimal.TryParse(text, CultureInfo.InvariantCulture, out var p)
            ? p / 100m
            : throw new FormatException($"not a percent: {text}");   // throw as an expression
    #endregion

    public static async Task RunAsync()
    {
        #region await-using
        await using var partner = new PartnerConnection();   // IAsyncDisposable
        await Task.Yield();
        Console.WriteLine("partner rates fetched (simulated)");
        #endregion
    }
}
