# Access Control

## What are the access control principles at Acme Cloud?

Access control at Acme Cloud follows four principles for staff access to internal systems and to customer data.

- **Least privilege** – each person and each service gets only the access the job needs.
- **Need to know** – access to Confidential and Restricted data needs a reason that is written down.
- **Separation of duties** – no one approves their own access request, pull request or production change.
- **Everything is logged** – every production access by staff is recorded in the audit log.

The data levels Public, Internal, Confidential and Restricted are defined in `docs/security/data-classification.md`.

## How do Acme Cloud staff sign in to internal systems?

Staff sign in to every internal system through the company single sign-on. Multi-factor authentication with a security key or a passkey is required for all staff. SMS codes are not accepted for staff accounts. Staff sessions for production tools end after **12 hours**, and after **30 minutes** without activity. Shared accounts are not allowed: every action is tied to one named staff account.

## Who has access to production?

No engineer has standing write access to production databases or to customer content. Standing access is limited to the following.

| Role | Standing access |
|------|-----------------|
| Engineer on a service team | Read access to logs and metrics of all services, deploy rights for the team's own service through the release pipeline |
| Primary and secondary on-call | The same, plus read-only database access to the team's own service during the shift |
| Team Platform Infrastructure | Administration of Kubernetes, the event bus, the API gateway and database infrastructure, without access to customer content |
| Support agent | Account details, plan, invoices and tickets through the support console |
| Team Trust and Compliance | Read access to the audit log and to access records |

Anything beyond standing access is requested as just-in-time access.

## How does just-in-time production access work?

1. The engineer requests access in the access tool and states the system, the level (read or write) and the reason, with an incident ID such as `INC-2026-041` or a ticket ID such as `SUP-58213`.
2. A second person approves the request: the engineering manager of the owning team, or the incident commander during a SEV1 or SEV2 incident.
3. Access is granted for at most **8 hours** and ends automatically.
4. Every command and query run with the access is recorded.
5. Team Trust and Compliance reviews a sample of just-in-time sessions every **month**.

Write access to the Audit Log database is never granted as just-in-time access to a single engineer. Write access to the Audit Log database needs two engineers working together and the approval of Team Trust and Compliance.

## What is break-glass access?

Break-glass access is emergency access for a SEV1 incident when the normal approval path is not available. Break-glass access is granted for at most **1 hour**, pages Team Trust and Compliance at once and is reviewed within **1 business day**. Using break-glass access without a SEV1 incident is a security incident.

## When can support staff see customer data?

Support agents see Confidential account data in the support console: the account, plan, members, invoices and tickets. Support agents do not see Restricted customer content such as files, tasks and comments. If a ticket cannot be solved without looking at customer content, the agent asks the customer for consent on the ticket. Consent gives a Tier 2 agent view-only access to the named workspace for **24 hours**. The access is written to the customer's audit log. Support rules are in `services/support/docs/sla-and-escalation.md`.

## How do services authenticate to each other?

Each service has its own service identity. Calls between services pass through the API gateway or the event bus and carry a short-lived service token that lasts at most **1 hour**. A service may call only the endpoints and read only the event topics that its identity is allowed to use. A service connects only to its own PostgreSQL database, with a database role that belongs to that service alone. Service credentials are stored in the secrets manager and rotated at least every **90 days**.

## How is customer access controlled inside the product?

Customers control access to their own workspaces with five roles: Owner, Admin, Billing admin, Member and Guest. The roles are defined in `docs/glossary.md` and `services/accounts/docs/members-and-roles.md`. Programmatic access uses API keys with scopes, described in `services/auth/docs/api-keys.md`. Every permission check runs on the server for every request. A workspace's data is never visible to another workspace.

## How often is access reviewed?

- Each engineering manager reviews the access of the team every **90 days** and removes access that is no longer needed.
- Team Trust and Compliance reviews administrator access to infrastructure and to the secrets manager every **90 days**.
- Access that has not been used for **60 days** is removed automatically.
- The results of each access review are kept for **2 years**.

## What happens to access when someone joins, moves or leaves?

- **Joining** – a new member of staff gets the standard access of the role on day 1. Production-related access is added after the security training.
- **Moving teams** – the access of the old team is removed within **5 business days**.
- **Leaving** – all access is removed within **24 hours** of the last working day, and at once when the departure is not voluntary. Secrets that the person could read are rotated within **7 days**.

## How are secrets and keys managed?

Secrets are stored only in the secrets manager and reach services as environment variables. Secrets are never written to code, configuration files, tickets, chat or this repository. Staff do not use customer API keys. A secret that may have been exposed is rotated at once and reported in `#team-trust`. Customer API keys that appear in a public code repository are revoked automatically, as described in `services/auth/docs/api-keys.md`.

Last reviewed: 2026-11-26
