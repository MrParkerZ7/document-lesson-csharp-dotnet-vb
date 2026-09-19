Imports System.Globalization
Imports L06.LegacyRating
Imports Xunit

' Characterization tests pin what the legacy code DOES today, quirks
' included. Expected premiums were captured from a run, not a spec.
Public Class LegacyPremiumCharacterizationTests

    Private Shared Function Quote(code As String,
                                  Optional dob As String = "1990-03-10",
                                  Optional months As Integer = 120,
                                  Optional claimFree As Integer = 0,
                                  Optional sum As Decimal = 287500D) As Decimal
        Dim born = Date.ParseExact(dob, "yyyy-MM-dd", CultureInfo.InvariantCulture)
        Return LegacyPremium.CalcPremium(code, sum, born, #1/1/2026#,
                                         months, claimFree, claims:=0)
    End Function

#Region "pin-premiums"
    <Theory>
    <InlineData("CLASS1", 205000, "2001-12-31", 6, 0, 4481)>
    <InlineData("class1", 287500, "2001-12-31", 18, 5, 2857)>
    Public Sub PinsTodaysPremium(code As String, sum As Integer, dob As String,
                                 months As Integer, claimFree As Integer,
                                 expected As Integer)
        Assert.Equal(CDec(expected), Quote(code, dob, months, claimFree, sum))
    End Sub
#End Region

#Region "pin-quirks"
    <Theory>
    <InlineData("class1")>
    <InlineData("  Class1 ")>
    Public Sub CoverCodeIgnoresCaseAndSpaces(code As String)
        Assert.Equal(Quote("CLASS1"), Quote(code))
    End Sub

    <Fact>
    Public Sub AgeCountsYearNumbersNotBirthdays()
        ' Both drivers are 24 on 1 Jan 2026. DateDiff says the one born
        ' on 31 Dec 2001 is 25, so no young-driver loading applies.
        Assert.True(Quote("CLASS1", dob:="2001-12-31") <
                    Quote("CLASS1", dob:="2002-01-01"))
    End Sub

    <Fact>
    Public Sub EighteenMonthsCountsAsTwoYears()
        ' 18 / 12 = 1.5 rounds to 2 (experienced); 17 / 12 rounds to 1.
        Assert.Equal(Quote("CLASS1", months:=120), Quote("CLASS1", months:=18))
        Assert.True(Quote("CLASS1", months:=18) < Quote("CLASS1", months:=17))
    End Sub

    <Fact>
    Public Sub ClaimFreeYearsAboveFiveUseTheSixthSlot()
        Assert.Equal(Quote("CLASS1", claimFree:=5), Quote("CLASS1", claimFree:=7))
        Assert.True(Quote("CLASS1", claimFree:=5) < Quote("CLASS1", claimFree:=4))
    End Sub
#End Region

    <Fact>
    Public Sub UnknownCoverReturnsMinusOneAndAReason()
        Dim reason As String = Nothing
        Dim premium = LegacyPremium.CalcPremium("CLASS4", 287500D, #3/10/1990#,
                                                #1/1/2026#, 120, 0, 0, False, reason)
        Assert.Equal(-1D, premium)
        Assert.Equal("unknown cover CLASS4", reason)
    End Sub

End Class
