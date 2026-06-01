# Analytics — Input Schemas & Examples

The MCP server exposes three analytics tools:

- `mcp__ayrshare__get_post_analytics` → `POST /analytics/post` — per-post metrics by **Ayrshare Post ID**.
- `mcp__ayrshare__get_post_analytics_by_social_id` → `POST /analytics/post` — per-post metrics by **native Social Post ID**.
- `mcp__ayrshare__get_social_network_analytics` → `POST /analytics/social` — account/network-level analytics.

All three are scoped to the profile set by the `Profile-Key` connection header. **No tool takes a `profileKey` argument** — profile scoping is the connection's `Profile-Key` header (set in the MCP client config), not a per-call parameter, and `passthrough` cannot carry it. Omit the header to act on the account's primary/Business profile. Most tools also accept an optional `passthrough` object (record) for advanced/undocumented API params; its keys are flattened onto the request top level (credential/identity keys are dropped).

Platform enums:
- `POST_PLATFORMS` (used by `get_social_network_analytics`, and by `platforms` in `get_post_analytics`): twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads.
- `ANALYTICS_PLATFORMS` (used by `get_post_analytics_by_social_id`): bluesky, facebook, instagram, linkedin, pinterest, reddit, snapchat, threads, tiktok, twitter, youtube.

---

## `mcp__ayrshare__get_post_analytics`

`POST /analytics/post`

Engagement metrics for one **specific post sent via Ayrshare**, identified by its **Ayrshare Post ID**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | The Ayrshare Post ID returned by `mcp__ayrshare__create_post` (or found via `mcp__ayrshare__get_post_history`). |
| `platforms` | string[] | no | Subset of POST_PLATFORMS to narrow the response to specific networks for that post. |
| `passthrough` | object | no | Advanced/undocumented API params; flattened onto the request top level. |

Example call:

```json
{ "id": "AYRSHARE_POST_ID_HERE" }
```

Narrow to specific networks:

```json
{ "id": "AYRSHARE_POST_ID_HERE", "platforms": ["instagram", "linkedin"] }
```

Returns per-network engagement metrics for that post (likes, comments, shares, views, etc.). Available fields differ by platform, and a freshly published post may return zeros until metrics populate. (Source: Ayrshare docs "Analytics on a Post", `apis/analytics/post`.)

---

## `mcp__ayrshare__get_post_analytics_by_social_id`

`POST /analytics/post`

The same per-post metrics, but for a post identified by its **native Social Post ID** — for posts that did **not** originate via Ayrshare, or when you only have the native id. This is a separate tool from `get_post_analytics`; the difference is the id type and the required single `platform`.

`mcp__ayrshare__get_platform_history` is one way to find the native Social Post ID (the `id` field), but only for the platforms it covers — it excludes **gmb, reddit, and telegram**, so for a network it doesn't cover (e.g. reddit, which *is* an ANALYTICS_PLATFORMS value) take the native id from the platform itself. See the History skill. Supported analytics platforms (ANALYTICS_PLATFORMS): **bluesky, facebook, instagram, linkedin, pinterest, reddit, snapchat, threads, tiktok, twitter, youtube**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | A single native Social Post ID (the network's own post id). |
| `platform` | string | yes | Exactly **one** platform from ANALYTICS_PLATFORMS (singular, not an array). |
| `passthrough` | object | no | Advanced/undocumented API params; flattened onto the request top level. |

Example — a Facebook post by Social Post ID:

```json
{
  "id": "104923907983682_108329000309742",
  "platform": "facebook"
}
```

Example — an X/Twitter post by Social Post ID:

```json
{
  "id": "1979851549871354062",
  "platform": "twitter"
}
```

Notes / gotchas:
- **Use for posts not sent via Ayrshare.** For Ayrshare-sent posts, use `get_post_analytics` with the Ayrshare Post ID.
- **One platform per call.** `platform` is a single value; query a different network with a separate call.
- **Ownership required.** The linked account must own the post. **Exception: YouTube** — a non-owned video returns descriptive metadata (title, description, tags, channel title, privacy status, thumbnail URLs) but **zeros** for all numeric metrics (views, likes, comments, shares, subscriber changes, watch time, playlist additions).
- **X/Twitter threads:** query each tweet's Social Post ID with its own call; thread replies are not auto-included when querying the parent tweet.
- X does not return non-public or organic metrics for posts not sent by the authorized user.
- Instagram posts published before the account was converted to a business account have limited analytics.

The response shape matches `get_post_analytics` — see "Analytics on a Post by Social ID" (`apis/analytics/social-by-id`).

---

## `mcp__ayrshare__get_social_network_analytics`

`POST /analytics/social`

**Account/network-level analytics** — followers, impressions, reach, demographics, and other profile-level numbers — for the requested social network(s). This is the **social network account's** analytics, **not** an Ayrshare User Profile.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platforms` | string[] | yes | One or more platforms from POST_PLATFORMS. |
| `quarters` | number | no | Number of quarters of historical data to return (1–4). |
| `daily` | boolean | no | Return daily-granularity data points. |
| `period60Days` | boolean | no | TikTok: return the 60-day period view. |
| `passthrough` | object | no | Advanced/undocumented API params; flattened onto the request top level. |

Example call:

```json
{ "platforms": ["instagram", "linkedin"] }
```

With options:

```json
{ "platforms": ["tiktok"], "quarters": 2, "daily": true, "period60Days": true }
```

Returns network-level metrics per requested social network (followers, impressions, reach, demographics, etc.). Some metrics require platform eligibility (e.g. business/creator accounts) and are simply absent otherwise. This is the account/network-level endpoint — it does **not** return per-post engagement; for that, use `get_post_analytics` or `get_post_analytics_by_social_id`. (Source: Ayrshare docs "Analytics on a Social Network", `apis/analytics/social`.)
