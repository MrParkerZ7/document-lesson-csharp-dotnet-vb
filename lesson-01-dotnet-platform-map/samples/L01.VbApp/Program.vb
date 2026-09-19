Imports System.Reflection
Imports L01.PlatformKit

Module Program
    Sub Main()
#Region "program"
        Dim r = PlatformProbe.Capture(
            Assembly.GetExecutingAssembly())

        Console.WriteLine($"Hello from VB on {r.Framework}")
        Console.WriteLine($"  target    {r.TargetFramework}")
        Console.WriteLine($"  os        {r.OperatingSystem}")
        Console.WriteLine($"  arch      {r.Arch}")
        Console.WriteLine($"  server GC {r.ServerGc}")
        Console.WriteLine($"  JIT on    {r.JitOn}")
        Console.WriteLine($"  image     {r.ImageRuntimeVersion}")
        Console.WriteLine($"  assembly  {r.CallerAssembly}")
#End Region

#Region "equality"
        ' VB can USE the C# record (read it, compare it) but has
        ' no expression that makes a modified copy of it.
        Dim same = r.Equals(PlatformProbe.Capture(
            Assembly.GetExecutingAssembly()))
        Console.WriteLine($"  equal?    {same}")    ' True
#End Region
    End Sub
End Module
