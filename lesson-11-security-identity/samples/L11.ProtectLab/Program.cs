using System.Security.Cryptography;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.Extensions.DependencyInjection;

#region protect
var instanceA = NewKeyRing();
var shareLinks = instanceA.CreateProtector("quotes.share-link")
    .ToTimeLimitedDataProtector();

var link = shareLinks.Protect("Q-1001", TimeSpan.FromMinutes(10));
var expired = shareLinks.Protect("Q-1001", DateTimeOffset.UtcNow.AddSeconds(-1));
var tampered = link[..^4] + (link[^4] == 'A' ? 'B' : 'A') + link[^3..];

var attempts = new (string Name, Func<string> Read)[]
{
    ("same purpose, same key ring", () => shareLinks.Unprotect(link)),
    ("other purpose", () => instanceA.CreateProtector("quotes.accept-link")
        .ToTimeLimitedDataProtector().Unprotect(link)),
    ("one character changed", () => shareLinks.Unprotect(tampered)),
    ("expired a second ago", () => shareLinks.Unprotect(expired)),
    ("another instance's key ring", () => NewKeyRing().CreateProtector("quotes.share-link")
        .ToTimeLimitedDataProtector().Unprotect(link)),
};
#endregion

Console.WriteLine($"share link for Q-1001: {link.Length} chars, starts {link[..5]}");
Console.WriteLine();

foreach (var (name, read) in attempts)
{
    try
    {
        Console.WriteLine($"{name,-29}{read()}");
    }
    catch (CryptographicException e)
    {
        Console.WriteLine($"{name,-29}rejected: {Reason(e.Message)}");
    }
}

#region key-ring
// A key ring that lives and dies with one process. Without a shared key store
// (PersistKeysTo...), every container instance has one of these.
static IDataProtectionProvider NewKeyRing()
{
    var services = new ServiceCollection();
    services.AddDataProtection()
        .SetApplicationName("motorquote")       // apps that share payloads share this name
        .UseEphemeralDataProtectionProvider();  // keys in memory only
    return services.BuildServiceProvider().GetRequiredService<IDataProtectionProvider>();
}
#endregion

// Keep the stable part of a message such as "The payload expired at <timestamp>."
static string Reason(string message) =>
    message.Split(" at ", 2)[0].TrimEnd('.');
