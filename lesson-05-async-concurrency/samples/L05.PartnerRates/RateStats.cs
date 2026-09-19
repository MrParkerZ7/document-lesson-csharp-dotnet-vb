using System.Collections.Concurrent;

namespace L05.PartnerRates;

/// <summary>Running statistics that many partner calls update at the same time.</summary>
public sealed class RateStats
{
    #region stats
    private readonly Lock _gate = new();   // .NET 9 / C# 13: a dedicated lock type
    private Quoted? _best;
    private int _quoted, _timedOut, _failed;

    public void Record(PartnerOutcome outcome)
    {
        switch (outcome)
        {
            case Quoted q:
                Interlocked.Increment(ref _quoted);      // one integer: no lock needed
                lock (_gate)                             // read-compare-write: needs the lock
                {
                    if (_best is null || q.Premium.Amount < _best.Premium.Amount)
                        _best = q;
                }
                break;
            case TimedOut:
                Interlocked.Increment(ref _timedOut);
                break;
            case Failed:
                Interlocked.Increment(ref _failed);
                break;
        }
    }
    #endregion

    // Named *Count on purpose: a property called TimedOut would make `case TimedOut:` above
    // bind to the property instead of the record type (error CS0029).
    public int QuotedCount => Volatile.Read(ref _quoted);
    public int TimedOutCount => Volatile.Read(ref _timedOut);
    public int FailedCount => Volatile.Read(ref _failed);

    public Quoted? Best
    {
        get
        {
            lock (_gate)
            {
                return _best;
            }
        }
    }
}

/// <summary>Concurrent callers asking for the same key share one in-flight call.</summary>
public sealed class SingleFlight<TKey, TValue> where TKey : notnull
{
    #region single-flight
    private readonly ConcurrentDictionary<TKey, Lazy<Task<TValue>>> _inFlight = new();

    public Task<TValue> RunAsync(TKey key, Func<TKey, Task<TValue>> call)
    {
        // GetOrAdd can run its factory twice under a race — so the factory only builds a cheap
        // Lazy wrapper, and only the Lazy that won is ever started: one partner call per key
        var lazy = _inFlight.GetOrAdd(key, k => new Lazy<Task<TValue>>(() => call(k)));
        return lazy.Value;
    }
    #endregion

    public bool Forget(TKey key) => _inFlight.TryRemove(key, out _);
}
