# History — Input Schemas & Examples

The MCP server reaches the Ayrshare API through two history tools:

- `mcp__ayrshare__get_post_history` (`GET /history`) — posts sent via Ayrshare (Ayrshare Post IDs).
- `mcp__ayrshare__get_platform_history` (`GET /history/:platform`) — native social posts, including posts not made via Ayrshare (native Social Post IDs).

Both are **profile-scoped**: choose the profile with an optional `profileKey` tool argument or the `Profile-Key` connection header (the argument wins when both are set). With neither, calls act on the account's primary/Business profile.

## `mcp__ayrshare__get_post_history`

`GET /history`

Returns Ayrshare Post IDs for posts published or scheduled through Ayrshare. All fields optional.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `limit` | integer | no | Max number of posts to return, 1-1000. Default 25. (Results are cached ~1 min when `limit` > 25.) |
| `platforms` | string[] (enum) | no | Filter to a subset of POST platforms (OR logic). |
| `startDate` | string (ISO 8601) | no | Start of an explicit date window (inclusive). |
| `endDate` | string (ISO 8601) | no | End of an explicit date window (inclusive). Use with `startDate`. |
| `lastDays` | integer | no | Filter to posts from the last N days. Default 30; pass `0` for all time. Ignored when both `startDate` and `endDate` are provided. |
| `status` | string (enum) | no | Filter by lifecycle state. One of: `awaiting approval`, `deleted`, `error`, `paused`, `pending`, `processing`, `success`. (`deleted` posts are only returned when this is explicitly set to `deleted`; `processing` means the post is currently being sent.) |
| `type` | string (enum) | no | Filter by post type: `immediate` (sent right away) or `scheduled` (used `scheduleDate`). |
| `autoRepostId` | string | no | Filter by auto-repost series ID (assigned when creating an auto-repost). Pass `all` to retrieve all auto-repost series. |

`platforms` enum (subset of the 13 POST platforms):
`twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads`

Examples:

```jsonc
// Last 7 days on LinkedIn, up to 50 posts (profile chosen by the connection's Profile-Key header)
{ "lastDays": 7, "platforms": ["linkedin"], "limit": 50 }
```

```jsonc
// Default recent history, no filters (last 30 days, up to 25 posts)
{}
```

```jsonc
// All time, only failed posts
{ "lastDays": 0, "status": "error" }
```

```jsonc
// Onboarding verification — confirm a freshly linked profile.
// Scope comes from the connection's Profile-Key header, not this payload.
{}
```

Returns the matching posts (published and scheduled), including each post's Ayrshare `id` — the id you feed to `mcp__ayrshare__get_post_analytics`, `mcp__ayrshare__get_post`, `mcp__ayrshare__update_post`, and `mcp__ayrshare__retry_post`. An empty result is valid (e.g. a newly onboarded profile with no posts).

## `mcp__ayrshare__get_platform_history`

`GET /history/:platform`

Returns **native** social posts for a single platform, **including posts not created through Ayrshare**. Each record carries a native Social Post `id` — the id you feed to `mcp__ayrshare__get_post_analytics_by_social_id` (native id + `platform`). This is the bridge between History and Analytics for non-Ayrshare posts.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string (enum) | **yes** | The single platform to read native history for. |
| `limit` | integer | no | Max number of posts to return, 1-500 (default 10). Keep at or below 100 for best performance. |
| `skipAnalytics` | boolean | no | Return only the Social Post ID without full analytics (faster; avoids errors when limit > 100). |
| `pagePublished` | boolean | no | Facebook only — when true, return only posts published by the Page itself. |
| `userId` | string | no | Twitter/X only, target user by numeric Twitter ID. Use the API key only; a `profileKey` (argument or `Profile-Key` header) returns Error 400. |
| `userName` | string | no | Twitter/X only, target user by handle. Use the API key only; a `profileKey` (argument or `Profile-Key` header) returns Error 400. |
| `next` | string | no | Pagination cursor returned by a prior call (`meta.pagination.next`). |
| `since` | string | no | Facebook only — ISO date filtering posts on or after (e.g. `2026-03-17`). |
| `until` | string | no | Facebook only — ISO date filtering posts on or before (e.g. `2026-03-20`). |
| `dataType` | string (enum) | no | Facebook and Instagram only — `posts` or `stories`. Omit to return both. |

`platform` enum (the 10 history platforms — note this excludes `gmb`, `reddit`, and `telegram`):
`bluesky, facebook, instagram, linkedin, pinterest, snapchat, threads, tiktok, twitter, youtube`

Examples:

```jsonc
// Native Facebook posts, last published window, lighter response
{ "platform": "facebook", "skipAnalytics": true, "since": "2026-05-01", "until": "2026-06-01" }
```

```jsonc
// Native Instagram stories
{ "platform": "instagram", "dataType": "stories" }
```

```jsonc
// Paginate to the next page of native Twitter/X posts
{ "platform": "twitter", "limit": 100, "next": "CURSOR_FROM_PRIOR_CALL" }
```

The returned native Social Post `id` then feeds analytics-by-social-id:

```jsonc
// Analytics on a non-Ayrshare post, by native Social Post ID
{
  "id": "104923907983682_108329000309742",
  "platform": "facebook"
}
```

See the Analytics skill (`../../analytics/SKILL.md`) for the full analytics-by-social-id workflow.
