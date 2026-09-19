using System.Data.Common;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace L09.Data;

#region interceptor
// Records every command EF Core sends, sync or async. Tests assert on
// Count (the N+1 is a number, not a feeling); the console prints Sql.
public sealed class SqlCommandLog : DbCommandInterceptor
{
    private readonly List<string> _sql = [];

    public int Count => _sql.Count;
    public IReadOnlyList<string> Sql => _sql;
    public void Reset() => _sql.Clear();

    public override ValueTask<InterceptionResult<DbDataReader>> ReaderExecutingAsync(
        DbCommand command, CommandEventData eventData,
        InterceptionResult<DbDataReader> result, CancellationToken cancellationToken = default)
    {
        _sql.Add(command.CommandText);
        return ValueTask.FromResult(result);
    }

    // ...plus ReaderExecuting, NonQueryExecuting(Async) and ScalarExecuting(Async),
    // the same shape: sync and async paths are separate overrides.
#endregion

    public override InterceptionResult<DbDataReader> ReaderExecuting(
        DbCommand command, CommandEventData eventData,
        InterceptionResult<DbDataReader> result)
    {
        _sql.Add(command.CommandText);
        return result;
    }

    public override InterceptionResult<int> NonQueryExecuting(
        DbCommand command, CommandEventData eventData, InterceptionResult<int> result)
    {
        _sql.Add(command.CommandText);
        return result;
    }

    public override ValueTask<InterceptionResult<int>> NonQueryExecutingAsync(
        DbCommand command, CommandEventData eventData,
        InterceptionResult<int> result, CancellationToken cancellationToken = default)
    {
        _sql.Add(command.CommandText);
        return ValueTask.FromResult(result);
    }

    public override InterceptionResult<object> ScalarExecuting(
        DbCommand command, CommandEventData eventData, InterceptionResult<object> result)
    {
        _sql.Add(command.CommandText);
        return result;
    }

    public override ValueTask<InterceptionResult<object>> ScalarExecutingAsync(
        DbCommand command, CommandEventData eventData,
        InterceptionResult<object> result, CancellationToken cancellationToken = default)
    {
        _sql.Add(command.CommandText);
        return ValueTask.FromResult(result);
    }
}
