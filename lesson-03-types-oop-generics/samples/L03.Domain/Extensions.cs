namespace L03.Domain;

#region extension-block
public static class CoverageClassExtensions
{
    // C# 14: members for a type you cannot change
    extension(CoverageClass coverage)
    {
        public bool CoversOwnDamage => coverage
            is CoverageClass.Class1
            or CoverageClass.Class2Plus
            or CoverageClass.Class3Plus;

        public string Code => coverage switch
        {
            CoverageClass.Class1 => "1",
            CoverageClass.Class2Plus => "2+",
            CoverageClass.Class3Plus => "3+",
            CoverageClass.Class3 => "3",
            _ => throw new ArgumentOutOfRangeException(
                nameof(coverage)), // enums are open
        };
    }

    // no receiver name: static members of CoverageClass
    extension(CoverageClass)
    {
        public static CoverageClass FromCode(string code) =>
            Enum.GetValues<CoverageClass>()
                .First(c => c.Code == code);
    }
}
#endregion

#region classic-extension
public static class DriverExtensions
{
    // the pre-C# 14 form: a static method with a `this` parameter
    public static bool IsYoungOn(this Driver driver, DateOnly day) =>
        driver.AgeOn(day) < 25;
}
#endregion
