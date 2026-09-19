namespace L05.PartnerRates;

/// <summary>An amount of money. THB by default; every rate in these samples is illustrative.</summary>
public readonly record struct Money(decimal Amount, string Currency = "THB")
{
    public override string ToString() => $"{Amount:N2} {Currency}";
}

/// <summary>Thai motor coverage classes: 1 = comprehensive … 3 = third-party only.</summary>
public enum CoverageClass { Class1, Class2Plus, Class3Plus, Class3 }

/// <summary>The part of a MotorQuote request a rating partner needs.</summary>
public sealed record QuoteRequest(string Make, int Year, CoverageClass Coverage, Money SumInsured);
