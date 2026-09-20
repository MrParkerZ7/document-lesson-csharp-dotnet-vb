using L07.Core;

namespace L07.Pricing;

/// <summary>+20% when the driver is younger than 25 on the quote start date.
/// Illustrative, not a real tariff — the same tariff as every other lesson.</summary>
public sealed class YoungDriverLoading : IRatingRule
{
    public string Name => "young driver";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        return request.DriverAge < 25 ? 0.20m : 0m;
    }
}

/// <summary>Claims in the last five years: one is +10%, two is +25%,
/// three or more is not a loading at all — the quote is declined.</summary>
public sealed class ClaimsLoading : IRatingRule
{
    public string Name => "claims";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        return request.ClaimsLast5Years switch
        {
            <= 0 => 0m,
            1 => 0.10m,
            2 => 0.25m,
            _ => throw new QuoteDeclinedException(QuoteDeclinedException.ThreeOrMoreClaims),
        };
    }
}

/// <summary>Commercial use: +25%, or +35% for an engine above 3,000 cc.</summary>
public sealed class CommercialUseLoading : IRatingRule
{
    public string Name => "commercial use";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (request.Use != VehicleUse.Commercial)
        {
            return 0m;
        }

        return request.EngineCc > 3_000 ? 0.35m : 0.25m;
    }
}
