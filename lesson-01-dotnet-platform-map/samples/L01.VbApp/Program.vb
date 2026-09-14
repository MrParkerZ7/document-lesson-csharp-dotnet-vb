Imports System.Reflection
Imports L01.PlatformKit

Module Program
    Sub Main()
#Region "program"
        Dim r = PlatformReport.Capture(
            Assembly.GetExecutingAssembly())

        Console.WriteLine($"Hello from VB on {r.Framework}")
        Console.WriteLine($"  os        {r.OperatingSystem}")
        Console.WriteLine($"  arch      {r.ProcessArchitecture}")
        Console.WriteLine($"  JIT on    {r.DynamicCodeCompiled}")
        Console.WriteLine($"  metadata  {r.MetadataVersion}")
        Console.WriteLine($"  assembly  {r.CallerAssembly}")
#End Region

#Region "record-equality"
        ' VB can USE the C# record (read it, compare it) but has
        ' no `With` syntax to make a modified copy of it.
        Dim same = r.Equals(PlatformReport.Capture(
            Assembly.GetExecutingAssembly()))
        Console.WriteLine($"  equal?    {same}")    ' True
#End Region
    End Sub
End Module
