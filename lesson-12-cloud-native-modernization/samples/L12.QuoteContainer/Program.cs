using System.Text.Json.Serialization;
using Amazon.Lambda.AspNetCoreServer.Hosting;
using L12.QuoteContainer;
using L12.RatingVb;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using OpenTelemetry;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);

#region hosting
// Kestrel in the container. The Lambda adapter replaces Kestrel only when the
// process runs inside Lambda: one codebase, two hosting targets.
builder.Services.AddAWSLambdaHosting(LambdaEventSource.HttpApi);

// ECS sends SIGTERM, waits stopTimeout (30 s by default), then SIGKILL.
// Finish in-flight requests well inside that window.
builder.Services.Configure<HostOptions>(
    o => o.ShutdownTimeout = TimeSpan.FromSeconds(20));
#endregion

#region telemetry
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("motorquote-api"))
    .WithTracing(t => t
        .AddSource(QuoteTelemetry.Source.Name)
        .AddAspNetCoreInstrumentation())
    .WithMetrics(m => m
        .AddMeter(QuoteTelemetry.Meter.Name)
        .AddAspNetCoreInstrumentation())
    .WithLogging();

// Export over OTLP only when a collector is configured, e.g. an ADOT or
// CloudWatch agent sidecar on ECS listening on http://localhost:4317.
if (builder.Configuration["OTEL_EXPORTER_OTLP_ENDPOINT"] is not null)
    builder.Services.AddOpenTelemetry().UseOtlpExporter();
#endregion

builder.Services.AddHealthChecks()
    .AddCheck<RatingSelfCheck>("rating", tags: ["ready"]);
builder.Services.ConfigureHttpJsonOptions(o =>
    o.SerializerOptions.Converters.Add(new JsonStringEnumConverter()));

var app = builder.Build();

#region health
// liveness = the process answers; readiness = its dependencies work
app.MapHealthChecks("/health/live", new HealthCheckOptions
    { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new HealthCheckOptions
    { Predicate = check => check.Tags.Contains("ready") });

app.Lifetime.ApplicationStopping.Register(() =>
    app.Logger.LogInformation("Stop signal received: draining requests"));
#endregion

#region endpoint
app.MapPost("/quotes", (QuoteRequest req, ILogger<QuoteRequest> log) =>
{
    using var span = QuoteTelemetry.Source.StartActivity("rate-quote");
    span?.SetTag("motorquote.coverage", req.Coverage.ToString());

    var p = Rating.Quote(req.Coverage, req.SumInsured, req.DriverAge,
                         req.ClaimsLast5Years, req.Commercial);

    QuoteTelemetry.QuotesIssued.Add(1,
        new KeyValuePair<string, object?>("coverage", req.Coverage.ToString()));
    // a message TEMPLATE, not an interpolated string: Coverage and Total
    // become searchable fields in CloudWatch Logs
    log.LogInformation("Quoted {Coverage}: total {Total} THB", req.Coverage, p.Total);
    return TypedResults.Ok(p);
});
#endregion

app.Run();
