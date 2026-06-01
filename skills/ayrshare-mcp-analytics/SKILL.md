---
name: ayrshare-mcp-analytics
description: |
  Social media analytics for the Ayrshare MCP server — metrics for a specific post, and analytics on a social network (account/network-level metrics like followers, impressions, and reach). Use whenever someone wants performance data: "how did my post do", "engagement on that tweet", likes/comments/shares/views/impressions/reach for a post, follower counts, reach or impressions for an account, "analytics for our LinkedIn", "how is our Instagram growing", or comparing networks. Also use when pulling analytics for a post that was NOT created through Ayrshare (by its native Social Post ID). Trigger when calling `mcp__ayrshare__get_post_analytics` or `mcp__ayrshare__get_social_analytics`, and even without the word "Ayrshare" — if the user wants social media stats for a post or a network through an AI assistant, this is the skill. For the shared auth model and retry rules, see `../ayrshare-mcp-getting-started/SKILL.md`.
---

# Ayrshare MCP — Analytics

Two analytics tools, split by *what* they measure. Picking the wrong one is the main failure mode in this group, so anchor on the distinction before calling either:

- **`mcp__ayrshare__get_post_analytics`** — metrics for one **specific post**: its likes, comments, shares, views, etc. Two lookup methods (see below): by **Ayrshare Post ID** (the default, for posts sent via Ayrshare) or by **Social Post ID** (the network's native id, for posts that did *not* originate via Ayrshare).
- **`mcp__ayrshare__get_social_analytics`** — **analytics on a social network**: account/network-level metrics like followers, impressions, reach, and other profile-level numbers for a connected social account.

Both are **profile-scoped**.

## Functions

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__get_post_analytics` | Engagement metrics for a specific post | `POST /analytics/post` | Yes | `id` — the Ayrshare Post ID, **OR** the Social Post ID + `searchPlatformId: true` | `profileKey`, `platforms` (required when searching by Social Post ID), `postIds` (batch of Social Post IDs) |
| `mcp__ayrshare__get_social_analytics` | Analytics on a social network (followers, impressions, reach — account/network-level) | `POST /analytics/social` | Yes | `platforms` | `profileKey` |

Full input schemas, both `get_post_analytics` lookup methods with example payloads, the per-platform metric notes, and example responses are in [`references/schemas.md`](references/schemas.md).

## Auth

Both tools are **profile-scoped**. Pass a `profileKey` to read a specific client's analytics; omit it to read the Business account's own analytics. When supplied, `profileKey` replaces the Business key as the auth key for that request — unlike the Profiles tools, where a `profileKey` is just data. Profile key can also be set as a default via the `AYRSHARE_PROFILE_KEY` env var and overridden per-call. Full two-layer model: `../ayrshare-mcp-getting-started/SKILL.md`.

## Usage guidance

- **Choose by scope, not by platform.** "How did this post do" → `get_post_analytics`. "How many followers / what's our reach / analytics on our LinkedIn network" → `get_social_analytics` with the platform(s). They are not interchangeable and rarely both needed for one question.
- **`get_post_analytics` has two lookup methods — pick by where the post came from:**
  - **(a) By Ayrshare Post ID (default).** Use for posts sent via Ayrshare. Pass the `id` returned by `mcp__ayrshare__create_post` (or found via `mcp__ayrshare__get_history`). No `searchPlatformId` needed. This is the recommended path for any Ayrshare-sent post.
  - **(b) By Social Post ID.** Use for posts that did **not** originate via Ayrshare. Pass the social network's **native** post id as `id` (or several via `postIds`), the single target `platforms` value, **and** `searchPlatformId: true` to tell the endpoint you're searching by Social Post ID. Supported platforms: Facebook, Instagram, LinkedIn, Threads, TikTok, Twitter, YouTube. Find these native ids via the **get-history-by-social-id** path (the `id` field) — see the History skill for that workflow.
  - Recommended to use method (b) **only** for posts not sent via Ayrshare; for Ayrshare-sent posts always use the Ayrshare Post ID (method a).
- **Get the post id first.** For method (a), look up the Ayrshare `id` via `create_post` output or `mcp__ayrshare__get_history`. For method (b), look up the native Social Post ID via the history-by-social-id path. If the user only describes a post in prose, resolve the id before calling.
- **`get_social_analytics` is "analytics on a social network."** Pass the platform(s) you want network-level metrics for. Some metrics require platform eligibility (e.g. business/creator accounts).
- **Reading a client's numbers?** Pass that client's `profileKey`. Omitting it returns the Business account's own analytics, which is usually not what was asked.

## Gotchas

- **Wrong tool = wrong answer.** Post-level vs network-level is the #1 error. `get_post_analytics` is *per post*; `get_social_analytics` is *analytics on a social network* (followers/impressions/reach). If the user asks about a post, the social tool will not have post metrics, and vice versa.
- **Social Post ID method needs `searchPlatformId: true`.** Method (b) silently misbehaves without it — the endpoint will try to treat the native id as an Ayrshare id. Always include `searchPlatformId: true` AND a single `platforms` value when searching by Social Post ID.
- **Ownership matters for the Social Post ID method.** The linked account must own the post. **Exception: YouTube** — querying a non-owned video by social id returns descriptive metadata (title, description, tags, channel title, privacy status, thumbnails) but **zeros** for all numeric metrics (views, likes, comments, etc.).
- **X/Twitter threads via Social Post ID.** Each tweet's Social Post ID must be provided individually; thread replies are not automatically included when you query the parent tweet's id.
- **Analytics availability varies by platform.** Not every network exposes every metric; some require the post to be a certain type or the account to meet platform eligibility. A missing field is often a platform limitation, not a tool failure. (X, for example, withholds non-public/organic metrics for posts not sent by the authorized user.)
- **Fresh posts may have no data yet.** Metrics lag publication — a post analyzed seconds after going live can legitimately return zeros or empty fields. That is not an error; the data simply hasn't populated. Don't retry in a loop expecting numbers to appear.
- **Omitting `profileKey` reads the Business account, not the client.** To get a specific client's analytics, pass their `profileKey`. (Profile-scoped behavior — see `../ayrshare-mcp-getting-started/SKILL.md`.)
- **On failure, call `mcp__ayrshare__explain_error`, then surface it — don't loop.** These are reads, but a 4xx (bad id, wrong key, ineligible account, missing `searchPlatformId`) won't fix itself on retry. Translate the error via `mcp__ayrshare__explain_error` and present it. 429 gets at most one retry. (Mirrors the global retry-safety rule.)
