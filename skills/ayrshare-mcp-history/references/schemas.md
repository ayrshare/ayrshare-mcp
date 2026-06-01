# History — Input Schema & Examples

Endpoint is relative to the API base `https://api.ayrshare.com/api`. The MCP server reaches it through `mcp__ayrshare__get_history` (`GET /history`). Profile-scoped: pass `profileKey` for a client's history, omit it for the Business account's own. A `profileKey` can also be set as the default via the `AYRSHARE_PROFILE_KEY` env var and overridden per-call.

## `mcp__ayrshare__get_history`

`GET /history`

Returns Ayrshare post ids for posts published or scheduled through Ayrshare.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profileKey` | string | no | Profile key for profile-scoped history. Omit for account-level history. When supplied, replaces the Business key as auth. |
| `lastDays` | integer | no | Filter to posts from the last N days |
| `platform` | string (enum) | no | Filter by a single platform |

`platform` enum:
`bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube`

Examples:

```json
// One client's last 7 days on LinkedIn
{ "profileKey": "CLIENT_PROFILE_KEY", "lastDays": 7, "platform": "linkedin" }
```

```json
// Account-level full history, no filters
{}
```

```json
// Onboarding verification — confirm a freshly linked profile
{ "profileKey": "NEW_PROFILE_KEY" }
```

Returns the matching posts (published and scheduled), including each post's Ayrshare `id` — useful for feeding `mcp__ayrshare__get_post_analytics` method (a). An empty result is valid (e.g. a newly onboarded profile with no posts).

## History by Social ID (for posts not created through Ayrshare)

For posts that did **not** originate via Ayrshare, there is a history-by-social-id capability: look up a post by its **native** Social Post ID to retrieve the post's native history record (including its native `id`). That native `id` is what `mcp__ayrshare__get_post_analytics` method (b) consumes (native id + `searchPlatformId: true`). This is the bridge between History and Analytics for non-Ayrshare posts. (Source: Ayrshare docs "Posts History by Social ID", `apis/history/history-social-id`.)

- Supported platforms: **Facebook, Instagram, LinkedIn, Threads, TikTok, Twitter, YouTube**.
- The native Social Post ID can come from the `postIds` field of the `/post` endpoint, the `id` field of a standard `get_history` response, or a post URL.
- The linked account must **own** the post to retrieve its history by social id.

Underlying REST shape (for reference): `GET /history/{socialId}?searchPlatformId=true&platform={platform}`, where `searchPlatformId` is always `true` and `platform` is one of the seven supported values, e.g.:

```
GET /history/104923907983682_108329000309742?searchPlatformId=true&platform=facebook
```

The returned `id` (a native Social Post ID) then feeds analytics method (b):

```json
// Analytics on that non-Ayrshare post, by Social Post ID
{
  "id": "104923907983682_108329000309742",
  "platforms": ["facebook"],
  "searchPlatformId": true
}
```

See the Analytics skill (`../ayrshare-mcp-analytics/SKILL.md`) for the full analytics-by-social-id workflow.
