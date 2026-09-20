using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Time.Testing;

namespace L10.QuoteApi.Tests;

public class QuoteApiTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    private static readonly JsonSerializerOptions Json =
        new(JsonSerializerDefaults.Web) { Converters = { new JsonStringEnumConverter() } };

    #region round-trip
    [Fact]
    public async Task Post_then_get_returns_the_same_quote()
    {
        var ct = TestContext.Current.CancellationToken;
        using var client = factory.CreateClient();

        var created = await client.PostAsJsonAsync("/quotes", Requests.Standard(), Json, ct);
        var quote = await created.Content.ReadFromJsonAsync<Quote>(Json, ct);
        var fetched = await client.GetFromJsonAsync<Quote>(created.Headers.Location, Json, ct);

        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
        Assert.Equal(6_767.96m, quote!.Premium.Total.Amount);
        Assert.Equal(quote.Id, fetched!.Id);
    }
    #endregion

    #region swap-clock
    [Fact]
    public async Task Accepting_an_expired_quote_returns_409()
    {
        var ct = TestContext.Current.CancellationToken;
        var clock = new FakeTimeProvider(new DateTimeOffset(2026, 10, 1, 9, 0, 0, TimeSpan.Zero));
        await using var app = factory.WithWebHostBuilder(host =>
            host.ConfigureTestServices(services => services.AddSingleton<TimeProvider>(clock)));
        using var client = app.CreateClient();

        var created = await client.PostAsJsonAsync("/quotes", Requests.Standard(), Json, ct);
        var quote = await created.Content.ReadFromJsonAsync<Quote>(Json, ct);
        clock.Advance(TimeSpan.FromDays(31));
        var accepted = await client.PostAsync($"/quotes/{quote!.Id}/accept", null, ct);

        Assert.Equal(HttpStatusCode.Conflict, accepted.StatusCode);
    }
    #endregion

    [Fact]
    public async Task An_unknown_quote_is_404()
    {
        using var client = factory.CreateClient();

        var response = await client.GetAsync($"/quotes/{Guid.NewGuid()}",
            TestContext.Current.CancellationToken);

        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
