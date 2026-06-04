---
name: analytics
description: |
  Social media analytics for the Ayrshare MCP server — metrics for a specific post, and account/network-level analytics on a connected social network (followers, impressions, reach, demographics). Use whenever someone wants performance data: "how did my post do", "engagement on that tweet", likes/comments/shares/views/impressions/reach for a post, follower counts, reach or impressions for an account, "analytics for our LinkedIn", "how is our Instagram growing", or comparing networks. Also use when pulling analytics for a post that was NOT created through Ayrshare (by its native Social Post ID). Trigger when calling `mcp__ayrshare__get_post_analytics`, `mcp__ayrshare__get_post_analytics_by_social_id`, or `mcp__ayrshare__get_social_network_analytics`, and even without the word "Ayrshare" — if the user wants social media stats for a post or a network through an AI assistant, this is the skill. For the shared auth model and retry rules, see `../getting-started/SKILL.md`.
---

# Ayrshare MCP — Analytics

Three analytics tools, split by *what* they measure and *which kind of id* identifies the post. Picking the wrong one is the main failure mode in this group, so anchor on the distinction before calling any of them:

- **`mcp__ayrshare__get_post_analytics`** — metrics for one **specific post sent via Ayrshare**: its likes, comments, shares, views, etc. Identify the post by its **Ayrshare Post ID** (the `id` returned by `mcp__ayrshare__create_post` or found via `mcp__ayrshare__get_post_history`).
- **`mcp__ayrshare__get_post_analytics_by_social_id`** — the same per-post metrics, but for a post identified by its **native Social Post ID** (the network's own id). Use this for posts that did *not* originate via Ayrshare, or when all you have is the native id.
- **`mcp__ayrshare__get_social_network_analytics`** — **account/network-level analytics** for a connected social network: followers, impressions, views, demographics, and other profile-level numbers (and reach, where the platform provides it). This is the **social network account's** analytics, **not** an Ayrshare User Profile's.

All three are profile-scoped: choose the profile with an optional `profileKey` tool argument or the `Profile-Key` header (see Auth below; the argument wins when both are set).

## Functions

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__get_post_analytics` | Engagement metrics for a post sent via Ayrshare | `POST /analytics/post` | `id` — the Ayrshare Post ID | `platforms` (subset of POST_PLATFORMS) |
| `mcp__ayrshare__get_post_analytics_by_social_id` | Engagement metrics for a post by its native Social Post ID | `POST /analytics/post` | `id` — the native Social Post ID; `platform` — exactly **one** of `ANALYTICS_PLATFORMS` | — (none) |
| `mcp__ayrshare__get_social_network_analytics` | Account/network-level analytics (followers, impressions, views, demographics) | `POST /analytics/social` | `platforms` — array of POST_PLATFORMS | `quarters` (1–4), `daily` (bool), `period60Days` (bool, TikTok; not with `daily`), `youtube` (`{ lifetime: bool }`), `userId` (X only), `userName` (X only) |

`ANALYTICS_PLATFORMS` (for `get_post_analytics_by_social_id`): bluesky, facebook, instagram, linkedin, pinterest, reddit, snapchat, threads, tiktok, twitter, youtube.

Full input schemas, example payloads, the per-platform metric notes, and example responses are in [`references/schemas.md`](references/schemas.md).

## Auth

All three tools are profile-scoped: choose the profile with an optional `profileKey` tool argument or the `Profile-Key` connection header (the argument wins when both are set). To read a specific client's analytics, pass that client's `profileKey` as the argument, or configure the connection's `Profile-Key`; with neither set, calls read the account's primary/Business profile. Full model: `../getting-started/SKILL.md`.

**Exception, `get_social_network_analytics` `userId`/`userName` (Twitter/X):** targeting a specific X user by `userId` (numeric Twitter ID) or `userName` (handle) instead of the linked account must use the **API key only**; that lookup is not profile-scoped. Supplying a `profileKey` (argument *or* `Profile-Key` header) alongside `userId`/`userName` returns **Error 400**. All other analytics calls are profile-scoped as above. See `references/schemas.md`.

## Usage guidance

- **Choose by scope first, then by id type.** "How did this post do" → a post-analytics tool. "How many followers / what's our reach / analytics on our LinkedIn network" → `get_social_network_analytics` with the platform(s). Post-level and network-level tools are not interchangeable and rarely both needed for one question.
- **Pick the post tool by where the post came from:**
  - **Sent via Ayrshare → `get_post_analytics`.** Pass the Ayrshare Post `id` returned by `mcp__ayrshare__create_post` (or found via `mcp__ayrshare__get_post_history`). Optionally narrow to a subset of `platforms`. This is the recommended path for any Ayrshare-sent post.
  - **Made outside Ayrshare (or you only have the native id) → `get_post_analytics_by_social_id`.** Pass the social network's **native** post id as `id` plus exactly one `platform` from ANALYTICS_PLATFORMS. `mcp__ayrshare__get_platform_history` is *one* way to find that native id (the `id` field), but only for the platforms it covers — it excludes **gmb, reddit, and telegram**, so for a network it doesn't cover (e.g. reddit, which *is* an ANALYTICS_PLATFORMS value) take the native id from the platform itself. See the History skill for that workflow.
- **Get the id first.** For `get_post_analytics`, look up the Ayrshare `id` via `create_post` output or `mcp__ayrshare__get_post_history`. For `get_post_analytics_by_social_id`, look up the native Social Post ID via `mcp__ayrshare__get_platform_history` where it's supported (it excludes gmb, reddit, telegram); otherwise take the native id directly from the platform. If the user only describes a post in prose, resolve the id before calling.
- **`get_social_network_analytics` is the social network account's analytics.** Pass the `platforms` array you want network-level metrics for. Some metrics require platform eligibility (e.g. business/creator accounts). It does **not** describe an Ayrshare User Profile — it describes the connected social account itself.

## Gotchas

- **Wrong tool = wrong answer.** Post-level vs network-level is the #1 error. `get_post_analytics` / `get_post_analytics_by_social_id` are *per post*; `get_social_network_analytics` is *account/network-level* (followers/impressions/views). If the user asks about a post, the network tool will not have post metrics, and vice versa.
- **Ayrshare id vs native id picks the tool — they are different tools, not flags.** An Ayrshare Post ID goes to `get_post_analytics`; a native Social Post ID goes to `get_post_analytics_by_social_id`. Passing a native id to `get_post_analytics` (or vice versa) returns nothing useful.
- **`get_post_analytics_by_social_id` needs exactly one `platform`.** It takes a single `platform` value (singular), not an array — the network you're querying the native id on.
- **Ownership matters for the Social Post ID tool.** The linked account must own the post. **Exception: YouTube** — querying a non-owned video by social id returns descriptive metadata (title, description, tags, channel title, privacy status, thumbnails) but **zeros** for all numeric metrics (views, likes, comments, etc.).
- **X/Twitter threads via Social Post ID.** Query each tweet's Social Post ID individually; thread replies are not automatically included when you query the parent tweet's id.
- **Analytics availability varies by platform.** Not every network exposes every metric; some require the post to be a certain type or the account to meet platform eligibility. A missing field is often a platform limitation, not a tool failure. (X, for example, withholds non-public/organic metrics for posts not sent by the authorized user.)
- **Fresh posts may have no data yet.** Metrics lag publication — a post analyzed seconds after going live can legitimately return zeros or empty fields. That is not an error; the data simply hasn't populated. Don't retry in a loop expecting numbers to appear.
- **Profile scoping is the `profileKey` argument or the `Profile-Key` header.** To read a specific client's analytics, pass that client's `profileKey` as the argument or set the connection's `Profile-Key`; the argument wins when both are set. (See `../getting-started/SKILL.md`.)
- **On failure, call `mcp__ayrshare__explain_error`, then surface it — don't loop.** These are reads, but a 4xx (bad id, wrong platform, ineligible account) won't fix itself on retry. Translate the error via `mcp__ayrshare__explain_error` and present it. 429 gets at most one retry. (Mirrors the global retry-safety rule.)
