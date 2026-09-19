using System.Reflection;
using System.Runtime;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;

namespace L01.PlatformKit;

#region report-record
/// <summary>An immutable snapshot of the runtime a program is executing on.</summary>
public sealed record PlatformReport(
    string Framework,            // the runtime running this process: ".NET 10.0.12"
    string TargetFramework,      // what the assembly was BUILT for: ".NETCoreApp,Version=v10.0"
    string OperatingSystem,
    Architecture Arch,
    bool ServerGc,               // workstation (False) or server (True) garbage collector
    bool JitOn,                  // False under Native AOT: no code is compiled at run time
    string ImageRuntimeVersion,  // "v4.0.30319" on every modern .NET: a CLR 4 header string
    string CallerAssembly);
#endregion

/// <summary>Reads the facts a <see cref="PlatformReport"/> holds from the running process.</summary>
public static class PlatformProbe
{
    #region capture
    public static PlatformReport Capture(Assembly caller) => new(
        Framework: RuntimeInformation.FrameworkDescription,
        TargetFramework: caller
            .GetCustomAttribute<TargetFrameworkAttribute>()
            ?.FrameworkName ?? "(none)",
        OperatingSystem: RuntimeInformation.OSDescription,
        Arch: RuntimeInformation.ProcessArchitecture,
        ServerGc: GCSettings.IsServerGC,
        JitOn: RuntimeFeature.IsDynamicCodeCompiled,
        ImageRuntimeVersion: caller.ImageRuntimeVersion,
        CallerAssembly: caller.GetName().Name ?? "(unnamed)");
    #endregion
}
