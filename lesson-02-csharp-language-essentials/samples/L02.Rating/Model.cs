namespace L02.Rating;

// The MotorQuote vocabulary. Records, structs and enums are lesson 03's topic;
// here they are only the nouns the rating rules talk about.
// Every rate in this library is ILLUSTRATIVE, not a real tariff.

public enum CoverageClass { Class1, Class2Plus, Class3Plus, Class3 }

public enum VehicleUse { Private, Commercial }

public readonly record struct Money(decimal Amount, string Currency = "THB");

public sealed record Vehicle(
    string Make, string Model, int Year, int EngineCc,
    VehicleUse Use, Money SumInsured);

public sealed record Driver(
    DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years)
{
    #region age-on
    public int AgeOn(DateOnly date)
    {
        int age = date.Year - DateOfBirth.Year;
        return DateOfBirth > date.AddYears(-age) ? age - 1 : age;
    }
    #endregion
}

public sealed record QuoteRequest(
    Vehicle Vehicle, Driver Driver, CoverageClass Coverage, DateOnly StartDate);

public sealed record Premium(
    decimal Base, decimal Loadings, decimal Discount, decimal Net,
    decimal StampDuty, decimal Vat, decimal Total);

/// <summary>Thrown when the rules refuse to quote. Unchecked, like every .NET exception.</summary>
public sealed class QuoteDeclinedException(string reason)
    : Exception($"Quote declined: {reason}")
{
    public string Reason { get; } = reason;
}
