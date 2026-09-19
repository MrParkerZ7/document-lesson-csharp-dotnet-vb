namespace L02.Syntax;

static class PatternsTour
{
    public static void Run()
    {
        Console.WriteLine();
        Console.WriteLine("[patterns]");

        #region patterns
        object input = new Vehicle("Isuzu", "D-Max", 2023, 3_000,
                                   VehicleUse.Commercial, new Money(900_000m));

        // type pattern + property patterns (+ extended property pattern, C# 10)
        string segment = input switch
        {
            Vehicle { Use: VehicleUse.Commercial, EngineCc: >= 3_000 } => "heavy commercial",
            Vehicle { Use: VehicleUse.Commercial } => "commercial",
            Vehicle { SumInsured.Amount: > 2_000_000m } => "high value",
            Vehicle => "private",
            null => "nothing",
            _ => "not a vehicle",
        };
        Console.WriteLine(segment);

        // `is` with a declaration pattern: test and narrow in one step
        if (input is Vehicle { Year: < 2010 } old)
            Console.WriteLine($"old vehicle {old.Year}");
        else if (input is not null)
            Console.WriteLine("recent or not a vehicle");
        #endregion

        #region list-patterns
        // a partner rate file: RATE,<class>,<percent>[,note]   (list patterns, C# 11)
        string[] lines = ["RATE,Class1,2.1", "RATE,Class3", "RATE,Class2Plus,1.2,promo", "EOF"];
        foreach (var line in lines)
        {
            string parsed = line.Split(',') switch
            {
                ["RATE", var cls, var pct] => $"{cls} at {pct}%",
                ["RATE", var cls, var pct, .. var rest] => $"{cls} at {pct}% (+{rest.Length} field)",
                ["RATE", ..] => "rate line without a percent",
                ["EOF"] => "end of file",
                _ => "unknown line",
            };
            Console.WriteLine(parsed);
        }
        #endregion

        #region enum-trap
        var bogus = (CoverageClass)7;        // compiles: an int
        Console.WriteLine(Enum.IsDefined(bogus));   // False
        try
        {
            RatingRules.BaseRate(bogus, new Money(1m));
        }
        catch (ArgumentOutOfRangeException e)
        {
            Console.WriteLine($"discard arm hit: {e.ParamName}");
        }
        #endregion
    }
}
