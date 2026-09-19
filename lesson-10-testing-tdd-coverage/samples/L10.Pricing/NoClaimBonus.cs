namespace L10.Pricing;

/// <summary>No-claim bonus by claim-free years. Illustrative, not a real tariff.</summary>
public static class NoClaimBonus
{
    #region ncb-rule
    public static decimal DiscountFor(int claimFreeYears) =>
        claimFreeYears switch
        {
            < 0 => throw new ArgumentOutOfRangeException(
                nameof(claimFreeYears), "cannot be negative"),
            0 => 0.00m,
            1 => 0.20m,
            2 => 0.25m,
            3 => 0.30m,
            4 => 0.40m,
            _ => 0.50m,
        };
    #endregion
}
