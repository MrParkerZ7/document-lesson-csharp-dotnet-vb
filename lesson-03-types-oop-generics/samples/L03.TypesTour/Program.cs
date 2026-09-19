using System.Collections;
using System.Globalization;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using L03.Domain;
using L03.Reports;

// Every number printed here is quoted in the lesson-03 PDF. No clock, no randomness,
// and one culture, so the output is the same on every machine.
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
Console.WriteLine($"L03.TypesTour on {RuntimeInformation.FrameworkDescription}");

#region copy-trap
var tallies = new List<Tally> { new() };
var copy = tallies[0];        // Tally is a struct: this is a COPY
copy.Add();
Console.WriteLine($"copy       copy.Count={copy.Count} list[0].Count={tallies[0].Count}");

var blank = default(Money);   // no constructor ran
Console.WriteLine($"default    default(Money).Currency is null: {blank.Currency is null}");
#endregion

Console.WriteLine($"size       Money={Unsafe.SizeOf<Money>()} bytes, QuoteId={Unsafe.SizeOf<QuoteId>()}, "
                  + $"CoverageClass={Unsafe.SizeOf<CoverageClass>()}");

#region allocations
const int N = 1_000;
var structArray = Allocated(() =>
{
    var a = new Money[N];                 // one array, values inline
    for (var i = 0; i < N; i++) a[i] = Money.Thb(i);
    Keep.Sink = a;
});
var classArray = Allocated(() =>
{
    var a = new MoneyClass[N];            // one array + N objects
    for (var i = 0; i < N; i++) a[i] = new MoneyClass(i, "THB");
    Keep.Sink = a;
});
var boxedArray = Allocated(() =>
{
    var a = new object[N];                // one array + N boxes
    for (var i = 0; i < N; i++) a[i] = Money.Thb(i);
    Keep.Sink = a;
});
#endregion
Console.WriteLine($"alloc      Money[]={structArray:N0} MoneyClass[]={classArray:N0} object[] of Money={boxedArray:N0} bytes");

Console.WriteLine($"generated  class={IlMethods(typeof(MoneyClass))} struct={IlMethods(typeof(MoneyStruct))} "
                  + $"record={IlMethods(typeof(MoneyRecord))} record struct={IlMethods(typeof(MoneyRecordStruct))} methods");

var young = Samples.YoungDriver();
Console.WriteLine("dispatch   asBase.Factor / asBase.Describe / asDerived.Describe:");

#region dispatch-demo
RatingRule asBase = new YoungDriverLoading();
var asDerived = (YoungDriverLoading)asBase;

Console.WriteLine(asBase.Factor(young));      // virtual
Console.WriteLine(asBase.Describe(young));    // static type
Console.WriteLine(asDerived.Describe(young)); // hiding one
#endregion

IRateTable table = new StandardRateTable();
Console.WriteLine($"dim        IRateTable.BasePremium = {table.BasePremium(young)}");

var ids = Ids.ParseAll<QuoteId>("Q-000042", "Q-000043");
Console.WriteLine($"reified    {Ids.Describe<QuoteId>()} | {Ids.Describe<PolicyNumber>()} | parsed {string.Join(", ", ids)}");

var listOfInt = Allocated(() =>
{
    var list = new List<int>(N);
    for (var i = 0; i < N; i++) list.Add(i);
    Keep.Sink = list;
});
var listOfObject = Allocated(() =>
{
    var list = new List<object>(N);
    for (var i = 0; i < N; i++) list.Add(i);  // boxes every int
    Keep.Sink = list;
});
var arrayList = Allocated(() =>
{
    var list = new ArrayList(N);             // the .NET 1.x collection
    for (var i = 0; i < N; i++) list.Add(i);  // boxes every int too
    Keep.Sink = list;
});
Console.WriteLine($"generics   List<int>={listOfInt:N0} List<object>={listOfObject:N0} ArrayList={arrayList:N0} bytes for {N:N0} ints");

Counter<QuoteId>.Hits++;
Counter<QuoteId>.Hits++;
Counter<PolicyNumber>.Hits++;
Console.WriteLine($"statics    Counter<QuoteId>.Hits={Counter<QuoteId>.Hits} Counter<PolicyNumber>.Hits={Counter<PolicyNumber>.Hits}");

var sumDecimal = Totals.Sum([1.25m, 2.25m, 3.00m], 0m);
var sumMoney = Totals.Sum([Money.Thb(1_000m), Money.Thb(500m)], Money.Thb(0m));
Console.WriteLine($"math       Sum<decimal>={sumDecimal} Sum<Money>={sumMoney}");

var card = (IReportRenderer<QuoteReport>)new SummaryCardRenderer(); // `in` makes this legal
var report = new QuoteReport(Samples.StartDate, []);
Console.WriteLine($"variance   card renderer as IReportRenderer<QuoteReport>: {card.Render(report).Replace(Environment.NewLine, " ")}");

Console.WriteLine($"extension  Class2Plus.Code={CoverageClass.Class2Plus.Code} "
                  + $"Class3.CoversOwnDamage={CoverageClass.Class3.CoversOwnDamage} FromCode(\"3+\")={CoverageClass.FromCode("3+")}");
Console.WriteLine($"enum       (CoverageClass)42 is defined: {Enum.IsDefined((CoverageClass)42)}");
Console.WriteLine("equality   five==alsoFive / Equals / vinA==vinB / set.Contains / broken.Contains:");

#region boxing-equality
object five = 5, alsoFive = 5;
Console.WriteLine(five == alsoFive);        // False: two boxes
Console.WriteLine(five.Equals(alsoFive));   // True: Int32.Equals

var vinA = new Vin("MR0FZ22G801234567");
var vinB = new Vin("mr0fz22g801234567");
Console.WriteLine(vinA == vinB);            // True: overloaded ==
Console.WriteLine(new HashSet<Vin> { vinA }.Contains(vinB)); // True

var broken = new HashSet<BrokenVin> { new("MR0FZ22G801234567") };
Console.WriteLine(broken.Contains(new("mr0fz22g801234567"))); // False
#endregion

var quote = Samples.Quote(42, young);
var policy = quote.Accept(new PolicyNumber(7));
string expire;
try
{
    quote.Expire();
    expire = "allowed";
}
catch (InvalidOperationException e)
{
    expire = $"throws ({e.Message})";
}
Console.WriteLine($"premium    net {quote.Premium.Net}, stamp duty {quote.Premium.StampDuty}, VAT {quote.Premium.Vat}, total {quote.Premium.Total}");
Console.WriteLine($"status     {quote.Id} {quote.Status} -> policy {policy.Number}; Expire() now {expire}");

static long Allocated(Action action)
{
    var before = GC.GetAllocatedBytesForCurrentThread();
    action();
    return GC.GetAllocatedBytesForCurrentThread() - before;
}

static int IlMethods(Type type)
{
    const BindingFlags all = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance
                             | BindingFlags.Static | BindingFlags.DeclaredOnly;
    return type.GetMethods(all).Length + type.GetConstructors(all).Length;
}

#region one-liners
// two data members each; count what the compiler adds
public sealed class MoneyClass(decimal amount, string currency)
{
    public decimal Amount { get; } = amount;
    public string Currency { get; } = currency;
}

public readonly struct MoneyStruct(decimal amount, string currency)
{
    public decimal Amount { get; } = amount;
    public string Currency { get; } = currency;
}

public sealed record MoneyRecord(decimal Amount, string Currency);

public readonly record struct MoneyRecordStruct(decimal Amount, string Currency);
#endregion

/// <summary>A mutable struct — the shape the copy trap needs.</summary>
public struct Tally
{
    public int Count { get; private set; }
    public void Add() => Count++;
}

public static class Keep
{
    public static object? Sink;
}

public static class Counter<T>
{
    public static int Hits;
}
