using L07.Core;

namespace L07.Pricing;

#region ncb-rule
/// <summary>The C# port: 10% off per claim-free
/// year, at most 50%, none after a claim.</summary>
public sealed class NoClaimBonus : IRatingRule
{
    public string Name => "no-claim bonus";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (request.ClaimsLast5Years > 0)
        {
            return 0m;
        }

        var years = Math.Clamp(request.ClaimFreeYears, 0, 5);
        return -0.10m * years;
    }
}
#endregion
