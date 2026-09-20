using System.Diagnostics;
using System.Diagnostics.Metrics;
using L12.RatingVb;
using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace L12.QuoteContainer;

public sealed record QuoteRequest(
    CoverageClass Coverage, decimal SumInsured, int DriverAge,
    int LicenceYears, int ClaimsLast5Years, bool Commercial,
    int EngineCc);

/// <summary>One ActivitySource and one Meter per service — OpenTelemetry subscribes to them by name.</summary>
public static class QuoteTelemetry
{
    public static readonly ActivitySource Source = new("MotorQuote.Api");
    public static readonly Meter Meter = new("MotorQuote.Api");
    public static readonly Counter<long> QuotesIssued =
        Meter.CreateCounter<long>("motorquote.quotes.issued");
}

/// <summary>Readiness: the VB rating library loads and returns a premium.</summary>
public sealed class RatingSelfCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        var p = Rating.Quote(CoverageClass.Class3, 100_000m, 40, 20, 0, false, 1500);
        return Task.FromResult(p.Total > 0
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Unhealthy("rating returned a zero premium"));
    }
}
