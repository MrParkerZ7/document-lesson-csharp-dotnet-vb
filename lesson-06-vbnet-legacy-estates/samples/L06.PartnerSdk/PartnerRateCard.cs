namespace L06.PartnerSdk;

#region partner-sdk
// A rating partner's C# SDK: legal C#, awkward from Visual Basic.
public class PartnerRateCard
{
    public decimal Loading { get; set; } = 0.15m;

    // differs from Loading only by case: fine in C#
    public decimal loading(int claims) => Loading * claims;

    // the case-distinct name a VB caller can actually reach
    public decimal LoadingFor(int claims) => loading(claims);

    // ref + optional: VB may pass a property here
    public static void AddFee(ref decimal amount, decimal fee = 35m) =>
        amount += fee;
}
#endregion
