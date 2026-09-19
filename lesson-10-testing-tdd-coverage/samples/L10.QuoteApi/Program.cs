using System.Text.Json.Serialization;
using L10.Pricing;

var builder = WebApplication.CreateBuilder(args);

#region services
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<IQuoteRepository, InMemoryQuoteRepository>();
builder.Services.AddSingleton<PremiumCalculator>();
builder.Services.AddSingleton<QuoteService>();
builder.Services.AddProblemDetails();
builder.Services.ConfigureHttpJsonOptions(options =>
    options.SerializerOptions.Converters.Add(new JsonStringEnumConverter()));
#endregion

var app = builder.Build();

#region endpoints
app.MapPost("/quotes", async (QuoteRequest request, QuoteService quotes, CancellationToken ct) =>
{
    var quote = await quotes.CreateAsync(request, ct);
    return Results.Created($"/quotes/{quote.Id}", quote);
});

app.MapGet("/quotes/{id:guid}", async (Guid id, IQuoteRepository repo, CancellationToken ct) =>
    await repo.FindAsync(id, ct) is { } quote ? Results.Ok(quote) : Results.NotFound());

app.MapPost("/quotes/{id:guid}/accept", async (Guid id, QuoteService quotes, CancellationToken ct) =>
{
    var quote = await quotes.AcceptAsync(id, ct);
    return quote.Status == QuoteStatus.Expired
        ? Results.Problem(statusCode: StatusCodes.Status409Conflict, title: "Quote expired")
        : Results.Ok(quote);
});
#endregion

app.Run();
