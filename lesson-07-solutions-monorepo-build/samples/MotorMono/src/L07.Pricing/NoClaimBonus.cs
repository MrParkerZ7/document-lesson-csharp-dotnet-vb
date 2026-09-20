using L07.Core;

namespace L07.Pricing;

#region ncb-rule
/// <summary>The C# port of the shared no-claim
/// ladder: 20-50% off, none after a claim.</summary>
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

        return request.ClaimFreeYears switch
        {
            <= 0 => 0m,
            1 => -0.20m,
            2 => -0.25m,
            3 => -0.30m,
            4 => -0.40m,
            _ => -0.50m,
        };
    }
}
#endregion
