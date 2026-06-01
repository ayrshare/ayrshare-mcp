# History — Input Schemas & Examples

The MCP server reaches the Ayrshare API through two history tools:

- `mcp__ayrshare__get_post_history` (`GET /history`) — posts sent via Ayrshare (Ayrshare Post IDs).
- `mcp__ayrshare__get_platform_history` (`GET /history/:platform`) — native social posts, including posts not made via Ayrshare (native Social Post IDs).

Both are **profile-scoped via the connection's `Profile-Key` header**, not a per-call argument. Include `Profile-Key: <profileKey>` in the MCP client config (`.mcp.json` headers) to act as one client profile; omit it to act on the account's primary/Business profile. There is no `profileKey` parameter on either tool, and `passthrough` cannot carry one (it is a blocked credential key).

## `mcp__ayrshare__get_post_history`

`GET /history`

Returns Ayrshare Post IDs for posts published or scheduled through Ayrshare. All fields optional.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `limit` | integer | no | Max number of posts to return, 1-1000. Default 25. |
| `platforms` | string[] (enum) | no | Filter to a subset of POST platforms. |
| `startDate` | string (ISO 8601) | no | Start of an explicit date window. |
| `endDate` | string (ISO 8601) | no | End of an explicit date window. |
| `lastDays` | integer | no | Filter to posts from the last N days. Default 30; pass `0` for all time. |
| `status` | string (enum) | no | Filter by lifecycle state. One of: `awaiting approval`, `deleted`, `error`, `paused`, `pending`, `success`. |
| `type` | string | no | Filter by post type. |
| `passthrough` | object | no | Advanced/undocumented API params, flattened onto the request. Credential keys (`profileKey`, `apiKey`, `uid`, etc.) are dropped. |

`platforms` enum (subset of the 13 POST platforms):
`twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads`

Examples:

```json
// Last 7 days on LinkedIn, up to 50 posts (profile chosen by the connection's Profile-Key header)
{ "lastDays": 7, "platforms": ["linkedin"], "limit": 50 }
```

```json
// Default recent history, no filters (last 30 days, up to 25 posts)
{}
```

```json
// All time, only failed posts
{ "lastDays": 0, "status": "error" }
```

```json
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
| `limit` | integer | no | Max number of posts to return, 1-500. |
| `skipAnalytics` | boolean | no | Skip the inline analytics payload for faster, lighter responses. |
| `pagePublished` | boolean | no | Facebook only — restrict to posts published by the Page. |
| `userId` | string | no | Twitter/X only — target user id. |
| `userName` | string | no | Twitter/X only — target user handle. |
| `next` | string | no | Pagination cursor returned by a prior call. |
| `since` | string (ISO 8601) | no | Facebook only — start of date window. |
| `until` | string (ISO 8601) | no | Facebook only — end of date window. |
| `dataType` | string (enum) | no | `posts` or `stories`. |
| `passthrough` | object | no | Advanced/undocumented API params, flattened onto the request. Credential keys (`profileKey`, `apiKey`, `uid`, etc.) are dropped. |

`platform` enum (the 10 history platforms — note this excludes `gmb`, `reddit`, and `telegram`):
`bluesky, facebook, instagram, linkedin, pinterest, snapchat, threads, tiktok, twitter, youtube`

Examples:

```json
// Native Facebook posts, last published window, lighter response
{ "platform": "facebook", "skipAnalytics": true, "since": "2026-05-01T00:00:00Z", "until": "2026-06-01T00:00:00Z" }
```

```json
// Native Instagram stories
{ "platform": "instagram", "dataType": "stories" }
```

```json
// Paginate to the next page of native Twitter/X posts
{ "platform": "twitter", "limit": 100, "next": "CURSOR_FROM_PRIOR_CALL" }
```

The returned native Social Post `id` then feeds analytics-by-social-id:

```json
// Analytics on a non-Ayrshare post, by native Social Post ID
{
  "id": "104923907983682_108329000309742",
  "platform": "facebook"
}
```

See the Analytics skill (`../ayrshare-mcp-analytics/SKILL.md`) for the full analytics-by-social-id workflow.
