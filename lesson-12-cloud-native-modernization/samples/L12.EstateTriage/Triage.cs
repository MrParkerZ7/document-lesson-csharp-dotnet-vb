namespace L12.EstateTriage;

/// <summary>The AWS "7 Rs" migration strategies.</summary>
public enum Strategy { Retire, Retain, Rehost, Relocate, Repurchase, Replatform, Refactor }

public sealed record App(
    string Name, string Language, string Framework, string Kind,
    IReadOnlySet<string> Signals, string Traffic, string Value);

public sealed record Decision(Strategy Strategy, string Target, string Path);

public static class Triage
{
    #region rules
    // First matching arm wins — order the arms from "stop" to "default".
    public static Decision Decide(App app) => app switch
    {
        { Value: "none" } =>
            new(Strategy.Retire, "-", "archive the data, switch it off"),
        { Kind: "cots" } =>
            new(Strategy.Repurchase, "SaaS", "replace with the vendor's SaaS"),
        { Framework: "vb6", Kind: "desktop" } =>
            new(Strategy.Refactor, "desktop", "rewrite in C# for .NET: VB6 is COM, not .NET"),
        { Framework: "vb6" } =>
            new(Strategy.Refactor, "ECS Fargate", "rewrite in C# as a service: VB6 is COM"),
        { Signals: var s } when s.Contains("com-interop") || s.Contains("gac") =>
            new(Strategy.Rehost, "EC2 Windows/IIS", "lift as-is; port once COM/GAC is gone"),
        { Signals: var s } when s.Contains("msmq") =>
            new(Strategy.Replatform, "ECS Fargate", "BackgroundService; MSMQ becomes SQS"),
        { Kind: "winforms" } =>
            new(Strategy.Retain, "desktop", "retarget net10.0-windows in place"),
        { Framework: "net8.0" or "net9.0" } =>
            new(Strategy.Replatform, "ECS Fargate", "retarget net10.0 + container publish"),
        { Kind: "wcf" } =>
            new(Strategy.Replatform, "ECS Fargate", "CoreWCF; gRPC for new callers"),
        { Kind: "webforms" } =>
            new(Strategy.Refactor, "ECS Fargate", "Blazor pages strangled behind YARP"),
        { Kind: "batch", Traffic: "spiky" } =>
            new(Strategy.Refactor, "Lambda", "event-driven function per job"),
        { Kind: "mvc" or "webapi" } =>
            new(Strategy.Replatform, "ECS Fargate", "ASP.NET Core + System.Web adapters"),
        _ =>
            new(Strategy.Replatform, "ECS Fargate", "port to net10.0"),
    };
    #endregion
}

public static class Inventory
{
    public static IReadOnlyList<App> Load(string path) =>
        File.ReadLines(path)
            .Skip(1)
            .Where(line => line.Length > 0)
            .Select(line => line.Split(','))
            .Select(c => new App(c[0], c[1], c[2], c[3],
                c[4].Split(';', StringSplitOptions.RemoveEmptyEntries).ToHashSet(),
                c[5], c[6]))
            .ToList();
}
