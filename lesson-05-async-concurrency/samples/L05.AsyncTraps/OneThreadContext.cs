using System.Collections.Concurrent;
using System.Diagnostics;

namespace L05.AsyncTraps;

/// <summary>
/// A SynchronizationContext like a UI thread or classic ASP.NET: posted continuations queue up and
/// run only when the owning thread pumps them. A blocked owner never pumps.
/// </summary>
public sealed class OneThreadContext : SynchronizationContext
{
    private readonly BlockingCollection<(SendOrPostCallback Callback, object? State)> _queue = new();

    public override void Post(SendOrPostCallback d, object? state) => _queue.Add((d, state));

    public override void Send(SendOrPostCallback d, object? state) =>
        throw new NotSupportedException("this demo context only queues work");

    /// <summary>Runs queued work on the calling thread until a callback throws or the budget ends.</summary>
    public Exception? PumpUntilException(TimeSpan budget)
    {
        var clock = Stopwatch.StartNew();
        while (clock.Elapsed < budget)
        {
            if (!_queue.TryTake(out var item, TimeSpan.FromMilliseconds(20))) continue;
            try
            {
                item.Callback(item.State);
            }
            catch (Exception ex)
            {
                return ex;
            }
        }
        return null;
    }

    /// <summary>Runs <paramref name="body"/> on a new thread that owns this context.</summary>
    public T RunOnOwnThread<T>(Func<T> body)
    {
        T result = default!;
        var thread = new Thread(() =>
        {
            SetSynchronizationContext(this);
            result = body();
        }) { IsBackground = true };
        thread.Start();
        thread.Join();
        return result;
    }
}
