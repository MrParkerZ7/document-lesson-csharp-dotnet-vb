// Hosting lab: configuration precedence, options validation, DI lifetimes, captive dependencies
// and keyed services — the container behaviour behind every ASP.NET Core app, with no web server.
using System.ComponentModel.DataAnnotations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;

Console.WriteLine("1 configuration: the last source that sets a key wins");
#region config-precedence
Environment.SetEnvironmentVariable(
    "L08LAB_Quotes__ValidityDays", "14");   // __ means :

var config = new ConfigurationBuilder()
    // stand-ins for appsettings.json and .Production.json
    .AddInMemoryCollection([new("Quotes:ValidityDays", "30")])
    .AddInMemoryCollection([new("Quotes:ValidityDays", "21")])
    .AddEnvironmentVariables(prefix: "L08LAB_")
    .AddCommandLine(["--Quotes:ValidityDays=7"])
    .Build();

string[] layers =
[
    "appsettings.json", "appsettings.Production.json",
    "environment", "command line",
];
foreach (var (source, layer) in config.Providers.Zip(layers))
{
    source.TryGet("Quotes:ValidityDays", out var value);
    Console.WriteLine($"   {layer,-28} {value}");
}
var wins = config["Quotes:ValidityDays"];
Console.WriteLine($"   => Quotes:ValidityDays = {wins}");
#endregion

Console.WriteLine("2 options validation: fail at start-up, not on first use");
#region options-validation
var builder = Host.CreateEmptyApplicationBuilder(new HostApplicationBuilderSettings());
builder.Configuration.AddInMemoryCollection([new("Quotes:ValidityDays", "0")]);
builder.Services.AddOptions<QuoteOptions>()
    .BindConfiguration("Quotes")
    .ValidateDataAnnotations()
    .ValidateOnStart();

using (var host = builder.Build())
{
    try
    {
        await host.StartAsync();
        Console.WriteLine("   started (no validation ran)");
    }
    catch (OptionsValidationException ex)
    {
        Console.WriteLine($"   {ex.GetType().Name}");
        Say("", ex.Failures.First());
    }
}
#endregion

Console.WriteLine("3 lifetimes: two requests, each resolving every service twice");
#region lifetimes
var services = new ServiceCollection()
    .AddTransient<TransientOp>()
    .AddScoped<ScopedOp>()
    .AddSingleton<SingletonOp>();

using (var root = services.BuildServiceProvider())
{
    foreach (var request in new[] { "A", "B" })
    {
        // ASP.NET Core opens one scope per HTTP request
        using var scope = root.CreateScope();
        var sp = scope.ServiceProvider;
        Console.WriteLine($"   request {request}: "
            + $"transient {Ids<TransientOp>(sp)}  "
            + $"scoped {Ids<ScopedOp>(sp)}  "
            + $"singleton {Ids<SingletonOp>(sp)}");
    }
}
#endregion

Console.WriteLine("4 captive dependency: a singleton holding a scoped service");
#region captive
var captive = new ServiceCollection()
    .AddScoped<ScopedOp>()
    .AddSingleton<PriceCache>();                  // PriceCache(ScopedOp scoped)

using (var lax = captive.BuildServiceProvider())  // no validation: default outside Development
{
    using var first = lax.CreateScope();
    using var second = lax.CreateScope();
    var a = first.ServiceProvider.GetRequiredService<PriceCache>().Scoped.Id;
    var b = second.ServiceProvider.GetRequiredService<PriceCache>().Scoped.Id;
    Say("unvalidated:", $"scope 1 sees ScopedOp #{a}, scope 2 sees ScopedOp #{b}");
}

try
{
    captive.BuildServiceProvider(new ServiceProviderOptions
    {
        ValidateScopes = true,                    // both are switched on in Development
        ValidateOnBuild = true,
    });
}
catch (AggregateException ex)
{
    var cause = ex.InnerExceptions[0];
    Say("validated:", cause.InnerException?.Message ?? cause.Message);
}
#endregion

Console.WriteLine("5 keyed services: one interface, a key per implementation");
#region keyed
using (var keyed = new ServiceCollection()
    .AddKeyedSingleton<INotifier, SmsNotifier>("sms")
    .AddKeyedSingleton<INotifier, LineNotifier>("line")
    .BuildServiceProvider())
{
    var line = keyed.GetRequiredKeyedService<INotifier>("line");
    var unkeyed = keyed.GetService<INotifier>();
    Console.WriteLine($"   key \"line\" resolves {line.GetType().Name}");
    Console.WriteLine($"   unkeyed INotifier    {unkeyed?.GetType().Name ?? "null"}");
}
#endregion

// Prints "   label  text", wrapping text at 62 columns under its first line.
static void Say(string label, string text)
{
    var line = $"   {label,-12} ";
    foreach (var word in text.Split(' '))
    {
        if (line.Length + word.Length > 62 && line.Trim().Length > label.Length)
        {
            Console.WriteLine(line.TrimEnd());
            line = new string(' ', 16);
        }
        line += word + " ";
    }
    Console.WriteLine(line.TrimEnd());
}

static string Ids<T>(IServiceProvider sp) where T : Operation =>
    $"{sp.GetRequiredService<T>().Id},{sp.GetRequiredService<T>().Id}";

sealed class QuoteOptions
{
    [Range(1, 90)] public int ValidityDays { get; set; } = 30;
}

abstract class Operation
{
    public abstract int Id { get; }
}

abstract class Operation<TSelf> : Operation
{
    private static int _created;                  // one counter per closed generic type
    private readonly int _id = Interlocked.Increment(ref _created);
    public override int Id => _id;
}

sealed class TransientOp : Operation<TransientOp>;
sealed class ScopedOp : Operation<ScopedOp>;
sealed class SingletonOp : Operation<SingletonOp>;

sealed class PriceCache(ScopedOp scoped)
{
    public ScopedOp Scoped { get; } = scoped;
}

interface INotifier;
sealed class SmsNotifier : INotifier;
sealed class LineNotifier : INotifier;
