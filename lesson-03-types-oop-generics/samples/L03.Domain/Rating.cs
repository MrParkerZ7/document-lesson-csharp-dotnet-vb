using static System.FormattableString;

namespace L03.Domain;

#region interfaces
public interface IRateTable
{
    decimal RateFor(CoverageClass coverage);

    // C# 8 default interface method: a class need not implement it, but
    // it does not inherit it: call it through an IRateTable reference
    Money BasePremium(QuoteRequest request) =>
        request.Vehicle.SumInsured * RateFor(request.Coverage);
}

/// <summary>The curriculum tariff: illustrative rates, not a real tariff.</summary>
public sealed class StandardRateTable : IRateTable
{
    public decimal RateFor(CoverageClass coverage) => coverage switch
    {
        CoverageClass.Class1 => 0.021m,
        CoverageClass.Class2Plus => 0.012m,
        CoverageClass.Class3Plus => 0.009m,
        CoverageClass.Class3 => 0.004m,
        _ => throw new ArgumentOutOfRangeException(nameof(coverage)),
    };
}
#endregion

#region dispatch
public abstract class RatingRule
{
    public abstract string Name { get; }

    // virtual too: loadings add up, a discount multiplies
    public virtual bool IsDiscount => false;

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

/// <summary>Three or more claims in five years: the tariff declines the quote.</summary>
public sealed class QuoteDeclinedException(QuoteRequest request)
    : InvalidOperationException("3+ claims in 5 years")
{
    public QuoteRequest Request { get; } = request;
}

public sealed class ClaimsLoading : RatingRule
{
    public override string Name => "claims";

    public override decimal Factor(QuoteRequest r) => r.Driver.ClaimsLast5Years switch
    {
        0 => 1.00m,
        1 => 1.10m,
        2 => 1.25m,
        _ => throw new QuoteDeclinedException(r),
    };
}

public sealed class NoClaimBonus : RatingRule
{
    public override string Name => "no-claim bonus";

    // the only rule that discounts, so the calculator multiplies it in last
    public override bool IsDiscount => true;

    public override decimal Factor(QuoteRequest r) => ClaimFreeYears(r.Driver) switch
    {
        0 => 1.00m,   // 0% off
        1 => 0.80m,   // 20%
        2 => 0.75m,   // 25%
        3 => 0.70m,   // 30%
        4 => 0.60m,   // 40%
        _ => 0.50m,   // 50%
    };

    private static int ClaimFreeYears(Driver driver) =>
        driver.ClaimsLast5Years == 0 ? driver.LicenceYears : 0;
}

public sealed class CommercialUseLoading : RatingRule
{
    public override string Name => "commercial use";

    public override decimal Factor(QuoteRequest r) => r.Vehicle switch
    {
        { Use: VehicleUse.Private } => 1.00m,
        { EngineCc: > 3_000 } => 1.35m,
        _ => 1.25m,
    };
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
        var loadings = 0m;
        var discount = 1.00m;
        foreach (var rule in _rules)
            if (rule.IsDiscount)
                discount *= rule.Factor(request);
            else
                loadings += rule.Factor(request) - 1.00m;

        // one rounding, on the tariff's own composition
        var net = rates.BasePremium(request)   // captured
                  * ((1.00m + loadings) * discount);
        return new Premium(net);
    }
}
#endregion
