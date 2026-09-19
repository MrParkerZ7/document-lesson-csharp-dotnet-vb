#region file-scoped
namespace L02.Syntax;   // file-scoped (C# 10): no braces

// No using lines: IDisposable, ValueTask and Console
// resolve through the SDK's implicit global usings.

// a primary constructor (C# 12) - lesson 03
sealed class AuditScope(string name) : IDisposable
{
    public void Dispose() =>
        Console.WriteLine($"dispose {name}");
}

sealed class PartnerConnection : IAsyncDisposable
{
    public ValueTask DisposeAsync()
    {
        Console.WriteLine("async dispose partner connection");
        return ValueTask.CompletedTask;
    }
}
#endregion
