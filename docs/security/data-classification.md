# Data Classification

## What are the data classification levels at Acme Cloud?

Acme Cloud classifies all data into four levels. The level decides who may see the data, where the data may be stored and how the data is protected.

| Level | Meaning | Examples |
|-------|---------|----------|
| **Public** | Meant for everyone | Help center articles, the status page, public API documentation, published prices |
| **Internal** | For Acme Cloud staff, harmless if seen by a customer | Runbooks, coding standards, team channel names, alert names |
| **Confidential** | Business data and customer account data | Account and workspace details, member names and email addresses, invoices, support tickets, usage metrics per account |
| **Restricted** | Customer content and security material | Files, projects, tasks and comments stored by customers, password hashes, MFA secrets, API keys, session tokens, signing keys, audit log entries |

Data that is not labelled is treated as **Confidential** until its owner classifies it.

## Who decides the classification of data?

The team that owns the service where the data is created decides the classification. For example, Team Storage Platform classifies file content and Team Revenue Engineering classifies invoices. Team Trust and Compliance reviews the classification of every new kind of data before the data reaches production, and settles disagreements. When two levels could apply, the higher level applies.

## How must Public and Internal data be handled?

Public data can be shared freely once Team Customer Support or the document owner has approved its publication. Internal data stays inside Acme Cloud's own tools and repositories. Internal data may be discussed in any internal Slack channel and may be stored on company laptops. Internal data is not posted on public websites, public repositories or personal accounts.

## How must Confidential data be handled?

- Confidential data is stored only in production systems and in approved internal tools such as the ticket system.
- Access is limited to staff whose role needs the data, as described in `docs/security/access-control.md`.
- Confidential data is encrypted in transit and at rest.
- Confidential data is not copied to laptops, test environments, spreadsheets or chat messages. Refer to an account by its ID, for example `acc_7F3K9Q2M`, instead of by a person's name or email address.
- Support tickets are kept for **3 years** after closing and then anonymized, as described in `services/support/docs/sla-and-escalation.md`.

## How must Restricted data be handled?

- Restricted data never leaves the production environment of the region where the workspace was created.
- No member of staff reads customer content without a recorded reason. Access to customer content needs the customer's consent on a support ticket, or an approved security investigation.
- Every access to Restricted data by staff is written to the audit log.
- Secrets such as API keys and signing keys are stored only in the secrets manager. Secrets never appear in code, configuration files, logs, tickets or chat. An API key is shown in documentation and logs only as its prefix, `acme_live_` or `acme_test_`.
- Restricted data is encrypted at rest with keys that are rotated at least every **12 months**.

## Which kinds of data does Acme Cloud not collect?

Acme Cloud does not ask for and does not store the following kinds of data in its own systems:

- Full payment card numbers and card security codes. Cards are held by the payment processor, as described in `services/billing/docs/payment-methods.md`.
- Government-issued identity numbers, such as social security numbers, national identity numbers, tax identity numbers, passport numbers and driving licence numbers.
- Patient records and other health records.
- Passwords in readable form. Only password hashes are stored.

Customers decide what they put into their own files and tasks. The customer terms ask customers not to store these kinds of data in Acme Cloud unless their contract covers it.

## What must never be pasted into tickets, chat or logs?

Staff and customers must never paste the following into a support ticket, a Slack message, a pull request, a log line or this repository:

- Passwords, MFA codes, backup codes, API keys, session tokens and private keys.
- Full payment card numbers or card security codes.
- Government-issued identity numbers of any kind.
- Patient or health records.
- The content of a customer's files, tasks or comments.

If a customer sends such data in a ticket, the support agent removes the data from the ticket with the redaction tool, tells the customer and does not use the data. Support never asks for or accepts a customer's password, full card number or MFA code.

## How long is data kept?

| Data | Retention |
|------|-----------|
| Customer content after an account is closed | **30 days**, then permanently deleted from primary storage |
| Backups that contain deleted customer content | Purged within a further **35 days** |
| Closed support tickets | **3 years**, then anonymized |
| Audit log entries | **90 days** on Pro, **1 year** on Business, **7 years** on Enterprise |
| File version history | **7 days** on Free, **30 days** on Starter, **180 days** on Pro, **1 year** on Business, unlimited on Enterprise |
| Service logs | **30 days** |

Account closure and deletion are described in `services/accounts/docs/account-lifecycle.md`. Plan limits are listed in `services/accounts/docs/plans-and-limits.md`.

## Where may each classification level be stored?

| Location | Public | Internal | Confidential | Restricted |
|----------|--------|----------|--------------|------------|
| This documentation repository | Yes | Yes | No | No |
| Internal Slack channels | Yes | Yes | No | No |
| Ticket system | Yes | Yes | Yes | No |
| Staging and test environments | Yes | Yes | No | No |
| Production databases and object storage | Yes | Yes | Yes | Yes |
| Company laptops | Yes | Yes | No | No |

Staging and test environments use generated, fictional data only.

## What happens when data is mishandled?

Any member of staff who sees Confidential or Restricted data in the wrong place reports the finding in `#team-trust` on the same day. Team Trust and Compliance decides whether the finding is a security incident and, if so, follows `docs/security/incident-response.md`. Reporting a mistake promptly is expected and is never punished.

Last reviewed: 2026-11-26
