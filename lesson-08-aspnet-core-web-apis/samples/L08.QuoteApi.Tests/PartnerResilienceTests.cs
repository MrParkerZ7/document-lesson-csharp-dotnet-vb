using System.Net;
using System.Net.Http.Json;
using System.Text.Json;

namespace L08.QuoteApi.Tests;

/// <summary>Each test boots its own app, so the partner attempt counter starts at zero.</summary>
public sealed class PartnerResilienceTests
{
    [Fact]
    public async Task Partner_that_fails_twice_is_retried_and_the_call_succeeds()
    {
        await using var factory = new QuoteApiFactory();
        factory.Partner.FailuresBeforeSuccess = 2;

        var response = await factory.CreateClient()
            .GetAdvancingClock(factory.Clock, "/partners/p07/rates?coverage=Class1");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal(3, factory.Partner.Attempts);
    }

    #region partner-failure-test
    [Fact]
    public async Task Partner_that_keeps_failing_becomes_503_and_degraded_health()
    {
        await using var factory = new QuoteApiFactory();
        factory.Partner.FailuresBeforeSuccess = int.MaxValue;
        var client = factory.CreateClient();

        var response = await client.GetAdvancingClock(
            factory.Clock, "/partners/p09/rates?coverage=Class1");

        Assert.Equal(HttpStatusCode.ServiceUnavailable, response.StatusCode);
        Assert.Equal(4, factory.Partner.Attempts);            // 1 try + 3 retries
        Assert.Equal("30", response.Headers.RetryAfter?.ToString());
        var problem = await response.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("p09", problem.GetProperty("partnerId").GetString());

        var health = await client.GetAsync("/health");
        Assert.Equal(HttpStatusCode.OK, health.StatusCode);   // Degraded is still 200
        Assert.Equal("Degraded", await health.Content.ReadAsStringAsync());
    }
    #endregion
}
