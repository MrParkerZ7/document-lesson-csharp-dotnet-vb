using System.Net;
using System.Net.Http.Headers;
using L11.SecureQuoteApi.Security;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace L11.SecureQuoteApi.Tests;

public sealed class SecurityBehaviourTests
{
    #region mapping-trap
    [Fact]
    public async Task Default_claim_mapping_renames_scp_so_the_owner_gets_403()
    {
        // MapInboundClaims = true is the JwtBearer default; the app turns it off
        await using var factory = new SecureApiFactory { MapInboundClaims = true };
        using var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer",
            TestTokens.Create("cust-a", "Quotes.Read Quotes.Write"));

        using var response = await client.GetAsync("/quotes/Q-1001");

        // the token is valid (not 401), but "scp" arrived under a long URI claim type
        Assert.Equal(HttpStatusCode.Forbidden, response.StatusCode);
    }
    #endregion

    [Fact]
    public async Task One_subject_is_throttled_after_its_permit_limit()
    {
        await using var factory = new SecureApiFactory()
            .WithWebHostBuilder(b => b.UseSetting("RateLimit:PerMinute", "2"));
        using var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer",
            TestTokens.Create("cust-a", "Quotes.Read"));

        var statuses = new List<HttpStatusCode>();
        for (var i = 0; i < 3; i++)
        {
            using var response = await client.GetAsync("/quotes/Q-1001");
            statuses.Add(response.StatusCode);
        }

        Assert.Equal([HttpStatusCode.OK, HttpStatusCode.OK, HttpStatusCode.TooManyRequests], statuses);
    }

    [Fact]
    public async Task Health_is_anonymous_even_with_an_expired_token()
    {
        await using var factory = new SecureApiFactory();
        using var client = factory.CreateClient();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer",
            TestTokens.Create("cust-a", "Quotes.Read", expiresIn: TimeSpan.FromMinutes(-10)));

        using var response = await client.GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    #region entra-test
    [Fact]
    public void Entra_registration_derives_the_authority_from_the_AzureAd_section()
    {
        var config = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
        {
            ["AzureAd:Instance"] = "https://login.microsoftonline.com/",
            ["AzureAd:TenantId"] = "00000000-0000-0000-0000-00000000a011",
            ["AzureAd:ClientId"] = "00000000-0000-0000-0000-00000000c011",
        }).Build();
        var services = new ServiceCollection().AddLogging();
        services.AddSingleton<IConfiguration>(config);

        services.AddQuoteApiEntra(config);
        using var provider = services.BuildServiceProvider();
        var jwt = provider.GetRequiredService<IOptionsMonitor<JwtBearerOptions>>()
            .Get(JwtBearerDefaults.AuthenticationScheme);

        Assert.Equal("https://login.microsoftonline.com/00000000-0000-0000-0000-00000000a011/v2.0",
            jwt.Authority);
        Assert.False(jwt.MapInboundClaims);
        Assert.Equal(TimeSpan.FromSeconds(30), jwt.TokenValidationParameters.ClockSkew);
        Assert.Equal("name", jwt.TokenValidationParameters.NameClaimType);
    }
    #endregion
}
