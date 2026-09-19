#region top-level
// Program.cs IS the entry point: no class, no Main.
// Imports: GlobalUsings.cs + the SDK's implicit usings.
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;

Console.WriteLine("L02.Syntax - C# in MotorQuote terms");
TypesTour.Run();
StringsTour.Run();
NullsTour.Run();
PatternsTour.Run();
MethodsTour.Run();
ErrorsTour.Run();
await ErrorsTour.RunAsync();   // await works at top level

return 0;                      // ...and so do args and return
#endregion
