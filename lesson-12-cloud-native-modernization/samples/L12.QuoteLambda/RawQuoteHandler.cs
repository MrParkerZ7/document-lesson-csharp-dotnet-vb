using System.Text.Json;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using L12.RatingVb;

namespace L12.QuoteLambda;

/// <summary>
/// The same function without Annotations: the handler receives the raw HTTP API v2 event.
/// Handler string: L12.QuoteLambda::L12.QuoteLambda.RawQuoteHandler::FunctionHandler
/// </summary>
public sealed class RawQuoteHandler
{
    #region raw-cs
    static readonly JsonSerializerOptions Json =
        JsonSerializerOptions.Web;

    public APIGatewayHttpApiV2ProxyResponse FunctionHandler(
        APIGatewayHttpApiV2ProxyRequest request,
        ILambdaContext context)
    {
        var input = JsonSerializer.Deserialize<QuoteRequest>(
            request.Body ?? "{}", Json);
        if (input is null ||
            !Enum.TryParse(input.Coverage, true,
                out CoverageClass coverage))
            return Respond(400, "\"unknown coverage\"");

        var p = Rating.Quote(coverage, input.SumInsured,
            input.DriverAge, input.ClaimsLast5Years,
            input.Commercial);
        return Respond(201, JsonSerializer.Serialize(p, Json));
    }

    static APIGatewayHttpApiV2ProxyResponse Respond(
        int status, string body) => new()
    {
        StatusCode = status,
        Body = body,
        Headers = new Dictionary<string, string>
            { ["Content-Type"] = "application/json" },
    };
    #endregion
}
