using L11.Gateway;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;

namespace L11.SecureQuoteApi.Tests;

#region factory
public class TestKeyFactory<TEntryPoint> : WebApplicationFactory<TEntryPoint>
    where TEntryPoint : class
{
    public bool MapInboundClaims { get; init; }   // false = what both apps configure

    protected override void ConfigureWebHost(IWebHostBuilder builder) =>
        builder.ConfigureTestServices(services =>
            services.Configure<JwtBearerOptions>(JwtBearerDefaults.AuthenticationScheme, o =>
            {
                // No discovery call: trust the local test key instead of the authority's JWKS.
                // Issuer, audience, lifetime and signature are still validated for real.
                o.Authority = null;
                o.Configuration = new OpenIdConnectConfiguration { Issuer = TestTokens.Issuer };
                o.Configuration.SigningKeys.Add(TestTokens.Key);
                o.MapInboundClaims = MapInboundClaims;
            }));
}
#endregion

public sealed class SecureApiFactory : TestKeyFactory<SecureQuoteApiMarker>
{
}

public sealed class GatewayFactory : TestKeyFactory<GatewayMarker>
{
}
