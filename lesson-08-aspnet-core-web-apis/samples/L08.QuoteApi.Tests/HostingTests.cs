using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using L08.QuoteApi.Notifications;
using L08.QuoteApi.Quotes;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using MotorQuote.Rating;

namespace L08.QuoteApi.Tests;

public sealed class HostingTests(QuoteApiFactory factory) : IClassFixture<QuoteApiFactory>
{
    [Fact]
    public async Task Accepting_a_quote_notifies_on_the_requested_channel_in_the_background()
    {
        var client = factory.CreateClient();
        var created = await client.PostAsJsonAsync("/quotes", Requests.Quote(notifyVia: "line"));
        var id = (await created.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("quoteId").GetString();
        var policy = await (await client.PostAsync($"/quotes/{id}/accept", null))
            .Content.ReadFromJsonAsync<JsonElement>();
        var expected = $"line  {policy.GetProperty("policyNumber").GetString()}";

        var log = factory.Services.GetRequiredService<NotificationLog>();
        var deadline = DateTime.UtcNow.AddSeconds(5);
        while (!log.Sent.Contains(expected) && DateTime.UtcNow < deadline)
            await Task.Delay(20);

        Assert.Contains(expected, log.Sent);
    }

    [Fact]
    public void Scoped_services_resolve_inside_a_scope_and_share_singletons()
    {
        using var first = factory.Services.CreateScope();
        using var second = factory.Services.CreateScope();

        Assert.NotSame(first.ServiceProvider.GetRequiredService<QuoteService>(),
            second.ServiceProvider.GetRequiredService<QuoteService>());
        Assert.Same(first.ServiceProvider.GetRequiredService<IQuoteStore>(),
            second.ServiceProvider.GetRequiredService<IQuoteStore>());
    }

    #region captive-test
    [Fact]
    public void Captive_dependency_is_rejected_when_the_provider_is_built()
    {
        var services = new ServiceCollection()
            .AddScoped<PolicyNumbers>()
            .AddSingleton<PolicyCache>();         // singleton -> scoped: captive

        var error = Assert.Throws<AggregateException>(() =>
            services.BuildServiceProvider(new ServiceProviderOptions
            {
                ValidateScopes = true,
                ValidateOnBuild = true,
            }));

        var cause = error.InnerExceptions[0].InnerException!;
        Assert.Contains("Cannot consume scoped service", cause.Message);
    }
    #endregion

    [Fact]
    public void Keyed_notification_channels_resolve_by_key_and_not_without_one()
    {
        using var scope = factory.Services.CreateScope();

        Assert.IsType<LineChannel>(scope.ServiceProvider.GetRequiredKeyedService<INotificationChannel>("line"));
        Assert.Null(scope.ServiceProvider.GetService<INotificationChannel>());
    }

    [Fact]
    public void Options_are_bound_from_appsettings_json()
    {
        Assert.Equal(30, factory.Services.GetRequiredService<IOptions<QuoteOptions>>().Value.ValidityDays);
        Assert.Equal(0.021m, factory.Services.GetRequiredService<IOptions<RatingOptions>>().Value.Class1Rate);
    }

    private sealed class PolicyCache(PolicyNumbers numbers)
    {
        public PolicyNumbers Numbers { get; } = numbers;
    }
}

public sealed class VbRatingTests
{
    #region vb-rating-test
    [Theory]                         // Class 1 on 800,000 THB: the track's canonical tariff
    [InlineData(36, 10, 0, VehicleUse.Private, 1_800, 9_023.95)]
    [InlineData(22, 2, 1, VehicleUse.Private, 1_800, 23_462.28)]
    [InlineData(40, 20, 0, VehicleUse.Commercial, 1_800, 11_279.94)]
    [InlineData(40, 20, 0, VehicleUse.Commercial, 3_500, 12_182.34)]
    public void Visual_Basic_calculator_prices_the_illustrative_tariff(
        int age, int licenceYears, int claims, VehicleUse use, int engineCc, double expectedTotal)
    {
        var calculator = new PremiumCalculator(Options.Create(new RatingOptions()));

        var premium = calculator.Calculate(new RatingInput(
            CoverageClass.Class1, 800_000m, age, licenceYears, claims, use, engineCc));

        Assert.Equal((decimal)expectedTotal, premium.Total);
    }

    // The canonical tariff declines three or more claims in five years instead of pricing them.
    [Fact]
    public void Three_claims_in_five_years_are_declined_rather_than_loaded()
    {
        var calculator = new PremiumCalculator(Options.Create(new RatingOptions()));

        var premium = calculator.Calculate(new RatingInput(
            CoverageClass.Class1, 800_000m, 36, 10, 3, VehicleUse.Private, 1_800));

        Assert.True(premium.IsDeclined);
        Assert.Equal("3+ claims in 5 years", premium.DeclineReason);
        Assert.Equal(0m, premium.Total);
    }
    #endregion

    // The worked example of _curriculum.md "Canonical tariff": Class 1, 550,000 THB, driver 23 with four
    // claim-free licence years. Every rung of the tariff is exercised, so a drift fails here first.
    [Fact]
    public void The_curriculum_worked_example_prices_to_the_published_total()
    {
        var calculator = new PremiumCalculator(Options.Create(new RatingOptions()));

        var premium = calculator.Calculate(new RatingInput(
            CoverageClass.Class1, 550_000m, 23, 4, 0, VehicleUse.Private, 1_800));

        Assert.Equal(11_550.00m, premium.BasePremium);
        Assert.Equal(8_316.00m, premium.NetPremium);
        Assert.Equal(33.26m, premium.StampDuty);
        Assert.Equal(584.45m, premium.Vat);
        Assert.Equal(8_933.71m, premium.Total);
    }
}

/// <summary>Each case boots its own app: before the fix, a failed message stopped the host.</summary>
public sealed class DispatcherTests
{
    [Theory]
    [InlineData("fax")]       // no channel is registered under this key
    [InlineData("timeout")]   // the gateway throws TaskCanceledException, as HttpClient.Timeout does
    public async Task A_failed_notification_is_logged_and_the_host_keeps_serving(string channel)
    {
        await using var factory = new QuoteApiFactory().WithWebHostBuilder(web =>
            web.ConfigureTestServices(services =>
                services.AddKeyedScoped<INotificationChannel, TimingOutChannel>("timeout")));
        var queue = factory.Services.GetRequiredService<NotificationQueue>();
        var log = factory.Services.GetRequiredService<NotificationLog>();

        Assert.True(queue.TryEnqueue(new QuoteAccepted(Guid.NewGuid(), "MQ-900001", channel)));
        Assert.True(queue.TryEnqueue(new QuoteAccepted(Guid.NewGuid(), "MQ-900002", "line")));
        var deadline = DateTime.UtcNow.AddSeconds(5);
        while (!log.Sent.Contains("line  MQ-900002") && DateTime.UtcNow < deadline)
            await Task.Delay(20);

        Assert.Contains("line  MQ-900002", log.Sent);   // the message after the failure was sent
        var lifetime = factory.Services.GetRequiredService<IHostApplicationLifetime>();
        Assert.False(lifetime.ApplicationStopping.IsCancellationRequested);
        Assert.Equal(HttpStatusCode.OK, (await factory.CreateClient().GetAsync("/health")).StatusCode);
    }

    private sealed class TimingOutChannel : INotificationChannel
    {
        public Task SendAsync(QuoteAccepted message, CancellationToken ct) =>
            throw new TaskCanceledException("The request was canceled due to the configured "
                + "HttpClient.Timeout of 100 seconds elapsing.");
    }
}
