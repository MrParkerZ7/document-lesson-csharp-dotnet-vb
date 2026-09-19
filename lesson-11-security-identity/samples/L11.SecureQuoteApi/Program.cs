using System.Security.Claims;
using System.Threading.RateLimiting;
using L11.SecureQuoteApi.Quotes;
using L11.SecureQuoteApi.Security;
using Microsoft.AspNetCore.Authorization;
using static L11.SecureQuoteApi.Security.QuoteClaims;

var builder = WebApplication.CreateBuilder(args);
var config = builder.Configuration;

#region choose-authority
// One API, two ways to trust an identity provider (section 4)
if (config["Identity:Provider"] == "Entra")
{
    builder.Services.AddQuoteApiEntra(config);   // Microsoft.Identity.Web
}
else
{
    builder.Services.AddQuoteApiJwt(config);     // plain JwtBearer, any OIDC authority
}
#endregion

#region policies
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("quotes.read", p => p.RequireAssertion(c =>
        c.User.HasScope(ReadScope)
        || c.User.IsInRole(ReadAllPermission)))
    .AddPolicy("quotes.write", p => p.RequireAssertion(c =>
        c.User.HasScope(WriteScope)))
    .AddPolicy("underwriting", p => p
        .RequireRole(UnderwriterRole)
        .RequireAssertion(c => c.User.HasScope(ReadScope)))
    // endpoints without RequireAuthorization are NOT public
    .SetFallbackPolicy(new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build());

builder.Services.AddSingleton<IAuthorizationHandler,
    QuoteAuthorizationHandler>();
#endregion

#region hardening
builder.Services.AddCors(o => o.AddDefaultPolicy(p => p
    .WithOrigins(config.GetSection("Cors:Origins").Get<string[]>() ?? [])
    .WithMethods("GET", "POST")
    .WithHeaders("Authorization", "Content-Type")));

builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    // one bucket per token subject; callers without one share their IP's bucket
    o.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(http =>
        RateLimitPartition.GetFixedWindowLimiter(
            http.User.SubjectId() ?? http.Connection.RemoteIpAddress?.ToString() ?? "anonymous",
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = config.GetValue("RateLimit:PerMinute", 60),
                Window = TimeSpan.FromMinutes(1),
            }));
});
#endregion

builder.Services.AddSingleton<QuoteStore>();

var app = builder.Build();

#region pipeline
// No UseHttpsRedirection or UseHsts: an API listens on HTTPS only. A redirect
// arrives after the client has already sent its bearer token over plain HTTP.
app.UseCors();                  // before auth: a CORS preflight carries no token
app.UseAuthentication();        // who are you?  -> HttpContext.User
app.UseRateLimiter();           // needs the subject, so after authentication
app.UseAuthorization();         // may you?      -> 401, 403 or the endpoint
#endregion

#region read-endpoint
app.MapGet("/health", () => "ok").AllowAnonymous();

var quotes = app.MapGroup("/quotes");

quotes.MapGet("/{id}", async (string id, ClaimsPrincipal user,
    QuoteStore store, IAuthorizationService authz) =>
{
    if (store.Find(id) is not { } quote)
    {
        return Results.NotFound();
    }
    // the policy said "may read quotes"; this asks "may read THIS quote"
    var result = await authz.AuthorizeAsync(user, quote, QuoteOperations.Read);
    return result.Succeeded ? Results.Ok(quote) : Results.Forbid();
}).RequireAuthorization("quotes.read");
#endregion

quotes.MapPost("", (QuoteRequest request, ClaimsPrincipal user, QuoteStore store) =>
{
    // the owner comes from the token, never from the request body
    if (user.SubjectId() is not { } owner)
    {
        return Results.Forbid();
    }
    var quote = store.Add(owner, request.SumInsured);
    return Results.Created($"/quotes/{quote.QuoteId}", quote);
}).RequireAuthorization("quotes.write");

quotes.MapPost("/{id}/accept", async (string id, ClaimsPrincipal user,
    QuoteStore store, IAuthorizationService authz) =>
{
    if (store.Find(id) is not { } quote)
    {
        return Results.NotFound();
    }
    var result = await authz.AuthorizeAsync(user, quote, QuoteOperations.Accept);
    return result.Succeeded ? Results.Ok(store.Accept(quote)) : Results.Forbid();
}).RequireAuthorization("quotes.write");

app.MapGet("/underwriting/referrals", (QuoteStore store) => store.Referrals())
    .RequireAuthorization("underwriting");

app.Run();
