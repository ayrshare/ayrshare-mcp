# Example payloads — Ayrshare MCP posts

Inputs passed to the MCP tools. Platforms prioritized: twitter, facebook, instagram, linkedin. Remember the required order: `mcp__ayrshare__validate_post` → confirm with the user → `mcp__ayrshare__create_post`.

Profile scoping is **not** in these payloads — it is the `Profile-Key` connection header (set in the MCP client config), never a per-call `profileKey` argument. See `../../getting-started/SKILL.md`.

## Validate before posting (dry-run)

```json
{
  "post": "We just shipped dark mode. Try it out and tell us what you think.",
  "platforms": ["twitter", "linkedin"]
}
```

This is `mcp__ayrshare__validate_post`. It reports platform-specific issues (char limits, unsupported media) WITHOUT publishing. Surface any issues, ask how to proceed, then confirm and call `mcp__ayrshare__create_post` with the same inputs.

## Post now to X/Twitter and LinkedIn

```json
{
  "post": "We just shipped dark mode. Try it out and tell us what you think.",
  "platforms": ["twitter", "linkedin"]
}
```

This posts under whichever profile the connection's `Profile-Key` header selects (the primary/Business profile if the header is unset).

## Schedule a post

```json
{
  "post": "Join our webinar this Friday at 10am PT. Link in bio.",
  "platforms": ["facebook", "instagram", "linkedin"],
  "scheduleDate": "2026-06-05T17:00:00Z"
}
```

Note: `scheduleDate` is absolute ISO 8601 in UTC, and must be a future time. "Friday at 10am PT" was converted to `2026-06-05T17:00:00Z` before the call — the API does not parse human phrasing. To schedule for a different client profile, reconfigure the connection's `Profile-Key` header; there is no per-call profile argument.

## Post with attached media

```json
{
  "post": "Our new case study is live: https://example.com/case-study/acme",
  "platforms": ["twitter", "facebook"],
  "mediaUrls": ["https://cdn.example.com/casestudy-hero.jpg"]
}
```

The `mediaUrls` entry should be a URL you've already confirmed reachable/valid via `mcp__ayrshare__validate_media` (see `../../media/SKILL.md`).

## Fetch a post's status

```json
{ "id": "POST_ID_RETURNED_BY_CREATE_POST" }
```

`id` is the only input to `mcp__ayrshare__get_post`.

## Reschedule a pending post (push the time back)

```json
{
  "id": "POST_ID_RETURNED_BY_CREATE_POST",
  "scheduleDate": "2026-06-06T17:00:00Z"
}
```

`mcp__ayrshare__update_post` requires `id` plus at least one editable field. Editable fields: `scheduleDate`, `approved`, `notes`, `disableComments`, `scheduledPause`, `youTubeOptions`.

## Approve a pending post

```json
{
  "id": "POST_ID_RETURNED_BY_CREATE_POST",
  "approved": true
}
```

## Retry a post that errored

```json
{ "id": "ERRORED_POST_ID" }
```

`mcp__ayrshare__retry_post` only applies when the post is in status `error`; it retries ONCE and only if the error was retryable. Check status with `mcp__ayrshare__get_post` if unsure. On any error, call `mcp__ayrshare__explain_error` and surface the plain-language explanation rather than auto-retrying a 4xx. To recover a failure, use `retry_post` — not a second `create_post`.
