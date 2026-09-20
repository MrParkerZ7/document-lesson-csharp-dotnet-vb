// API tour: drives the real L08.QuoteApi pipeline in memory and prints what a client would see.
// Rates are illustrative, not a real tariff. The clock is fixed so the output is repeatable.
using System.Globalization;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using L08.QuoteApi.Notifications;
using L08.QuoteApi.Partners;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Time.Testing;

// WebApplicationFactory reads MvcTestingAppManifest.json (the API's content root) from the
// current directory — a test runner starts in the output folder, a console app does not.
Directory.SetCurrentDirectory(AppContext.BaseDirectory);

var clock = new FakeTimeProvider(new DateTimeOffset(2026, 9, 1, 9, 0, 0, TimeSpan.Zero));
var partner = new TourPartner();

await using var api = new WebApplicationFactory<PartnerRateClient>().WithWebHostBuilder(web =>
{
    web.UseEnvironment("Tour");
    web.UseSetting("Partners:Resilience:Retry:Delay", "00:00:00.010");
    web.UseSetting("RateLimits:QuoteWritesPerMinute", "4");
    web.ConfigureLogging(logging => logging.ClearProviders());
    web.ConfigureTestServices(services =>
    {
        services.AddSingleton<TimeProvider>(clock);
        services.AddHttpClient<IPartnerRateClient, PartnerRateClient>()
            .ConfigurePrimaryHttpMessageHandler(() => partner);
    });
});
var http = api.CreateClient();

var adult = Body(dateOfBirth: "1990-05-01", licenceYears: 10, claims: 0, sumInsured: 800_000, notifyVia: "line");
var young = Body(dateOfBirth: "2004-01-01", licenceYears: 2, claims: 1, sumInsured: 800_000, notifyVia: "sms");
var risky = Body(dateOfBirth: "1990-05-01", licenceYears: 10, claims: 3, sumInsured: 800_000, notifyVia: "email");
var broken = Body(dateOfBirth: "1990-05-01", licenceYears: 10, claims: 0, sumInsured: 10, notifyVia: "fax");

var created = await Send("POST", "/quotes", adult);
var quote = await created.Content.ReadFromJsonAsync<JsonElement>();
Print("POST", "/quotes", created, Premium(quote));
var youngResponse = await Send("POST", "/quotes", young);
Print("POST", "/quotes  (driver 22, 1 claim)", youngResponse,
    Premium(await youngResponse.Content.ReadFromJsonAsync<JsonElement>()));

// the tariff declines 3+ claims in five years: a status and a reason, not an error
var risk = await Send("POST", "/quotes", risky);
var riskQuote = await risk.Content.ReadFromJsonAsync<JsonElement>();
Print("POST", "/quotes  (3 claims in 5 years)", risk,
    $"{riskQuote.GetProperty("status").GetString()}, {riskQuote.GetProperty("declineReason").GetString()}");

var invalid = await Send("POST", "/quotes", broken);
Print("POST", "/quotes  (invalid body)", invalid, "errors: " + string.Join(", ",
    (await invalid.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("errors").EnumerateObject()
        .Select(e => e.Name)));

var limited = await Send("POST", "/quotes", adult);
Print("POST", "/quotes  (5th write this minute)", limited, $"{limited.Content.Headers.ContentType?.MediaType}");

var id = quote.GetProperty("quoteId").GetString();
var fetched = await Send("GET", "/quotes/{id}", path: $"/quotes/{id}");
Print("GET", "/quotes/{id}", fetched, (await fetched.Content.ReadFromJsonAsync<JsonElement>())
    .GetProperty("status").GetString()!);
var missing = await Send("GET", $"/quotes/{Guid.Empty}");
Print("GET", "/quotes/{unknown id}", missing, $"{missing.Content.Headers.ContentType?.MediaType}");

var accepted = await Send("POST", "/quotes/{id}/accept", path: $"/quotes/{id}/accept");
var policy = await accepted.Content.ReadFromJsonAsync<JsonElement>();
Print("POST", "/quotes/{id}/accept", accepted, $"policy {policy.GetProperty("policyNumber")}, " +
    $"{policy.GetProperty("inception")} to {policy.GetProperty("expiry")}");
var again = await Send("POST", "/quotes/{id}/accept", path: $"/quotes/{id}/accept");
Print("POST", "/quotes/{id}/accept  (again)", again,
    (await again.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("detail").GetString()!);

var tariff = await Send("GET", "/tariff/Class3Plus");
Print("GET", "/tariff/Class3Plus  (VB endpoint)", tariff, await tariff.Content.ReadAsStringAsync());

partner.FailuresBeforeSuccess = 2;
var retried = await SendAdvancingClock("/partners/p07/rates?coverage=Class1");
Print("GET", "/partners/p07/rates  (fails twice)", retried, $"partner attempts {partner.TakeAttempts()}");
partner.FailuresBeforeSuccess = int.MaxValue;
var down = await SendAdvancingClock("/partners/p09/rates?coverage=Class1");
Print("GET", "/partners/p09/rates  (always fails)", down,
    $"partner attempts {partner.TakeAttempts()}, Retry-After {down.Headers.RetryAfter}");

var health = await Send("GET", "/health");
Print("GET", "/health", health, await health.Content.ReadAsStringAsync());

var openApi = await Send("GET", "/openapi/v1.json");
var document = await openApi.Content.ReadFromJsonAsync<JsonElement>();
Print("GET", "/openapi/v1.json", openApi, $"openapi {document.GetProperty("openapi")}, " +
    $"{document.GetProperty("paths").EnumerateObject().Count()} paths");
string[] verbs = ["get", "post", "put", "patch", "delete"];
foreach (var path in document.GetProperty("paths").EnumerateObject())
{
    foreach (var operation in path.Value.EnumerateObject().Where(o => verbs.Contains(o.Name)))
    {
        var codes = operation.Value.GetProperty("responses").EnumerateObject().Select(r => r.Name);
        Console.WriteLine($"     {operation.Name.ToUpperInvariant(),-5}{path.Name,-33}documents {string.Join(" ", codes)}");
    }
}

var log = api.Services.GetRequiredService<NotificationLog>();
for (var i = 0; i < 100 && log.Sent.Count == 0; i++)
    await Task.Delay(20);
Console.WriteLine($"background notification sent: {string.Join("; ", log.Sent)}");

// The resilience pipeline's retry delays run on the injected (fake) clock: move time forward.
async Task<HttpResponseMessage> SendAdvancingClock(string url)
{
    var call = http.GetAsync(url);
    while (!call.IsCompleted)
    {
        clock.Advance(TimeSpan.FromMilliseconds(100));
        await Task.WhenAny(call, Task.Delay(5));
    }
    return await call;
}

Task<HttpResponseMessage> Send(string method, string route, object? body = null, string? path = null) =>
    http.SendAsync(new HttpRequestMessage(new HttpMethod(method), path ?? route)
    {
        Content = body is null ? null : JsonContent.Create(body),
    });

static void Print(string method, string route, HttpResponseMessage response, string detail) =>
    Console.WriteLine($"{method,-5}{route,-38}{(int)response.StatusCode}  {detail}");

static string Premium(JsonElement quote)
{
    var p = quote.GetProperty("premium");
    string Amount(string name) =>
        p.GetProperty(name).GetProperty("amount").GetDecimal().ToString("N2", CultureInfo.InvariantCulture);
    return $"net {Amount("net")}  total {Amount("total")} {p.GetProperty("total").GetProperty("currency")}";
}

static object Body(string dateOfBirth, int licenceYears, int claims, decimal sumInsured, string notifyVia) => new
{
    vehicle = new { make = "Toyota", model = "Corolla Cross", year = 2024, engineCc = 1800, use = "Private", sumInsured },
    driver = new { dateOfBirth, licenceYears, claimsLast5Years = claims },
    coverage = "Class1",
    startDate = "2026-09-15",
    notifyVia,
};

sealed class TourPartner : HttpMessageHandler
{
    private int _attempts;

    public int FailuresBeforeSuccess { get; set; }

    public int TakeAttempts() => Interlocked.Exchange(ref _attempts, 0);

    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var attempt = Interlocked.Increment(ref _attempts);
        return Task.FromResult(attempt <= FailuresBeforeSuccess
            ? new HttpResponseMessage(HttpStatusCode.ServiceUnavailable)
            : new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = JsonContent.Create(new { partnerId = "p07", coverage = "Class1", rate = 0.021m }),
            });
    }
}
