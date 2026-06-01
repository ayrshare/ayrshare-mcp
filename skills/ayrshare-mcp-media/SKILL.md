---
name: ayrshare-mcp-media
description: |
  Use whenever someone wants to upload, list, verify, resize, or otherwise confirm an image/video is usable for a social post through the Ayrshare MCP server — the `mcp__ayrshare__validate_media` tool. Trigger on phrasings like "upload this image so I can post it", "check that this video URL works before posting", "resize my image for Instagram", "make this fit a story", "what's in my media library", "is this picture going to be rejected", or any time a post needs an attachment and the media isn't confirmed yet — even if the user never says "Ayrshare", "MCP", or names a tool. Also trigger when a post failed because of a bad/unreachable media URL. IMPORTANT: the Ayrshare MCP has NO media upload, library, or resize tool — media is referenced by public URL and `validate_media` only HEAD-checks that a URL is reachable. For installing/configuring the server and the auth model, this skill cross-links to `../ayrshare-mcp-getting-started/SKILL.md`. To attach a validated media URL to a post, see `../ayrshare-mcp-posts/SKILL.md`.
---

# Ayrshare MCP — Media (validation)

There is **one** media tool: `mcp__ayrshare__validate_media`. It HEAD-checks that a media URL is reachable and reports the content type, so you can confirm an image/video URL is usable **before** attaching it to a post.

**The key concept — Ayrshare MCP does not store media.** There is **no upload, no media library, and no resize tool**. You reference media by its **public URL** in a post's `mediaUrls` array (see `../ayrshare-mcp-posts/SKILL.md`). `validate_media` is how you check that URL is reachable and the right content type before posting. There is no upload/list/resize step.

If a user asks to "upload", "store in the library", or "resize for Instagram": there is no MCP tool for that. The agent must obtain a **publicly hosted URL** (e.g. on the user's CDN, S3, or any public host) at the correct dimensions, validate it, then attach the URL to the post. Route the user to supply a hosted URL.

- API base (REST endpoint the tool wraps): `https://api.ayrshare.com/api`
- Media is referenced by URL in a post's `mediaUrls` array — see `../ayrshare-mcp-posts/SKILL.md`.

## Function table

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__validate_media` | HEAD-check that a media URL is reachable and report its content type, before using it in a post | POST `/media/urlExists` | `mediaUrl` (a single media URL string) | `passthrough` |

Per-platform media constraints to check before posting (dimensions, aspect ratios, size, duration) are in `references/limits.md`. Example payloads are in `references/examples.md`.

## Auth note

This tool operates on the profile selected by the connection's `Profile-Key` header — there is **no per-call `profileKey` argument**. The Business API key (HTTP Bearer) is configured when the MCP server is installed; see `../ayrshare-mcp-getting-started/SKILL.md` for installation and the full auth model. To act on a different client profile, reconfigure the connection's `Profile-Key` header; omit it to act under the account's primary/Business profile. `passthrough` **cannot** carry a `profileKey` — it is a blocked credential key.

## Usage guidance

- **The reliable sequence before a post with media:** (1) obtain a **publicly reachable URL** for the media (the user's CDN/S3/any public host) — there is no upload tool; (2) call `mcp__ayrshare__validate_media` with that `mediaUrl` to confirm it's reachable and the content type is what you expect; (3) pass the validated URL(s) into `mcp__ayrshare__create_post`'s `mediaUrls`. Validating first turns a post-time failure into a clear, early error.
- **`validate_media` answers "will this URL work at all"** — is it reachable, and is it the content type you expect. It does **not** transform, resize, or store the media.
- **No resize tool — supply correctly-sized media by URL.** Each network has different dimension/aspect-ratio requirements (see `references/limits.md`). The agent must supply media already sized for each target platform; the MCP cannot resize. If a post targets several networks with conflicting requirements, host the correctly-sized variant for each and attach the right URL per platform.

## Gotchas

- **Validate BEFORE posting.** The most common media failure is a bad or unreachable URL surfacing only when `mcp__ayrshare__create_post` runs. Run `mcp__ayrshare__validate_media` first to catch it early; a post referencing a URL that 404s or is the wrong content type will fail.
- **No upload / no library / no resize.** The MCP only validates a URL. If the user wants media "uploaded", "stored", or "resized", explain there is no such tool — they must host the media at a public URL (at the right dimensions) and reference it by URL. Don't claim media was uploaded or resized.
- **Constraints are per-platform — there is no resize tool to fix them.** Each network has different dimension/aspect-ratio/size/duration requirements (e.g. Instagram square/portrait vs an X landscape image vs a 9:16 story). One asset is rarely valid everywhere. Check `references/limits.md` and supply a correctly-sized URL per target platform.
- **Media must be reachable before `create_post` references it.** Don't put an unvalidated URL in `mediaUrls`. Confirm with `validate_media` first, then reference that URL (cross-link: `../ayrshare-mcp-posts/SKILL.md`).
- **Profile scoping is the `Profile-Key` header, not a param.** There is no `profileKey` argument and `passthrough` cannot carry one. To target a different client profile, reconfigure the connection's `Profile-Key` header. (Shared rule — see getting-started.)
- **On failure, explain — don't auto-retry.** When `validate_media` reports an unreachable or wrong-type URL, surface that to the user (and use `mcp__ayrshare__explain_error` if a numeric error code came back) rather than auto-retrying. A 4xx means the URL is unreachable, the wrong type, or the key/profile is wrong — fix the input, don't loop. A 429 gets at most one retry after a short delay. (Mirror of the global retry-safety rule — full version in getting-started.)
