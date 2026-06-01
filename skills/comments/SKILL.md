---
name: comments
model: claude-sonnet-4-6
effort: high
description: |
  Use whenever someone wants to read, add, reply to, or remove comments on a social media post through the Ayrshare MCP server — the `mcp__ayrshare__get_comments`, `mcp__ayrshare__post_comment`, `mcp__ayrshare__reply_comment`, and `mcp__ayrshare__delete_comment` tools. Trigger on phrasings like "leave a comment on that post", "reply to that commenter", "respond to the top comment", "what are people saying on my LinkedIn post", "pull the comments", "delete that comment", or "answer the question someone left on Instagram" — even if the user never says "Ayrshare", "MCP", or names a tool. Also trigger when a user wants to engage with an audience under an existing post rather than create a new post. For installing/configuring the server and the auth model, this skill cross-links to `../getting-started/SKILL.md`. To create the post being commented on, see `../post/SKILL.md`.
---

# Ayrshare MCP — Comments

The engagement tools: read comments on a post, add a new top-level comment, reply to an existing comment, and delete a comment. All four are **profile-scoped** — they accept an optional `profileKey` to act on a specific client profile, or omit it to act under the Business account.

- API base (REST endpoints the tools wrap): `https://api.ayrshare.com/api`
- Comments are scoped to a post you already published; you need that post's `id` (returned by `mcp__ayrshare__create_post` — see `../post/SKILL.md`).

## Function table

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__get_comments` | Read comments on a post | GET `/comments` | Yes | `id` (post id) | `profileKey` |
| `mcp__ayrshare__post_comment` | Add a NEW top-level comment to a post | POST `/comments` | Yes | `id` (post id), `comment` (text) | `profileKey`, `platforms` |
| `mcp__ayrshare__reply_comment` | Reply to an EXISTING comment | POST `/comments` | Yes | `commentId` (the comment to reply to), `comment` (text) | `profileKey` |
| `mcp__ayrshare__delete_comment` | Delete a comment | DELETE `/comments` | Yes | `id` / `commentId` | `profileKey` |

Field names beyond the core inputs and example payloads are in `references/examples.md`. Note `post_comment` and `reply_comment` share the same `POST /comments` endpoint — they differ by the target (a post vs an existing comment).

## Auth note

All comment tools are profile-scoped. The Business API key is configured when the MCP server is installed — see `../getting-started/SKILL.md` for installation and the full auth model; don't re-derive it here. A profile key may come from the `AYRSHARE_PROFILE_KEY` environment default (applied to every call automatically) OR a per-call `profileKey` param that overrides it. **Omit `profileKey` on purpose** to operate under the Business account when no env default is set.

## Usage guidance

- **`post_comment` vs `reply_comment`** — pick by target, not by wording. A NEW top-level comment ON A POST is `post_comment` (needs the post `id`). A reply to an EXISTING comment is `reply_comment` (needs that comment's `commentId`). "Reply to the post" usually means a top-level comment → `post_comment`; "reply to that person/commenter" means `reply_comment`. When unsure, call `mcp__ayrshare__get_comments` first to see the comment thread and grab the right `commentId`.
- **Read before you write.** To respond to a specific comment, `mcp__ayrshare__get_comments` gives you the comment ids and text. Don't guess a `commentId`.
- **Match the profile to the post.** Comment on a post under the same `profileKey` that owns the post. Commenting under the Business account on a client's post (or vice versa) targets the wrong identity.

## Gotchas

- **`post_comment` vs `reply_comment` confusion — the #1 mistake.** Both hit `POST /comments`. `mcp__ayrshare__post_comment` adds a brand-new comment on the post itself (keyed by post `id`); `mcp__ayrshare__reply_comment` responds to one existing comment (keyed by `commentId`). Using the wrong one posts your text in the wrong place. Read the thread with `mcp__ayrshare__get_comments` if the target isn't obvious.
- **Comments are platform-dependent — not every network supports them.** Comment create/read/reply availability varies by platform; a network in your post's `platforms` may not accept comment operations at all. Don't assume a comment tool works everywhere a post does. Surface the platform limitation rather than retrying.
- **Wrong/missing `profileKey` layer.** Omitting `profileKey` (with no `AYRSHARE_PROFILE_KEY` env default) acts under the **Business account**, not the client. Only omit on purpose. (Shared rule — see getting-started.)
- **On failure, explain — don't auto-retry.** When any comment tool errors, call `mcp__ayrshare__explain_error` to translate the API error to plain language, then surface it. Never auto-retry post/reply/delete on a 4xx — a 4xx means bad input, wrong key, an unsupported platform, or a missing/already-deleted comment; retrying a comment write can double-post and retrying a delete is pointless once the comment is gone. A 429 gets at most one retry after a short delay. (Mirror of the global retry-safety rule — full version in getting-started.)
