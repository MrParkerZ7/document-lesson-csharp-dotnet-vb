Imports System.Runtime.CompilerServices
Imports System.Security.Claims
Imports System.Security.Cryptography
Imports System.Security.Principal
Imports Microsoft.IdentityModel.JsonWebTokens
Imports Microsoft.IdentityModel.Tokens

Module Program
    Private Const Issuer As String = "https://login.example.test/tenant-l11/v2.0"
    Private Const Audience As String = "api://l11-secure-quote-api"
    Private ReadOnly Registered As String() = {"iss", "aud", "exp", "nbf", "iat"}

    Sub Main()
        Dim key As New SymmetricSecurityKey(RandomNumberGenerator.GetBytes(32))
        Dim token = MintUnderwriterToken(key)
        Console.WriteLine("One underwriter access token, read twice")

#Region "main"
        For Each mapClaims In {True, False}
            Dim user = ReadUser(token, key, mapClaims)
            Console.WriteLine()
            Console.WriteLine($"MapInboundClaims = {mapClaims}")
            For Each c In user.Claims.Where(
                    Function(x) Not Registered.Contains(x.Type))
                Console.WriteLine($"  {c.Type} = {c.Value}")
            Next
            Console.WriteLine(
                $"  IsInRole(""Underwriter"") = {user.IsInRole("Underwriter")}")
            Console.WriteLine(
                $"  HasScope(""Quotes.Read"") = {user.HasScope("Quotes.Read")}")
        Next
#End Region

        Console.WriteLine()
        Console.WriteLine("A Forms-era principal, read as claims")
#Region "legacy-principal"
        ' What Web Forms code found in Thread.CurrentPrincipal after a
        ' Forms login: a GenericPrincipal. Since .NET 4.5 it IS a
        ' ClaimsPrincipal, so no conversion is needed.
        Dim legacy As New GenericPrincipal(
            New GenericIdentity("uw-1", "Forms"), {"Underwriter"})
        Dim asClaims As ClaimsPrincipal = legacy
        For Each c In asClaims.Claims
            Console.WriteLine($"  {c.Type} = {c.Value}")
        Next
        Console.WriteLine(
            $"  IsInRole(""Underwriter"") = {asClaims.IsInRole("Underwriter")}")
#End Region
    End Sub

#Region "read-user"
    Function ReadUser(token As String, key As SecurityKey,
                      mapClaims As Boolean) As ClaimsPrincipal
        Dim handler As New JsonWebTokenHandler With {
            .MapInboundClaims = mapClaims
        }
        Dim parameters As New TokenValidationParameters With {
            .ValidIssuer = Issuer,
            .ValidAudience = Audience,
            .IssuerSigningKey = key,
            .RoleClaimType = "roles"
        }
        ' a console Main cannot Await; blocking here is safe (no
        ' synchronization context) and nowhere else — lesson 05
        Dim result = handler.ValidateTokenAsync(token, parameters).
            GetAwaiter().GetResult()
        Return New ClaimsPrincipal(result.ClaimsIdentity)
    End Function
#End Region

#Region "has-scope"
    <Extension>
    Function HasScope(user As ClaimsPrincipal,
                      scope As String) As Boolean
        ' Entra puts every delegated scope in ONE claim: "a b c"
        Dim scp = user.FindFirst("scp")?.Value
        If scp Is Nothing Then
            Return False
        End If
        Dim scopes = scp.Split(" "c,
            StringSplitOptions.RemoveEmptyEntries)
        Return scopes.Contains(scope, StringComparer.Ordinal)
    End Function
#End Region

    Function MintUnderwriterToken(key As SecurityKey) As String
        Dim descriptor As New SecurityTokenDescriptor With {
            .Issuer = Issuer,
            .Audience = Audience,
            .Expires = DateTime.UtcNow.AddMinutes(5),
            .SigningCredentials = New SigningCredentials(key, SecurityAlgorithms.HmacSha256),
            .Claims = New Dictionary(Of String, Object) From {
                {"sub", "uw-1"},
                {"scp", "Quotes.Read Quotes.Write"},
                {"roles", New String() {"Underwriter"}}
            }
        }
        Return New JsonWebTokenHandler().CreateToken(descriptor)
    End Function
End Module
