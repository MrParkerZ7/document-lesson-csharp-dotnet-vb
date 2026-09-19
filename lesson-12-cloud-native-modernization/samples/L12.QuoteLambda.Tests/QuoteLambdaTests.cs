using System.Globalization;
using System.Text.Json;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.TestUtilities;
using L12.QuoteLambdaVb;
using L12.RatingVb;

namespace L12.QuoteLambda.Tests;

public class RatingRulesTests
{
    // Hand-calculated from the ILLUSTRATIVE rules in L12.RatingVb/Rating.vb.
    [Theory]
    [InlineData(CoverageClass.Class1, 800_000, 30, 0, false, "16243.11")]
    [InlineData(CoverageClass.Class1, 800_000, 22, 1, false, "23823.23")]
    [InlineData(CoverageClass.Class3, 100_000, 40, 0, true, "667.12")]
    public void Totals_follow_the_illustrative_rules(
        CoverageClass coverage, int sumInsured, int age, int claims, bool commercial, string total)
    {
        var p = Rating.Quote(coverage, sumInsured, age, claims, commercial);
        Assert.Equal(decimal.Parse(total, CultureInfo.InvariantCulture), p.Total);
    }
}

public class QuoteFunctionsTests
{
    readonly InMemoryQuoteStore store = new();
    readonly TestLambdaContext context = new();

    static QuoteRequest Request(string coverage) => new(coverage, 800_000m, 30, 0, false);

    [Fact]
    public void Create_returns_201()
    {
        var result = new QuoteFunctions(store).CreateQuote(Request("Class1"), context);
        Assert.Equal(201, (int)result.StatusCode);
    }

    [Fact]
    public void Unknown_coverage_returns_400()
    {
        var result = new QuoteFunctions(store).CreateQuote(Request("Class9"), context);
        Assert.Equal(400, (int)result.StatusCode);
    }

    [Fact]
    public void A_saved_quote_reads_back_and_an_unknown_id_is_404()
    {
        var saved = store.Save(Rating.Quote(CoverageClass.Class3, 100_000m, 40, 0, false));
        var functions = new QuoteFunctions(store);
        Assert.Equal(200, (int)functions.GetQuote(saved.QuoteId).StatusCode);
        Assert.Equal(404, (int)functions.GetQuote("no-such-quote").StatusCode);
    }
}

public class GeneratedWrapperTests
{
    #region wrapper-test
    [Fact]
    public void The_generated_handler_maps_an_http_api_event()
    {
        // the class Lambda actually instantiates: written by the Annotations source generator
        var handler = new QuoteFunctions_CreateQuote_Generated();
        var request = new APIGatewayHttpApiV2ProxyRequest
        {
            Body = """{"coverage":"Class1","sumInsured":800000,"driverAge":30}""",
        };

        using var stream = handler.CreateQuote(request, new TestLambdaContext());
        var response = JsonSerializer.Deserialize<APIGatewayHttpApiV2ProxyResponse>(stream);

        Assert.Equal(201, response!.StatusCode);
        Assert.StartsWith("/quotes/", response.Headers["location"]);
    }
    #endregion

    [Fact]
    public void A_body_that_is_not_json_is_rejected_by_the_generated_code_with_400()
    {
        var handler = new QuoteFunctions_CreateQuote_Generated();
        var request = new APIGatewayHttpApiV2ProxyRequest { Body = "not json" };

        using var stream = handler.CreateQuote(request, new TestLambdaContext());
        var response = JsonSerializer.Deserialize<APIGatewayHttpApiV2ProxyResponse>(stream);

        Assert.Equal(400, response!.StatusCode);
    }
}

public class HandlerParityTests
{
    [Theory]
    [InlineData("""{"coverage":"Class1","sumInsured":800000,"driverAge":30,"claimsLast5Years":0,"commercial":false}""")]
    [InlineData("""{"coverage":"class3plus","sumInsured":350000,"driverAge":21,"claimsLast5Years":2,"commercial":true}""")]
    [InlineData("""{"coverage":"Class9","sumInsured":1,"driverAge":40,"claimsLast5Years":0,"commercial":false}""")]
    public void The_csharp_and_vb_handlers_answer_identically(string body)
    {
        var request = new APIGatewayHttpApiV2ProxyRequest { Body = body };
        var cs = new RawQuoteHandler().FunctionHandler(request, new TestLambdaContext());
        var vb = new QuoteHandler().FunctionHandler(request, new TestLambdaContext());
        Assert.Equal(cs.StatusCode, vb.StatusCode);
        Assert.Equal(cs.Body, vb.Body);
    }
}
