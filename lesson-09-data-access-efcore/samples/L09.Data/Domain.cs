namespace L09.Data;

#region money
// A value object: no key, compared by value. Configuration.cs maps it
// with ComplexProperty (complex types are never found by convention):
// columns on the owning row, no table.
public readonly record struct Money(decimal Amount, string Currency)
{
    public static Money Thb(decimal amount) => new(amount, "THB");
}

// A record class works too (Driver_* columns): also ComplexProperty.
public sealed record Driver(
    DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years);
#endregion

public enum CoverageClass { Class1, Class2Plus, Class3Plus, Class3 }

public enum VehicleUse { Private, Commercial }

public enum QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }
