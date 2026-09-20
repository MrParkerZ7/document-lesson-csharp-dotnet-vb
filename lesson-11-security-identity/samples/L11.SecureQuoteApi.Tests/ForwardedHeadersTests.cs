using System.Net;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;

namespace L11.SecureQuoteApi.Tests;

public sealed class ForwardedHeadersTests
{
    #region balancer-trap
    [Theory]
    [InlineData("10.0.0.0/16", HttpStatusCode.OK)]     // the balancer's network is trusted
    [InlineData(null, HttpStatusCode.TooManyRequests)] // default: loopback only, one shared bucket
    public async Task Callers_behind_one_balancer_need_forwarded_headers_to_get_their_own_bucket(
        string? trustedNetwork, HttpStatusCode secondCaller)
    {
        await using var factory = new SecureApiFactory().WithWebHostBuilder(b =>
        {
            b.UseSetting("RateLimit:PerMinute", "1");
            if (trustedNetwork is not null)
            {
                b.UseSetting("Proxy:Network", trustedNetwork);
            }
            b.ConfigureTestServices(services =>
                services.AddSingleton<IStartupFilter, BalancerAddressFilter>());
        });
        using var client = factory.CreateClient();

        using var first = await Get(client, "203.0.113.7");
        using var second = await Get(client, "203.0.113.8");   // a different caller

        Assert.Equal(HttpStatusCode.OK, first.StatusCode);
        Assert.Equal(secondCaller, second.StatusCode);
    }

    private static Task<HttpResponseMessage> Get(HttpClient client, string caller)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, "/health");
        request.Headers.Add("X-Forwarded-For", caller);
        return client.SendAsync(request);
    }

    // TestServer has no socket: pretend every request arrives from the balancer at 10.0.1.5
    private sealed class BalancerAddressFilter : IStartupFilter
    {
        public Action<IApplicationBuilder> Configure(Action<IApplicationBuilder> next) => app =>
        {
            app.Use((context, nextMiddleware) =>
            {
                context.Connection.RemoteIpAddress = IPAddress.Parse("10.0.1.5");
                return nextMiddleware(context);
            });
            next(app);
        };
    }
    #endregion
}
