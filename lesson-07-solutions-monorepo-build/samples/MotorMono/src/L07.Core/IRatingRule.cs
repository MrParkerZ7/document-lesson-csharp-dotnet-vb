namespace L07.Core;

#region contract
/// <summary>One rating rule. Any module of the mono-repo can contribute rules:
/// C# and Visual Basic projects implement this same interface.</summary>
public interface IRatingRule
{
    string Name { get; }

    /// <summary>+0.25 is a 25% loading, -0.10 a 10% discount, on the base premium.</summary>
    decimal Factor(QuoteRequest request);
}
#endregion
