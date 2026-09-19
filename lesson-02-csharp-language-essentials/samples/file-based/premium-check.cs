#!/usr/bin/env -S dotnet --
#:project ../L02.Rating/L02.Rating.csproj
#:property PublishAot=false

// A file-based app (.NET 10 SDK): no .csproj, no Main, no namespace.
//   dotnet premium-check.cs              the worked example
//   dotnet premium-check.cs -- 3         the same driver with 3 claims
using System.Globalization;
using L02.Rating;

var inv = CultureInfo.InvariantCulture;   // the same digits on every machine
int claims = args is [var first, ..] ? int.Parse(first, inv) : 0;
var request = Examples.YoungDriver(claims);

if (PremiumCalculator.TryCalculate(request, out var premium, out var reason))
    Console.WriteLine(string.Create(inv, $"total {premium.Total:N2} THB (net {premium.Net:N2})"));
else
    Console.WriteLine($"declined: {reason}");
