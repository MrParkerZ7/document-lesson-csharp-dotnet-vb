using System.Numerics;

namespace L03.Domain;

#region generic-math
public static class Totals
{
    // one algorithm for int, decimal and Money: `+` is found per
    // type argument through a static abstract operator (.NET 7+)
    public static T Sum<T>(IEnumerable<T> items, T seed)
        where T : IAdditionOperators<T, T, T>
    {
        var total = seed;
        foreach (var item in items)
            total += item;
        return total;
    }
}
#endregion
