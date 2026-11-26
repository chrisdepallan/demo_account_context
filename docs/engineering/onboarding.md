# Engineering Onboarding

## Who is the engineering onboarding guide for?

The engineering onboarding guide is for every new engineer at Acme Cloud, in any of the 12 service teams. The guide covers the first **90 days**: what to read, how to set up a machine, how to make a first change and when on-call starts. Each new engineer gets an onboarding buddy from the same team for the first **30 days**.

## What does Acme Cloud engineering build?

Acme Cloud is a hosted project-management and file-storage product. The product is built from **12 services**, each owned by one team.

| Service | Team | Slack channel |
|---------|------|---------------|
| accounts | Team Accounts Platform | `#team-accounts` |
| auth | Team Identity | `#team-identity` |
| billing | Team Revenue Engineering | `#team-billing` |
| support | Team Customer Support | `#support-escalations` |
| projects | Team Work Management | `#team-projects` |
| files | Team Storage Platform | `#team-storage` |
| notifications | Team Messaging | `#team-notifications` |
| webhooks | Team Developer Platform | `#team-developer-platform` |
| search | Team Search and Discovery | `#team-search` |
| audit-log | Team Trust and Compliance | `#team-trust` |
| integrations | Team Ecosystem | `#team-ecosystem` |
| analytics | Team Data Platform | `#team-data` |

Shared infrastructure (Kubernetes, databases, the event bus, the API gateway and object storage) is run by Team Platform Infrastructure in `#team-platform`.

## What should a new engineer read first?

Read these documents in the first week, in this order:

1. `README.md` – what the repository is and how it is laid out.
2. `docs/company-overview.md` – the product, the three regions and the uptime targets.
3. `docs/glossary.md` – accounts, workspaces, seats, roles and other terms.
4. The README of the new engineer's own service, for example `services/projects/README.md`.
5. `docs/engineering/coding-standards.md` and `docs/engineering/testing-strategy.md`.
6. `docs/engineering/release-process.md` and `docs/engineering/on-call.md`.
7. `docs/security/data-classification.md` and `docs/security/access-control.md`.

## How do I set up a development machine?

1. Install Python **3.12** or later and Git. The services use the Python standard library only, so there is nothing to install with a package manager.
2. Clone the repository and create a branch. Branch naming rules are in `docs/engineering/release-process.md`.
3. Run every service's tests from the repository root.

```bash
python tools/run_tests.py
```

4. Check that the documentation links are valid.

```bash
python tools/check_links.py
```

5. Ask the onboarding buddy for access to the staging environment. Production access is not part of the standard setup and is requested separately, as described in `docs/security/access-control.md`.

## What is the layout of a service folder?

Every service folder under `services/` has the same layout, shown here for the Billing service:

- `services/billing/README.md` – what the service does, key concepts, endpoints and owners.
- An OpenAPI description of the service's HTTP API.
- A default configuration file in the service's config folder.
- A Python package named `acme_billing`. The Audit Log service's package is named `acme_audit_log`.
- A tests folder with `unittest` tests.
- A docs folder with customer-facing and internal documentation.

## What does the first week look like?

- **Day 1** – accounts, laptop, Slack channels, meeting the team and the onboarding buddy.
- **Day 2** – development machine set up and all tests passing locally.
- **Days 3–5** – a first pull request: a small fix or a documentation change in the engineer's own service. The first pull request is merged within the first **5 working days**.

## What happens in the first 30, 60 and 90 days?

- **By day 30** – the new engineer has shipped at least **1** change to production, has completed the security training and knows the service's runbooks in `docs/runbooks/`.
- **By day 60** – the new engineer has completed **2 shadow shifts** on the team's on-call rotation, working beside the primary on-call.
- **By day 90** – the new engineer joins the on-call rotation as secondary, and as primary on the following rotation.

No engineer joins the on-call rotation before day **60** and before both shadow shifts are done.

## Which security training is required?

Every new engineer completes the security and data handling training within the first **30 days**, and repeats the training every **12 months**. The training covers the four data classification levels, the rule that customer data never leaves production, and how to report a security incident through `docs/security/incident-response.md`.

## Where do I ask questions?

- Questions about one service – the owning team's Slack channel from the table in this guide.
- Questions about infrastructure and deployments – `#team-platform`.
- Questions about security or customer data – `#team-trust`.
- Questions about an ongoing incident – `#incidents`. Do not ask the on-call engineer directly during an incident.

Last reviewed: 2026-11-26
