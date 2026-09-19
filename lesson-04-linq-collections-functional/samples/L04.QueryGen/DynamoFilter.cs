using System.Collections;
using System.Globalization;
using System.Linq.Expressions;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace L04.QueryGen;

/// <summary>A DynamoDB-style filter: expression text plus its #name and :value placeholder maps.</summary>
public sealed record FilterExpression(
    string Expression,
    IReadOnlyDictionary<string, string> Names,
    IReadOnlyDictionary<string, object> Values);

public static class DynamoFilter
{
    #region entry-point
    // Expression<Func<T, bool>>: the compiler hands the lambda over as DATA, not as IL
    public static FilterExpression From<T>(Expression<Func<T, bool>> predicate)
    {
        var translator = new Translator(predicate.Parameters[0]);
        var text = translator.Condition(predicate.Body);
        return new FilterExpression(text, translator.Names, translator.Values);
    }
    #endregion
}

internal sealed class Translator(ParameterExpression item)
{
    private const int MaxInValues = 100; // DynamoDB: an IN list holds at most 100 values

    private static readonly Dictionary<ExpressionType, string> Comparators = new()
    {
        [ExpressionType.Equal] = "=",
        [ExpressionType.NotEqual] = "<>",
        [ExpressionType.LessThan] = "<",
        [ExpressionType.LessThanOrEqual] = "<=",
        [ExpressionType.GreaterThan] = ">",
        [ExpressionType.GreaterThanOrEqual] = ">=",
    };

    public Dictionary<string, string> Names { get; } = [];
    public Dictionary<string, object> Values { get; } = [];

    #region translate
    // one switch over node shapes: pattern matching is the visitor
    public string Condition(Expression e) => e switch
    {
        BinaryExpression { NodeType: ExpressionType.AndAlso } b
            => $"({Condition(b.Left)} AND {Condition(b.Right)})",
        BinaryExpression { NodeType: ExpressionType.OrElse } b
            => $"({Condition(b.Left)} OR {Condition(b.Right)})",
        UnaryExpression { NodeType: ExpressionType.Not } u
            => $"NOT ({Condition(u.Operand)})",
        BinaryExpression b when Comparators.TryGetValue(b.NodeType, out var op)
            => Compare(b.Left, op, b.Right),
        MethodCallExpression { Method.Name: "StartsWith", Object: { } s } m when IsOnItem(s)
            => $"begins_with({Path(s)}, {Operand(m.Arguments[0], typeof(string))})",
        MethodCallExpression { Method.Name: "Contains" } m
            => Contains(m),
        MemberExpression m when m.Type == typeof(bool) && IsOnItem(m)
            => $"{Path(m)} = {Constant(true)}",
        _ => throw Unsupported(e),
    };
    #endregion

    private string Compare(Expression left, string op, Expression right)
    {
        if (!IsOnItem(Strip(left)))
        {
            if (!IsOnItem(Strip(right))) throw Unsupported(left);
            (left, right, op) = (right, left, Flip(op)); // 2020 < q.Year  ->  q.Year > 2020
        }
        var attribute = Strip(left); // enum comparisons arrive as Convert(q.Coverage, Int32)
        return $"{Path(attribute)} {op} {Operand(right, attribute.Type)}";
    }

    private string Contains(MethodCallExpression m)
    {
        if (m.Object is { } target && IsOnItem(target)) // q.Vehicle.Model.Contains("x")
            return $"contains({Path(target)}, {Operand(m.Arguments[0], typeof(string))})";

        var (source, probe) = m.Object is null
            ? (m.Arguments[0], m.Arguments[1])          // static: Enumerable / MemoryExtensions
            : (m.Object, m.Arguments[0]);               // instance: List<T>.Contains
        var attribute = Strip(probe);
        if (!IsOnItem(attribute)) throw Unsupported(m);

        var values = Items(source).Select(v => Constant(Normalise(v, attribute.Type))).ToList();
        if (values.Count is 0 or > MaxInValues)
            throw new NotSupportedException($"IN needs 1 to {MaxInValues} values, got {values.Count}");
        return $"{Path(attribute)} IN ({string.Join(", ", values)})";
    }

    #region path-and-placeholders
    // q.Vehicle.Make -> #n0.#n1 ; the same attribute name always reuses its placeholder
    private string Path(Expression e)
    {
        var members = new Stack<MemberInfo>(); // walked leaf-first, so the root ends on top
        for (var node = e; node != item; node = ((MemberExpression)node).Expression!)
            members.Push(((MemberExpression)node).Member);

        var path = new List<string>();
        foreach (var member in members)
        {
            // stored = a field or an auto-property; a hand-written getter is computed in C#
            if (member is PropertyInfo p
                && p.GetMethod?.IsDefined(typeof(CompilerGeneratedAttribute)) != true)
                throw new NotSupportedException(
                    $"'{member.Name}' is computed in C#; it is not a stored attribute");
            path.Add(Name(member.Name));
        }
        return string.Join(".", path);
    }

    private string Name(string attribute)
    {
        foreach (var (key, value) in Names)
            if (value == attribute) return key;
        var added = $"#n{Names.Count}";
        Names[added] = attribute;
        return added;
    }

    // everything NOT rooted in the item (constants, captured locals) is evaluated right now
    private string Operand(Expression e, Type attributeType) =>
        IsOnItem(Strip(e)) ? Path(Strip(e)) : Constant(Normalise(Evaluate(e), attributeType));
    #endregion

    private string Constant(object value)
    {
        var added = $":v{Values.Count}";
        Values[added] = value;
        return added;
    }

    private bool IsOnItem(Expression e) => e switch
    {
        ParameterExpression p => p == item,
        MemberExpression { Expression: { } inner } => IsOnItem(inner),
        _ => false,
    };

    private static Expression Strip(Expression e) =>
        e is UnaryExpression { NodeType: ExpressionType.Convert } u ? u.Operand : e;

    private static object Evaluate(Expression e) =>
        Expression.Lambda(e).Compile().DynamicInvoke()
        ?? throw new NotSupportedException($"null is not a filter value: {e}");

    private static IEnumerable<object> Items(Expression source)
    {
        // an implicit array-to-span conversion wraps the array: unwrap it to reach the array itself
        if (source is MethodCallExpression { Method.Name: "op_Implicit" } conversion)
            source = conversion.Arguments[0];
        return Evaluate(Strip(source)) is IEnumerable items
            ? items.Cast<object>()
            : throw new NotSupportedException($"'{source}' is not a collection");
    }

    private static object Normalise(object value, Type attributeType) => value switch
    {
        Enum e => e.ToString(),
        _ when attributeType.IsEnum => Enum.ToObject(attributeType, value).ToString()!,
        DateOnly d => d.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture),
        _ => value,
    };

    private static string Flip(string op) => op switch
    {
        "<" => ">",
        "<=" => ">=",
        ">" => "<",
        ">=" => "<=",
        _ => op,
    };

    private static NotSupportedException Unsupported(Expression e) =>
        new($"Cannot translate '{e}' ({e.NodeType}) to a filter expression");
}
