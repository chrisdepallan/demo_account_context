# Sharing Links

## What is a share link?

A share link is a URL that opens a file or folder without adding the person to the project or folder first. Links look like `https://app.acme-cloud.example/s/lnk_2P8D5KM3`. Each link has an audience, an access level, and optionally an expiry date and a password.

## Who can open a share link?

Each link has one of three audiences:

- `workspace` – any Owner, Admin or Member of the workspace who is signed in.
- `invited` – only the people named on the link, who must sign in. This is how files are shared with Guests.
- `anyone` – anybody who has the URL, with no sign-in. These are called public links.

## What access levels can a link give?

- `view` – open and download the file.
- `comment` – view, plus add comments.
- `edit` – comment, plus upload new versions and rename the file.

Guests are limited to `view` and `comment` even when a link offers `edit`, in line with `services/accounts/docs/members-and-roles.md`.

## What can public links do on my plan?

| Rule for `anyone` links | Free | Starter | Pro | Business | Enterprise |
|-------------------------|------|---------|-----|----------|------------|
| Access levels | view | view, comment | view, comment, edit | view, comment, edit | view, comment, edit |
| Default expiry | 7 days | 30 days | 30 days | 30 days | 30 days |
| Longest expiry | 7 days | 30 days | 365 days | No expiry allowed | No expiry allowed |
| Password protection | No | Yes | Yes | Yes | Yes |

Public links on Free are `view` only and always expire after **7 days**. Starter adds `comment` and expiry up to **30 days**. Pro adds `edit` and expiry up to **365 days**. Business and Enterprise can create public links that never expire.

## Who can create a share link?

Owners, Admins and Members can create links for files they can edit. Guests and Billing admins cannot create links. A file or folder can have up to **50** active links.

## How do I create a share link?

Open the file, select **Share → Create link**, choose the audience and access level, then set an expiry and a password if needed. Through the API, use `POST /v2/files/{workspace_id}/files/{file_id}/share-links`.

## When do links expire?

Links for the `workspace` and `invited` audiences do not expire unless an expiry is set. Links for `anyone` get the plan's default expiry (**7 days** on Free, **30 days** on other plans) and cannot be set longer than the plan's longest expiry. An expired link shows a "link expired" page; the file itself is not affected. The creator can extend an expired link within the same limits.

## When is a password required?

- A public link with `edit` access always needs a password.
- When an Owner or Admin turns on **Settings → Files → Sharing → Require password on public links**, every new `anyone` link needs one.
- Otherwise a password is optional on Starter and above. Free accounts cannot set link passwords.

Passwords must be at least **8 characters**. After **5** wrong attempts a link is locked for **15 minutes**.

## How do I turn off public links for my workspace?

Owners and Admins can switch off **Settings → Files → Sharing → Allow public links**. Existing `anyone` links stop working within **60 seconds** and new ones cannot be created. Links for `workspace` and `invited` audiences keep working.

## How do I revoke a link?

Open **Share → Manage links** on the file and select **Revoke**. Revocation takes effect within **60 seconds**. Links also stop working when the file is moved to the trash, and start working again if the file is restored before the link expires.

## What happens to links when I downgrade?

Existing links keep working until they expire, but `anyone` links that break the new plan's rules are tightened on the day the downgrade takes effect: access is lowered to the highest level the plan allows, and the expiry is shortened to the plan's longest expiry counted from that day.

Last reviewed: 2026-11-26
