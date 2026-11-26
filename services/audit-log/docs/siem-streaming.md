# Audit Log SIEM Streaming

## What is SIEM streaming?

Streaming sends every new audit log entry to the customer's own security monitoring system (SIEM) shortly after it is recorded. It lets a security team alert on events such as `login.failed` or `api_key.created` and keep entries for longer than the plan's retention window.

## Which plans include SIEM streaming?

| Plan | Streams per account |
|------|---------------------|
| Pro | Not available |
| Business | **1** |
| Enterprise | **5** |

Pro accounts can use exports or the API instead; see `services/audit-log/docs/retention-and-export.md`.

## Which destinations are supported?

| Destination type | What Acme Cloud needs |
|------------------|-----------------------|
| `https` | An HTTPS URL that accepts `POST` requests with a JSON body |
| `splunk_hec` | The HTTP Event Collector URL and its token |
| `datadog` | The Datadog site and an API key for log intake |
| `s3` | A bucket name, a region and a role that Acme Cloud may assume to write objects |

Destination URLs must use HTTPS with a valid certificate. Plain HTTP is rejected.

## How do I set up a stream?

1. An Owner or Admin goes to **Settings → Security → Audit log → Streaming → Add stream**.
2. Choose the destination type and enter its details. Credentials are stored encrypted and are never shown again.
3. Optionally limit the stream to some categories, for example only authentication and security.
4. Select **Send test event**. A sample `audit_log.stream_tested` entry is delivered and the result is shown.
5. Select **Enable**. New entries start flowing within **60 seconds**.

Creating, changing and deleting a stream are recorded in the audit log.

## How fast are entries delivered?

Entries are sent in batches of up to **500 entries**, or every **30 seconds**, whichever comes first. Most entries reach the destination within **2 minutes** of the action. Each delivery request times out after **10 seconds**.

## What format are streamed entries in?

Each batch is a JSON array of entries (JSON Lines objects for `s3`, gzip-compressed). Every entry has the same fields as in the export, including `id`, `occurred_at`, `event_type`, `actor`, `ip_address`, `sequence`, `prev_hash` and `hash`. The fields are listed in `services/audit-log/docs/recorded-events.md`.

## How do I check that a batch really came from Acme Cloud?

For `https` destinations, each request carries an `X-Acme-Audit-Signature` header: an HMAC-SHA256 of the request body, computed with the stream's signing secret. The signing secret is shown **once** when the stream is created and can be rotated at any time. Reject requests whose signature does not match.

## What happens if my SIEM is down?

Delivery is **at least once**, so the SIEM should de-duplicate on the entry `id`.

- A failed batch is retried with exponential backoff, starting at **1 minute**, for up to **24 hours**.
- After 24 hours of continuous failure the stream is **paused** and Owners and Admins are emailed.
- When the stream is resumed, entries from the last **7 days** are sent again automatically (backfill). Older entries must be fetched by export.

The audit log itself is not affected by a failing stream: entries are always recorded.

## Does streaming respect data regions?

Entries are sent from the region where they are stored (`us-east`, `eu-central` or `ap-south`). Acme Cloud does not move them to another region first. Where the destination is located is the customer's choice.

## How do I pause or delete a stream?

Go to **Settings → Security → Audit log → Streaming**, then select **Pause** or **Delete**. A paused stream keeps its settings and can be resumed with the 7-day backfill. Deleting a stream removes its stored credentials immediately. On a downgrade from Business to Pro, streams are deleted when the downgrade takes effect.

Last reviewed: 2026-11-26
