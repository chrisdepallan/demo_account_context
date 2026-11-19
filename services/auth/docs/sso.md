# Single Sign-On (SSO)

## Which plans include SSO?

SSO with SAML 2.0 or OpenID Connect is available on **Business** and **Enterprise**. SCIM user provisioning is **Enterprise only**.

## Which identity providers are supported?

Any SAML 2.0 or OIDC provider. Step-by-step guides exist for Okta, Microsoft Entra ID (Azure AD), Google Workspace, OneLogin and JumpCloud.

## How do I set up SAML SSO?

1. An Admin goes to **Settings → Security → SSO → Add SAML connection**.
2. Copy the Acme Cloud values into the identity provider:
   - ACS URL: `https://auth.acme-cloud.example/saml/acs/{workspace_id}`
   - Entity ID: `https://auth.acme-cloud.example/saml/{workspace_id}`
   - NameID format: `emailAddress`
3. Upload the provider's metadata XML or paste its SSO URL and X.509 certificate.
4. Verify the email domain by adding the TXT record shown on screen to DNS.
5. Select **Test connection**, then **Enable**.

## Can I force everyone to use SSO?

Yes. After SSO is enabled and the domain is verified, Admins can turn on **Enforce SSO**. Password login is then disabled for everyone on the verified domain except the Owner, who keeps password + MFA as a break-glass login.

## What does "SAML response signature invalid" mean?

The certificate in Acme Cloud does not match the one the identity provider is signing with. This usually happens after the provider rotates its certificate. Upload the new certificate in **Settings → Security → SSO**.

## What happens to users removed from the identity provider?

- **With SCIM** (Enterprise): the user is deactivated in Acme Cloud within **5 minutes**.
- **Without SCIM**: the user can no longer log in through SSO, but still uses a seat until an Admin removes them manually.

Last reviewed: 2026-11-19
