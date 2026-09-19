using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.VisualBasic;
using L03.Domain;

namespace L03.Reports.Tests;

/// <summary>
/// Compiles Visual Basic against the lesson-03 C# assemblies with the Roslyn VB compiler (package 5.9.0,
/// the same 5.9 compiler line the .NET SDK 10.0.401 ships) and pins the error each C#-only feature
/// produces, so the lesson's claims about what VB can and cannot reach are re-proved on every test run.
/// </summary>
public class VbCompilerTests
{
    #region vb-compiler-tests
    // each snippet runs inside: Sub Run(R As QuoteRequest, Q As Quote)
    [Theory]
    [InlineData("Dim c = CoverageClass.Class2Plus.Code", "BC30456")]
    [InlineData("Dim f = CoverageClass.FromCode(\"3+\")", "BC30456")]
    [InlineData("Dim quote As New Quote With {.Id = New QuoteId(1), .Request = R}", "BC37321")]
    [InlineData("Q.ValidUntil = R.StartDate", "BC37311")]
    [InlineData("Dim p = New StandardRateTable().BasePremium(R)", "BC30456")]
    [InlineData("Dim r2 = R With {.Coverage = CoverageClass.Class3}", "BC30205")]
    public void A_CSharp_only_feature_fails_to_compile(string vb, string error) =>
        Assert.Equal([error], Errors(InSub(vb)));

    // ...and the workaround for each compiles cleanly
    [Theory]
    [InlineData("Dim c = CoverageClassExtensions.get_Code(CoverageClass.Class2Plus)")]
    [InlineData("Dim f = CoverageClassExtensions.FromCode(\"3+\")")]
    [InlineData("Dim p = CType(New StandardRateTable(), IRateTable).BasePremium(R)")]
    [InlineData("Dim r2 = New QuoteRequest(R.Vehicle, R.Driver, CoverageClass.Class3, R.StartDate)")]
    public void Its_workaround_compiles(string vb) =>
        Assert.Empty(Errors(InSub(vb)));
    #endregion

    #region vb-declarations
    [Theory]
    [InlineData(HalfRates, "BC30149")]    // a default interface member must be re-implemented
    [InlineData(VbIdentifier, "BC37315")] // static abstract members cannot be implemented
    [InlineData(ParseOnT, "BC32098")]     // T.Parse on a type parameter
    public void A_declaration_fails_to_compile(string vb, string error) =>
        Assert.Equal([error], Errors(vb));
    #endregion

    private const string HalfRates = """
        Class HalfRates
            Implements IRateTable
            Function BaseRate(c As CoverageClass) As Decimal Implements IRateTable.BaseRate
                Return 0.01D
            End Function
        End Class
        """;

    private const string VbIdentifier = """
        Structure VbId
            Implements IIdentifier(Of VbId)
        End Structure
        """;

    private const string ParseOnT = """
        Function ParseOne(Of T As IIdentifier(Of T))(text As String) As T
            Return T.Parse(text)
        End Function
        """;

    [Fact]
    public void Visual_Basic_names_are_case_insensitive() =>
        Assert.Equal(["BC30734"], Errors(InSub("Dim q = 1"))); // q collides with the parameter Q

    [Fact]
    public void The_probe_itself_compiles_clean_Visual_Basic() =>
        Assert.Empty(Errors(InSub("Dim same = (R = R) AndAlso Q.Status = QuoteStatus.Quoted")));

    private static string InSub(string statement) =>
        $"Sub Run(R As QuoteRequest, Q As Quote){Environment.NewLine}{statement}{Environment.NewLine}End Sub";

    /// <summary>Distinct error ids from compiling `members` inside a module, Option Strict On.</summary>
    private static string[] Errors(string members)
    {
        var source = string.Join(Environment.NewLine,
            "Option Strict On", "Imports System", "Imports L03.Domain", "Module Probe", members, "End Module");
        var compilation = VisualBasicCompilation.Create(
            "Probe",
            [VisualBasicSyntaxTree.ParseText(source)],
            References(),
            new VisualBasicCompilationOptions(OutputKind.DynamicallyLinkedLibrary, optionStrict: OptionStrict.On));
        return compilation.GetDiagnostics()
            .Where(d => d.Severity == DiagnosticSeverity.Error)
            .Select(d => d.Id)
            .Distinct()
            .Order(StringComparer.Ordinal)
            .ToArray();
    }

    private static List<MetadataReference> References()
    {
        var paths = ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")!)
            .Split(Path.PathSeparator)
            .Append(typeof(Money).Assembly.Location)
            .Append(typeof(ReportService<>).Assembly.Location);
        return paths
            .DistinctBy(Path.GetFileName, StringComparer.OrdinalIgnoreCase)
            .Select(p => (MetadataReference)MetadataReference.CreateFromFile(p))
            .ToList();
    }
}
