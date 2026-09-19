using L05.Notifications;

const int count = 36, intakeCapacity = 8, laneCapacity = 4;

#region main
// a safety net: the demo ends even if a sender never finishes
using var shutdown = new CancellationTokenSource(TimeSpan.FromSeconds(10));
var dispatcher = new Dispatcher(intakeCapacity, laneCapacity);

var running = dispatcher.RunAsync(shutdown.Token);     // router + senders start, then wait
await foreach (var n in QuoteEvents.ReadAsync(count, shutdown.Token))
    await dispatcher.SubmitAsync(n, shutdown.Token);   // pauses whenever the intake is full
dispatcher.Complete();                                 // no more writes: drain, then stop

var report = await running;
#endregion

Console.WriteLine($"{count} notifications, intake capacity {intakeCapacity}, lane capacity {laneCapacity}");
foreach (var (channel, sent) in report.Sent)
{
    var retried = channel == NotifyChannel.Line ? $", {report.Retries} retried" : "";
    Console.WriteLine($"  {channel,-6}{sent,3} sent{retried}");
}
Console.WriteLine($"  producer waited for space {report.ProducerWaits} time(s)");
