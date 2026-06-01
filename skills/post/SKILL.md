---
name: post
description: |
  Use whenever someone wants to validate, publish, schedule, edit, fetch, or retry a social media post through the Ayrshare MCP server — the `mcp__ayrshare__validate_post`, `mcp__ayrshare__create_post`, `mcp__ayrshare__get_post`, `mcp__ayrshare__update_post`, and `mcp__ayrshare__retry_post` tools. Trigger on phrasings like "post this to LinkedIn and X", "schedule a tweet for Friday", "share this image on Instagram and Facebook", "queue this announcement for next week", "edit the scheduled post", "approve the pending post", "reschedule that post", or "that post failed, try it again" — even if the user never says "Ayrshare", "MCP", or names a specific tool. Also trigger when a user references a returned post `id` and wants to change, inspect, or retry it. For installing/configuring the server and the auth model, this skill cross-links to `../getting-started/SKILL.md`. For attaching images/video, cross-links to `../media/SKILL.md`.
---

# Ayrshare MCP — Posts

The validate/write/read/lifecycle tools for individual social posts: validate, create or schedule, fetch, update, and retry. All operate on the profile selected by the connection's `Profile-Key` header — there is **no per-call `profileKey` argument**.

- API base (REST endpoints the tools wrap): `https://api.ayrshare.com/api`
- Platform enum (the only valid values, verbatim): `twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads` — full table with notes in `references/platforms.md`.

## Function table

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__validate_post` | Dry-run a post: check platform-specific issues (char limits, unsupported media) WITHOUT publishing | POST `/validate/post` | `post` (text), `platforms` (array of enum) | `mediaUrls`, `scheduleDate` (ISO 8601), and the full content/scheduling/platform-options surface — see `references/create-post-schema.md` |
| `mcp__ayrshare__create_post` | Create or schedule a post | POST `/post` | `post` (text), `platforms` (array of enum) | `mediaUrls`, `scheduleDate` (ISO 8601), and the full content/scheduling/platform-options surface — see `references/create-post-schema.md` |
| `mcp__ayrshare__get_post` | Fetch a post's details/status | GET `/post/:id` | `id` | — (none) |
| `mcp__ayrshare__update_post` | Update a PENDING post (edit/approve/reschedule) | PATCH `/post` | `id` + at least one of the optional fields | `scheduleDate`, `approved` (bool), `notes` (string), `disableComments` (bool), `scheduledPause` (bool), `youTubeOptions` (object) |
| `mcp__ayrshare__retry_post` | Retry a post in status `error`, once, if the error was retryable | PUT `/post/retry` | `id` | — (none) |

Full `create_post`/`validate_post` input schema and example payloads are in `references/create-post-schema.md` and `references/examples.md`.

## Auth note

The Business API key (`Authorization: Bearer <key>`) is configured when the MCP server is installed — see `../getting-started/SKILL.md` for installation and the full auth model; don't re-derive it here. Profile scoping is **not** a per-call parameter: it is the optional `Profile-Key` connection header set in the MCP client config (`.mcp.json` headers). To act as a different client profile you reconfigure the connection's `Profile-Key`; omit it to act under the account's primary/Business profile.

## Usage guidance

- **Sequencing is mandatory: validate → confirm → create.** Always call `mcp__ayrshare__validate_post` first to dry-run the content/platforms for issues (character limits, unsupported media) without publishing. Surface any issues and ask how to proceed. Then show the user a summary (content, platforms, scheduled time) and get explicit confirmation. Only then call `mcp__ayrshare__create_post`. On any per-platform failure in the result, call `mcp__ayrshare__explain_error` and surface the plain-language explanation.
- **Publishing vs scheduling** is one tool: `mcp__ayrshare__create_post`. Omit `scheduleDate` to post immediately; include it (ISO 8601, a future time) to schedule. There is no separate "schedule" tool. `create_post` is synchronous and returns per-platform `postIds`.
- **Editing** is primarily for PENDING posts (scheduled, awaiting approval). Use `mcp__ayrshare__update_post` with the returned `id` and at least one editable field: `scheduleDate` (reschedule), `approved` (approve), `notes`, `disableComments`, `scheduledPause`, or `youTubeOptions`.
- **Inspecting** before acting: when the user references a prior post and you're unsure of its state (scheduled, live, error), call `mcp__ayrshare__get_post` with the `id` first to read its status, then decide between update or retry.
- **Retry** is narrow: `mcp__ayrshare__retry_post` re-attempts a post in status `error`, ONCE, and only if the error was retryable. It is not a generic "send again" — to recover a failure, use `retry_post`, NOT a second `create_post`. See Gotchas.
- **Attaching media:** put image/video URLs in `mediaUrls`. Validate them first — sequencing in Gotchas, full media workflow in `../media/SKILL.md`.
- **Capture the `id`** returned by `create_post`. Get/update/retry all key off it; without it you can't manage the post later.

## Gotchas

- **Always validate before posting.** The repo's social-manager agent enforces `mcp__ayrshare__validate_post` → confirm → `mcp__ayrshare__create_post`. Skipping validation lets avoidable per-platform rejections (over-limit text, unsupported media) reach publish time.
- **Profile scoping is a header, not an argument.** No post tool takes a `profileKey` parameter. The profile is selected by the `Profile-Key` connection header in the MCP client config; with it unset, every call acts under the account's primary/Business profile. To target a client profile, reconfigure the connection header. (Shared rule — see getting-started.)
- **Invalid `platforms` enum value.** `platforms` accepts only the 13 values listed above. Common misses: `x` or `X` instead of `twitter`; `google`, `google_business`, or `googlebusiness` instead of `gmb`; `fb`/`ig`/`li` shorthands. One bad value rejects the call — see `references/platforms.md`.
- **`scheduleDate` must be ISO 8601.** e.g. `2026-06-05T14:30:00Z`. Omit the field entirely to post now — do not pass an empty string or a human phrase like "Friday". Convert relative dates to an absolute ISO timestamp yourself before calling.
- **Media must exist and verify before you reference it.** A `mediaUrls` entry that is unreachable or the wrong format fails the post. Check media first via `../media/SKILL.md` (`mcp__ayrshare__validate_media`, which HEAD-checks a URL is reachable and reports its content type), then pass the confirmed URLs into `create_post`.
- **Advanced fields are first-class typed inputs — there is no generic `passthrough`.** `create_post`/`validate_post` accept far more than `post`/`platforms`/`mediaUrls`/`scheduleDate`: `firstComment`, `autoSchedule`, `autoRepost`, `autoHashtag`, `unsplash`, `disableComments`, `shortenLinks`, `requiresApproval`, `notes`, `idempotencyKey`, and 12 per-platform option objects (e.g. `youTubeOptions.title`, required for YouTube; `redditOptions.title` + `subreddit`, required for Reddit). Set them directly as top-level fields. There is no `passthrough`/escape-hatch field — unknown keys are dropped. Full list in `references/create-post-schema.md`.
- **`retry_post` is error-only and one-shot.** It re-attempts a post in status `error`, exactly once, and only if the error was retryable. It is not a way to duplicate a successful post. Calling it on a non-error post won't behave like "post again". Check status with `mcp__ayrshare__get_post` if unsure.
- **On failure, explain — don't auto-retry.** When any post tool errors, call `mcp__ayrshare__explain_error` to translate the API error to plain language, then surface it. Never auto-retry create/update on a 4xx (bad input, wrong key, missing permission) — retrying a write can duplicate a post. A 429 gets at most one retry after a short delay. (Mirror of the global retry-safety rule — full version in getting-started.)
