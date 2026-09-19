using System.Net;
using System.Net.Http.Headers;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;

namespace L11.SecureQuoteApi.Tests;

public sealed class MiddlewareOrderTests
{
    #region order-trap
    [Theory]
    [InlineData(true, HttpStatusCode.OK)]
    [InlineData(false, HttpStatusCode.Unauthorized)]   // the SAME valid token
    public async Task Authentication_must_run_before_authorization(
        bool authenticateFirst, HttpStatusCode expected)
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.WebHost.UseTestServer();
        builder.Services.AddAuthorization();
        builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(o =>
            {
                o.Audience = TestTokens.Audience;
                o.Configuration = new OpenIdConnectConfiguration { Issuer = TestTokens.Issuer };
                o.Configuration.SigningKeys.Add(TestTokens.Key);
            });
        await using var app = builder.Build();

        if (authenticateFirst) { app.UseAuthentication(); app.UseAuthorization(); }
        else { app.UseAuthorization(); app.UseAuthentication(); }   // compiles, runs, rejects
        app.MapGet("/quotes/{id}", (string id) => id).RequireAuthorization();
        await app.StartAsync();

        using var client = app.GetTestClient();
        client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", TestTokens.Create("cust-a", "Quotes.Read"));
        using var response = await client.GetAsync("/quotes/Q-1001");

        Assert.Equal(expected, response.StatusCode);
    }
    #endregion

    #region fallback-trap
    [Theory]
    [InlineData(false, HttpStatusCode.OK)]             // "forgot the attribute": public
    [InlineData(true, HttpStatusCode.Unauthorized)]    // fallback policy: needs a user
    public async Task Endpoint_without_metadata_is_public_unless_a_fallback_policy_exists(
        bool fallbackPolicy, HttpStatusCode expected)
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.WebHost.UseTestServer();
        builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer();
        var authorization = builder.Services.AddAuthorizationBuilder();
        if (fallbackPolicy)
        {
            authorization.SetFallbackPolicy(new AuthorizationPolicyBuilder()
                .RequireAuthenticatedUser().Build());
        }
        await using var app = builder.Build();
        app.UseAuthentication();
        app.UseAuthorization();
        app.MapGet("/forgotten", () => "secret");   // no RequireAuthorization, no AllowAnonymous
        await app.StartAsync();

        using var response = await app.GetTestClient().GetAsync("/forgotten");   // no token

        Assert.Equal(expected, response.StatusCode);
    }
    #endregion
}
