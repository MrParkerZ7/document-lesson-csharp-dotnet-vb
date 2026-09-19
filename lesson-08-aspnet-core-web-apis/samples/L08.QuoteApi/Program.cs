using System.Text.Json.Serialization;
using L08.QuoteApi.CrossCutting;
using L08.QuoteApi.Notifications;
using L08.QuoteApi.Partners;
using L08.QuoteApi.Quotes;
using MotorQuote.Rating;

#region services
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<PartnerExceptionHandler>();
builder.Services.AddValidation();                        // new in .NET 10
builder.Services.AddOpenApi();
builder.Services.AddHealthChecks().AddCheck<PartnerHealthCheck>("partners");
builder.Services.ConfigureHttpJsonOptions(o =>           // minimal APIs
    o.SerializerOptions.Converters.Add(new JsonStringEnumConverter()));
builder.Services.AddControllers().AddJsonOptions(o =>    // controllers: separate options
    o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));

builder.Services.AddQuoteModule(builder.Configuration);  // C# module
builder.Services.AddMotorRating(builder.Configuration);  // VB module
builder.Services.AddPartnerClients(builder.Configuration);
builder.Services.AddNotifications();
builder.Services.AddQuoteRateLimits();
builder.Services.AddOutputCache();
builder.Services.AddCors(cors => cors.AddPolicy("broker-portal",
    policy => policy.WithOrigins("https://brokers.example").AllowAnyHeader()));
#endregion

#region pipeline
var app = builder.Build();

app.UseExceptionHandler();     // exceptions -> ProblemDetails
app.UseStatusCodePages();      // bodiless 4xx/5xx too
app.UseCors("broker-portal");  // after the implicit routing
app.UseRateLimiter();
app.UseOutputCache();

if (!app.Environment.IsProduction())
    app.MapOpenApi();          // GET /openapi/v1.json
app.MapHealthChecks("/health");
app.MapControllers();          // PartnersController
app.MapQuotes();               // minimal API group, C#
app.MapTariff().CacheOutput(); // minimal API group, VB

app.Run();
#endregion
