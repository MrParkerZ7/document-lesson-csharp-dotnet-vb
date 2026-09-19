using System.Threading.Channels;

namespace L05.Notifications;

/// <summary>
/// intake (bounded) → router → one bounded lane per channel → one sender per lane.
/// A full channel makes its writer wait: that is the back-pressure.
/// </summary>
public sealed class Dispatcher
{
    private static readonly Dictionary<NotifyChannel, TimeSpan> SendLatency = new()
    {
        [NotifyChannel.Sms] = TimeSpan.FromMilliseconds(12),
        [NotifyChannel.Email] = TimeSpan.FromMilliseconds(20),
        [NotifyChannel.Line] = TimeSpan.FromMilliseconds(8),
    };

    private readonly Channel<Notification> _intake;
    private readonly Dictionary<NotifyChannel, Channel<Notification>> _lanes;
    private int _producerWaits, _retries;

    #region bounded-channel
    public Dispatcher(int intakeCapacity, int laneCapacity)
    {
        // Wait (the default FullMode): a full intake pauses the producer instead of dropping work
        _intake = Channel.CreateBounded<Notification>(new BoundedChannelOptions(intakeCapacity)
        {
            FullMode = BoundedChannelFullMode.Wait,
            SingleReader = true,                    // only the router reads the intake
        });
        _lanes = Enum.GetValues<NotifyChannel>()
            .ToDictionary(c => c, _ => Channel.CreateBounded<Notification>(laneCapacity));
    }

    public async ValueTask SubmitAsync(Notification n, CancellationToken ct)
    {
        if (_intake.Writer.TryWrite(n)) return;     // room: no waiting at all
        Interlocked.Increment(ref _producerWaits);  // full: count it, then wait for space
        await _intake.Writer.WriteAsync(n, ct);
    }

    public void Complete() => _intake.Writer.Complete();   // "no more notifications"
    #endregion

    #region pipeline
    public async Task<DispatchReport> RunAsync(CancellationToken ct)
    {
        // start one sender per lane; each waits for work
        var senders = _lanes.Select(lane => SendAllAsync(lane.Key, lane.Value.Reader, ct)).ToArray();

        // the router: ends when the intake is completed AND empty
        await foreach (var n in _intake.Reader.ReadAllAsync(ct))
            await _lanes[n.Channel].Writer.WriteAsync(n, ct);   // waits if that lane is full

        foreach (var lane in _lanes.Values) lane.Writer.Complete();  // let the senders drain
        var sent = await Task.WhenAll(senders);
        var perChannel = sent.ToDictionary(s => s.Channel, s => s.Count);
        return new DispatchReport(perChannel, _retries, _producerWaits);
    }
    #endregion

    private async Task<(NotifyChannel Channel, int Count)> SendAllAsync(
        NotifyChannel channel, ChannelReader<Notification> reader, CancellationToken ct)
    {
        var count = 0;
        await foreach (var n in reader.ReadAllAsync(ct))
        {
            await SendAsync(channel, n, ct);
            count++;
        }
        return (channel, count);
    }

    private async Task SendAsync(NotifyChannel channel, Notification n, CancellationToken ct)
    {
        for (var attempt = 1; ; attempt++)
        {
            await Task.Delay(SendLatency[channel], ct);   // the provider's API call
            // a LINE rate-limit reply on the first attempt for every fifth message: retry once
            var rejected = channel == NotifyChannel.Line && n.Id % 5 == 0 && attempt == 1;
            if (!rejected) return;
            Interlocked.Increment(ref _retries);
        }
    }
}
