# Runbook – SSO Certificate Expiry

## When to use this runbook

Use the SSO certificate expiry runbook when a certificate used for SAML single sign-on is about to expire or has expired. Two kinds of certificate are involved.

- **Customer identity provider certificate** – the X.509 certificate that a customer's identity provider uses to sign SAML responses. One certificate is stored per SAML connection.
- **Acme Cloud SAML signing certificate** – the certificate that `auth.acme-cloud.example` uses to sign SAML requests. One certificate is shared by all workspaces.

Alerts that lead to the SSO certificate expiry runbook:

- Alert `AuthSsoCertificateExpiringSoon` – a certificate expires in **30 days** or less (warning) or in **7 days** or less (critical).
- Alert `AuthSsoSignatureFailuresHigh` – more than **20** SAML responses failed signature validation over **10 minutes**.
- Customers report the error "SAML response signature invalid", which is explained in `services/auth/docs/sso.md`.

## Impact

An expired customer identity provider certificate blocks SSO login for every user of that one workspace. If **Enforce SSO** is on, only the Owner can still sign in, using password and MFA as the break-glass login. An expired Acme Cloud SAML signing certificate breaks SSO for every Business and Enterprise workspace whose identity provider validates signed requests.

One affected workspace is **SEV3**. Many affected workspaces, or an expired Acme Cloud SAML signing certificate, is **SEV1**.

## Diagnosis

1. Find out which certificate triggered the alert. The alert label `scope` is `customer` or `platform`.
2. For a customer identity provider certificate, list the SAML connections that expire soon.

```bash
psql "$AUTH_DB_URL" -h auth-db.us-east.internal.acme-cloud.example -c "
  SELECT workspace_id, idp_cert_not_after
  FROM saml_connections
  WHERE idp_cert_not_after < now() + interval '30 days'
  ORDER BY idp_cert_not_after;"
```

3. For the Acme Cloud SAML signing certificate, read the expiry date from the published metadata.

```bash
curl -s https://auth.acme-cloud.example/saml/metadata \
  | grep -o "<ds:X509Certificate>.*</ds:X509Certificate>" \
  | sed -e "s/<[^>]*>//g" | base64 -d | openssl x509 -inform der -noout -enddate
```

4. Check the signature failures by workspace to see whether one workspace or many workspaces are affected.

```bash
kubectl --context prod-us-east -n auth logs deploy/auth-api --since=30m | grep "saml_signature_invalid" | tail -n 50
```

The table and column names in the query are illustrative. Check the Auth service schema before running the query.

## Mitigation

1. For a customer identity provider certificate, Acme Cloud cannot replace the certificate. An Admin of the workspace must upload the new certificate in **Settings → Security → SSO**.
2. Ask Team Customer Support to contact the workspace Admins **30 days** and again **7 days** before expiry. Enterprise customers are also contacted by their Customer Success Manager.
3. If the customer certificate has already expired, tell the workspace Owner to sign in with password and MFA and upload the new certificate. Never turn off **Enforce SSO** on behalf of a customer.
4. For the Acme Cloud SAML signing certificate, publish the new certificate in the metadata next to the old certificate at least **30 days** before the old certificate expires. Both certificates stay valid during the overlap.
5. Switch signing to the new certificate only after the overlap has started and customers have been notified. Remove the old certificate after it expires.
6. Confirm recovery by checking that `AuthSsoSignatureFailuresHigh` has cleared for **30 minutes**.

## Escalation

- Team Identity owns the SSO certificate expiry runbook. Use `#team-identity`.
- Page the Team Identity on-call immediately if the Acme Cloud SAML signing certificate expires in **7 days** or less and no replacement has been published.
- Hand customer contact to Team Customer Support in `#support-escalations`. Support never changes SSO settings for a customer based on email alone.
- Tell Team Trust and Compliance in `#team-trust` if a private key may have been exposed.

## After the incident

- Record the new expiry date and create a calendar reminder **60 days** before the next expiry.
- The Acme Cloud SAML signing certificate is rotated every **12 months** with a **30-day** overlap. Confirm that the next rotation has an owner.
- Add a note to the customer's support ticket (format `SUP-58213`) with the date on which the customer uploaded the new certificate.
- For a SEV1 or SEV2 incident, write a postmortem within **5 business days**.

Last reviewed: 2026-11-26
