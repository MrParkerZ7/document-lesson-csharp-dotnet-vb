namespace L13.DebugLab.Tests;

public class RunSettingsTests
{
    #region TestsRunSettings
    // Passes only if the .runsettings file was applied.
    [Fact, Trait("Category", "Environment")]
    public void The_runsettings_file_was_applied()
    {
        Assert.Equal("applied", Env("L13_RUNSETTINGS"));
        Assert.Equal("240", Env("L13_BATCH_SIZE"));
    }

    private static string? Env(string name) =>
        Environment.GetEnvironmentVariable(name);
    #endregion
}
