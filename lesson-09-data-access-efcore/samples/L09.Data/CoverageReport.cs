using System.Data.Common;
using Dapper;

namespace L09.Data;

public sealed record CoverageRow(string Coverage, long Quotes, long Lines);

public static class CoverageReport
{
    #region dapper
    public static async Task<List<CoverageRow>> ByCoverageAsync(
        DbConnection connection, string status)
    {
        const string sql = """
            SELECT q.Coverage, COUNT(DISTINCT q.Id) AS Quotes,
                   COUNT(l.Id) AS Lines
            FROM Quotes q
            LEFT JOIN PremiumLines l ON l.QuoteId = q.Id
            WHERE q.Status = @status
            GROUP BY q.Coverage
            ORDER BY q.Coverage
            """;
        var rows = await connection.QueryAsync<CoverageRow>(
            sql, new { status });
        return rows.AsList();
    }
    #endregion
}
