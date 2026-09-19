using L11.SecureQuoteApi.Quotes;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;

namespace L11.SecureQuoteApi.Security;

public static class QuoteOperations
{
    public static readonly OperationAuthorizationRequirement Read =
        new() { Name = nameof(Read) };

    public static readonly OperationAuthorizationRequirement Accept =
        new() { Name = nameof(Accept) };
}

#region owner-handler
// "May this caller do this operation to THIS quote?" — asked after the policy passed
public sealed class QuoteAuthorizationHandler
    : AuthorizationHandler<OperationAuthorizationRequirement, Quote>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OperationAuthorizationRequirement requirement,
        Quote quote)
    {
        var user = context.User;
        var isOwner = user.SubjectId() == quote.OwnerId;

        var allowed = requirement.Name switch
        {
            // read: the owner, any underwriter, or a back-office app
            nameof(QuoteOperations.Read) => isOwner
                || user.IsInRole(QuoteClaims.UnderwriterRole)
                || user.IsInRole(QuoteClaims.ReadAllPermission),
            // accept: the owner only — nobody accepts a quote for a customer
            nameof(QuoteOperations.Accept) => isOwner,
            _ => false,
        };

        if (allowed)
        {
            context.Succeed(requirement);
        }
        // no context.Fail(): another handler may still succeed the requirement
        return Task.CompletedTask;
    }
}
#endregion
