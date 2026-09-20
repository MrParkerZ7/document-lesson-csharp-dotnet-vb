using System.Globalization;
using System.Text.Json;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.TestUtilities;
using L12.QuoteLambdaVb;
using L12.RatingVb;

namespace L12.QuoteLambda.Tests;

public class RatingRulesTests
{
    // Worked out separately from the track's ILLUSTRATIVE tariff (curriculum, "Canonical tariff").
    // Row 1 is that tariff's worked example: 8,316.00 net + 33.26 stamp duty + 584.45 VAT.
    [Theory]
    [InlineData(CoverageClass.Class1, 550_000, 23, 4, 0, false, 1500, "8933.71")]
    [InlineData(CoverageClass.Class1, 800_000, 30, 10, 0, false, 1500, "9023.95")]
    [InlineData(CoverageClass.Class2Plus, 1_200_000, 45, 15, 1, false, 2000, "17016.60")]
    [InlineData(CoverageClass.Class3Plus, 350_000, 21, 3, 2, true, 3500, "6091.17")]
    [InlineData(CoverageClass.Class3, 100_000, 40, 20, 0, true, 1600, "268.57")]
    public void Totals_follow_the_illustrative_tariff(
        CoverageClass coverage, int sumInsured, int age, int licenceYears,
        int claims, bool commercial, int engineCc, string total)
    {
        var p = Rating.Quote(coverage, sumInsured, age, licenceYears, claims, commercial, engineCc);
        Assert.Equal(decimal.Parse(total, CultureInfo.InvariantCulture), p.Total);
    }

    [Fact]
    public void Three_claims_decline_the_quote()
    {
        Assert.Throws<QuoteDeclinedException>(
            () => Rating.Quote(CoverageClass.Class1, 800_000, 30, 10, 3, false, 1500));
    }
}

public class QuoteFunctionsTests
{
    readonly InMemoryQuoteStore store = new();
    readonly TestLambdaContext context = new();

    static QuoteRequest Request(string coverage, int claims = 0) =>
        new(coverage, 800_000m, 30, 10, claims, false, 1500);

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
    public void Three_claims_return_422()
    {
        var result = new QuoteFunctions(store).CreateQuote(Request("Class1", claims: 3), context);
        Assert.Equal(422, (int)result.StatusCode);
    }

    [Fact]
    public void A_saved_quote_reads_back_and_an_unknown_id_is_404()
    {
        var saved = store.Save(Rating.Quote(CoverageClass.Class3, 100_000m, 40, 20, 0, false, 1500));
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
    [InlineData("""{"coverage":"Class1","sumInsured":550000,"driverAge":23,"licenceYears":4,"claimsLast5Years":0,"commercial":false,"engineCc":1500}""")]
    [InlineData("""{"coverage":"class3plus","sumInsured":350000,"driverAge":21,"licenceYears":3,"claimsLast5Years":2,"commercial":true,"engineCc":3500}""")]
    [InlineData("""{"coverage":"Class9","sumInsured":1,"driverAge":40,"licenceYears":20,"claimsLast5Years":0,"commercial":false,"engineCc":1500}""")]
    [InlineData("""{"coverage":"Class1","sumInsured":800000,"driverAge":30,"licenceYears":10,"claimsLast5Years":3,"commercial":false,"engineCc":1500}""")]
    public void The_csharp_and_vb_handlers_answer_identically(string body)
    {
        var request = new APIGatewayHttpApiV2ProxyRequest { Body = body };
        var cs = new RawQuoteHandler().FunctionHandler(request, new TestLambdaContext());
        var vb = new QuoteHandler().FunctionHandler(request, new TestLambdaContext());
        Assert.Equal(cs.StatusCode, vb.StatusCode);
        Assert.Equal(cs.Body, vb.Body);
    }
}
