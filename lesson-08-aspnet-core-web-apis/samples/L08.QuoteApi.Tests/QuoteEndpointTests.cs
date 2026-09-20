using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using MotorQuote.Rating;

namespace L08.QuoteApi.Tests;

public sealed class QuoteEndpointTests(QuoteApiFactory factory) : IClassFixture<QuoteApiFactory>
{
    private readonly HttpClient _client = factory.CreateClient();

    #region post-test
    [Fact]
    public async Task Post_quote_returns_201_and_location()
    {
        var response = await _client.PostAsJsonAsync(
            "/quotes", Requests.Quote());

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var quote = await response.Content
            .ReadFromJsonAsync<JsonElement>();
        var id = quote.GetProperty("quoteId").GetString();
        Assert.Equal($"/quotes/{id}",
            response.Headers.Location?.OriginalString);
        Assert.Equal(9_023.95m, Total(quote));
    }
    #endregion

    // A quote the tariff declines is stored as data, not raised as an error: 201 with a status.
    [Fact]
    public async Task Three_claims_are_declined_with_a_status_and_a_reason_and_no_premium()
    {
        var response = await _client.PostAsJsonAsync("/quotes", Requests.Quote(claims: 3));

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var quote = await response.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("Declined", quote.GetProperty("status").GetString());
        Assert.Equal("3+ claims in 5 years", quote.GetProperty("declineReason").GetString());
        Assert.Equal(JsonValueKind.Null, quote.GetProperty("premium").ValueKind);
    }

    [Fact]
    public async Task Get_returns_the_stored_quote()
    {
        var created = await Create();

        var fetched = await _client.GetFromJsonAsync<JsonElement>($"/quotes/{created.GetProperty("quoteId")}");

        Assert.Equal("Quoted", fetched.GetProperty("status").GetString());
        Assert.Equal(Total(created), Total(fetched));
    }

    [Fact]
    public async Task Get_unknown_quote_returns_404_problem_details()
    {
        var response = await _client.GetAsync($"/quotes/{Guid.NewGuid()}");

        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        Assert.Equal("application/problem+json", response.Content.Headers.ContentType?.MediaType);
    }

    [Fact]
    public async Task Accept_issues_a_policy_once_then_conflicts()
    {
        var id = (await Create()).GetProperty("quoteId").GetString();

        var first = await _client.PostAsync($"/quotes/{id}/accept", null);
        var second = await _client.PostAsync($"/quotes/{id}/accept", null);

        Assert.Equal(HttpStatusCode.OK, first.StatusCode);
        var policy = await first.Content.ReadFromJsonAsync<JsonElement>();
        Assert.StartsWith("MQ-", policy.GetProperty("policyNumber").GetString());
        Assert.Equal("2027-09-14", policy.GetProperty("expiry").GetString());
        Assert.Equal(HttpStatusCode.Conflict, second.StatusCode);
        var problem = await second.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("The quote is AlreadyAccepted.", problem.GetProperty("detail").GetString());
    }

    [Theory]
    [InlineData("vehicle.sumInsured", 10, "line", "2026-09-15")]
    [InlineData("notifyVia", 800_000, "fax", "2026-09-15")]
    [InlineData("StartDate", 800_000, "line", "2026-08-01")]
    public async Task Invalid_request_returns_400_with_the_failing_field(
        string field, int sumInsured, string notifyVia, string startDate)
    {
        var response = await _client.PostAsJsonAsync("/quotes",
            Requests.Quote(sumInsured: sumInsured, notifyVia: notifyVia, startDate: startDate));

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        var problem = await response.Content.ReadFromJsonAsync<JsonElement>();
        var fields = problem.GetProperty("errors").EnumerateObject().Select(e => e.Name);
        Assert.Contains(field, fields, StringComparer.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task Controller_endpoint_calls_partner_through_typed_client()
    {
        var rate = await _client.GetFromJsonAsync<JsonElement>("/partners/p07/rates?coverage=Class1");

        Assert.Equal("p07", rate.GetProperty("partnerId").GetString());
        Assert.Equal(0.021m, rate.GetProperty("rate").GetDecimal());
    }

    private async Task<JsonElement> Create()
    {
        var response = await _client.PostAsJsonAsync("/quotes", Requests.Quote());
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    private static decimal Total(JsonElement quote) =>
        quote.GetProperty("premium").GetProperty("total").GetProperty("amount").GetDecimal();
}

/// <summary>Its own factory: moving the fake clock forward would break the other classes' start dates.</summary>
public sealed class QuoteExpiryTests(QuoteApiFactory factory) : IClassFixture<QuoteApiFactory>
{
    [Fact]
    public async Task Accept_after_the_validity_window_returns_409_expired()
    {
        var client = factory.CreateClient();
        var created = await client.PostAsJsonAsync("/quotes", Requests.Quote());
        var id = (await created.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("quoteId").GetString();

        factory.Clock.Advance(TimeSpan.FromDays(31));   // Quotes:ValidityDays is 30
        var response = await client.PostAsync($"/quotes/{id}/accept", null);

        Assert.Equal(HttpStatusCode.Conflict, response.StatusCode);
        var problem = await response.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("The quote is Expired.", problem.GetProperty("detail").GetString());
    }
}

public sealed class ValidationScopeTests
{
    #region validation-scope-test
    [Fact]
    public async Task AddValidation_checks_VB_parameters_but_not_VB_declared_types()
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.WebHost.UseTestServer();
        builder.Services.AddValidation();        // called from C#, as Program.cs does
        await using var app = builder.Build();
        app.MapRatingChecks();                   // endpoints and types written in VB
        await app.StartAsync();
        var client = app.GetTestClient();

        var parameter = await client.GetAsync("/checks/years/9");
        var property = await client.PostAsJsonAsync("/checks/vehicle", new { years = 9 });

        Assert.Equal(HttpStatusCode.BadRequest, parameter.StatusCode);  // <Range> enforced
        Assert.Equal(HttpStatusCode.OK, property.StatusCode);           // <Range> ignored
    }
    #endregion
}
