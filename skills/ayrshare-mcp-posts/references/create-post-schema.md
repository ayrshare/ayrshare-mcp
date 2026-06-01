# `mcp__ayrshare__create_post` / `mcp__ayrshare__validate_post` — full input schema

`POST /post` (create) and `POST /validate/post` (validate). `validate_post` takes the **same** content/platform inputs as `create_post` and reports platform-specific issues (character limits, unsupported media) as a dry-run — it does NOT publish. Always validate before creating.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `post` | string | Yes | The text content of the post. |
| `platforms` | array of enum | Yes | Networks to publish to. Enum: `twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads`. Always an array. See `platforms.md`. |
| `mediaUrls` | array of string | No | URLs of images/videos to attach. Must be reachable and a valid format — validate first (see `../../ayrshare-mcp-media/SKILL.md`). |
| `scheduleDate` | string (ISO 8601) | No | When to publish, e.g. `2026-06-05T14:30:00Z`. A future time schedules the post; omit to publish immediately. |
| `passthrough` | object | No | Advanced/undocumented API params. Keys are flattened onto the request top level. Credential/identity keys (`profileKey`, `apiKey`, `uid`, etc.) and snake_case aliases of validated fields are dropped — `passthrough` CANNOT carry `profileKey`. |

`create_post` is synchronous and returns per-platform `postIds`. To recover a failed send, use `retry_post` — NOT a second `create_post`.

## Profile scoping (not an input)

There is **no `profileKey` argument** on any of these tools. The profile is selected by the `Profile-Key` connection header in the MCP client config (`.mcp.json` headers). Omit the header to act under the account's primary/Business profile; set it to target a specific client profile. See `../../ayrshare-mcp-getting-started/SKILL.md`.

## Lifecycle tools (key off the returned `id`)

| Tool | Endpoint | Inputs |
|------|----------|--------|
| `mcp__ayrshare__get_post` | GET `/post/:id` | `id` (required) — the ONLY input |
| `mcp__ayrshare__update_post` | PATCH `/post` | `id` (required) + at least one of: `scheduleDate`, `approved` (bool), `notes` (string), `disableComments` (bool), `scheduledPause` (bool), `youTubeOptions` (object); optional `passthrough`. Primarily for editing/approving/rescheduling a PENDING post. |
| `mcp__ayrshare__retry_post` | PUT `/post/retry` | `id` (required, must be a post in status `error`); optional `passthrough`. Retries ONCE, only if the error was retryable. |

## Reminders

- Validate (`mcp__ayrshare__validate_post`) → confirm with the user → create (`mcp__ayrshare__create_post`). On per-platform failure, call `mcp__ayrshare__explain_error`.
- `create_post` returns an `id`. Capture it — every other tool here needs it.
- `scheduleDate` omitted = post now. Never pass an empty string.
- `update_post` requires at least one editable field alongside `id`; it is primarily for PENDING posts.
- `retry_post` only applies to posts in status `error`, retries once, and only if retryable.
