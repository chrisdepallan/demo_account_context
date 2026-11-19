# Plans and Limits

## Plan comparison

| Limit / feature | Free | Starter | Pro | Business | Enterprise |
|-----------------|------|---------|-----|----------|------------|
| Max members | 3 | 10 | 100 | 500 | Unlimited |
| Guests per paid seat | – | 5 | 5 | 5 | 5 |
| Workspaces | 1 | 1 | 3 | 10 | Unlimited |
| Storage | 2 GB total | 10 GB/seat | 50 GB/seat | 200 GB/seat | 1 TB/seat |
| Max file upload | 250 MB | 250 MB | 5 GB | 5 GB | 5 GB |
| Version history | 7 days | 30 days | 180 days | 1 year | Unlimited |
| API requests | 100/min | 300/min | 1,000/min | 3,000/min | 10,000/min |
| SSO (SAML/OIDC) | No | No | No | Yes | Yes |
| SCIM provisioning | No | No | No | No | Yes |
| Audit log retention | – | – | 90 days | 1 year | 7 years |
| Data regions | us-east | us-east | us-east | us-east, eu-central | All |
| Uptime SLA | – | 99.9% | 99.9% | 99.95% | 99.99% |

## What happens when I hit the storage limit?

At **90%** usage the Owner and Admins get an email warning. At **100%**, new uploads are blocked but existing files stay accessible and editable. Buying more seats, upgrading, or adding a storage pack (100 GB for $10/month) lifts the block immediately.

## What happens when I hit the API rate limit?

Requests over the limit get HTTP `429 Too Many Requests` with a `Retry-After` header in seconds. Limits are counted per account, not per API key.

## How do I upgrade or downgrade?

- **Upgrade**: takes effect immediately. The price difference for the rest of the billing period is charged right away (prorated).
- **Downgrade**: takes effect at the end of the current billing period. No partial refund is issued.
- Downgrading is blocked if current usage exceeds the lower plan's limits (for example more members or storage). Usage must be reduced first.

## Enterprise plan details

- Minimum 50 seats, annual contract only.
- Includes a named Customer Success Manager, 24/7 critical support and a 99.99% uptime SLA.
- Custom terms (DPA, security review, invoicing) are handled by Sales: `sales@acme-cloud.example`.

Last reviewed: 2026-11-19
