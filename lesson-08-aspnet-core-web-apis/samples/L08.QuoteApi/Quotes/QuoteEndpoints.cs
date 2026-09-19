using L08.QuoteApi.CrossCutting;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace L08.QuoteApi.Quotes;

public static class QuoteEndpoints
{
    #region map-quotes
    public static RouteGroupBuilder MapQuotes(
        this IEndpointRouteBuilder app)
    {
        var quotes = app.MapGroup("/quotes").WithTags("Quotes");

        quotes.MapPost("/", Create)
            .AddEndpointFilter<StartDateFilter>()
            .RequireRateLimiting(RateLimits.QuoteWrites)
            .ProducesValidationProblem()        // 400
            .ProducesProblem(Status429TooManyRequests);

        quotes.MapGet("/{id:guid}", Get);
        quotes.MapPost("/{id:guid}/accept", Accept);
        return quotes;
    }
    #endregion

    #region handlers
    private static Created<QuoteResponse> Create(QuoteRequest request, QuoteService service)
    {
        var quote = service.Create(request);
        return TypedResults.Created($"/quotes/{quote.QuoteId}", quote);
    }

    private static Results<Ok<QuoteResponse>, NotFound> Get(Guid id, QuoteService service) =>
        service.Find(id) is { } quote ? TypedResults.Ok(quote) : TypedResults.NotFound();

    private static Results<Ok<PolicyResponse>, NotFound, Conflict<ProblemDetails>> Accept(
        Guid id, QuoteService service) => service.Accept(id) switch
    {
        { Outcome: AcceptOutcome.Accepted, Policy: { } policy } => TypedResults.Ok(policy),
        { Outcome: AcceptOutcome.NotFound } => TypedResults.NotFound(),
        var failed => TypedResults.Conflict(new ProblemDetails
        {
            Title = "Quote cannot be accepted",
            Detail = $"The quote is {failed.Outcome}.",
            Status = StatusCodes.Status409Conflict,
        }),
    };
    #endregion
}

#region endpoint-filter
/// <summary>A rule DataAnnotations cannot express: it needs the clock from DI.</summary>
public sealed class StartDateFilter(TimeProvider clock) : IEndpointFilter
{
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context, EndpointFilterDelegate next)
    {
        var request = context.GetArgument<QuoteRequest>(0);
        var today = DateOnly.FromDateTime(clock.GetUtcNow().UtcDateTime);

        if (request.StartDate < today || request.StartDate > today.AddDays(60))
        {
            return TypedResults.ValidationProblem(new Dictionary<string, string[]>
            {
                ["StartDate"] = ["Must be between today and 60 days ahead."],
            });
        }
        return await next(context);   // filters run in order before next, reverse after
    }
}
#endregion
