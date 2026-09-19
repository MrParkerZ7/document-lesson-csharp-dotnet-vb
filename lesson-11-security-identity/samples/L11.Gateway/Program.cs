using Microsoft.AspNetCore.Authentication.JwtBearer;

var builder = WebApplication.CreateBuilder(args);

#region gateway
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        builder.Configuration.Bind("Identity", o);   // Authority, Audience
        o.MapInboundClaims = false;
        o.TokenValidationParameters.RoleClaimType = "roles";
        // as the API: with the 5-minute default an expired token was proxied (a 502 in tests)
        o.TokenValidationParameters.ClockSkew = TimeSpan.FromSeconds(30);
    });

#region gateway-policies
// coarse checks only: "a valid token" and "an underwriter" — the API still decides per quote
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("customer-api", p => p.RequireAuthenticatedUser())
    .AddPolicy("underwriting", p => p.RequireRole("Underwriter"));

builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
app.MapReverseProxy();   // every route names its AuthorizationPolicy in appsettings.json
app.Run();
#endregion
#endregion
