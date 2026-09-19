using System.Collections.Concurrent;
using System.Threading.Channels;

namespace L08.QuoteApi.Notifications;

public sealed record QuoteAccepted(Guid QuoteId, string PolicyNumber, string Channel);

/// <summary>Singleton hand-off between request threads and the background dispatcher (channels: lesson 05).</summary>
public sealed class NotificationQueue
{
    private readonly Channel<QuoteAccepted> _channel = Channel.CreateBounded<QuoteAccepted>(100);

    public ChannelReader<QuoteAccepted> Reader => _channel.Reader;

    public bool TryEnqueue(QuoteAccepted message) => _channel.Writer.TryWrite(message);
}

/// <summary>Singleton record of what was sent — stands in for SMS, email and LINE gateways.</summary>
public sealed class NotificationLog
{
    private readonly ConcurrentQueue<string> _sent = new();

    public void Record(string line) => _sent.Enqueue(line);

    public IReadOnlyCollection<string> Sent => _sent.ToArray();
}

public interface INotificationChannel
{
    Task SendAsync(QuoteAccepted message, CancellationToken ct);
}

public sealed class SmsChannel(NotificationLog log) : INotificationChannel
{
    public Task SendAsync(QuoteAccepted m, CancellationToken ct)
    {
        log.Record($"sms   {m.PolicyNumber}");
        return Task.CompletedTask;
    }
}

public sealed class EmailChannel(NotificationLog log) : INotificationChannel
{
    public Task SendAsync(QuoteAccepted m, CancellationToken ct)
    {
        log.Record($"email {m.PolicyNumber}");
        return Task.CompletedTask;
    }
}

public sealed class LineChannel(NotificationLog log) : INotificationChannel
{
    public Task SendAsync(QuoteAccepted m, CancellationToken ct)
    {
        log.Record($"line  {m.PolicyNumber}");
        return Task.CompletedTask;
    }
}

#region background-service
public sealed class NotificationDispatcher(
    NotificationQueue queue,
    IServiceScopeFactory scopes,
    ILogger<NotificationDispatcher> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await foreach (var message in queue.Reader.ReadAllAsync(stoppingToken))
        {
            try   // the whole unit of work: scope, resolution and send
            {
                // a singleton must not hold scoped services: one scope per message
                await using var scope = scopes.CreateAsyncScope();
                var channel = scope.ServiceProvider
                    .GetRequiredKeyedService<INotificationChannel>(message.Channel);
                await channel.SendAsync(message, stoppingToken);
            }
            catch (Exception ex) when (!stoppingToken.IsCancellationRequested)
            {
                // anything escaping ExecuteAsync stops the host: an unknown key, a gateway
                // timeout (TaskCanceledException) and every other failure end up here
                logger.LogError(ex, "Notification {PolicyNumber} via {Channel} failed",
                    message.PolicyNumber, message.Channel);
            }
        }
    }
}
#endregion

public static class NotificationModule
{
    #region keyed-services
    public static IServiceCollection AddNotifications(this IServiceCollection services)
    {
        services.AddSingleton<NotificationQueue>();
        services.AddSingleton<NotificationLog>();
        services.AddKeyedScoped<INotificationChannel, SmsChannel>("sms");
        services.AddKeyedScoped<INotificationChannel, EmailChannel>("email");
        services.AddKeyedScoped<INotificationChannel, LineChannel>("line");
        services.AddHostedService<NotificationDispatcher>();
        return services;
    }
    #endregion
}
