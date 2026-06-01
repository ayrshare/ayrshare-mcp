# Example payloads — Ayrshare MCP posts

Inputs passed to the MCP tools. Platforms prioritized: twitter, facebook, instagram, linkedin. Remember the required order: `mcp__ayrshare__validate_post` → confirm with the user → `mcp__ayrshare__create_post`.

## Validate before posting

```json
{
  "post": "We just shipped dark mode. Try it out and tell us what you think.",
  "platforms": ["twitter", "linkedin"]
}
```

This is `mcp__ayrshare__validate_post`. It reports platform-specific issues (char limits, unsupported media) without publishing. Surface any issues, ask how to proceed, then confirm and call `mcp__ayrshare__create_post` with the same inputs.

## Post now to X/Twitter and LinkedIn (under the Business account)

```json
{
  "post": "We just shipped dark mode. Try it out and tell us what you think.",
  "platforms": ["twitter", "linkedin"]
}
```

## Schedule a post for a specific client profile

```json
{
  "post": "Join our webinar this Friday at 10am PT. Link in bio.",
  "platforms": ["facebook", "instagram", "linkedin"],
  "profileKey": "PROFILE_KEY_FROM_CREATE_PROFILE",
  "scheduleDate": "2026-06-05T17:00:00Z"
}
```

Note: `scheduleDate` is absolute ISO 8601 in UTC. "Friday at 10am PT" was converted to `2026-06-05T17:00:00Z` before the call — the API does not parse human phrasing. `profileKey` here overrides any `AYRSHARE_PROFILE_KEY` env default.

## Post with attached media + link shortening

```json
{
  "post": "Our new case study is live: https://example.com/case-study/acme",
  "platforms": ["twitter", "facebook"],
  "mediaUrls": ["https://cdn.example.com/casestudy-hero.jpg"],
  "shortenLinks": true
}
```

The `mediaUrls` entry should be a URL you've already confirmed reachable/valid via `mcp__ayrshare__verify_media` (see `../../ayrshare-mcp-media/SKILL.md`).

## Fetch a post's status

```json
{ "id": "POST_ID_RETURNED_BY_CREATE_POST" }
```

## Update a scheduled post (push the time back)

```json
{
  "id": "POST_ID_RETURNED_BY_CREATE_POST",
  "scheduleDate": "2026-06-06T17:00:00Z"
}
```

## Delete a post

```json
{ "id": "POST_ID_RETURNED_BY_CREATE_POST" }
```

(Will not remove posts made through TEST accounts — those are permanent.)

## Retry a FAILED post

```json
{ "id": "FAILED_POST_ID" }
```

Only valid when the post's prior send failed. Check with `mcp__ayrshare__get_post` if unsure. On any error, call `mcp__ayrshare__explain_error` and surface the plain-language explanation rather than auto-retrying a 4xx.
