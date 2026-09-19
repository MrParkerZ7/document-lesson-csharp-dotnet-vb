using System.Runtime.CompilerServices;

namespace L05.Notifications;

public enum NotifyChannel { Sms, Email, Line }

public sealed record Notification(int Id, string QuoteId, NotifyChannel Channel, string Text);

public sealed record DispatchReport(
    IReadOnlyDictionary<NotifyChannel, int> Sent, int Retries, int ProducerWaits);

public static class QuoteEvents
{
    #region async-stream
    // cold and pull-based, like a Kotlin Flow: nothing
    // runs until someone iterates it with await foreach
    public static async IAsyncEnumerable<Notification> ReadAsync(
        int count,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        for (var id = 1; id <= count; id++)
        {
            await Task.Yield();   // stand-in for an event read
            ct.ThrowIfCancellationRequested();
            var channel = (id % 4) switch
            {
                0 => NotifyChannel.Email,
                2 => NotifyChannel.Sms,
                _ => NotifyChannel.Line,   // LINE is the default
            };
            var quoteId = $"Q-{1000 + id}";
            yield return new Notification(id, quoteId, channel,
                $"Quote {quoteId} is ready");
        }
    }
    #endregion
}
