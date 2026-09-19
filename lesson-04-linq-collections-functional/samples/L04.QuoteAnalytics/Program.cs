using System.Globalization;
using System.Linq.Expressions;
using L04.QueryGen;
using L04.QuoteData;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
var quotes = QuoteBook.Generate();
var policies = QuoteBook.IssuePolicies(quotes);
Console.WriteLine($"MotorQuote dashboard: {quotes.Count} quotes, illustrative rates");

Console.WriteLine("conversion by coverage class   quoted accepted rate");
foreach (var c in QuoteDashboard.Conversion(quotes))
    Console.WriteLine($"  {c.Coverage,-11}{c.Quoted,20}{c.Accepted,9}{c.Rate * 100,7:0.0}%");

Console.WriteLine("premium bands, all quotes");
foreach (var (band, n) in QuoteDashboard.Bands(quotes))
    Console.WriteLine($"  {band,-9}{n,5}");

Console.WriteLine("top makes, accepted quotes");
foreach (var m in QuoteDashboard.TopMakes(quotes))
    Console.WriteLine($"  {m.Rank}. {m.Make,-8}{m.Sold,4}");

Console.WriteLine("accepted premium by class, THB");
foreach (var (coverage, total) in QuoteDashboard.PremiumByClass(quotes))
    Console.WriteLine($"  {coverage,-11}{total,12:N0}");

var issuance = QuoteDashboard.Issuance(quotes, policies).ToList();
var pending = issuance.Count(x => x.Policy == "(pending)");
Console.WriteLine($"issuance       {issuance.Count} accepted, {pending} pending");
var batches = QuoteDashboard.ExportBatches(quotes).Select(b => b.Length);
Console.WriteLine($"export batches {string.Join(" + ", batches)}");
Console.WriteLine($"lookup         {QuoteDashboard.ByMake(quotes)["Toyota"].Count()} Toyota quotes");

Console.WriteLine();
#region expression-demo
#region func-vs-expression
Func<Quote, bool> compiled = q => q.Coverage == CoverageClass.Class1;
Expression<Func<Quote, bool>> tree = q => q.Coverage == CoverageClass.Class1;
Console.WriteLine($"compiled  {compiled.GetType().Name}  -> {compiled(quotes[0])}");
Console.WriteLine($"tree      {tree.Body.NodeType}  -> {tree.Body}");
#endregion

#region array-contains
string[] shortlist = ["Toyota", "Honda"];
Expression<Func<Quote, bool>> inList = q => shortlist.Contains(q.Vehicle.Make);
var call = (MethodCallExpression)inList.Body;
Console.WriteLine($"binds to  {call.Method.DeclaringType!.Name}.{call.Method.Name}");
#endregion

#region generate-filter
var minPremium = 15_000m;
var filter = DynamoFilter.From<Quote>(q =>
    q.Coverage == CoverageClass.Class1
    && q.Total.Amount >= minPremium
    && q.Vehicle.Make.StartsWith("To"));
Console.WriteLine($"FilterExpression  {filter.Expression}");
Console.WriteLine($"Names             {string.Join(", ", filter.Names)}");
Console.WriteLine($"Values            {string.Join(", ", filter.Values)}");
#endregion
#endregion
