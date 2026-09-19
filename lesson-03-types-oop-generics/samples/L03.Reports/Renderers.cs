using System.Globalization;
using System.Text;
using System.Text.Json;
using L03.Domain;
using static System.FormattableString;

namespace L03.Reports;

#region renderer-base
public abstract class ReportRenderer<TReport> : IReportRenderer<TReport>
    where TReport : Report
{
    public abstract string Format { get; }

    // not virtual: the skeleton is fixed (template method)
    public string Render(TReport report)
    {
        var text = new StringBuilder();
        WriteHeader(text, report);
        WriteBody(text, report);
        return text.ToString().TrimEnd();
    }

    // virtual: a hook with a default a subclass may replace
    protected virtual void WriteHeader(StringBuilder text, TReport report) =>
        text.AppendLine(Invariant($"# {report.Title} - {report.AsOf:yyyy-MM-dd}"));

    // abstract: every renderer must supply the body
    protected abstract void WriteBody(StringBuilder text, TReport report);
}
#endregion

#region csv-renderer
// the "Excel" format: one CSV row per quote line
public sealed class CsvRenderer : ReportRenderer<QuoteReport>
{
    private static readonly CultureInfo Inv =
        CultureInfo.InvariantCulture;

    public override string Format => "csv";

    protected override void WriteHeader(
        StringBuilder text, QuoteReport report) =>
        text.AppendLine("quote,vehicle,class,total_thb");

    protected override void WriteBody(
        StringBuilder text, QuoteReport report)
    {
        foreach (var q in report.Lines)
            text.AppendLine(string.Join(",",
                q.Id, q.Vehicle, q.Coverage.Code,
                q.Total.Amount.ToString(Inv)));
    }
}
#endregion

/// <summary>The "PDF" format: a fixed-width text table.</summary>
public sealed class TextTableRenderer : ReportRenderer<QuoteReport>
{
    public override string Format => "text";

    protected override void WriteBody(StringBuilder text, QuoteReport report)
    {
        foreach (var q in report.Lines)
            text.AppendLine(Invariant($"{q.Id,-9} {q.Vehicle,-14} class {q.Coverage.Code,-3} {q.Total,18}"));
        var total = Totals.Sum(report.Lines.Select(l => l.Total), Money.Thb(0m));
        text.AppendLine(Invariant($"{report.Lines.Count} quotes, total {total}"));
    }
}

/// <summary>The "JSON" format, through System.Text.Json.</summary>
public sealed class JsonRenderer : ReportRenderer<QuoteReport>
{
    public override string Format => "json";

    // JSON has no header line: override the hook with an empty body
    protected override void WriteHeader(StringBuilder text, QuoteReport report) { }

    protected override void WriteBody(StringBuilder text, QuoteReport report) =>
        text.Append(JsonSerializer.Serialize(new
        {
            title = report.Title,
            asOf = report.AsOf,
            lines = report.Lines.Select(l => new
            {
                id = l.Id.ToString(),
                vehicle = l.Vehicle,
                coverage = l.Coverage.Code,
                total = l.Total.Amount,
            }),
        }));
}

/// <summary>Renders ANY report as a one-line card: usable as IReportRenderer&lt;QuoteReport&gt; through `in`.</summary>
public sealed class SummaryCardRenderer : ReportRenderer<Report>
{
    public override string Format => "card";

    protected override void WriteBody(StringBuilder text, Report report) =>
        text.AppendLine($"({report.GetType().Name})");
}

#region strategy
// DI-friendly: the container passes every IReportRenderer<TReport> registration
public sealed class ReportService<TReport>(
    IEnumerable<IReportRenderer<TReport>> renderers)
    where TReport : Report
{
    private readonly Dictionary<string, IReportRenderer<TReport>>
        _byFormat = renderers.ToDictionary(
            r => r.Format, StringComparer.OrdinalIgnoreCase);

    public IEnumerable<string> Formats => _byFormat.Keys;

    public string Render(TReport report, string format) =>
        _byFormat.TryGetValue(format, out var renderer)
            ? renderer.Render(report)
            : throw new NotSupportedException($"format '{format}'");
}
#endregion
