using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;

namespace L08.QuoteApi.Tests;

public sealed class CrossCuttingTests(QuoteApiFactory factory) : IClassFixture<QuoteApiFactory>
{
    [Fact]
    public async Task Health_endpoint_reports_healthy_as_plain_text()
    {
        var response = await factory.CreateClient().GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("Healthy", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Cors_preflight_allows_the_broker_portal_origin_only()
    {
        var client = factory.CreateClient();

        var allowed = await client.SendAsync(Preflight("https://brokers.example"));
        var other = await client.SendAsync(Preflight("https://evil.example"));

        Assert.Equal("https://brokers.example",
            allowed.Headers.GetValues("Access-Control-Allow-Origin").Single());
        Assert.False(other.Headers.Contains("Access-Control-Allow-Origin"));
    }

    [Fact]
    public async Task Tariff_endpoint_written_in_visual_basic_is_served_and_cached()
    {
        var client = factory.CreateClient();

        var first = await client.GetAsync("/tariff/Class3Plus");
        var second = await client.GetAsync("/tariff/Class3Plus");

        Assert.Equal(HttpStatusCode.OK, first.StatusCode);
        var row = await first.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("Class3Plus", row.GetProperty("coverage").GetString());
        Assert.Equal(0.009m, row.GetProperty("baseRate").GetDecimal());
        Assert.False(first.Headers.Contains("Age"));
        Assert.True(second.Headers.Contains("Age"));     // served by the output cache
    }

    [Fact]
    public async Task OpenApi_document_is_version_3_1_and_lists_every_route()
    {
        var document = await factory.CreateClient().GetFromJsonAsync<JsonElement>("/openapi/v1.json");

        Assert.StartsWith("3.1", document.GetProperty("openapi").GetString());
        var paths = document.GetProperty("paths").EnumerateObject().Select(p => p.Name).ToList();
        Assert.Contains("/quotes", paths);
        Assert.Contains("/quotes/{id}", paths);
        Assert.Contains("/quotes/{id}/accept", paths);
        Assert.Contains("/tariff/{coverage}", paths);
        Assert.Contains("/partners/{partnerId}/rates", paths);
    }

    private static HttpRequestMessage Preflight(string origin) => new(HttpMethod.Options, "/quotes")
    {
        Headers =
        {
            { "Origin", origin },
            { "Access-Control-Request-Method", "POST" },
        },
    };
}

public sealed class RateLimitTests
{
    #region rate-limit-test
    [Fact]
    public async Task Third_quote_in_the_same_minute_is_rejected_with_429()
    {
        await using var factory = new QuoteApiFactory { QuoteWritesPerMinute = 2 };
        var client = factory.CreateClient();

        var responses = new List<HttpResponseMessage>();
        for (var i = 0; i < 3; i++)
            responses.Add(await client.PostAsJsonAsync("/quotes", Requests.Quote()));

        Assert.Equal([HttpStatusCode.Created, HttpStatusCode.Created, HttpStatusCode.TooManyRequests],
            responses.Select(r => r.StatusCode));
        // the limiter writes no body, so UseStatusCodePages turns the 429 into ProblemDetails
        Assert.Equal("application/problem+json", responses[2].Content.Headers.ContentType?.MediaType);
    }
    #endregion
}

public sealed class JsonOptionsTests
{
    [Fact]
    public async Task Minimal_APIs_and_controllers_read_separate_json_options()
    {
        // remove the enum converter from the MVC options only
        await using var factory = new QuoteApiFactory().WithWebHostBuilder(web =>
            web.ConfigureTestServices(services =>
                services.Configure<Microsoft.AspNetCore.Mvc.JsonOptions>(
                    o => o.JsonSerializerOptions.Converters.Clear())));
        var client = factory.CreateClient();

        var controller = await client.GetFromJsonAsync<JsonElement>("/partners/p07/rates?coverage=Class1");
        var minimalApi = await client.GetFromJsonAsync<JsonElement>("/tariff/Class3Plus");

        Assert.Equal(JsonValueKind.Number, controller.GetProperty("coverage").ValueKind);   // 0
        Assert.Equal("Class3Plus", minimalApi.GetProperty("coverage").GetString());         // unchanged
    }
}
