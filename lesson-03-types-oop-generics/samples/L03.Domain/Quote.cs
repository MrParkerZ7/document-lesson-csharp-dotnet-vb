namespace L03.Domain;

/// <summary>An entity: identity matters and its state changes.</summary>
public sealed class Quote
{
    #region quote-entity
    public required QuoteId Id { get; init; }
    public required QuoteRequest Request { get; init; }
    public required Premium Premium { get; init; }
    public DateOnly ValidUntil { get; init; }

    // C# 14 `field`: guard a setter without declaring a backing field
    public QuoteStatus Status
    {
        get;
        private set => field = CanMove(field, value)
            ? value
            : throw new InvalidOperationException($"{field} -> {value}");
    } = QuoteStatus.Quoted;

    public Policy Accept(PolicyNumber number)
    {
        Status = QuoteStatus.Accepted;
        return new Policy(number, Id,
            Request.StartDate, Request.StartDate.AddYears(1));
    }
    #endregion

    public void Expire() => Status = QuoteStatus.Expired;

    public void Decline() => Status = QuoteStatus.Declined;

    private static bool CanMove(QuoteStatus from, QuoteStatus to) =>
        (from, to) switch
        {
            (QuoteStatus.Draft, QuoteStatus.Quoted) => true,
            (QuoteStatus.Quoted, QuoteStatus.Accepted
                or QuoteStatus.Expired or QuoteStatus.Declined) => true,
            _ => false,
        };
}
