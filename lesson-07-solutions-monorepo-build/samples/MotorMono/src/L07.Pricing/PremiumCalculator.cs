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

/// <summary>Applies every rule it is given. Rates and taxes are illustrative, not a real tariff.</summary>
public sealed class PremiumCalculator(IEnumerable<IRatingRule> rules)
{
    private readonly IRatingRule[] _rules = [.. rules];

    public Premium Calculate(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        var basePremium = request.SumInsured.Times(BaseRates.For(request.Coverage)).Rounded();

        var adjustments = _rules
            .Select(rule => new PremiumLine(
                rule.Name, ModuleOf(rule), basePremium.Times(rule.Factor(request)).Rounded()))
            .Where(line => line.Amount.Amount != 0m)
            .ToList();

        var net = adjustments.Aggregate(basePremium, (sum, line) => sum.Plus(line.Amount));
        var stampDuty = net.Times(Taxes.StampDutyRate).Rounded();
        var vat = net.Plus(stampDuty).Times(Taxes.VatRate).Rounded();
        return new Premium(basePremium, adjustments, net, stampDuty, vat, net.Plus(stampDuty).Plus(vat));
    }

    // the assembly - the module of the mono-repo - that the rule was compiled into
    private static string ModuleOf(IRatingRule rule) => rule.GetType().Assembly.GetName().Name ?? "?";
}
