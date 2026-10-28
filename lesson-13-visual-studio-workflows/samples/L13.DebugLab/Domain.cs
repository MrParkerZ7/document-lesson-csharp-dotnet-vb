using System.Diagnostics;

namespace L13.DebugLab;

public enum CoverageClass { Class1, Class2Plus, Class3Plus, Class3 }

public enum VehicleUse { Private, Commercial }

#region MoneyDisplay
// {Amount} and {Currency,nq} are expressions the debugger
// evaluates: Locals, Watch and data tips show the result.
[DebuggerDisplay("{Amount} {Currency,nq}")]
public readonly record struct Money(
    decimal Amount, string Currency)
{
    public static Money Thb(decimal amount) =>
        new(amount, "THB");
}
#endregion

public sealed record Vehicle(string Make, string Model, int Year, int EngineCc, VehicleUse Use, Money SumInsured);

public sealed record Driver(DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years);

#region RequestDisplay
// A DebuggerDisplay may walk into members: this one reads Vehicle.Make and Vehicle.SumInsured.
[DebuggerDisplay("{Coverage} · {Vehicle.Make} · sum {Vehicle.SumInsured}")]
public sealed record QuoteRequest(Vehicle Vehicle, Driver Driver, CoverageClass Coverage, DateOnly StartDate);
#endregion

[DebuggerDisplay("net {Net} · total {Total}")]
public sealed record Premium(Money Base, decimal LoadingRate, decimal DiscountRate,
                             Money Net, Money StampDuty, Money Vat, Money Total);

/// <summary>A domain outcome, not a crash: the tariff declines 3 or more claims in 5 years.</summary>
public sealed class QuoteDeclinedException(string reason) : Exception(reason);
