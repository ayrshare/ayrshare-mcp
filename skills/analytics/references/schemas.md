# Analytics — Input Schemas & Examples

Endpoints are relative to the API base `https://api.ayrshare.com/api`. The MCP server reaches them through the tools `mcp__ayrshare__get_post_analytics` (`POST /analytics/post`) and `mcp__ayrshare__get_social_analytics` (`POST /analytics/social`).

Both tools are profile-scoped: pass `profileKey` to read a client's analytics, omit it to read the Business account's own. A `profileKey` can also be set as the default via the `AYRSHARE_PROFILE_KEY` env var and overridden per-call.

Platform enum (used by `get_social_analytics`):
`bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube`

---

## `mcp__ayrshare__get_post_analytics`

`POST /analytics/post`

Metrics for one **specific post**. There are **two lookup methods**; choose based on whether the post originated via Ayrshare.

### Method (a) — by Ayrshare Post ID (default, for posts sent via Ayrshare)

Use the `id` returned by `mcp__ayrshare__create_post` (or found via `mcp__ayrshare__get_history`). No `searchPlatformId`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | The Ayrshare Post ID returned by `mcp__ayrshare__create_post` (or found via `mcp__ayrshare__get_history`) |
| `profileKey` | string | no | Read a specific profile's post analytics. Omit for the Business account. When supplied, replaces the Business key as auth. |

Example call:

```json
{ "id": "AYRSHARE_POST_ID_HERE", "profileKey": "OPTIONAL_PROFILE_KEY" }
```

Returns per-network engagement metrics for that post (likes, comments, shares, views, etc.). Available fields differ by platform, and a freshly published post may return zeros until metrics populate.

### Method (b) — by Social Post ID (for posts NOT sent via Ayrshare)

For posts that did **not** originate via Ayrshare, pass the social network's **native** post id plus `searchPlatformId: true` to tell the endpoint you're searching by Social Post ID. The same `POST /analytics/post` call is used — only the id type and the `searchPlatformId` flag change.

Find the native Social Post ID via the **get-history-by-social-id** path (the `id` field) — see the History skill. (Source: Ayrshare docs "Analytics on a Post by Social ID", `apis/analytics/social-by-id`.)

Supported platforms: **Facebook, Instagram, LinkedIn, Threads, TikTok, Twitter, YouTube**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | one of `id`/`postIds` | A single Social Post ID (the native id from the social network). |
| `postIds` | string[] | one of `id`/`postIds` | Batch of Social Post IDs (max 100) to fetch in one request. |
| `platforms` | string[] | yes | Exactly **one** platform value, from the supported set above. |
| `searchPlatformId` | boolean | yes | Must be `true` to search by Social Post ID. |
| `profileKey` | string | no | Read a specific profile's analytics. Omit for the Business account. When supplied, replaces the Business key as auth. |

Example — single Facebook post by Social Post ID:

```json
{
  "id": "104923907983682_108329000309742",
  "platforms": ["facebook"],
  "searchPlatformId": true
}
```

Example — batch of X/Twitter posts by Social Post ID:

```json
{
  "postIds": ["1979851549871354062", "2011793803951137234"],
  "platforms": ["twitter"],
  "searchPlatformId": true
}
```

Notes / gotchas for method (b):
- **Recommended only for posts not sent via Ayrshare.** For Ayrshare-sent posts, use method (a) with the Ayrshare Post ID.
- **Ownership required.** The linked account must own the post. **Exception: YouTube** — a non-owned video returns descriptive metadata (title, description, tags, channel title, privacy status, thumbnail URLs) but **zeros** for all numeric metrics (views, likes, comments, shares, subscriber changes, watch time, playlist additions).
- **X/Twitter threads:** each tweet's Social Post ID must be supplied individually via `postIds`; thread replies are not auto-included when querying the parent tweet.
- X does not return non-public or organic metrics for posts not sent by the authorized user.
- Instagram posts published before the account was converted to a business account have limited analytics.

The response shape is identical to method (a) — see "Analytics on a Post" (`apis/analytics/post`).

---

## `mcp__ayrshare__get_social_analytics`

`POST /analytics/social`

**Analytics on a social network** — account/network-level metrics such as followers, impressions, reach, and other profile-level numbers — for the requested platform(s).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platforms` | string[] | yes | One or more platforms from the enum above |
| `profileKey` | string | no | Read a specific profile's social-network analytics. Omit for the Business account. When supplied, replaces the Business key as auth. |

Example call:

```json
{ "platforms": ["instagram", "linkedin"], "profileKey": "OPTIONAL_PROFILE_KEY" }
```

Returns network-level metrics per requested social network (followers, impressions, reach, etc.). Some metrics require platform eligibility (e.g. business/creator accounts) and are simply absent otherwise. This is the "analytics on a social network" endpoint — it does **not** return per-post engagement; for that, use `mcp__ayrshare__get_post_analytics`.
