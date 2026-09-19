Imports L10.Pricing
Imports Microsoft.Extensions.Time.Testing
Imports NSubstitute
Imports Xunit

Namespace L10.Pricing.VbTests

    Public Class QuoteServiceVbTests

#Region "vb-fake-time"
        Private Shared ReadOnly Nine As New DateTimeOffset(
            2026, 10, 1, 9, 0, 0, TimeSpan.Zero)

        <Fact>
        Public Async Function Expired_after_30_days() As Task
            Dim ct = TestContext.Current.CancellationToken
            Dim time As New FakeTimeProvider(Nine)
            Dim repo = Substitute.For(Of IQuoteRepository)()
            Dim service As New QuoteService(
                repo, New PremiumCalculator(), time)

            Dim quote = Await service.CreateAsync(Request(), ct)
            repo.FindAsync(quote.Id, ct).Returns(quote)
            time.Advance(QuoteService.Validity) ' still valid
            time.Advance(TimeSpan.FromTicks(1)) ' one tick late
            Dim result = Await service.AcceptAsync(quote.Id, ct)

            Assert.Equal(QuoteStatus.Expired, result.Status)
        End Function
#End Region

        Private Shared Function Request() As QuoteRequest
            Dim start As New DateOnly(2026, 10, 1)
            Return New QuoteRequest(
                New Vehicle("Toyota", "Yaris", 2023, 1200, VehicleUse.Private,
                            New Money(600000D, "THB")),
                New Driver(start.AddYears(-36), 10, 0),
                CoverageClass.Class1,
                start)
        End Function

    End Class

End Namespace
