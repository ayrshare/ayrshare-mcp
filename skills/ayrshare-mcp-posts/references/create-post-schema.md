# `mcp__ayrshare__create_post` / `mcp__ayrshare__validate_post` — full input schema

`POST /post` (create) and `POST /post/validate` (validate) — both profile-scoped. `validate_post` takes the same content/platform inputs as `create_post` and reports platform-specific issues (character limits, unsupported media) without publishing. Always validate before creating.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `post` | string | Yes | The text content of the post. |
| `platforms` | array of enum | Yes | Networks to publish to. Enum: `bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube`. Always an array. See `platforms.md`. |
| `profileKey` | string | No | Profile to post on behalf of. May come from the `AYRSHARE_PROFILE_KEY` env default or this per-call param (per-call overrides the default). Omit (with no env default) to post under the Business account. |
| `mediaUrls` | array of string | No | URLs of images/videos to attach. Must be reachable and a valid format — verify first (see `../../ayrshare-mcp-media/SKILL.md`). |
| `scheduleDate` | string (ISO 8601) | No | When to publish, e.g. `2026-06-05T14:30:00Z`. Omit to publish immediately. |
| `shortenLinks` | boolean | No | (create_post only) Shorten URLs found in `post` text. |

## X/Twitter BYO credentials

If you are bringing your own X/Twitter app credentials, `X_API_KEY` and `X_API_SECRET` are supplied as connection headers when posting to `twitter` (per the repo's `/ayrshare:post` flow). They are configured in the environment, not passed in the post body.

## Lifecycle tools (key off the returned `id`)

| Tool | Endpoint | Inputs |
|------|----------|--------|
| `mcp__ayrshare__get_post` | GET `/post` | `id` (required), `profileKey` (optional) |
| `mcp__ayrshare__update_post` | PUT `/post` | `id` (required) + fields to change, `profileKey` (optional) |
| `mcp__ayrshare__delete_post` | DELETE `/post` | `id` (required), `profileKey` (optional) |
| `mcp__ayrshare__retry_post` | POST `/post/retry` | `id` (required, must be a FAILED post), `profileKey` (optional) |

## Reminders

- Validate (`mcp__ayrshare__validate_post`) → confirm with the user → create (`mcp__ayrshare__create_post`). On per-platform failure, call `mcp__ayrshare__explain_error`.
- `create_post` returns an `id`. Capture it — every other tool here needs it.
- `scheduleDate` omitted = post now. Never pass an empty string.
- TEST-account posts cannot be deleted.
- `retry_post` only applies to posts that FAILED.
