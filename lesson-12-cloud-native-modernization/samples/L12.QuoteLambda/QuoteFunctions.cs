using Amazon.Lambda.Annotations;
using Amazon.Lambda.Annotations.APIGateway;
using Amazon.Lambda.Core;
using L12.RatingVb;

[assembly: LambdaSerializer(
    typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace L12.QuoteLambda;

/// <summary>
/// Lambda Annotations: the source generator writes QuoteFunctions_CreateQuote_Generated, which maps
/// the HTTP API event to these parameters. Handler string:
/// L12.QuoteLambda::L12.QuoteLambda.QuoteFunctions_CreateQuote_Generated::CreateQuote
/// </summary>
public sealed class QuoteFunctions(IQuoteStore store)
{
    #region annotations
    [LambdaFunction(MemorySize = 1024, Timeout = 10)]
    [HttpApi(LambdaHttpMethod.Post, "/quotes")]
    public IHttpResult CreateQuote(
        [FromBody] QuoteRequest request, ILambdaContext context)
    {
        if (!Enum.TryParse(request.Coverage, true,
                out CoverageClass coverage))
            return HttpResults.BadRequest("unknown coverage");

        var p = Rating.Quote(coverage, request.SumInsured,
            request.DriverAge, request.ClaimsLast5Years,
            request.Commercial);
        var quote = store.Save(p);

        context.Logger.LogInformation("Quoted {QuoteId}: {Total}",
            quote.QuoteId, p.Total);
        return HttpResults.Created(
            $"/quotes/{quote.QuoteId}", quote);
    }
    #endregion

    #region get
    [LambdaFunction]
    [HttpApi(LambdaHttpMethod.Get, "/quotes/{id}")]
    public IHttpResult GetQuote(string id) =>
        store.Find(id) is { } quote
            ? HttpResults.Ok(quote)
            : HttpResults.NotFound();
    #endregion
}
