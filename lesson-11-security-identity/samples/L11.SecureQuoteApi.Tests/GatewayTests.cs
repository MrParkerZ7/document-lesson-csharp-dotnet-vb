using System.Net.Http.Headers;

namespace L11.SecureQuoteApi.Tests;

public sealed class GatewayTests(GatewayFactory factory) : IClassFixture<GatewayFactory>
{
    #region gateway-test
    [Theory]
    [InlineData(null, "/api/quotes/Q-1001", 401)]
    [InlineData("expired", "/api/quotes/Q-1001", 401)]
    [InlineData("customer", "/api/underwriting/referrals", 403)]
    public async Task Gateway_rejects_before_it_proxies(string? caller, string path, int expected)
    {
        using var client = factory.CreateClient();
        var token = caller switch
        {
            "expired" => TestTokens.Create("cust-a", "Quotes.Read",
                expiresIn: TimeSpan.FromMinutes(-2)),
            "customer" => TestTokens.Create("cust-a", "Quotes.Read"),
            _ => null,
        };
        if (token is not null)
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        }

        // no destination is reachable in the test: a 401 or 403 proves the request stopped here
        using var response = await client.GetAsync(path);

        Assert.Equal(expected, (int)response.StatusCode);
    }
    #endregion
}
