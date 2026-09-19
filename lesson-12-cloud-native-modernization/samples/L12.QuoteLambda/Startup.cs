using System.Text.Json;
using Amazon.Lambda.Annotations;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace L12.QuoteLambda;

#region startup
[LambdaStartup]
public sealed class Startup
{
    // Runs once per execution environment (Lambda's init phase), not once per request.
    public HostApplicationBuilder ConfigureHostBuilder()
    {
        var builder = new HostApplicationBuilder();
        builder.Services.AddSingleton<IQuoteStore, InMemoryQuoteStore>();
        SnapStart.RegisterHooks();
        return builder;
    }
}
#endregion

/// <summary>Lambda SnapStart runtime hooks (Amazon.Lambda.Core 2.5.0 or later).</summary>
public static class SnapStart
{
    /// <summary>Different for every execution environment — because it is renewed after restore.</summary>
    public static string EnvironmentId { get; private set; } = NewId();

    static string NewId() => Guid.NewGuid().ToString("N");

    #region snapstart
    // SnapStart snapshots ONE initialised environment and resumes many copies of it.
    public static void RegisterHooks()
    {
        // Before the snapshot: drive a request through the raw handler (JSON in, rating,
        // JSON out) so restored copies skip its JIT. Call it more than once (tiered
        // compilation) and cause no side effects: this handler saves nothing.
        SnapshotRestore.RegisterBeforeSnapshot(() =>
        {
            var body = JsonSerializer.Serialize(
                new QuoteRequest("class1", 800_000m, 30, 0, false), JsonSerializerOptions.Web);
            var request = new APIGatewayHttpApiV2ProxyRequest { Body = body };
            var handler = new RawQuoteHandler();
            for (var i = 0; i < 10; i++)
                handler.FunctionHandler(request, null!);
            return ValueTask.CompletedTask;
        });

        // After restore: every copy starts with the same memory, so renew anything unique.
        SnapshotRestore.RegisterAfterRestore(() =>
        {
            EnvironmentId = NewId();
            return ValueTask.CompletedTask;
        });
    }
    #endregion
}
