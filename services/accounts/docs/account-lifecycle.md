# Account Lifecycle

## Account states

| State | Meaning | Can users log in? | Can users edit? |
|-------|---------|-------------------|-----------------|
| `trialing` | In the 14-day Pro trial | Yes | Yes |
| `active` | Paid or Free, in good standing | Yes | Yes |
| `past_due` | Payment failed, inside the 14-day grace period | Yes | Yes |
| `read_only` | Grace period over, still unpaid | Yes | No |
| `closed` | Closed by Owner or by Acme, within 30-day retention | No | No |
| `deleted` | Permanently deleted | No | No |

## Signing up

- Sign-up needs an email address and a verified email. The verification link is valid for **24 hours**.
- One email address can own only one account, but can be a member of any number of workspaces.
- New accounts start in `trialing` on the Pro plan for 14 days.

## What happens when the trial ends?

- With a payment method on file: the account moves to `active` on Pro and the first charge is made.
- Without a payment method: the account moves to `active` on Free. If it has more than 3 members, extra members become guests until seats are bought.

## How do I close an account?

1. The Owner goes to **Settings → Account → Close account**.
2. They type the account name to confirm.
3. Any active subscription is cancelled. Annual plans closed within 30 days of purchase are refunded in full; otherwise no refund is issued for unused time.
4. The account moves to `closed` and all members are signed out.

Only the Owner can close an account. Admins cannot.

## How long is data kept after closing?

Data is kept for **30 days** after closing. During that time the Owner can restore the account from the link in the closure email, or support can restore it. On day 31 the account moves to `deleted` and data is permanently erased from primary storage. Backups are purged within a further **35 days**.

## Can a deleted account be recovered?

No. Once an account is `deleted`, its data cannot be recovered by anyone, including Acme Cloud support.

## Inactive Free accounts

Free accounts with no logins for **12 months** receive a warning email, followed by a second warning 30 days later. If there is still no login after a further 30 days, the account is closed and the normal 30-day retention applies.

## Exporting data

The Owner or an Admin can export all workspace data from **Settings → Workspace → Export**. Exports are delivered as a ZIP with JSON and original files. The download link is valid for **7 days**. One export per workspace can run at a time.

Last reviewed: 2026-11-19
