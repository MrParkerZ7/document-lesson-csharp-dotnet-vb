using System.Reflection;
using System.Runtime;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace L01.PlatformKit;

#region report-record
/// <summary>An immutable snapshot of the runtime a program is executing on.</summary>
public sealed record PlatformReport(
    string Framework,              // ".NET 10.0.x" — the product you installed
    string RuntimeVersion,         // CLR version, e.g. 10.0.0
    string OperatingSystem,
    Architecture ProcessArchitecture,
    bool ServerGc,                 // workstation vs server garbage collector
    bool DynamicCodeCompiled,      // true = JIT is on; false under Native AOT
    string MetadataVersion,        // "v4.0.30319" on every modern .NET (a trap!)
    string CallerAssembly)
{
    public static PlatformReport Capture(Assembly caller) => new(
        Framework: RuntimeInformation.FrameworkDescription,
        RuntimeVersion: Environment.Version.ToString(),
        OperatingSystem: RuntimeInformation.OSDescription,
        ProcessArchitecture: RuntimeInformation.ProcessArchitecture,
        ServerGc: GCSettings.IsServerGC,
        DynamicCodeCompiled: RuntimeFeature.IsDynamicCodeCompiled,
        MetadataVersion: caller.ImageRuntimeVersion,
        CallerAssembly: caller.GetName().Name ?? "(unnamed)");
}
#endregion
