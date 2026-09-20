using L07.Core;

namespace L07.Pricing;

public sealed record PremiumLine(string Rule, string Module, Money Amount);

public sealed record Premium(
    Money Base,
    IReadOnlyList<PremiumLine> Adjustments,
    Money Net,
    Money StampDuty,
    Money Vat,
    Money Total);

/// <summary>Applies every rule it is given, in the order the tariff composes them: the loadings are
/// summed and applied to the base premium, then the no-claim discount applies to the loaded premium.
/// Rates and taxes are illustrative, not a real tariff.</summary>
public sealed class PremiumCalculator(IEnumerable<IRatingRule> rules)
{
    private readonly IRatingRule[] _rules = [.. rules];

    public Premium Calculate(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        var basePremium = request.SumInsured.Times(BaseRates.For(request.Coverage)).Rounded();

        // a rule that declines the quote throws from Factor, so ask every rule once, up front
        var factors = _rules.Select(rule => (Rule: rule, Factor: rule.Factor(request))).ToList();
        var loaded = basePremium.Times(1m + factors.Where(f => f.Factor > 0m).Sum(f => f.Factor));
        var discount = factors.Where(f => f.Factor < 0m).Sum(f => f.Factor);

        var adjustments = factors
            .Select(f => new PremiumLine(f.Rule.Name, ModuleOf(f.Rule),
                (f.Factor < 0m ? loaded : basePremium).Times(f.Factor).Rounded()))
            .Where(line => line.Amount.Amount != 0m)
            .ToList();

        var net = loaded.Times(1m + discount).Rounded();
        var stampDuty = net.Times(Taxes.StampDutyRate).Rounded();
        var vat = net.Plus(stampDuty).Times(Taxes.VatRate).Rounded();
        return new Premium(basePremium, adjustments, net, stampDuty, vat, net.Plus(stampDuty).Plus(vat));
    }

    // the assembly - the module of the mono-repo - that the rule was compiled into
    private static string ModuleOf(IRatingRule rule) => rule.GetType().Assembly.GetName().Name ?? "?";
}
