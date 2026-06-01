---
name: comments
description: |
  Use whenever someone wants to read, add, or reply to comments on a social media post through the Ayrshare MCP server — the `mcp__ayrshare__get_comments`, `mcp__ayrshare__add_comment`, and `mcp__ayrshare__reply_comment` tools. Trigger on phrasings like "leave a comment on that post", "reply to that commenter", "respond to the top comment", "what are people saying on my LinkedIn post", "pull the comments", or "answer the question someone left on Instagram" — even if the user never says "Ayrshare", "MCP", or names a tool. Also trigger when a user wants to engage with an audience under an existing post rather than create a new post. For installing/configuring the server and the auth model, this skill cross-links to `../getting-started/SKILL.md`. To create the post being commented on, see `../post/SKILL.md`.
---

# Ayrshare MCP — Comments

The engagement tools: read comments on a post, add a new top-level comment, and reply to an existing comment.

- API base (REST endpoints the tools wrap): `https://api.ayrshare.com/api`
- Comments are scoped to a post you already published; you need that post's `id` (returned by `mcp__ayrshare__create_post` — see `../post/SKILL.md`).
- **Profile scoping is a connection header, not a tool argument.** No comment tool takes a `profileKey` param. To act as a specific client profile, the MCP connection's `Profile-Key` header is set in the client config; omit it to act under the account's primary/Business profile. See `../getting-started/SKILL.md`.

## Supported platforms (COMMENT_PLATFORMS)

`get_comments` and `add_comment` accept these networks: bluesky, facebook, instagram, linkedin, reddit, tiktok, twitter, youtube. Not every network in your post's `platforms` supports comment operations — surface the limitation rather than retrying.

## Function table

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__get_comments` | Read comments on a post | GET `/comments` | `id` | `searchPlatformId` (bool; `id` is a Social Post/Comment ID), `commentId` (bool; with `searchPlatformId`, `id` is a Social Comment ID), `platform` (one COMMENT_PLATFORMS; required when `searchPlatformId`), `passthrough` |
| `mcp__ayrshare__add_comment` | Add a NEW top-level comment to a post | POST `/comments` | `id`, `comment` (text; @mentions inline) | `platforms` (COMMENT_PLATFORMS subset), `searchPlatformId` (bool; requires exactly one platform), `mediaUrls` (exactly 1 URL; FB/LinkedIn/X only), `passthrough` |
| `mcp__ayrshare__reply_comment` | Reply to an EXISTING comment | POST `/comments/reply` | `commentId` (Ayrshare Comment ID, or Social Comment ID if `searchPlatformId`), `comment`, `platforms` (exactly one if `searchPlatformId`) | `searchPlatformId` (bool), `mediaUrls` (1), `videoId` (required for TikTok Social-Comment-ID replies), `objResponse` (bool), `passthrough` |

Field names beyond the core inputs and example payloads are in `references/examples.md`. Note `add_comment` posts to `/comments` (keyed by the post `id`) while `reply_comment` posts to `/comments/reply` (keyed by `commentId`).

## Auth note

These tools authenticate with the account's API key, configured when the MCP server is installed — see `../getting-started/SKILL.md` for installation and the full auth model; don't re-derive it here. Profile scoping is the per-connection `Profile-Key` header set in the MCP client config (`.mcp.json`), NOT a per-call argument and NOT something `passthrough` can carry. Omit the header to operate under the account's primary/Business profile.

## Usage guidance

- **`add_comment` vs `reply_comment`** — pick by target, not by wording. A NEW top-level comment ON A POST is `add_comment` (needs the post `id`). A reply to an EXISTING comment is `reply_comment` (needs that comment's `commentId`). "Reply to the post" usually means a top-level comment → `add_comment`; "reply to that person/commenter" means `reply_comment`. When unsure, call `mcp__ayrshare__get_comments` first to see the comment thread and grab the right `commentId`.
- **Read before you write.** To respond to a specific comment, `mcp__ayrshare__get_comments` gives you the comment ids and text. Don't guess a `commentId`.
- **Match the profile to the post.** Comment on a post under the same connection `Profile-Key` that owns the post. Commenting under the primary/Business profile on a client's post (or vice versa) targets the wrong identity.
- **`mediaUrls` is restricted.** Both `add_comment` and `reply_comment` accept at most one media URL, and only on Facebook, LinkedIn, and X (twitter).
- **TikTok Social-Comment-ID replies need `videoId`.** When replying to a TikTok comment by its Social Comment ID (`searchPlatformId`), `reply_comment` also requires `videoId`.

## Gotchas

- **`add_comment` vs `reply_comment` confusion — the #1 mistake.** `mcp__ayrshare__add_comment` adds a brand-new comment on the post itself (keyed by post `id`, POST `/comments`); `mcp__ayrshare__reply_comment` responds to one existing comment (keyed by `commentId`, POST `/comments/reply`). Using the wrong one posts your text in the wrong place. Read the thread with `mcp__ayrshare__get_comments` if the target isn't obvious.
- **Comments are platform-dependent — not every network supports them.** Comment create/read/reply availability varies by platform; only COMMENT_PLATFORMS (bluesky, facebook, instagram, linkedin, reddit, tiktok, twitter, youtube) are accepted, and a network in your post's `platforms` may still not accept a given comment operation. Don't assume a comment tool works everywhere a post does. Surface the platform limitation rather than retrying.
- **`searchPlatformId` changes what `id`/`commentId` means.** With `searchPlatformId`, `id`/`commentId` are NATIVE Social IDs rather than Ayrshare IDs, and exactly one platform must be supplied (`platform` on `get_comments`, one entry in `platforms` on `add_comment`/`reply_comment`).
- **On failure, explain — don't auto-retry.** When any comment tool errors, call `mcp__ayrshare__explain_error` to translate the API error to plain language, then surface it. Never auto-retry add/reply on a 4xx — a 4xx means bad input, an unsupported platform, or a missing comment; retrying a comment write can double-post. A 429 gets at most one retry after a short delay. (Mirror of the global retry-safety rule — full version in getting-started.) Poll `get_comments` no more than once every 10 minutes.
