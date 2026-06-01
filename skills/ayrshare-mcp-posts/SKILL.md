---
name: ayrshare-mcp-posts
description: |
  Use whenever someone wants to validate, publish, schedule, edit, fetch, delete, or retry a social media post through the Ayrshare MCP server — the `mcp__ayrshare__validate_post`, `mcp__ayrshare__create_post`, `mcp__ayrshare__get_post`, `mcp__ayrshare__update_post`, `mcp__ayrshare__delete_post`, and `mcp__ayrshare__retry_post` tools. Trigger on phrasings like "post this to LinkedIn and X", "schedule a tweet for Friday", "share this image on Instagram and Facebook", "queue this announcement for next week", "take down that post", "edit the scheduled post", or "that post failed, try it again" — even if the user never says "Ayrshare", "MCP", or names a specific tool. Also trigger when a user references a returned post `id` and wants to change, remove, or inspect it. For installing/configuring the server and the auth model, this skill cross-links to `../ayrshare-mcp-getting-started/SKILL.md`. For attaching images/video, cross-links to `../ayrshare-mcp-media/SKILL.md`.
---

# Ayrshare MCP — Posts

The validate/write/read/lifecycle tools for individual social posts: validate, create or schedule, fetch, update, delete, and retry. All are **profile-scoped** — they accept an optional `profileKey` to act on a specific client profile, or omit it to act under the Business account.

- API base (REST endpoints the tools wrap): `https://api.ayrshare.com/api`
- Platform enum (the only valid values, verbatim): `bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube` — full table with notes in `references/platforms.md`.

## Function table

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__validate_post` | Validate content for platform-specific issues (char limits, unsupported media) before publishing | POST `/post/validate` | Yes | `post` (text), `platforms` (array of enum) | `profileKey`, `mediaUrls`, `scheduleDate` (ISO 8601) |
| `mcp__ayrshare__create_post` | Create or schedule a post | POST `/post` | Yes | `post` (text), `platforms` (array of enum) | `profileKey`, `mediaUrls`, `scheduleDate` (ISO 8601), `shortenLinks` |
| `mcp__ayrshare__get_post` | Fetch a post's details/status | GET `/post` | Yes | `id` | `profileKey` |
| `mcp__ayrshare__update_post` | Update a (scheduled) post | PUT `/post` | Yes | `id` + the fields to change | `profileKey` |
| `mcp__ayrshare__delete_post` | Delete a published/scheduled post | DELETE `/post` | Yes | `id` | `profileKey` |
| `mcp__ayrshare__retry_post` | Retry a FAILED post | POST `/post/retry` | Yes | `id` | `profileKey` |

Full `create_post`/`validate_post` input schema and example payloads are in `references/create-post-schema.md` and `references/examples.md`.

## Auth note

All post tools are profile-scoped. The Business API key is configured when the MCP server is installed — see `../ayrshare-mcp-getting-started/SKILL.md` for installation and the full auth model; don't re-derive it here. A profile key may come from the `AYRSHARE_PROFILE_KEY` environment default (applied to every call automatically) OR a per-call `profileKey` param that overrides it. **Omit `profileKey` on purpose** to operate under the Business account itself when no env default is set.

## Usage guidance

- **Sequencing is mandatory: validate → confirm → create.** Always call `mcp__ayrshare__validate_post` first to check the content/platforms for issues (character limits, unsupported media). Surface any issues and ask how to proceed. Then show the user a summary (content, platforms, scheduled time) and get explicit confirmation. Only then call `mcp__ayrshare__create_post`. On any per-platform failure in the result, call `mcp__ayrshare__explain_error` and surface the plain-language explanation.
- **Publishing vs scheduling** is one tool: `mcp__ayrshare__create_post`. Omit `scheduleDate` to post immediately; include it (ISO 8601) to schedule. There is no separate "schedule" tool.
- **Editing** only makes sense for posts that haven't gone out yet. Use `mcp__ayrshare__update_post` with the returned `id` for scheduled posts. To "change" an already-published post, you generally delete and re-create.
- **Inspecting** before acting: when the user references a prior post and you're unsure of its state (scheduled, live, failed), call `mcp__ayrshare__get_post` first to read `id`/status, then decide between update, delete, or retry.
- **Retry** is narrow: `mcp__ayrshare__retry_post` only re-attempts a post that actually FAILED. It is not a generic "send again" — see Gotchas.
- **Attaching media:** put image/video URLs in `mediaUrls`. Verify them first — sequencing in Gotchas, full media workflow in `../ayrshare-mcp-media/SKILL.md`.
- **Capture the `id`** returned by `create_post`. Get/update/delete/retry all key off it; without it you can't manage the post later.

## Gotchas

- **Always validate before posting.** The repo's social-manager agent and `/ayrshare:post` command both require `mcp__ayrshare__validate_post` → confirm → `mcp__ayrshare__create_post`. Skipping validation lets avoidable per-platform rejections (over-limit text, unsupported media) reach publish time.
- **Wrong/missing `profileKey` layer.** Omitting `profileKey` (with no `AYRSHARE_PROFILE_KEY` env default) silently posts under the **Business account**, not the client you meant. Only omit it on purpose. (Shared rule — see getting-started.)
- **Invalid `platforms` enum value.** `platforms` accepts only the 13 values listed above. Common misses: `x` or `X` instead of `twitter`; `google` or `google_business` instead of `gmb`; `fb`/`ig`/`li` shorthands. One bad value rejects the call — see `references/platforms.md`.
- **`scheduleDate` must be ISO 8601.** e.g. `2026-06-05T14:30:00Z`. Omit the field entirely to post now — do not pass an empty string or a human phrase like "Friday". Convert relative dates to an absolute ISO timestamp yourself before calling.
- **Test-account posts are PERMANENT.** Posts created through Ayrshare TEST accounts cannot be deleted — `mcp__ayrshare__delete_post` will not remove them. Don't promise a user you can take a test post back down.
- **Media must exist and verify before you reference it.** A `mediaUrls` entry that is unreachable or the wrong format fails the post. Upload/verify media first via `../ayrshare-mcp-media/SKILL.md` (`mcp__ayrshare__verify_media`), then pass the confirmed URLs into `create_post`.
- **X/Twitter BYO credentials.** If `X_API_KEY` and `X_API_SECRET` are configured, they are passed as connection headers for X/Twitter posting — see `references/create-post-schema.md`.
- **`retry_post` is FAILED-only.** It re-attempts a post whose previous send failed; it is not a way to duplicate a successful post or re-run a delete. Calling it on a non-failed post won't behave like "post again". Check status with `mcp__ayrshare__get_post` if unsure.
- **On failure, explain — don't auto-retry.** When any post tool errors, call `mcp__ayrshare__explain_error` to translate the API error to plain language, then surface it. Never auto-retry create/update/delete on a 4xx (bad input, wrong key, missing permission) — retrying a write can duplicate a post; retrying a delete can compound damage. A 429 gets at most one retry after a short delay. (Mirror of the global retry-safety rule — full version in getting-started.)
