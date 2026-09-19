using L07.Core;

namespace L07.Pricing;

/// <summary>+25% when the driver is younger than 25. Illustrative, not a real tariff.</summary>
public sealed class YoungDriverLoading : IRatingRule
{
    public string Name => "young driver";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        return request.DriverAge < 25 ? 0.25m : 0m;
    }
}

/// <summary>+10% per claim in the last five years, at most +50%.</summary>
public sealed class ClaimsLoading : IRatingRule
{
    public string Name => "claims";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        return Math.Min(request.ClaimsLast5Years, 5) * 0.10m;
    }
}

/// <summary>+15% for a vehicle in commercial use.</summary>
public sealed class CommercialUseLoading : IRatingRule
{
    public string Name => "commercial use";

    public decimal Factor(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        return request.Use == VehicleUse.Commercial ? 0.15m : 0m;
    }
}
