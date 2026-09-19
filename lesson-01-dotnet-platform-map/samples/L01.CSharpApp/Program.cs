using System.Reflection;
using L01.PlatformKit;

#region program
var r = PlatformProbe.Capture(
    Assembly.GetExecutingAssembly());

Console.WriteLine($"Hello from C# on {r.Framework}");
Console.WriteLine($"  target    {r.TargetFramework}");
Console.WriteLine($"  os        {r.OperatingSystem}");
Console.WriteLine($"  arch      {r.Arch}");
Console.WriteLine($"  server GC {r.ServerGc}");
Console.WriteLine($"  JIT on    {r.JitOn}");
Console.WriteLine($"  image     {r.ImageRuntimeVersion}");
Console.WriteLine($"  assembly  {r.CallerAssembly}");
#endregion

#region equality
// records compare by VALUE, like a Kotlin data class
var flipped = r with { ServerGc = !r.ServerGc };
Console.WriteLine($"  same?     {r == flipped}"); // False
Console.WriteLine($"  copy?     {r == r with { }}"); // True
#endregion
