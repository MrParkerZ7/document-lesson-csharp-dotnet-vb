using System.ComponentModel.DataAnnotations;
using System.Threading.RateLimiting;
using L08.QuoteApi.Partners;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.Extensions.Options;

namespace L08.QuoteApi.CrossCutting;

#region exception-handler
public sealed class PartnerExceptionHandler(
    IProblemDetailsService problems,
    ILogger<PartnerExceptionHandler> logger) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext http, Exception exception, CancellationToken ct)
    {
        if (exception is not PartnerUnavailableException partner)
            return false;   // not ours: the next handler, then the default 500

        // .NET 10 no longer logs exceptions a handler reports as handled: log it yourself
        logger.LogWarning("Partner {PartnerId} unavailable: {Reason}",
            partner.PartnerId, partner.Message);

        http.Response.StatusCode = StatusCodes.Status503ServiceUnavailable;
        http.Response.Headers.RetryAfter = "30";
        return await problems.TryWriteAsync(new ProblemDetailsContext
        {
            HttpContext = http,
            Exception = exception,
            ProblemDetails =
            {
                Status = StatusCodes.Status503ServiceUnavailable,
                Title = "Rating partner unavailable",
                Detail = $"Partner {partner.PartnerId} did not answer after retries.",
                Extensions = { ["partnerId"] = partner.PartnerId },
            },
        });
    }
}
#endregion

public sealed class RateLimitOptions
{
    public const string SectionName = "RateLimits";

    [Range(1, 10_000)]
    public int QuoteWritesPerMinute { get; set; } = 20;
}

public static class RateLimits
{
    public const string QuoteWrites = "quote-writes";

    #region rate-limits
    public static IServiceCollection AddQuoteRateLimits(this IServiceCollection services)
    {
        services.AddOptions<RateLimitOptions>()
            .BindConfiguration(RateLimitOptions.SectionName)
            .ValidateDataAnnotations()
            .ValidateOnStart();

        return services.AddRateLimiter(limiter =>
        {
            limiter.RejectionStatusCode = StatusCodes.Status429TooManyRequests; // default is 503
            limiter.AddPolicy(QuoteWrites, http =>
            {
                var limits = http.RequestServices.GetRequiredService<IOptions<RateLimitOptions>>();
                return RateLimitPartition.GetFixedWindowLimiter(
                    partitionKey: http.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                    factory: _ => new FixedWindowRateLimiterOptions
                    {
                        PermitLimit = limits.Value.QuoteWritesPerMinute,
                        Window = TimeSpan.FromMinutes(1),
                        QueueLimit = 0,
                    });
            });
        });
    }
    #endregion
}
