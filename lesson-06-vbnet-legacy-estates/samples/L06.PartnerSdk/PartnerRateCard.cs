namespace L06.PartnerSdk;

#region partner-sdk
// A rating partner's C# SDK: legal C#, awkward from Visual Basic.
public class PartnerRateCard
{
    // the canonical loading for one claim (curriculum, "Canonical tariff")
    public decimal Loading { get; set; } = 0.10m;

    // differs from Loading only by case: fine in C#
    public decimal loading(int claims) => claims switch
    {
        0 => 0m,
        1 => Loading,
        2 => 0.25m,
        _ => throw new ArgumentOutOfRangeException(
            nameof(claims), "3+ claims in 5 years are declined"),
    };

    // the case-distinct name a VB caller can actually reach
    public decimal LoadingFor(int claims) => loading(claims);

    // ref + optional: VB may pass a property here
    public static void AddFee(ref decimal amount, decimal fee = 35m) =>
        amount += fee;
}
#endregion
