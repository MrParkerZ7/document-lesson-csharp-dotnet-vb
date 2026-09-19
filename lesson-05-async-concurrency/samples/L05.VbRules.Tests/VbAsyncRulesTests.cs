using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.VisualBasic;

namespace L05.VbRules.Tests;

public class VbAsyncRulesTests
{
    [Theory]
    [InlineData("Rejected/AwaitInCatch.vb", "BC36943", false)]
    [InlineData("Rejected/AwaitInFinally.vb", "BC36943", false)]
    [InlineData("Rejected/AwaitInSyncLock.vb", "BC36943", false)]
    [InlineData("Rejected/AsyncValueTask.vb", "BC36945", false)]
    [InlineData("Rejected/AsyncIterator.vb", "BC36936", false)]
    [InlineData("Rejected/AsyncMain.vb", "BC36934", true)]
    [InlineData("Rejected/SyncLockOnLock.vb", "BC37329", false)]
    [InlineData("Rejected/AwaitForEach.vb", "BC30201", false)]
    public void Vb_compiler_rejects(string file, string expectedId, bool exe)
    {
        var errors = CompileVb(file, exe ? OutputKind.ConsoleApplication : OutputKind.DynamicallyLinkedLibrary);
        Assert.True(errors.Any(e => e.Id == expectedId),
            $"{file}: expected {expectedId}, got [{string.Join(" | ", errors.Select(e => $"{e.Id} {e.GetMessage()}"))}]");
    }

    [Theory]
    [InlineData("Accepted/AwaitPatterns.vb")]
    public void Vb_compiler_accepts(string file)
    {
        var errors = CompileVb(file, OutputKind.DynamicallyLinkedLibrary);
        Assert.True(errors.Count == 0, string.Join(" | ", errors.Select(e => $"{e.Id} {e.GetMessage()}")));
    }

    #region compile
    private static List<Diagnostic> CompileVb(string file, OutputKind kind)
    {
        var path = Path.Combine(AppContext.BaseDirectory, "Snippets", file);
        var tree = VisualBasicSyntaxTree.ParseText(File.ReadAllText(path));
        // reference the same framework assemblies this test process runs on (net10.0)
        var references = ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")!)
            .Split(Path.PathSeparator)
            .Select(assembly => MetadataReference.CreateFromFile(assembly));
        var options = new VisualBasicCompilationOptions(kind, optionStrict: OptionStrict.On)
            .WithGlobalImports(GlobalImport.Parse(
                ["System", "System.Collections.Generic", "System.Threading", "System.Threading.Tasks"]));
        var compilation = VisualBasicCompilation.Create("Snippet", [tree], references, options);
        return [.. compilation.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error)];
    }
    #endregion
}
