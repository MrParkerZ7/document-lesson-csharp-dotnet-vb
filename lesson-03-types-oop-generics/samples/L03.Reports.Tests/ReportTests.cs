using System.Text.Json;
using L03.Domain;

namespace L03.Reports.Tests;

public class ReportServiceTests
{
    private static QuoteReport Report() => new QuoteReportSource(
        [Samples.Quote(42, Samples.YoungDriver()), Samples.Quote(43, Samples.CommercialPickup())],
        Samples.StartDate).Load();

    private static ReportService<QuoteReport> Service() =>
        new([new TextTableRenderer(), new CsvRenderer(), new JsonRenderer(), new SummaryCardRenderer()]);

    [Fact]
    public void Csv_has_a_header_and_one_row_per_quote()
    {
        const string expected = """
            quote,vehicle,class,total_thb
            Q-000042,Toyota Yaris,1,8527.63
            Q-000043,Isuzu D-Max,2+,10790.07
            """;
        Assert.Equal(expected.ReplaceLineEndings(), Service().Render(Report(), "csv").ReplaceLineEndings());
    }

    [Fact]
    public void The_text_table_totals_every_quote() =>
        Assert.EndsWith("2 quotes, total 19,317.70 THB", Service().Render(Report(), "text"));

    [Fact]
    public void Json_is_valid_and_carries_every_line()
    {
        using var json = JsonDocument.Parse(Service().Render(Report(), "json"));
        var lines = json.RootElement.GetProperty("lines");
        Assert.Equal(2, lines.GetArrayLength());
        Assert.Equal(8_527.63m, lines[0].GetProperty("total").GetDecimal());
        Assert.Equal("2026-10-01", json.RootElement.GetProperty("asOf").GetString());
    }

    [Theory]
    [InlineData("csv")]
    [InlineData("CSV")]
    [InlineData("Csv")]
    public void Formats_match_case_insensitively(string format) =>
        Assert.StartsWith("quote,vehicle", Service().Render(Report(), format));

    [Fact]
    public void An_unknown_format_is_rejected() =>
        Assert.Throws<NotSupportedException>(() => Service().Render(Report(), "pdf"));

    [Fact]
    public void Every_registered_format_is_listed() =>
        Assert.Equal(["card", "csv", "json", "text"], Service().Formats.Order(StringComparer.Ordinal));
}

public class VarianceTests
{
    private static readonly QuoteReport Empty = new(Samples.StartDate, []);

    [Fact]
    public void A_renderer_for_any_report_is_accepted_for_quote_reports()
    {
        IReportRenderer<QuoteReport> renderer = new SummaryCardRenderer(); // in
        Assert.EndsWith("(QuoteReport)", renderer.Render(Empty));
    }

    [Fact]
    public void A_source_of_quote_reports_is_a_source_of_reports()
    {
        IReportSource<Report> source = new QuoteReportSource([], Samples.StartDate); // out
        Assert.IsType<QuoteReport>(source.Load());
    }

    [Fact]
    public void The_header_hook_can_be_replaced_but_the_skeleton_cannot()
    {
        var csv = new CsvRenderer().Render(Empty);
        Assert.Equal("quote,vehicle,class,total_thb", csv);
        Assert.StartsWith("# Motor quotes - 2026-10-01", new TextTableRenderer().Render(Empty));
    }
}

public class RecordEqualityTests
{
    private static readonly QuoteLine Line =
        new(new QuoteId(1), "Toyota Yaris", CoverageClass.Class1, Money.Thb(1m));

    [Fact]
    public void Reports_over_the_same_list_instance_are_equal()
    {
        List<QuoteLine> lines = [Line];
        Assert.Equal(new QuoteReport(Samples.StartDate, lines), new QuoteReport(Samples.StartDate, lines));
    }

    [Fact]
    public void Reports_over_equal_but_separate_lists_are_not_equal()
    {
        var a = new QuoteReport(Samples.StartDate, [Line]);
        var b = new QuoteReport(Samples.StartDate, [Line]);
        Assert.NotEqual(a, b);
        Assert.Equal(a.Lines, b.Lines);
    }

    [Fact]
    public void Equality_includes_the_runtime_type()
    {
        Report a = new QuoteReport(Samples.StartDate, []);
        Report b = new OtherReport(Samples.StartDate);
        Assert.Equal("Motor quotes", a.Title);
        Assert.NotEqual(a, b);
    }

    private sealed record OtherReport(DateOnly AsOf) : Report("Motor quotes", AsOf);
}
