using System.Collections.Frozen;
using System.Collections.Immutable;
using System.Globalization;
using L04.QuoteData;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
var quotes = QuoteBook.Generate();

Console.WriteLine("1. collection expressions");
#region collection-expressions
int[] claimFreeYears = [0, 1, 2, 3, 4, 5];
List<string> makes = ["Toyota", "Honda"];
string[] shortlist = [.. makes, "Isuzu", .. makes.Take(1)];
IReadOnlyList<string> channels = ["SMS", "Email", "LINE"];

Console.WriteLine($"  shortlist  {string.Join(", ", shortlist)}");
Console.WriteLine($"  years      {claimFreeYears.Length} elements");
Console.WriteLine($"  channels is a List<string>? {channels is List<string>}");
Console.WriteLine($"  channels type {channels.GetType().Name}");
#endregion

Console.WriteLine("2. read-only is not immutable");
#region readonly-views
var classes = new List<string> { "Class1", "Class3" };
IReadOnlyList<string> view = classes; // same object
var wrapper = classes.AsReadOnly();   // live wrapper
var snapshot = classes.ToImmutableArray(); // copy
var frozen = classes.ToFrozenSet();   // copy, fast reads

classes.Add("Class2Plus");
Console.WriteLine($"  view      {view.Count}");
Console.WriteLine($"  wrapper   {wrapper.Count}");
Console.WriteLine($"  snapshot  {snapshot.Length}");
Console.WriteLine($"  frozen    {frozen.Count}");

((List<string>)view).Remove("Class1"); // compiles!
Console.WriteLine($"  after cast + Remove  {view.Count}");
#endregion

Console.WriteLine("3. frozen lookup table");
#region frozen
// built once at start-up, read on every quote: pay at build time, save at read time
FrozenDictionary<CoverageClass, decimal> baseRates =
    new Dictionary<CoverageClass, decimal>
    {
        [CoverageClass.Class1] = 0.021m,
        [CoverageClass.Class2Plus] = 0.012m,
        [CoverageClass.Class3Plus] = 0.009m,
        [CoverageClass.Class3] = 0.004m,
    }.ToFrozenDictionary();

Console.WriteLine($"  Class2Plus base rate  {baseRates[CoverageClass.Class2Plus]}");
Console.WriteLine($"  classes with a rate   {baseRates.Count}");
#endregion

Console.WriteLine("4. deferred execution");
#region deferred
var calls = 0;
bool Counted(Quote q) { calls++; return q.IsAccepted; }

var accepted = quotes.Where(Counted); // method group -> Func
Console.WriteLine($"  declared          calls = {calls}");

var count = accepted.Count();      // pass 1: all quotes
var first = accepted.First();      // pass 2: stops early
foreach (var item in accepted) { } // pass 3: all again
Console.WriteLine($"  three passes      calls = {calls}");

calls = 0;
var list = accepted.ToList();      // one pass, then data
_ = (list.Count, list[0]);
foreach (var item in list) { }
Console.WriteLine($"  ToList + 3 reads  calls = {calls}");
#endregion
Console.WriteLine($"  ({count} accepted, first {first.QuoteId})");

#region captured
var threshold = 4_000m;
var pricey = quotes.Where(q => q.Total.Amount > threshold);
Console.WriteLine($"  > threshold, run 1  {pricey.Count()}");

threshold = 6_000m; // the lambda captured the VARIABLE
Console.WriteLine($"  > threshold, run 2  {pricey.Count()}");
#endregion

#region modified
var queue = new List<string> { "Q-0001", "Q-0002" };
try
{
    foreach (var id in queue)
        if (id == "Q-0001") queue.Add("Q-0003");
}
catch (InvalidOperationException ex)
{
    Console.WriteLine($"  {ex.GetType().Name}");
}
#endregion

Console.WriteLine("5. iterators");
#region yield
var renewals = Renewals(new DateOnly(2026, 11, 1));
Console.WriteLine("  iterator created");
foreach (var date in renewals.Take(3))
    Console.WriteLine($"  renewal {date:yyyy-MM-dd}");

static IEnumerable<DateOnly> Renewals(DateOnly inception)
{
    Console.WriteLine("  (iterator body starts)");
    for (var d = inception; ; d = d.AddYears(1))
        yield return d;
}
#endregion

Console.WriteLine("6. closures");
#region closures
var byFor = new List<Func<int>>();
for (var i = 0; i < 3; i++)
    byFor.Add(() => i);            // ONE i, shared by all

var byForeach = new List<Func<int>>();
foreach (var year in new[] { 0, 1, 2 })
    byForeach.Add(() => year);     // a fresh year per pass

Console.WriteLine($"  for      {Run(byFor)}");
Console.WriteLine($"  foreach  {Run(byForeach)}");

static string Run(List<Func<int>> fs) =>
    string.Join(",", fs.Select(f => f()));
#endregion

Console.WriteLine("7. with copies are shallow");
#region with-shallow
var draft = new DraftQuote("Q-0001", Notes: ["created"]);
var renewal = draft with { QuoteId = "Q-0002" };
renewal.Notes.Add("renewal");   // the SAME List<string>

var notes = string.Join(" | ", draft.Notes);
var same = ReferenceEquals(draft.Notes, renewal.Notes);
Console.WriteLine($"  draft notes  {notes}");
Console.WriteLine($"  same list?   {same}");
#endregion

Console.WriteLine("8. delegate types are nominal");
#region delegate-types
Func<Quote, bool> isAccepted = q => q.IsAccepted;
// Predicate<Quote> p = isAccepted;  // error CS0029
Predicate<Quote> asPredicate = isAccepted.Invoke;

var counted = quotes.Count(isAccepted);
var found = quotes.ToList().FindAll(asPredicate).Count;
Console.WriteLine($"  Count {counted}, FindAll {found}");
#endregion

Console.WriteLine("9. a key that is not there");
#region missing-key
var byMake = quotes.ToLookup(q => q.Vehicle.Make);
var soldByMake = quotes.CountBy(q => q.Vehicle.Make)
    .ToDictionary();

var teslas = byMake["Tesla"].Count();
Console.WriteLine($"  lookup     {teslas} Tesla quotes");
try { _ = soldByMake["Tesla"]; }
catch (KeyNotFoundException ex)
{
    Console.WriteLine($"  dictionary {ex.GetType().Name}");
}
#endregion

record DraftQuote(string QuoteId, List<string> Notes);
