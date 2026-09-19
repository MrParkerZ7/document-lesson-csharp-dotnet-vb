using System.Text.Json;

namespace L02.Syntax;

sealed class QuoteDraft
{
    public string? Note { get; set; }
    public decimal Loading { get; set; }
}

sealed class PartnerDto
{
    public string Name { get; set; } = "";   // declared non-nullable
}

static class NullsTour
{
    static string? LookUpNote(string quoteId) => quoteId == "Q-0001" ? "renewal" : null;

    static QuoteDraft? FindDraft(string quoteId) => quoteId == "Q-0001" ? new QuoteDraft() : null;

    public static void Run()
    {
        Console.WriteLine();
        Console.WriteLine("[nulls]");

        #region nulls
        string? note = LookUpNote("Q-0002");  // maybe-null
        int length = note?.Length ?? 0;       // ?. then ??
        note ??= "no note";                   // assign only if null
        Console.WriteLine($"{note} ({length})");

        string sure = LookUpNote("Q-0001")!;  // ! = trust me
        Console.WriteLine(sure.ToUpperInvariant());

        QuoteDraft? draft = FindDraft("Q-0001");
        draft?.Note = "young driver";         // C# 14: ?. on the left
        draft?.Loading += 0.20m;              // compound works too
        Console.WriteLine($"{draft?.Note} {draft?.Loading}");
        #endregion

        #region runtime
        // int? is a real run-time type: Nullable<int>, a struct with HasValue
        int? claims = null;
        Console.WriteLine(typeof(int?) == typeof(Nullable<int>));    // True
        Console.WriteLine(claims.GetValueOrDefault());               // 0
        object boxed = claims!;
        Console.WriteLine(boxed is null);                            // True: boxing a null int? gives null

        // string? is NOT a type: it is a compile-time annotation on System.String
        var noteType = typeof(QuoteDraft).GetProperty(nameof(QuoteDraft.Note))!.PropertyType;
        Console.WriteLine(noteType == typeof(string));               // True

        // nothing enforces it at run time: a deserializer happily stores null
        var dto = JsonSerializer.Deserialize<PartnerDto>("""{ "Name": null }""")!;
        Console.WriteLine(dto.Name is null);                         // True
        var strict = new JsonSerializerOptions { RespectNullableAnnotations = true };
        try
        {
            JsonSerializer.Deserialize<PartnerDto>("""{ "Name": null }""", strict);
        }
        catch (JsonException)
        {
            Console.WriteLine("RespectNullableAnnotations: JsonException");
        }
        #endregion
    }
}
