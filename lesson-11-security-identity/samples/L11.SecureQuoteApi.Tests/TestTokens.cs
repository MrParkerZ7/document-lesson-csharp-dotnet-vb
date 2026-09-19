using System.Security.Cryptography;
using Microsoft.IdentityModel.JsonWebTokens;
using Microsoft.IdentityModel.Tokens;

namespace L11.SecureQuoteApi.Tests;

#region test-tokens
public static class TestTokens
{
    public const string Issuer = "https://login.example.test/tenant-l11/v2.0";
    public const string Audience = "api://l11-secure-quote-api";

    // One RSA key per test run: the API under test trusts it, nothing else ever sees it
    public static readonly RsaSecurityKey Key = new(RSA.Create(2048)) { KeyId = "l11-test" };

    public static string Create(string? sub = null, string? scp = null, string[]? roles = null,
        string audience = Audience, TimeSpan? expiresIn = null)
    {
        var claims = new Dictionary<string, object>();
        if (sub is not null) { claims["sub"] = sub; }
        if (scp is not null) { claims["scp"] = scp; }         // "Quotes.Read Quotes.Write"
        if (roles is not null) { claims["roles"] = roles; }   // a JSON array, as Entra issues

        var issued = DateTime.UtcNow.AddMinutes(-10);
        return new JsonWebTokenHandler().CreateToken(new SecurityTokenDescriptor
        {
            Issuer = Issuer,
            Audience = audience,
            Claims = claims,
            IssuedAt = issued,
            NotBefore = issued,
            Expires = DateTime.UtcNow + (expiresIn ?? TimeSpan.FromMinutes(5)),
            SigningCredentials = new SigningCredentials(Key, SecurityAlgorithms.RsaSha256),
        });
    }
}
#endregion
