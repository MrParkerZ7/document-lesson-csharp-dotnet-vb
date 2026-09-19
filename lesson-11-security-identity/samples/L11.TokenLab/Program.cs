using System.Security.Cryptography;
using Microsoft.IdentityModel.JsonWebTokens;
using Microsoft.IdentityModel.Tokens;

const string Issuer = "https://login.example.test/tenant-l11/v2.0";
const string Audience = "api://l11-secure-quote-api";
const string OtherTenant = "https://login.example.test/x";
const string PartnerApi = "api://l11-partner-api";

var idpKey = new RsaSecurityKey(RSA.Create(2048)) { KeyId = "idp-key-1" };
// same kid as the real key, different key material
var strangerKey = new RsaSecurityKey(RSA.Create(2048)) { KeyId = "idp-key-1" };

#region parameters
// What AddJwtBearer builds from Authority + Audience (the keys come from the JWKS)
var parameters = new TokenValidationParameters
{
    ValidIssuer = Issuer,
    ValidAudience = Audience,
    IssuerSigningKey = idpKey,
    // ClockSkew is not set, so TokenValidationParameters.DefaultClockSkew applies
};
#endregion

Console.WriteLine($"DefaultClockSkew = {TokenValidationParameters.DefaultClockSkew}");
Console.WriteLine();

#region cases
Action<TokenValidationParameters> asConfigured = _ => { };
Action<TokenValidationParameters> skew30s = p => p.ClockSkew = TimeSpan.FromSeconds(30);
Action<TokenValidationParameters> noAudience = p => p.ValidAudience = null;

var cases = new (string Name, string Token, Action<TokenValidationParameters> Adjust)[]
{
    ("valid token",              Mint(),                 asConfigured),
    ("expired 3 min ago",        Mint(expiresMin: -3),   asConfigured),
    ("same token, skew 30 s",    Mint(expiresMin: -3),   skew30s),
    ("audience of another API",  Mint(aud: PartnerApi),  asConfigured),
    ("API sets no audience",     Mint(),                 noAudience),
    ("issuer of another tenant", Mint(iss: OtherTenant), asConfigured),
    ("signed by a stranger key", Mint(key: strangerKey), asConfigured),
    ("unsigned, alg none",       Mint(unsigned: true),   asConfigured),
};

var handler = new JsonWebTokenHandler();
foreach (var (name, token, adjust) in cases)
{
    var p = parameters.Clone();
    adjust(p);
    var result = await handler.ValidateTokenAsync(token, p);
    var verdict = result.IsValid ? "ACCEPTED" : "rejected  " + result.Exception?.GetType().Name;
    Console.WriteLine($"{name,-26}{verdict}");
}
#endregion

string Mint(int expiresMin = 5, string aud = Audience, string iss = Issuer,
    RsaSecurityKey? key = null, bool unsigned = false)
{
    var issued = DateTime.UtcNow.AddMinutes(-10);
    return new JsonWebTokenHandler().CreateToken(new SecurityTokenDescriptor
    {
        Issuer = iss,
        Audience = aud,
        Claims = new Dictionary<string, object> { ["sub"] = "cust-a", ["scp"] = "Quotes.Read" },
        IssuedAt = issued,
        NotBefore = issued,
        Expires = DateTime.UtcNow.AddMinutes(expiresMin),
        SigningCredentials = unsigned ? null
            : new SigningCredentials(key ?? idpKey, SecurityAlgorithms.RsaSha256),
    });
}
