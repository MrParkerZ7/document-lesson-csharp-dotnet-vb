namespace L05.PartnerRates;

/// <summary>An access token that many concurrent partner calls share: one caller refreshes it, the rest wait.</summary>
#region token-gate
public sealed class PartnerToken(
    TimeProvider time, Func<CancellationToken, Task<string>> fetch, TimeSpan lifetime)
{
    private sealed record Issued(string Value, DateTimeOffset Expires);

    private readonly SemaphoreSlim _gate = new(1, 1);   // one refresh at a time
    private volatile Issued? _current;                  // one reference: no half-written token

    public async Task<string> GetAsync(CancellationToken ct = default)
    {
        if (_current is { } fresh && fresh.Expires > time.GetUtcNow())
            return fresh.Value;                          // fast path: no wait, no lock

        await _gate.WaitAsync(ct).ConfigureAwait(false); // waits without holding a thread
        try
        {
            var issued = _current;                       // the caller ahead may have refreshed
            if (issued is null || issued.Expires <= time.GetUtcNow())
            {
                var value = await fetch(ct).ConfigureAwait(false);   // an await inside the gate
                _current = issued = new Issued(value, time.GetUtcNow() + lifetime);
            }
            return issued.Value;
        }
        finally
        {
            _gate.Release();                             // always, or later callers wait forever
        }
    }
}
#endregion
