<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class QuoteForm
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()>
    Protected Overrides Sub Dispose(disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    Private components As System.ComponentModel.IContainer

#Region "withevents"
    Friend WithEvents CoverCodeBox As TextBox
    Friend WithEvents SumInsuredBox As NumericUpDown
    Friend WithEvents BirthDatePicker As DateTimePicker
    Friend WithEvents QuoteButton As Button
    Friend WithEvents ResultLabel As Label
#End Region

    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        components = New System.ComponentModel.Container()
        CoverCodeBox = New TextBox With {.Location = New Point(12, 12), .Width = 200, .Text = "CLASS1"}
        SumInsuredBox = New NumericUpDown With {.Location = New Point(12, 44), .Width = 200,
                                                .Maximum = 5000000D, .Increment = 25000D, .Value = 500000D}
        BirthDatePicker = New DateTimePicker With {.Location = New Point(12, 76), .Width = 200}
        QuoteButton = New Button With {.Location = New Point(12, 110), .Width = 200, .Text = "Quote"}
        ResultLabel = New Label With {.Location = New Point(12, 146), .Width = 320}
        Controls.AddRange(New Control() {CoverCodeBox, SumInsuredBox, BirthDatePicker, QuoteButton, ResultLabel})
        AutoScaleMode = AutoScaleMode.Font
        ClientSize = New Size(360, 190)
        Text = "MotorQuote - legacy VB form"
    End Sub

End Class
