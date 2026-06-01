---
name: ayrshare-mcp-media
description: |
  Use whenever someone wants to upload, list, verify, or resize images/video for social posts through the Ayrshare MCP server — the `mcp__ayrshare__upload_media`, `mcp__ayrshare__list_media`, `mcp__ayrshare__verify_media`, and `mcp__ayrshare__resize_media` tools. Trigger on phrasings like "upload this image so I can post it", "check that this video URL works before posting", "resize my image for Instagram", "make this fit a story", "what's in my media library", "is this picture going to be rejected", or any time a post needs an attachment and the media isn't confirmed yet — even if the user never says "Ayrshare", "MCP", or names a tool. Also trigger when a post failed because of a bad/unreachable media URL. For installing/configuring the server and the auth model, this skill cross-links to `../ayrshare-mcp-getting-started/SKILL.md`. To attach the verified media to a post, see `../ayrshare-mcp-posts/SKILL.md`.
---

# Ayrshare MCP — Media

The media tools: upload to the library, list what's there, verify a media URL is usable, and resize an image for a specific platform. All four are **profile-scoped** — they accept an optional `profileKey` to act on a specific client profile, or omit it to act under the Business account.

- API base (REST endpoints the tools wrap): `https://api.ayrshare.com/api`
- Media is referenced by URL in a post's `mediaUrls` array — see `../ayrshare-mcp-posts/SKILL.md`.

## Function table

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__upload_media` | Upload media to the library | POST `/media/upload` | Yes | media source (file/URL) | `profileKey` |
| `mcp__ayrshare__list_media` | List media in the library | GET `/media` | Yes | — | `profileKey` |
| `mcp__ayrshare__verify_media` | Verify a media URL is reachable/valid | POST `/media/verify` | Yes | media URL | `profileKey` |
| `mcp__ayrshare__resize_media` | Resize an image for a platform | POST `/media/resize` | Yes | media URL, target `platform` | `profileKey` |

Size/format limits and per-platform resize dimensions are in `references/limits.md`. Example payloads are in `references/examples.md`.

## Auth note

All media tools are profile-scoped. The Business API key is configured when the MCP server is installed — see `../ayrshare-mcp-getting-started/SKILL.md` for installation and the full auth model; don't re-derive it here. A profile key may come from the `AYRSHARE_PROFILE_KEY` environment default (applied to every call automatically) OR a per-call `profileKey` param that overrides it. **Omit `profileKey` on purpose** to operate under the Business account when no env default is set.

## Usage guidance

- **The reliable sequence before a post with media:** (1) get a usable URL — `mcp__ayrshare__upload_media` for local/new media, or use an existing URL; (2) `mcp__ayrshare__verify_media` to confirm it's reachable and a valid format; (3) optionally `mcp__ayrshare__resize_media` per target platform; (4) pass the confirmed URL(s) into `mcp__ayrshare__create_post`'s `mediaUrls`. Verifying first turns a post-time failure into a clear, early error.
- **`verify` vs `resize`** — `verify` answers "will this URL work at all"; `resize` produces a new URL fitted to one network's dimension/aspect rules. They're complementary, not interchangeable.
- **`list_media`** is for discovery — show the user what's already uploaded so they can reuse a URL instead of re-uploading.
- **Resize is per-platform.** If a post targets several networks with conflicting requirements, resize once per platform and attach the right URL to each — see Gotchas and `references/limits.md`.

## Gotchas

- **Verify BEFORE posting.** The most common media failure is a bad or unreachable URL surfacing only when `mcp__ayrshare__create_post` runs. Run `mcp__ayrshare__verify_media` first to catch it early; a post referencing a URL that 404s or is the wrong type will fail.
- **`resize_media` is PER-PLATFORM.** Each network has different dimension/aspect-ratio requirements (e.g. Instagram square/portrait vs an X landscape image vs a story aspect). One resized asset is not universally valid — resize per target platform and attach the correct URL to each. Dimensions in `references/limits.md`.
- **Size and format limits apply.** Uploads have per-type size caps and accepted formats (image vs video differ, and limits vary by platform). An oversized or unsupported file is rejected at upload or at post time — see `references/limits.md`.
- **Media must exist and verify before `create_post` references it.** Don't put a not-yet-uploaded or unverified URL in `mediaUrls`. Confirm with upload/verify first, then reference the resulting URL (cross-link: `../ayrshare-mcp-posts/SKILL.md`).
- **Wrong/missing `profileKey` layer.** Omitting `profileKey` (with no `AYRSHARE_PROFILE_KEY` env default) acts under the **Business account**, so media may land in the wrong library. Only omit on purpose. (Shared rule — see getting-started.)
- **On failure, explain — don't auto-retry.** When a media write (`upload`, `resize`) errors, call `mcp__ayrshare__explain_error` to translate the API error to plain language, then surface it. Never auto-retry a 4xx — it means oversized/unsupported/unreachable media or a wrong key. A 429 gets at most one retry after a short delay. (Mirror of the global retry-safety rule — full version in getting-started.)
