# Acme Cloud Data Model

## Core entities in the Acme Cloud data model

The Acme Cloud data model is built around the **account**, which owns **workspaces**, which hold **projects**, **tasks** and **files**. Every entity has exactly one owning service. Only the owning service writes the entity, and only the owning service's PostgreSQL database stores the entity. Other services keep the ID and, where needed, a read-only copy built from events.

```text
account (acc_)
  |-- subscription --- invoices (INV-)
  |-- support tickets (SUP-)
  |-- members and guests
  |-- audit entries (aud_)
  '-- workspaces (ws_)
        |-- projects (prj_) --- tasks (tsk_) --- comments
        |-- files (fil_) --- file versions, sharing links
        |-- webhook endpoints (whk_)
        |-- installed integrations (int_)
        '-- API keys (acme_live_, acme_test_)
```

## ID formats for Acme Cloud entities

| Entity | ID format | Example | Owning service |
|------|------|------|------|
| Account | `acc_` + **8** uppercase alphanumerics | `acc_7F3K9Q2M` | accounts |
| Workspace | `ws_` + **6** uppercase alphanumerics | `ws_4H8P2L` | accounts |
| Invoice | `INV-YYYY-NNNNNN` | `INV-2026-004812` | billing |
| Support ticket | `SUP-NNNNN` | `SUP-58213` | support |
| Project | `prj_` + **8** uppercase alphanumerics | `prj_9B4T7X2C` | projects |
| Task | `tsk_` + **8** uppercase alphanumerics | `tsk_5M8R3W6K` | projects |
| File | `fil_` + **8** uppercase alphanumerics | `fil_2Q7Z4N9D` | files |
| Webhook endpoint | `whk_` + **8** uppercase alphanumerics | `whk_6J3V8H1P` | webhooks |
| Event | `evt_` + **10** uppercase alphanumerics | `evt_4K9D2M7X1B` | the producing service |
| Audit entry | `aud_` + **10** uppercase alphanumerics | `aud_8R2F6T3Y9C` | audit-log |
| Installed integration | `int_` + **6** uppercase alphanumerics | `int_3G7K5W` | integrations |
| Notification | `ntf_` + **10** uppercase alphanumerics | `ntf_7C1X5B8N4L` | notifications |

API keys are not IDs. An API key is a secret that starts with `acme_live_` (production) or `acme_test_` (sandbox), is shown only once and is stored by the auth service only as a hash. The reasons for the ID formats are in `docs/adr/0003-path-versioning-and-opaque-prefixed-ids.md`.

## Account and workspace entities owned by the accounts service

- **Account** – the billing and legal entity. An account has exactly **one Owner**, one plan (Free, Starter, Pro, Business or Enterprise), one state (`trialing`, `active`, `past_due`, `read_only`, `closed` or `deleted`) and one home region.
- **Workspace** – a container for projects, files and members. A workspace belongs to exactly **one account** and has a region that is fixed at creation. An account can have **1** workspace on Free and Starter, **3** on Pro, **10** on Business and unlimited on Enterprise.
- **Member** – a person with access to a workspace and one role: Owner, Admin, Billing admin, Member or Guest. Members use seats; Guests do not.

Plan limits are in `services/accounts/docs/plans-and-limits.md`. Account states are in `services/accounts/docs/account-lifecycle.md`.

## Identity entities owned by the auth service

- **Login identity** – the email address, password hash and MFA factors of one person. One email address can own only **one account** but can be a member of any number of workspaces.
- **Session** – a signed-in browser or app. Sessions last **14 days** of inactivity on web and **90 days** on mobile.
- **SSO connection** – the SAML 2.0 or OIDC configuration of an account on Business or Enterprise.
- **API key** – scoped to exactly **one workspace**, with up to **25 active keys** per workspace.

The auth service stores no plan or role data. The auth service asks the accounts service which workspaces and roles a person has.

## Money entities owned by the billing service

- **Subscription** – exactly **one per account**: the plan, the seat count and the billing cycle (monthly or annual).
- **Invoice** – issued on every charge, numbered `INV-YYYY-NNNNNN`. An invoice belongs to one account.
- **Refund** and **credit** – always linked to one invoice or one account.
- **Payment method reference** – a token issued by the external payment processor. The billing database never holds card numbers; cards are held by the payment processor.

## Work entities owned by the projects service

- **Project** – belongs to exactly **one workspace**. ID prefix `prj_`.
- **Task** – belongs to exactly **one project**. ID prefix `tsk_`. A task can reference files by their `fil_` IDs.
- **Board**, **comment** and **automation rule** – belong to one project and are stored only in the projects database.

## Storage entities owned by the files service

- **File** – belongs to exactly **one workspace**. ID prefix `fil_`. File metadata is in the files database; file content is in the regional object store.
- **File version** – every upload over an existing file creates a version. Version history is kept for **7 days** on Free, **30 days** on Starter, **180 days** on Pro, **1 year** on Business and without limit on Enterprise.
- **Sharing link** – grants access to one file or folder.
- **Quota usage** – the running storage total per account, compared with the plan's storage limit.

## Entities owned by the platform services

| Entity | Owning service | Belongs to |
|------|------|------|
| Notification (`ntf_`) | notifications | One recipient in one account |
| Webhook endpoint (`whk_`) and delivery attempts | webhooks | One workspace |
| Search document | search | One workspace; rebuilt from project, task and file events |
| Audit entry (`aud_`) | audit-log | One account; entries form a hash chain per account and region |
| Installed integration (`int_`) | integrations | One workspace |
| Dashboard, metric and scheduled export | analytics | One workspace |
| Support ticket (`SUP-`) | support | One account |

## How Acme Cloud services reference each other's entities

- A service stores another service's entity only as an ID string, for example the projects database stores `ws_4H8P2L` but not the workspace name.
- There are no foreign keys and no joins across service databases. See `docs/adr/0001-one-database-per-service.md`.
- A service that needs another service's data for display or filtering keeps a read-only projection built from events on the Acme Event Bus, for example the search service's index.
- Every row that belongs to a customer carries the `account_id`, and workspace content also carries the `workspace_id`. The two columns drive region routing, quota checks and deletion.

## How deletion works across the Acme Cloud data model

Deleting an entity is a soft delete first: the row is marked deleted and hidden, then erased after a retention window. Closing an account soft-deletes everything the account owns for **30 days**, after which the `account.deleted` event tells every service to erase the data. Backups are purged within a further **35 days**. The decision record is `docs/adr/0010-soft-delete-with-retention-windows.md`.

Last reviewed: 2026-11-26
