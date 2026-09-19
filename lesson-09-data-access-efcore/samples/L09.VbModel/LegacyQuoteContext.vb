Imports Microsoft.EntityFrameworkCore

#Region "vb-model"
' A model declared in VB compiles and runs: the EF Core runtime is
' language-neutral. Only the design-time generators are C#-only.
Public Class LegacyQuote
    Public Property Id As Integer
    Public Property Reference As String = ""
    Public Property TotalAmount As Decimal
End Class

Public Class LegacyQuoteContext
    Inherits DbContext

    Public Property Quotes As DbSet(Of LegacyQuote)

    Protected Overrides Sub OnConfiguring(options As DbContextOptionsBuilder)
        options.UseSqlite("Data Source=legacy.db")
    End Sub
End Class
#End Region
