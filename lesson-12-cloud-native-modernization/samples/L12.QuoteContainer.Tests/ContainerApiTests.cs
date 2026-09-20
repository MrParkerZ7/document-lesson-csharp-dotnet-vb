using System.Diagnostics;
using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using OpenTelemetry.Trace;

namespace L12.QuoteContainer.Tests;

public sealed class ContainerApiTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    // the tariff's worked example (curriculum, "Canonical tariff"): total 8,933.71 THB
    static readonly object Request = new
    {
        coverage = "Class1", sumInsured = 550_000, driverAge = 23,
        licenceYears = 4, claimsLast5Years = 0, commercial = false,
        engineCc = 1500,
    };

    [Theory]
    [InlineData("/health/live")]
    [InlineData("/health/ready")]
    public async Task Health_endpoints_answer_200(string path)
    {
        var response = await factory.CreateClient().GetAsync(path);
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    [Fact]
    public void Shutdown_timeout_fits_inside_the_ecs_stop_timeout()
    {
        var host = factory.Services.GetRequiredService<IOptions<HostOptions>>().Value;
        Assert.True(host.ShutdownTimeout < TimeSpan.FromSeconds(30));
    }

    [Fact]
    public async Task Quote_total_comes_from_the_vb_rules()
    {
        var response = await factory.CreateClient().PostAsJsonAsync("/quotes", Request);
        var body = await response.Content.ReadFromJsonAsync<Premium>();
        Assert.Equal(8933.71m, body!.Total);
    }

    [Fact]
    public async Task Three_claims_decline_the_quote_with_422()
    {
        var declined = new
        {
            coverage = "Class1", sumInsured = 550_000, driverAge = 23,
            licenceYears = 4, claimsLast5Years = 3, commercial = false,
            engineCc = 1500,
        };
        var response = await factory.CreateClient().PostAsJsonAsync("/quotes", declined);
        Assert.Equal(HttpStatusCode.UnprocessableEntity, response.StatusCode);
    }

    #region span-test
    [Fact]
    public async Task A_quote_emits_a_server_span_and_a_domain_span()
    {
        var spans = new List<Activity>();
        using var app = factory.WithWebHostBuilder(web => web.ConfigureTestServices(
            services => services.ConfigureOpenTelemetryTracerProvider(
                tracing => tracing.AddInMemoryExporter(spans))));

        var response = await app.CreateClient().PostAsJsonAsync("/quotes", Request);
        response.EnsureSuccessStatusCode();

        // the server span stops after the response is written: wait for it
        SpinWait.SpinUntil(() => spans.ToArray().Any(s => s.Kind == ActivityKind.Server),
                           TimeSpan.FromSeconds(5));
        Assert.Contains(spans.ToArray(), s => s.DisplayName == "rate-quote");
        Assert.Contains(spans.ToArray(), s => s.Kind == ActivityKind.Server);
    }
    #endregion

    sealed record Premium(decimal Net, decimal StampDuty, decimal Vat, decimal Total);
}
