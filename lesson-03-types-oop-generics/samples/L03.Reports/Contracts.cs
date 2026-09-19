using L03.Domain;

namespace L03.Reports;

#region report-model
public abstract record Report(string Title, DateOnly AsOf);

public sealed record QuoteLine(
    QuoteId Id, string Vehicle, CoverageClass Coverage, Money Total);

public sealed record QuoteReport(
    DateOnly AsOf, IReadOnlyList<QuoteLine> Lines)
    : Report("Motor quotes", AsOf);
#endregion

#region variance
// `in` = contravariant: a renderer for ANY Report can
// stand in where a QuoteReport renderer is expected
public interface IReportRenderer<in TReport>
    where TReport : Report
{
    string Format { get; }
    string Render(TReport report);
}

// `out` = covariant: a source of QuoteReports
// is also a source of Reports
public interface IReportSource<out TReport>
    where TReport : Report
{
    TReport Load();
}
#endregion

/// <summary>Builds a report from quotes: the one IReportSource in the samples.</summary>
public sealed class QuoteReportSource(IEnumerable<Quote> quotes, DateOnly asOf)
    : IReportSource<QuoteReport>
{
    public QuoteReport Load() => new(
        asOf,
        quotes.Select(q => new QuoteLine(
                q.Id,
                $"{q.Request.Vehicle.Make} {q.Request.Vehicle.Model}",
                q.Request.Coverage,
                q.Premium.Total))
            .ToList());
}
