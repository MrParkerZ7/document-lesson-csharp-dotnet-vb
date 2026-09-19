using System.Globalization;
using System.Numerics;

namespace L03.Domain;

#region money
/// <summary>An amount in one currency: a value object, not an entity.</summary>
public readonly record struct Money(decimal Amount, string Currency)
    : IAdditionOperators<Money, Money, Money>
{
    public static Money Thb(decimal amount) => new(amount, "THB");

    public static Money operator +(Money left, Money right) =>
        left.Currency == right.Currency
            ? new(left.Amount + right.Amount, left.Currency)
            : throw new InvalidOperationException(
                $"cannot add {right.Currency} to {left.Currency}");

    public static Money operator *(Money money, decimal factor) =>
        money with
        {
            Amount = decimal.Round(money.Amount * factor, 2,
                MidpointRounding.AwayFromZero),
        };

    public override string ToString() =>
        Amount.ToString("N2", CultureInfo.InvariantCulture) + " " + Currency;
}
#endregion
