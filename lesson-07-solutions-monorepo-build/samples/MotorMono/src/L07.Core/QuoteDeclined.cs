namespace L07.Core;

/// <summary>Three or more claims in five years: the tariff declines the quote instead of pricing it.
/// A declined quote is a domain outcome, not a crash. This build lesson needs the smallest form of
/// that outcome, so it takes the exception one; the language lesson owns exceptions properly.</summary>
public sealed class QuoteDeclinedException : InvalidOperationException
{
    public const string ThreeOrMoreClaims = "3+ claims in 5 years";

    public QuoteDeclinedException()
        : base(ThreeOrMoreClaims)
    {
    }

    public QuoteDeclinedException(string message)
        : base(message)
    {
    }

    public QuoteDeclinedException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}
