Imports System.Globalization

Module Program
    Sub Main()
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture
        Console.WriteLine("L02.SyntaxVb - the same tour in Visual Basic")
        Tour.Types()
        Tour.Nulls()
        Tour.Patterns()
        Tour.Methods()
        Tour.Errors()
    End Sub
End Module
