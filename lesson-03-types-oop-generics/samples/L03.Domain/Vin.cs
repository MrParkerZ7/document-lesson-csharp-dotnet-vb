namespace L03.Domain;

#region equatable-class
// the pre-records way: every equality member by hand
public sealed class Vin : IEquatable<Vin>
{
    private static readonly StringComparer Rule =
        StringComparer.OrdinalIgnoreCase;

    public Vin(string value) => Value = value;
    public string Value { get; }

    public bool Equals(Vin? other) =>
        other is not null && Rule.Equals(Value, other.Value);
    public override bool Equals(object? obj) =>
        Equals(obj as Vin);
    public override int GetHashCode() =>
        Rule.GetHashCode(Value); // the SAME rule as Equals
    public static bool operator ==(Vin? a, Vin? b) =>
        a is null ? b is null : a.Equals(b);
    public static bool operator !=(Vin? a, Vin? b) =>
        !(a == b);
}
#endregion

#region equatable-record
// the same contract as a record: replace only what differs
public sealed record VinRecord(string Value)
{
    private static readonly StringComparer Rule =
        StringComparer.OrdinalIgnoreCase;

    public bool Equals(VinRecord? other) =>
        other is not null && Rule.Equals(Value, other.Value);

    public override int GetHashCode() =>
        Rule.GetHashCode(Value);

    // Equals(object), == and != are still generated,
    // and they call the Equals above
}
#endregion

/// <summary>The bug to avoid: equal by one rule, hashed by another.</summary>
public sealed class BrokenVin(string value) : IEquatable<BrokenVin>
{
    public string Value { get; } = value;

    public bool Equals(BrokenVin? other) =>
        other is not null && string.Equals(Value, other.Value, StringComparison.OrdinalIgnoreCase);

    public override bool Equals(object? obj) => Equals(obj as BrokenVin);

    public override int GetHashCode() => Value.GetHashCode(StringComparison.Ordinal); // case-SENSITIVE
}
