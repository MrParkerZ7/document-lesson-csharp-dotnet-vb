Imports System.Globalization
Imports L06.LegacyRating
Imports Xunit

' Characterization tests pin what the legacy code DOES today, quirks
' included. Expected premiums were captured from a run, not a spec.
Public Class LegacyPremiumCharacterizationTests

    Private Shared Function Quote(code As String,
                                  Optional dob As String = "1990-03-10",
                                  Optional months As Integer = 120,
                                  Optional claims As Integer = 0,
                                  Optional sum As Decimal = 287500D) As Decimal
        Dim born = Date.ParseExact(dob, "yyyy-MM-dd", CultureInfo.InvariantCulture)
        Return LegacyPremium.CalcPremium(code, sum, born, #1/1/2026#,
                                         months, claims)
    End Function

#Region "pin-premiums"
    ' The first row is the curriculum's worked example: 8,933.71 THB to the
    ' satang in the canonical tariff. The legacy prices in whole baht.
    <Theory>
    <InlineData("CLASS1", 550000, "2002-06-15", 48, 0, 8933)>
    <InlineData("class1", 287500, "2001-12-31", 18, 0, 4864)>
    <InlineData("CLASS2PLUS", 450000, "1990-03-10", 30, 1, 6381)>
    Public Sub PinsTodaysPremium(code As String, sum As Integer, dob As String,
                                 months As Integer, claims As Integer,
                                 expected As Integer)
        Assert.Equal(CDec(expected), Quote(code, dob, months, claims, sum))
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
    Public Sub LicenceMonthsRoundToTheNearestEvenYear()
        ' The no-claim discount follows licence years = months / 12,
        ' rounded half to even: 18 -> 2, but 30 -> 2 and 42 -> 4.
        Assert.Equal(Quote("CLASS1", months:=24), Quote("CLASS1", months:=18))
        Assert.Equal(Quote("CLASS1", months:=24), Quote("CLASS1", months:=30))
        Assert.Equal(Quote("CLASS1", months:=48), Quote("CLASS1", months:=42))
        Assert.True(Quote("CLASS1", months:=18) < Quote("CLASS1", months:=17))
    End Sub

    <Fact>
    Public Sub LicenceYearsAboveFiveUseTheSixthSlot()
        Assert.Equal(Quote("CLASS1", months:=60), Quote("CLASS1", months:=84))
        Assert.True(Quote("CLASS1", months:=60) < Quote("CLASS1", months:=48))
    End Sub

    <Fact>
    Public Sub AnyClaimLosesTheNoClaimDiscount()
        Assert.Equal(Quote("CLASS1", months:=6, claims:=1),
                     Quote("CLASS1", months:=120, claims:=1))
    End Sub
#End Region

    <Fact>
    Public Sub UnknownCoverReturnsMinusOneAndAReason()
        Dim reason As String = Nothing
        Dim premium = LegacyPremium.CalcPremium("CLASS4", 287500D, #3/10/1990#,
                                                #1/1/2026#, 120, 0, False, 1500, reason)
        Assert.Equal(-1D, premium)
        Assert.Equal("unknown cover CLASS4", reason)
    End Sub

    <Fact>
    Public Sub ThreeClaimsAreDeclinedWithAReason()
        Dim reason As String = Nothing
        Dim premium = LegacyPremium.CalcPremium("CLASS1", 287500D, #3/10/1990#,
                                                #1/1/2026#, 120, 3, False, 1500, reason)
        Assert.Equal(-1D, premium)
        Assert.Equal("3+ claims in 5 years", reason)
    End Sub

End Class
