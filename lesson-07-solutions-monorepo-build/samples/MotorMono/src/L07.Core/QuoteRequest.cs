namespace L07.Core;

/// <summary>Thai motor classes: 1 = comprehensive ... 3 = third-party only.</summary>
public enum CoverageClass
{
    Class1,
    Class2Plus,
    Class3Plus,
    Class3,
}

public enum VehicleUse
{
    Private,
    Commercial,
}

/// <summary>What the rating rules need to know about a quote. No names, no personal data.</summary>
public sealed record QuoteRequest(
    CoverageClass Coverage,
    Money SumInsured,
    int DriverAge,
    int ClaimFreeYears,
    int ClaimsLast5Years,
    VehicleUse Use = VehicleUse.Private);
