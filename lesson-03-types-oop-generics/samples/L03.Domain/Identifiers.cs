using System.Globalization;

namespace L03.Domain;

#region static-abstract
// C# 11 static abstract members: a contract on the TYPE, not the instance
public interface IIdentifier<TSelf> where TSelf : IIdentifier<TSelf>
{
    static abstract string Prefix { get; }
    static abstract TSelf Parse(string text);
}

public readonly record struct QuoteId(int Value) : IIdentifier<QuoteId>
{
    public static string Prefix => "Q-";

    public static QuoteId Parse(string text) =>
        new(int.Parse(text[Prefix.Length..], CultureInfo.InvariantCulture));

    public override string ToString() => $"{Prefix}{Value:D6}";
}
#endregion

public readonly record struct PolicyNumber(int Value) : IIdentifier<PolicyNumber>
{
    public static string Prefix => "P-";

    public static PolicyNumber Parse(string text) =>
        new(int.Parse(text[Prefix.Length..], CultureInfo.InvariantCulture));

    public override string ToString() => $"{Prefix}{Value:D8}";
}

#region reified
public static class Ids
{
    // T is a real type at run time: no Class<T> token needed
    public static List<T> ParseAll<T>(params string[] texts)
        where T : IIdentifier<T>
    {
        var ids = new List<T>(texts.Length);
        foreach (var text in texts)
            ids.Add(T.Parse(text)); // a static call on T
        return ids;
    }

    public static string Describe<T>()
        where T : IIdentifier<T> =>
        $"{typeof(T).Name} {T.Prefix} {default(T)}";
}
#endregion
