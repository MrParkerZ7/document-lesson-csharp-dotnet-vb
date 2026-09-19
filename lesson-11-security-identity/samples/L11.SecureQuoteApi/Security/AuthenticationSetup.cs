using L11.SecureQuoteApi.Partners;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

namespace L11.SecureQuoteApi.Security;

public static class AuthenticationSetup
{
    #region jwt-bearer
    // Any OpenID Connect authority: Entra ID, External ID, Auth0, Cognito, Keycloak
    public static IServiceCollection AddQuoteApiJwt(this IServiceCollection services,
        IConfiguration config)
    {
        var identity = config.GetSection("Identity");
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(o =>
            {
                o.Authority = identity["Authority"];   // discovery document + JWKS signing keys
                o.Audience = identity["Audience"];     // the aud claim must name THIS API
                o.MapInboundClaims = false;            // keep sub, scp, roles as issued
                o.TokenValidationParameters.NameClaimType = "name";
                o.TokenValidationParameters.RoleClaimType = "roles";
                o.TokenValidationParameters.ClockSkew = TimeSpan.FromSeconds(30);   // default 5 min
            });
        return services;
    }
    #endregion

    #region entra
    // Entra ID through Microsoft.Identity.Web: AzureAd:Instance + TenantId + ClientId
    public static IServiceCollection AddQuoteApiEntra(this IServiceCollection services,
        IConfiguration config)
    {
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddMicrosoftIdentityWebApi(config.GetSection("AzureAd"))
            .EnableTokenAcquisitionToCallDownstreamApi()  // OBO + client credentials
            .AddDownstreamApi("PartnerRates", config.GetSection("DownstreamApis:PartnerRates"))
            .AddInMemoryTokenCaches();              // several instances: AddDistributedTokenCaches

        // the library keeps its own defaults: repeat the claim and skew settings of 4.2
        services.Configure<JwtBearerOptions>(JwtBearerDefaults.AuthenticationScheme, o =>
        {
            o.MapInboundClaims = false;                             // same claim names as above
            o.TokenValidationParameters.NameClaimType = "name";
            o.TokenValidationParameters.RoleClaimType = "roles";
            o.TokenValidationParameters.ClockSkew = TimeSpan.FromSeconds(30);   // still 5 min
        });
        services.AddScoped<PartnerRatesClient>();
        return services;
    }
    #endregion
}
