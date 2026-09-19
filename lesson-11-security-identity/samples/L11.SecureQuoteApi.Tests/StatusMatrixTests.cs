using System.Net.Http.Headers;
using System.Net.Http.Json;
using L11.SecureQuoteApi.Quotes;

namespace L11.SecureQuoteApi.Tests;

public sealed class StatusMatrixTests(SecureApiFactory factory) : IClassFixture<SecureApiFactory>
{
    private static readonly string[] Endpoints =
    [
        "GET /quotes/Q-1001", "POST /quotes", "POST /quotes/Q-1001/accept", "GET /underwriting/referrals",
    ];

    #region callers
    private const string ReadWrite = "Quotes.Read Quotes.Write";

    private static readonly Dictionary<string, string?> Tokens = new()
    {
        ["anonymous"] = null,
        ["expired"] = TestTokens.Create("cust-a", ReadWrite, expiresIn: TimeSpan.FromMinutes(-2)),
        ["wrong-audience"] = TestTokens.Create("cust-a", ReadWrite, audience: "api://l11-partner-api"),
        ["owner"] = TestTokens.Create("cust-a", ReadWrite),
        ["other-customer"] = TestTokens.Create("cust-b", ReadWrite),
        ["owner-read-only"] = TestTokens.Create("cust-a", "Quotes.Read"),
        ["underwriter"] = TestTokens.Create("uw-1", "Quotes.Read", roles: ["Underwriter"]),
        ["underwriter-rw"] = TestTokens.Create("uw-1", ReadWrite, roles: ["Underwriter"]),
        ["back-office-app"] = TestTokens.Create(roles: ["Quotes.Read.All"]),   // no sub, no scp
    };
    #endregion

    #region matrix
    //                           GET quote  POST quotes  accept  referrals
    private static readonly (string Caller, int[] Expected)[] Matrix =
    [
        ("anonymous",           [401,       401,         401,    401]),
        ("expired",             [401,       401,         401,    401]),
        ("wrong-audience",      [401,       401,         401,    401]),
        ("owner",               [200,       201,         200,    403]),
        ("other-customer",      [403,       201,         403,    403]),
        ("owner-read-only",     [200,       403,         403,    403]),
        ("underwriter",         [200,       403,         403,    200]),
        ("underwriter-rw",      [200,       201,         403,    200]),
        ("back-office-app",     [200,       403,         403,    403]),
    ];
    #endregion

    public static TheoryData<string, string, int> Cases()
    {
        var data = new TheoryData<string, string, int>();
        foreach (var (caller, expected) in Matrix)
        {
            for (var i = 0; i < Endpoints.Length; i++)
            {
                data.Add(caller, Endpoints[i], expected[i]);
            }
        }
        return data;
    }

    #region matrix-test
    [Theory]
    [MemberData(nameof(Cases))]
    public async Task Caller_gets_the_expected_status(string caller, string endpoint, int expected)
    {
        var parts = endpoint.Split(' ');
        using var request = new HttpRequestMessage(new HttpMethod(parts[0]), parts[1]);
        if (Tokens[caller] is { } token)
        {
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        }
        if (endpoint == "POST /quotes")
        {
            request.Content = JsonContent.Create(new QuoteRequest("Toyota", 2024, 850_000m));
        }

        using var client = factory.CreateClient();
        using var response = await client.SendAsync(request);

        Assert.Equal(expected, (int)response.StatusCode);
    }
    #endregion
}
