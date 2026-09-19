using System.Collections.Concurrent;
using System.ComponentModel.DataAnnotations;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;
using MotorQuote.Rating;
using Polly;

namespace L08.QuoteApi.Partners;

public sealed class PartnerOptions
{
    public const string SectionName = "Partners";

    [Required, Url]
    public string BaseAddress { get; set; } = "https://partners.example/";
}

public sealed record PartnerRate(string PartnerId, CoverageClass Coverage, decimal Rate);

public sealed class PartnerUnavailableException(string partnerId, string reason, Exception? inner = null)
    : Exception(reason, inner)
{
    public string PartnerId { get; } = partnerId;
}

public interface IPartnerRateClient
{
    Task<PartnerRate> GetRateAsync(string partnerId, CoverageClass coverage, CancellationToken ct);
}

#region typed-client
/// <summary>Typed client: transient, gets an HttpClient built by IHttpClientFactory.</summary>
public sealed class PartnerRateClient(HttpClient http, PartnerHealth health) : IPartnerRateClient
{
    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web)
    {
        Converters = { new JsonStringEnumConverter() },
    };

    public async Task<PartnerRate> GetRateAsync(
        string partnerId, CoverageClass coverage, CancellationToken ct)
    {
        try
        {
            var rate = await http.GetFromJsonAsync<PartnerRate>(
                $"rates/{partnerId}?coverage={coverage}", Json, ct);
            health.Record(partnerId, succeeded: true);
            return rate ?? throw new PartnerUnavailableException(partnerId, "empty body");
        }
        catch (Exception ex) when (ex is HttpRequestException or ExecutionRejectedException)
        {
            health.Record(partnerId, succeeded: false);   // retries are already exhausted here
            throw new PartnerUnavailableException(partnerId, ex.Message, ex);
        }
    }
}
#endregion

public static class PartnerModule
{
    #region partner-registration
    public static IServiceCollection AddPartnerClients(
        this IServiceCollection services, IConfiguration config)
    {
        services.AddOptions<PartnerOptions>()
            .Bind(config.GetSection(PartnerOptions.SectionName))
            .ValidateDataAnnotations()
            .ValidateOnStart();
        services.AddSingleton<PartnerHealth>();

        services.AddHttpClient<IPartnerRateClient, PartnerRateClient>((sp, http) =>
            {
                var partners = sp.GetRequiredService<IOptions<PartnerOptions>>().Value;
                http.BaseAddress = new Uri(partners.BaseAddress);
            })
            .AddStandardResilienceHandler(config.GetSection("Partners:Resilience"));
        return services;
    }
    #endregion
}

/// <summary>Singleton: remembers whether each partner's last call succeeded.</summary>
public sealed class PartnerHealth
{
    private readonly ConcurrentDictionary<string, bool> _lastCall = new();

    public void Record(string partnerId, bool succeeded) => _lastCall[partnerId] = succeeded;

    public IReadOnlyList<string> Failing() =>
        [.. _lastCall.Where(p => !p.Value).Select(p => p.Key).Order()];
}

public sealed class PartnerHealthCheck(PartnerHealth health) : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken ct = default)
    {
        var failing = health.Failing();
        return Task.FromResult(failing.Count == 0
            ? HealthCheckResult.Healthy("every partner answered its last call")
            : HealthCheckResult.Degraded($"failing partners: {string.Join(", ", failing)}"));
    }
}

#region controller
[ApiController]
[Route("partners")]
public sealed class PartnersController(
    IPartnerRateClient partners) : ControllerBase
{
    [HttpGet("{partnerId:length(3)}/rates")]
    [ProducesResponseType<PartnerRate>(StatusCodes.Status200OK)]
    public async Task<ActionResult<PartnerRate>> GetRate(
        string partnerId,
        [FromQuery] CoverageClass coverage,
        CancellationToken ct)
    {
        return await partners.GetRateAsync(
            partnerId, coverage, ct);
    }
}
#endregion
