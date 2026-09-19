namespace L04.QuoteData;

/// <summary>Money as a value: a decimal amount, THB by default.</summary>
public readonly record struct Money(decimal Amount, string Currency = "THB");

/// <summary>Thai motor classes: 1 = comprehensive ... 3 = third-party only.</summary>
public enum CoverageClass { Class1, Class2Plus, Class3Plus, Class3 }

public enum VehicleUse { Private, Commercial }

public enum QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }

public sealed record Vehicle(
    string Make, string Model, int Year, int EngineCc, VehicleUse Use, Money SumInsured);

public sealed record Driver(DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years);

#region quote-record
public sealed record Quote(
    string QuoteId,
    Vehicle Vehicle,
    Driver Driver,
    CoverageClass Coverage,
    DateOnly StartDate,
    Money Total,
    QuoteStatus Status)
{
    // computed in C#, never stored: a query provider cannot translate it
    public bool IsAccepted => Status == QuoteStatus.Accepted;
}
#endregion

public sealed record Policy(string PolicyNumber, string QuoteId, DateOnly Inception, DateOnly Expiry);

public sealed record ClassConversion(CoverageClass Coverage, int Quoted, int Accepted)
{
    public decimal Rate => Quoted == 0 ? 0m : (decimal)Accepted / Quoted;
}

public sealed record MakeRank(int Rank, string Make, int Sold);
