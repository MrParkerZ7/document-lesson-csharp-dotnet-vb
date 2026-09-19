using static System.FormattableString;

namespace L03.Domain;

#region interfaces
public interface IRateTable
{
    decimal BaseRate(CoverageClass coverage);

    // C# 8 default interface method: a class need not implement it, but
    // it does not inherit it: call it through an IRateTable reference
    Money BasePremium(QuoteRequest request) =>
        request.Vehicle.SumInsured * BaseRate(request.Coverage);
}

/// <summary>Illustrative rates, not a real tariff.</summary>
public sealed class StandardRateTable : IRateTable
{
    public decimal BaseRate(CoverageClass coverage) => coverage switch
    {
        CoverageClass.Class1 => 0.0250m,
        CoverageClass.Class2Plus => 0.0160m,
        CoverageClass.Class3Plus => 0.0120m,
        CoverageClass.Class3 => 0.0040m,
        _ => throw new ArgumentOutOfRangeException(nameof(coverage)),
    };
}
#endregion

#region dispatch
public abstract class RatingRule
{
    public abstract string Name { get; }

    // virtual: a derived class MAY override it
    public virtual decimal Factor(QuoteRequest r) => 1.00m;

    // not virtual (the C# default): it can only be hidden
    public string Describe(QuoteRequest r) =>
        Invariant($"{Name} x{Factor(r)}");
}

public sealed class YoungDriverLoading : RatingRule
{
    public override string Name => "young driver";

    public override decimal Factor(QuoteRequest r) =>
        r.Driver.AgeOn(r.StartDate) < 25 ? 1.20m : 1.00m;

    // `new` HIDES the base method; it does not override it
    public new string Describe(QuoteRequest r) =>
        $"{Name} (hidden copy)";
}
#endregion

public sealed class ClaimsLoading : RatingRule
{
    public override string Name => "claims";

    public override decimal Factor(QuoteRequest r) =>
        1.00m + 0.15m * r.Driver.ClaimsLast5Years;
}

public sealed class NoClaimBonus : RatingRule
{
    public override string Name => "no-claim bonus";

    // 5% per claim-free licence year, capped at 25% (illustrative)
    public override decimal Factor(QuoteRequest r) =>
        r.Driver.ClaimsLast5Years == 0
            ? 1.00m - 0.05m * Math.Min(r.Driver.LicenceYears, 5)
            : 1.00m;
}

public sealed class CommercialUseLoading : RatingRule
{
    public override string Name => "commercial use";

    public override decimal Factor(QuoteRequest r) =>
        r.Vehicle.Use == VehicleUse.Commercial ? 1.25m : 1.00m;
}

#region primary-ctor
// C# 12 primary constructor: the DI shape, no boilerplate
public sealed class PremiumCalculator(
    IRateTable rates, IEnumerable<RatingRule> rules)
{
    // `rules` is a parameter, not a property, not readonly:
    // copy it once: nothing can re-assign or re-enumerate it
    private readonly RatingRule[] _rules = [.. rules];

    public Premium Calculate(QuoteRequest request)
    {
        var net = rates.BasePremium(request); // captured
        foreach (var rule in _rules)
            net *= rule.Factor(request);
        return new Premium(net);
    }
}
#endregion
