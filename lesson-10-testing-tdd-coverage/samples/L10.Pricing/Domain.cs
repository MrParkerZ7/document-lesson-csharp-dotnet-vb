namespace L10.Pricing;

// MotorQuote vocabulary (see the curriculum). All rates in this library are
// illustrative, not a real tariff.

public readonly record struct Money(decimal Amount, string Currency);

public enum CoverageClass { Class1, Class2Plus, Class3Plus, Class3 }

public enum VehicleUse { Private, Commercial }

public sealed record Vehicle(
    string Make, string Model, int Year, int EngineCc, VehicleUse Use, Money SumInsured);

public sealed record Driver(DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years);

public sealed record QuoteRequest(
    Vehicle Vehicle, Driver Driver, CoverageClass Coverage, DateOnly StartDate);

public sealed record Premium(Money Net, Money StampDuty, Money Vat, Money Total);

public enum QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }

public sealed record Quote(
    Guid Id, QuoteRequest Request, Premium Premium, DateTimeOffset ValidUntil, QuoteStatus Status);
