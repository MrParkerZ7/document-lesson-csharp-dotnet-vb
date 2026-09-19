using System.Globalization;

namespace L07.Core;

/// <summary>An amount of money: decimal, never double. THB unless stated.</summary>
public readonly record struct Money(decimal Amount, string Currency = "THB")
{
    public Money Plus(Money other)
    {
        if (other.Currency != Currency)
        {
            throw new InvalidOperationException($"Cannot add {other.Currency} to {Currency}.");
        }

        return this with { Amount = Amount + other.Amount };
    }

    public Money Times(decimal factor) => this with { Amount = Amount * factor };

    public Money Rounded() =>
        this with { Amount = Math.Round(Amount, 2, MidpointRounding.AwayFromZero) };

    public override string ToString() =>
        string.Create(CultureInfo.InvariantCulture, $"{Amount:N2} {Currency}");
}
