using System.Net;
using System.Net.Http.Json;
using L08.QuoteApi.Partners;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Time.Testing;

namespace L08.QuoteApi.Tests;

#region factory
/// <summary>Boots the real Program in memory (TestServer): no port, no network.</summary>
public sealed class QuoteApiFactory : WebApplicationFactory<Program>
{
    public FakeTimeProvider Clock { get; } =
        new(new DateTimeOffset(2026, 9, 1, 9, 0, 0, TimeSpan.Zero));

    public FakePartner Partner { get; } = new();

    public int QuoteWritesPerMinute { get; init; } = 1000;

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Testing");      // the factory's default is Development
        builder.UseSetting("Partners:Resilience:Retry:Delay", "00:00:00.010");
        builder.UseSetting("RateLimits:QuoteWritesPerMinute", QuoteWritesPerMinute.ToString());
        builder.UseDefaultServiceProvider(options =>
        {
            options.ValidateScopes = true;      // on by default only in Development
            options.ValidateOnBuild = true;
        });
        builder.ConfigureTestServices(services =>
        {
            services.AddSingleton<TimeProvider>(Clock);
            services.AddHttpClient<IPartnerRateClient, PartnerRateClient>()
                .ConfigurePrimaryHttpMessageHandler(() => Partner);  // no network
        });
    }
}
#endregion

public static class ClockDriving
{
    #region advance-clock
    /// <summary>
    /// The resilience pipeline takes TimeProvider from DI too: with a fake clock its retry
    /// delays and timeouts only elapse when the test moves time forward.
    /// </summary>
    public static async Task<HttpResponseMessage> GetAdvancingClock(
        this HttpClient client, FakeTimeProvider clock, string url)
    {
        var call = client.GetAsync(url);
        while (!call.IsCompleted)
        {
            clock.Advance(TimeSpan.FromMilliseconds(100));
            await Task.WhenAny(call, Task.Delay(5));
        }
        return await call;
    }
    #endregion
}

/// <summary>An in-process rating partner that fails a set number of times before answering.</summary>
public sealed class FakePartner : HttpMessageHandler
{
    private int _attempts;

    public int Attempts => _attempts;

    public int FailuresBeforeSuccess { get; set; }

    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var attempt = Interlocked.Increment(ref _attempts);
        if (attempt <= FailuresBeforeSuccess)
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.ServiceUnavailable));

        var partnerId = request.RequestUri!.Segments[^1];   // .../rates/p07?coverage=...
        return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = JsonContent.Create(new { partnerId, coverage = "Class1", rate = 0.021m }),
        });
    }
}

/// <summary>Request bodies as an external client sends them: plain JSON, no shared C# types.</summary>
public static class Requests
{
    public static object Quote(
        string startDate = "2026-09-15", string dateOfBirth = "1990-05-01", int licenceYears = 10,
        int claims = 0, string use = "Private", decimal sumInsured = 800_000m, string make = "Toyota",
        string coverage = "Class1", string notifyVia = "line") => new
    {
        vehicle = new { make, model = "Corolla Cross", year = 2024, engineCc = 1800, use, sumInsured },
        driver = new { dateOfBirth, licenceYears, claimsLast5Years = claims },
        coverage,
        startDate,
        notifyVia,
    };
}
