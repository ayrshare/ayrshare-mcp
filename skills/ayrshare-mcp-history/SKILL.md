---
name: ayrshare-mcp-history
description: |
  Post history for the Ayrshare MCP server — list past and scheduled posts, optionally filtered by recency and platform. Use whenever someone wants to see what's been posted: "show my recent posts", "what did we publish last week", "history for this client", "did that scheduled post go out", "list our LinkedIn posts", or to look up a post id for analytics. Also the verification step after onboarding a client — confirming their accounts linked — and the way to find a NATIVE Social Post ID for analytics on a post that wasn't created through Ayrshare. Trigger when calling `mcp__ayrshare__get_history`, and even without the word "Ayrshare" — if the user wants a log of social posts through an AI assistant, this is the skill. For the shared auth model and the full onboarding sequence, see `../ayrshare-mcp-getting-started/SKILL.md`.
---

# Ayrshare MCP — History

One tool: `mcp__ayrshare__get_history` retrieves post history, optionally filtered by recency and platform. It is **profile-scoped**, and its behavior pivots on whether you pass a `profileKey`. It also doubles as the **onboarding verification step** and as the way to find a **native Social Post ID** for analytics on posts not created through Ayrshare — see below.

## Functions

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__get_history` | Retrieve post history (past + scheduled); returns Ayrshare post ids | `GET /history` | Yes | — | `profileKey`, `lastDays` (integer), `platform` (enum) |

The same endpoint also supports a **history-by-social-id** mode for posts that did not originate via Ayrshare — see *Usage guidance* and [`references/schemas.md`](references/schemas.md).

Full input schema and example payloads/responses are in [`references/schemas.md`](references/schemas.md).

## Auth

`mcp__ayrshare__get_history` is **profile-scoped**. Pass a `profileKey` to get one client's history; omit it to get the Business account's own history. When supplied, `profileKey` replaces the Business key as the auth key for that request. A `profileKey` can also be set as the default via `AYRSHARE_PROFILE_KEY` and overridden per-call. Full two-layer model: `../ayrshare-mcp-getting-started/SKILL.md`.

## Usage guidance

- **`profileKey` decides whose history you see.** With it → that profile's posts. Without it → account-level history for the Business account. Pick deliberately; this is the same choice as every profile-scoped tool, just especially easy to get wrong here because the call works either way.
- **`lastDays` and `platform` are filters**, not required. Use `lastDays` to bound recency (e.g. last 7 days) and `platform` to narrow to one network. Omit both for the full history.
- **Onboarding verification.** After a client completes OAuth via the JWT link, call `get_history` with their `profileKey` to confirm the connection succeeded and surface their existing posts. This is step 4 of the onboarding sequence in `../ayrshare-mcp-getting-started/SKILL.md`.
- **Looking up an Ayrshare post id?** Standard `get_history` returns each post's Ayrshare `id` — the id you feed to `mcp__ayrshare__get_post_analytics` method (a) for Ayrshare-sent posts.
- **Finding a native Social Post ID (for posts not sent via Ayrshare).** There is also a **history-by-social-id** capability: look up a post by its native social-network id to retrieve that post's native `id`. That native id is exactly what `mcp__ayrshare__get_post_analytics` method (b) needs (the native id + `searchPlatformId: true`). So: history-by-social-id is how you find the native ids to feed analytics method (b). See the Analytics skill for the analytics side of this workflow. Supported platforms for the social-id path: Facebook, Instagram, LinkedIn, Threads, TikTok, Twitter, YouTube.

## Gotchas

- **Behavior depends on `profileKey`.** Supplying it returns that profile's history; omitting it returns account-level history. The call succeeds either way, so a missing `profileKey` silently returns the wrong scope rather than erroring — double-check whose history was actually requested.
- **`platform` and `lastDays` are filters, not selectors of scope.** They narrow results within whatever scope `profileKey` (or its absence) already chose. `platform` must be from the enum: `bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube`.
- **Two kinds of id.** Standard `get_history` returns Ayrshare post ids (for analytics method a). The history-by-social-id path returns / is keyed by **native** Social Post ids (for analytics method b). Don't mix them up — feeding a native id into analytics without `searchPlatformId: true` will fail or return the wrong post.
- **History-by-social-id ownership.** The linked account must own the post to retrieve its history by social id. Supported platforms are the seven listed above only.
- **This is the onboarding verification step.** If you reached here as part of onboarding, you should already hold the new `profileKey` from `mcp__ayrshare__create_profile`; use it. See the onboarding sequence in `../ayrshare-mcp-getting-started/SKILL.md`.
- **An empty result isn't an error.** A freshly onboarded profile with no posts yet legitimately returns an empty history. During onboarding, that confirms the account is linked, just unused.
- **On failure, call `mcp__ayrshare__explain_error`, then surface it — don't loop.** This is a read, but a 4xx (wrong key, bad filter, unsupported platform) won't fix itself on retry. Translate the error via `mcp__ayrshare__explain_error` and present it; 429 gets at most one retry. (Mirrors the global retry-safety rule.)
