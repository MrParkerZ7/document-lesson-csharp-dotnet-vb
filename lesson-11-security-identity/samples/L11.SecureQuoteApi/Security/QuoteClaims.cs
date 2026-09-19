using System.Security.Claims;

namespace L11.SecureQuoteApi.Security;

public static class QuoteClaims
{
    #region claim-names
    // Raw JWT claim names. They only survive because MapInboundClaims = false.
    public const string Scope = "scp";        // delegated scopes, ONE space-separated string
    public const string Roles = "roles";      // app roles AND application permissions
    public const string Subject = "sub";      // pairwise per app in Entra; oid is tenant-wide

    public const string ReadScope = "Quotes.Read";
    public const string WriteScope = "Quotes.Write";
    public const string ReadAllPermission = "Quotes.Read.All";   // client-credentials callers
    public const string UnderwriterRole = "Underwriter";
    #endregion

    #region has-scope
    public static bool HasScope(this ClaimsPrincipal user,
        string scope)
    {
        // Entra puts every delegated scope in ONE claim: "a b c"
        var scp = user.FindFirst(Scope)?.Value;
        if (scp is null)
        {
            return false;
        }
        var scopes = scp.Split(' ',
            StringSplitOptions.RemoveEmptyEntries);
        return scopes.Contains(scope, StringComparer.Ordinal);
    }
    #endregion

    public static string? SubjectId(this ClaimsPrincipal user) =>
        user.FindFirst(Subject)?.Value;
}
