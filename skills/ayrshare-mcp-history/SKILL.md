---
name: ayrshare-mcp-history
description: |
  Post history for the Ayrshare MCP server — list past and scheduled posts, optionally filtered by recency, platform, and status. Use whenever someone wants to see what's been posted: "show my recent posts", "what did we publish last week", "history for this client", "did that scheduled post go out", "list our LinkedIn posts", or to look up a post id for analytics. Also the verification step after onboarding a client — confirming their accounts linked — and the way to find a NATIVE Social Post ID for analytics on a post that wasn't created through Ayrshare. Trigger when calling `mcp__ayrshare__get_post_history` or `mcp__ayrshare__get_platform_history`, and even without the word "Ayrshare" — if the user wants a log of social posts through an AI assistant, this is the skill. For the shared auth model and the full onboarding sequence, see `../ayrshare-mcp-getting-started/SKILL.md`.
---

# Ayrshare MCP — History

Two tools:

- `mcp__ayrshare__get_post_history` — lists posts **sent via Ayrshare** (returns Ayrshare Post IDs). The default "what have we posted" tool, and the **onboarding verification step**.
- `mcp__ayrshare__get_platform_history` — returns **native social posts**, including posts **not** made through Ayrshare (returns native Social Post IDs). This is how you find a native Social Post ID to feed `mcp__ayrshare__get_post_analytics_by_social_id`.

Both are profile-scoped via the connection's `Profile-Key` header (see Auth) — neither takes a `profileKey` argument.

## Functions

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__get_post_history` | Retrieve history of posts sent via Ayrshare (past + scheduled); returns Ayrshare Post IDs | `GET /history` | — | `limit` (1-1000, default 25), `platforms` (array), `startDate`/`endDate` (ISO 8601), `lastDays` (default 30, 0=all), `status`, `type`, `passthrough` |
| `mcp__ayrshare__get_platform_history` | Retrieve native social posts (incl. posts not made via Ayrshare); returns native Social Post IDs | `GET /history/:platform` | `platform` (one enum value) | `limit` (1-500), `skipAnalytics`, `pagePublished` (FB), `userId`/`userName` (X), `next` (cursor), `since`/`until` (FB ISO dates), `dataType` (`posts`\|`stories`), `passthrough` |

Full input schemas and example payloads/responses are in [`references/schemas.md`](references/schemas.md).

## Auth

Both tools are **profile-scoped via the connection's `Profile-Key` header**, not a per-call argument. The header is set in the MCP client config (`.mcp.json` headers): include `Profile-Key: <profileKey>` to act as one client profile; omit it to act on the account's primary/Business profile. To switch profiles you reconfigure the connection header — you do **not** pass a `profileKey` parameter to the tool, and `passthrough` cannot carry one (it is a blocked credential key). Full two-layer model: `../ayrshare-mcp-getting-started/SKILL.md`.

## Usage guidance

- **The connection's `Profile-Key` header decides whose history you see.** With it → that profile's posts. Without it → the account's primary/Business profile. This is set at the connection level, not per call, so be deliberate about which connection (which `Profile-Key`) you're using.
- **`get_post_history` filters are all optional.** Use `lastDays` to bound recency (default 30; pass `0` for all time), `startDate`/`endDate` for an explicit ISO 8601 window, `platforms` to narrow to a subset of networks, `status` to filter by lifecycle state (`awaiting approval`, `deleted`, `error`, `paused`, `pending`, `success`), and `limit` to cap results (1-1000, default 25). Omit them all for the default recent history.
- **Onboarding verification.** After a client completes OAuth via the JWT link, call `get_post_history` on the connection scoped to their `Profile-Key` to confirm the connection succeeded and surface their existing posts. This is the verification step in the onboarding sequence in `../ayrshare-mcp-getting-started/SKILL.md`.
- **Looking up an Ayrshare Post ID?** `get_post_history` returns each post's Ayrshare `id` — the id you feed to `mcp__ayrshare__get_post_analytics` and `mcp__ayrshare__get_post` for Ayrshare-sent posts.
- **Finding a native Social Post ID (for posts not sent via Ayrshare).** Call `get_platform_history` with the `platform` (required). It returns native social posts — including posts not made through Ayrshare — each with a native Social Post `id`. That native id is exactly what `mcp__ayrshare__get_post_analytics_by_social_id` needs (native id + `platform`). So `get_platform_history` is how you find the native ids to feed analytics-by-social-id. See the Analytics skill for the analytics side of this workflow.

## Gotchas

- **Scope comes from the connection, not a parameter.** Whose history you get is fixed by the connection's `Profile-Key` header; there is no `profileKey` argument and the call succeeds regardless. Confirm you're on the right connection before trusting the results.
- **Two different tools, two different id types.** `get_post_history` returns **Ayrshare** Post IDs (for `get_post_analytics`, `get_post`, `retry_post`, `update_post`). `get_platform_history` returns **native** Social Post IDs (for `get_post_analytics_by_social_id`). Don't feed one tool's ids to a path expecting the other.
- **`get_platform_history` requires `platform`.** It is `GET /history/:platform`, so exactly one platform is required: one of `bluesky, facebook, instagram, linkedin, pinterest, snapchat, threads, tiktok, twitter, youtube`. (Note this 10-platform history set excludes `gmb`, `reddit`, and `telegram`, which the 13-platform POST set includes.)
- **`get_post_history` `platforms` is plural and an array.** It accepts a subset of the 13 POST platforms (`twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads`) and filters within the already-chosen profile scope — it does not change scope.
- **This is the onboarding verification step.** If you reached here as part of onboarding, the connection should already be scoped to the new client's `Profile-Key`; verify with `get_post_history`. See the onboarding sequence in `../ayrshare-mcp-getting-started/SKILL.md`.
- **An empty result isn't an error.** A freshly onboarded profile with no posts yet legitimately returns an empty history. During onboarding, that confirms the account is linked, just unused.
- **On failure, call `mcp__ayrshare__explain_error`, then surface it — don't loop.** These are reads, but a 4xx (bad filter, unsupported platform, wrong scope) won't fix itself on retry. Translate the error via `mcp__ayrshare__explain_error` and present it; 429 gets at most one retry. (Mirrors the global retry-safety rule.)
