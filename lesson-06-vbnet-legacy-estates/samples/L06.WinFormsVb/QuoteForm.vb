Imports L06.ModernRating

Public Class QuoteForm

#Region "handles-click"
    ' Handles wires the event of a control declared WithEvents in the
    ' designer file. The rating now lives in the C# port; the VB form
    ' only gathers input and shows the result (strangler step 1).
    Private Sub QuoteButton_Click(sender As Object, e As EventArgs) _
            Handles QuoteButton.Click
        Dim request As New QuoteRequest(
            CoverCodeBox.Text, SumInsuredBox.Value,
            DateOnly.FromDateTime(BirthDatePicker.Value),
            DateOnly.FromDateTime(Date.Today),
            LicenceMonths:=120, ClaimFreeYears:=0, Claims:=0)

        Dim premium As Decimal? = PremiumCalculator.Calculate(request)
        ResultLabel.Text = If(premium.HasValue,
                              $"{premium.Value:N0} THB (illustrative)",
                              "Declined")
    End Sub
#End Region

End Class
