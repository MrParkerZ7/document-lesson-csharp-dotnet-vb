using L08.QuoteApi.Notifications;
using Microsoft.Extensions.Options;
using MotorQuote.Rating;

namespace L08.QuoteApi.Quotes;

public readonly record struct AcceptResult(AcceptOutcome Outcome, PolicyResponse? Policy);

/// <summary>Scoped: one instance per HTTP request. Depends only on singletons.</summary>
public sealed class QuoteService(
    IQuoteStore store,
    PremiumCalculator calculator,          // implemented in Visual Basic
    PolicyNumbers policyNumbers,
    NotificationQueue notifications,
    TimeProvider clock,
    IOptions<QuoteOptions> options,
    ILogger<QuoteService> logger)
{
    public QuoteResponse Create(QuoteRequest request)
    {
        var input = new RatingInput(
            request.Coverage,
            request.Vehicle.SumInsured,
            AgeAt(request.Driver.DateOfBirth, request.StartDate),
            request.Driver.LicenceYears,
            request.Driver.ClaimsLast5Years,
            request.Vehicle.Use);

        var premium = calculator.Calculate(input);
        var now = clock.GetUtcNow();
        var quote = new Quote(Guid.CreateVersion7(now), request, premium,
            now.AddDays(options.Value.ValidityDays));
        store.Add(quote);
        return ToResponse(quote);
    }

    public QuoteResponse? Find(Guid id) => store.Find(id) is { } quote ? ToResponse(quote) : null;

    public AcceptResult Accept(Guid id)
    {
        if (store.Find(id) is not { } quote)
            return new(AcceptOutcome.NotFound, null);

        var outcome = quote.Accept(clock.GetUtcNow(), policyNumbers.Next);
        if (outcome != AcceptOutcome.Accepted)
            return new(outcome, null);

        var policy = new PolicyResponse(quote.PolicyNumber!, quote.Id,
            quote.Request.StartDate, quote.Request.StartDate.AddYears(1).AddDays(-1));
        // a bounded channel refuses work when it is full: never drop a notification silently
        if (!notifications.TryEnqueue(new QuoteAccepted(quote.Id, policy.PolicyNumber, quote.Request.NotifyVia)))
            logger.LogWarning("Notification queue full: policy {PolicyNumber} was not notified",
                policy.PolicyNumber);
        return new(outcome, policy);
    }

    private QuoteResponse ToResponse(Quote quote)
    {
        var p = quote.Premium;
        var currency = options.Value.Currency;
        return new QuoteResponse(quote.Id, quote.Status,
            new PremiumDto(new(p.BasePremium, currency), p.LoadingRate, p.DiscountRate,
                new(p.NetPremium, currency), new(p.StampDuty, currency), new(p.Vat, currency),
                new(p.Total, currency)),
            quote.ValidUntil);
    }

    private static int AgeAt(DateOnly dateOfBirth, DateOnly day)
    {
        var age = day.Year - dateOfBirth.Year;
        return dateOfBirth > day.AddYears(-age) ? age - 1 : age;
    }
}
