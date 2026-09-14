using System.Reflection;
using L01.PlatformKit;

#region program
var r = PlatformReport.Capture(
    Assembly.GetExecutingAssembly());

Console.WriteLine($"Hello from C# on {r.Framework}");
Console.WriteLine($"  os        {r.OperatingSystem}");
Console.WriteLine($"  arch      {r.ProcessArchitecture}");
Console.WriteLine($"  JIT on    {r.DynamicCodeCompiled}");
Console.WriteLine($"  metadata  {r.MetadataVersion}");
Console.WriteLine($"  assembly  {r.CallerAssembly}");
#endregion

#region record-equality
// records compare by VALUE, like a Kotlin data class
var flipped = r with { ServerGc = !r.ServerGc };
Console.WriteLine($"  same?     {r == flipped}"); // False
Console.WriteLine($"  copy?     {r == r with { }}"); // True
#endregion
