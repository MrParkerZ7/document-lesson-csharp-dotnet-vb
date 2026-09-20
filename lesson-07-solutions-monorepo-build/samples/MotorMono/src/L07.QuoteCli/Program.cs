using System.Globalization;
using System.Reflection;
using L07.Core;
using L07.Pricing;
using L07.Pricing.Vb;
using InformationalVersion = System.Reflection.AssemblyInformationalVersionAttribute;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;

#region compose
// One build graph, two languages: the calculator is C#, one of its rules is Visual Basic.
IRatingRule[] rules = [new YoungDriverLoading(), new ClaimsLoading(), new NoClaimBonusVb()];

// the worked example every lesson of the track prices: 8,933.71 THB in total
var request = new QuoteRequest(CoverageClass.Class1, new Money(550_000m),
    DriverAge: 23, ClaimFreeYears: 4, ClaimsLast5Years: 0);

var premium = new PremiumCalculator(rules).Calculate(request);
#endregion

#region build-info
// Facts that MSBuild compiled into this assembly
var assembly = Assembly.GetExecutingAssembly();
var facts = assembly
    .GetCustomAttributes<AssemblyMetadataAttribute>()
    .ToDictionary(a => a.Key, a => a.Value);
var version = assembly
    .GetCustomAttribute<InformationalVersion>()!
    .InformationalVersion.Split('+');

Console.WriteLine(
    $"MotorMono CLI {version[0]}  commit {Commit(version)}");
Console.WriteLine($"  projects   {facts["MotorProjects"]}");
Console.WriteLine($"  built via  {facts["BuiltFrom"]}");
#endregion

Console.WriteLine();
Console.WriteLine($"{request.Coverage} · sum insured {request.SumInsured} · driver age {request.DriverAge}");
Row("base premium", "", premium.Base);
foreach (var line in premium.Adjustments)
{
    Row(line.Rule, line.Module, line.Amount);
}

Row("net premium", "", premium.Net);
Row("stamp duty 0.4%", "", premium.StampDuty);
Row("VAT 7%", "", premium.Vat);
Row("total", "", premium.Total);
Console.WriteLine("rates are illustrative, not a real tariff");

static void Row(string label, string module, Money amount) =>
    Console.WriteLine($"  {label,-17}{module,-16}{amount,16}");

static string Commit(string[] version) => version.Length > 1 ? version[1][..7] : "(none)";
