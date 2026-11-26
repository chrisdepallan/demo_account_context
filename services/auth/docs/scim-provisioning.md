# SCIM Provisioning

## What is SCIM provisioning?

SCIM (System for Cross-domain Identity Management) lets an identity provider create, update and deactivate Acme Cloud users automatically. Acme Cloud supports **SCIM 2.0**. With SCIM turned on, the identity provider is the source of truth for who has access to a workspace.

## Which plans include SCIM?

SCIM is **Enterprise only**. Business accounts have SSO but must add and remove members by hand. SCIM needs a working SSO connection with a verified email domain first; see `services/auth/docs/sso.md`.

## How do I turn on SCIM?

1. An Admin goes to **Settings → Security → SSO → SCIM provisioning** and selects **Enable**.
2. Copy the SCIM base URL into the identity provider: `https://api.acme-cloud.example/v2/auth/scim/{workspace_id}`
3. Select **Generate token** and paste the bearer token into the identity provider. The token is shown **only once**.
4. Map the identity provider's groups to Acme Cloud roles.
5. Run the identity provider's test, then assign users or groups.

## How long does a SCIM token last?

A SCIM token is valid for **365 days**. The Owner and Admins are emailed **14 days** before it expires. Each workspace can have **2** active SCIM tokens so that a new one can be installed before the old one is revoked. Revoking a token takes effect within **60 seconds**.

## Which SCIM operations are supported?

| Operation | Supported |
|-----------|-----------|
| Create user | Yes |
| Update user name and email | Yes |
| Deactivate and reactivate user | Yes |
| Delete user | Yes (treated as deactivate) |
| Create, update and delete groups | Yes |
| Change password | No |

Passwords are never synced. SCIM users sign in through SSO.

## How quickly are changes applied?

Changes sent by the identity provider are applied within **5 minutes**. A user removed from the identity provider is deactivated in Acme Cloud within **5 minutes**, and their sessions end at the same time.

## What happens to a deactivated user?

- The user can no longer log in and all their sessions are ended.
- Their seat is freed and credited on the next invoice, prorated by day.
- Content they created stays in the workspace.
- API keys they created keep working until an Admin revokes them.

Reactivating the user in the identity provider restores their access and role, and uses a seat again.

## Which roles can SCIM assign?

Groups can be mapped to **Admin**, **Member** or **Guest**. The **Owner** and **Billing admin** roles cannot be assigned or removed through SCIM, and the Owner cannot be deactivated through SCIM. Users with no mapped group get the **Member** role.

## What happens if there are not enough seats?

On Enterprise there is no member limit, so new users are always created. Each new member adds a seat, which is charged prorated by day. Admins can set a **seat cap** under **Settings → Security → SSO → SCIM provisioning**; when the cap is reached, new users are rejected with HTTP `409` until the cap is raised.

## Are SCIM requests rate limited?

Yes. SCIM requests count towards the account's API limit, which is **10,000 requests per minute** on Enterprise. Requests over the limit get HTTP `429` with a `Retry-After` header, and identity providers retry automatically.

## Where can I see what SCIM changed?

Every SCIM change is written to the audit log with the actor shown as **SCIM**. Enterprise accounts keep audit log entries for **7 years**.

Last reviewed: 2026-11-26
