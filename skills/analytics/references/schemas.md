# Analytics — Input Schemas & Examples

The MCP server exposes three analytics tools:

- `mcp__ayrshare__get_post_analytics` → `POST /analytics/post` — per-post metrics by **Ayrshare Post ID**.
- `mcp__ayrshare__get_post_analytics_by_social_id` → `POST /analytics/post` — per-post metrics by **native Social Post ID**.
- `mcp__ayrshare__get_social_network_analytics` → `POST /analytics/social` — account/network-level analytics.

All three are scoped to the profile set by the `Profile-Key` connection header. **No tool takes a `profileKey` argument** — profile scoping is the connection's `Profile-Key` header (set in the MCP client config), not a per-call parameter. Omit the header to act on the account's primary/Business profile.

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

Example call:

```json
{ "id": "AYRSHARE_POST_ID_HERE" }
```

Narrow to specific networks:

```json
{ "id": "AYRSHARE_POST_ID_HERE", "platforms": ["instagram", "linkedin"] }
```

Returns per-network engagement metrics for that post (likes, comments, shares, views, etc.). Available fields differ by platform, and a freshly published post may return zeros until metrics populate. YouTube/TikTok can take 24-48 h to populate; Pinterest impressions can take 24-72 h. (Source: Ayrshare docs "Analytics on a Post", `apis/analytics/post`.)

---

## `mcp__ayrshare__get_post_analytics_by_social_id`

`POST /analytics/post`

The same per-post metrics, but for a post identified by its **native Social Post ID** — for posts that did **not** originate via Ayrshare, or when you only have the native id. This is a separate tool from `get_post_analytics`; the difference is the id type and the required single `platform`.

`mcp__ayrshare__get_platform_history` is one way to find the native Social Post ID (the `id` field), but only for the platforms it covers — it excludes **gmb, reddit, and telegram**, so for a network it doesn't cover (e.g. reddit, which *is* an ANALYTICS_PLATFORMS value) take the native id from the platform itself. See the History skill. Supported analytics platforms (ANALYTICS_PLATFORMS): **bluesky, facebook, instagram, linkedin, pinterest, reddit, snapchat, threads, tiktok, twitter, youtube**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | A single native Social Post ID (the network's own post id). |
| `platform` | string | yes | Exactly **one** platform from ANALYTICS_PLATFORMS (singular, not an array). |

The MCP boundary locks the request body to `{ id, platforms: [platform], searchPlatformId: true }` — no extra keys are forwarded.

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

**Account/network-level analytics** — followers, impressions, views, demographics, and other profile-level numbers (and reach, where the platform provides it) — for the requested social network(s). This is the **social network account's** analytics, **not** an Ayrshare User Profile.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platforms` | string[] | yes | One or more platforms from POST_PLATFORMS. |
| `quarters` | number | no | Number of quarters of historical data to return (1-4). Only values >= 1 activate date filtering; omit (or 0) for all-time. Incompatible with `period60Days`. |
| `daily` | boolean | no | Return daily time-series values instead of aggregated totals (Facebook, Instagram, Snapchat, TikTok, YouTube). **Do not combine with `period60Days`.** |
| `period60Days` | boolean | no | TikTok only. Returns only 60-day aggregate totals for comments, shares, and views. **Do not combine with `daily`.** |
| `youtube` | object | no | `{ lifetime: bool }` — when `lifetime` is true, include `lifetimeLikes` (sum of likes across all public channel videos; channels with >1,000 videos return null; cached 24 h). |
| `userId` | string | no | X/Twitter only. Analytics for a specific user by numeric Twitter ID instead of the linked account. Use the API key only — no Profile-Key. |
| `userName` | string | no | X/Twitter only. Analytics for a specific user by handle instead of the linked account. Use the API key only — no Profile-Key. |

Example call:

```json
{ "platforms": ["instagram", "linkedin"] }
```

With options (`daily` and `period60Days` are mutually exclusive — pick one):

```json
{ "platforms": ["instagram", "linkedin"], "quarters": 2, "daily": true }
```

```json
{ "platforms": ["tiktok"], "period60Days": true }
```

Returns network-level metrics per requested social network (followers, impressions, views, demographics, etc.; reach where the platform provides it). Some metrics require platform eligibility (e.g. business/creator accounts) and are simply absent otherwise. Facebook needs >=100 page likes for full analytics; Instagram demographics need >=100 engagements in 30 days; LinkedIn/TikTok may lag 24-48 h. This is the account/network-level endpoint — it does **not** return per-post engagement; for that, use `get_post_analytics` or `get_post_analytics_by_social_id`. (Source: Ayrshare docs "Analytics on a Social Network", `apis/analytics/social`.)
