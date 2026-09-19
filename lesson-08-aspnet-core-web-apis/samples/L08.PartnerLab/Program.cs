// Partner lab: IHttpClientFactory + the standard resilience handler against a fake rating partner.
// No network: the primary handler is an in-process stub that fails a set number of times.
using System.Net;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Http.Resilience;
using Microsoft.Extensions.Options;

Console.WriteLine("scenario                                  attempts  outcome");

await Run("no resilience handler, partner fails once", failures: 1, resilient: false);
await Run("standard handler, partner fails twice", failures: 2, resilient: true);
await Run("standard handler, partner always fails", failures: int.MaxValue, resilient: true);
await Run("standard handler, POST, unsafe excluded", failures: int.MaxValue, resilient: true,
    method: HttpMethod.Post);
await RunCircuit();
Invalid();

#region run-scenario
static async Task Run(string name, int failures, bool resilient, HttpMethod? method = null)
{
    var partner = new FlakyPartner(failures);
    var builder = new ServiceCollection()
        .AddHttpClient("partner", http => http.BaseAddress = new("https://partner.example/"))
        .ConfigurePrimaryHttpMessageHandler(() => partner);

    if (resilient)
    {
        #region unsafe-methods
        builder.AddStandardResilienceHandler(options =>
        {
            // default 2 s, exponential: shortened for the lab
            options.Retry.Delay = TimeSpan.FromMilliseconds(10);
            options.Retry.UseJitter = false;
            // POST, PUT, PATCH, DELETE get one attempt only
            options.Retry.DisableForUnsafeHttpMethods();
        });
        #endregion
    }

    using var provider = builder.Services.BuildServiceProvider();
    var client = provider.GetRequiredService<IHttpClientFactory>().CreateClient("partner");
    using var response = await client.SendAsync(new(method ?? HttpMethod.Get, "rates/p07"));
    Console.WriteLine($"{name,-42}{partner.Attempts,8}  {(int)response.StatusCode}");
}
#endregion

#region circuit-breaker
static async Task RunCircuit()
{
    var partner = new FlakyPartner(int.MaxValue);
    var builder = new ServiceCollection()
        .AddHttpClient("partner", http => http.BaseAddress = new("https://partner.example/"))
        .ConfigurePrimaryHttpMessageHandler(() => partner);
    #region early-breaker
    builder.AddStandardResilienceHandler(options =>
    {
        options.Retry.Delay = TimeSpan.FromMilliseconds(10);
        options.Retry.UseJitter = false;
        // defaults: 10% failures, at least 100 calls in 30 s
        options.CircuitBreaker.MinimumThroughput = 2;
        options.CircuitBreaker.FailureRatio = 0.5;
    });
    #endregion

    using var provider = builder.Services.BuildServiceProvider();
    var client = provider.GetRequiredService<IHttpClientFactory>().CreateClient("partner");
    for (var call = 1; call <= 3; call++)
    {
        var before = partner.Attempts;
        string outcome;
        try
        {
            using var response = await client.GetAsync("rates/p07");
            outcome = ((int)response.StatusCode).ToString();
        }
        catch (Exception ex)
        {
            outcome = ex.GetType().Name;
        }
        var name = $"breaker opens early, call {call}";
        Console.WriteLine($"{name,-42}{partner.Attempts - before,8}  {outcome}");
    }
}
#endregion

#region invalid-options
static void Invalid()
{
    var builder = new ServiceCollection()
        .AddHttpClient("partner")
        .AddStandardResilienceHandler(options =>
        {
            options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(20);
            options.CircuitBreaker.SamplingDuration = TimeSpan.FromSeconds(30);
        });

    using var provider = builder.Services.BuildServiceProvider();
    try
    {
        provider.GetRequiredService<IHttpClientFactory>().CreateClient("partner");
        Console.WriteLine("options accepted");
    }
    catch (OptionsValidationException ex)
    {
        Console.WriteLine("invalid options, rejected when the client is created:");
        var line = "";
        foreach (var word in ex.Failures.First().Split(' '))
        {
            if (line.Length + word.Length > 80)
            {
                Console.WriteLine($"  {line.TrimEnd()}");
                line = "";
            }
            line += word + " ";
        }
        Console.WriteLine($"  {line.TrimEnd()}");
    }
}
#endregion

sealed class FlakyPartner(int failuresBeforeSuccess) : HttpMessageHandler
{
    private int _attempts;

    public int Attempts => _attempts;

    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var attempt = Interlocked.Increment(ref _attempts);
        var status = attempt <= failuresBeforeSuccess ? HttpStatusCode.ServiceUnavailable : HttpStatusCode.OK;
        return Task.FromResult(new HttpResponseMessage(status));
    }
}
