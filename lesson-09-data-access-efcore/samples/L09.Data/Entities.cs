namespace L09.Data;

#region entities
// Plain classes: no base class, no annotations. The mapping lives in
// Configuration.cs, so the domain types stay persistence-ignorant.
public class Quote
{
    public int Id { get; set; }
    public required string Reference { get; set; }
    public int VehicleId { get; set; }
    public Vehicle Vehicle { get; set; } = null!;
    public required Driver Driver { get; set; }
    public CoverageClass Coverage { get; set; }
    public QuoteStatus Status { get; set; }
    public Money Total { get; set; }
    public DateOnly ValidUntil { get; set; }
    public List<PremiumLine> Lines { get; } = [];
    public Guid Version { get; set; }
}
#endregion

public class Vehicle
{
    public int Id { get; set; }
    public required string Make { get; set; }
    public required string Model { get; set; }
    public int Year { get; set; }
    public int EngineCc { get; set; }
    public VehicleUse Use { get; set; }
    public Money SumInsured { get; set; }
}

public class PremiumLine
{
    public int Id { get; set; }
    public int QuoteId { get; set; }
    public required string Kind { get; set; }
    public Money Amount { get; set; }
}

public class Policy
{
    public int Id { get; set; }
    public required string PolicyNumber { get; set; }
    public int QuoteId { get; set; }
    public Quote Quote { get; set; } = null!;
    public DateOnly Inception { get; set; }
    public DateOnly Expiry { get; set; }
}
