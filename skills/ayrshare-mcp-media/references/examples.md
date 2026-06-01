# Example payloads — Ayrshare MCP media

Inputs passed to the MCP tools. The reliable order is upload (if needed) → verify → resize (per platform) → attach to a post's `mediaUrls`.

## Upload media to the library

```json
{
  "file": "https://cdn.example.com/launch-hero.png"
}
```

This is `mcp__ayrshare__upload_media`. Returns a URL usable in a post's `mediaUrls`. If you already host the file at a reachable URL, you can skip uploading and pass that URL straight to `mcp__ayrshare__create_post`. Max 30 MB through upload; uploaded files expire after 90 days.

## List what's in the library

```json
{ "profileKey": "PROFILE_KEY_FROM_CREATE_PROFILE" }
```

This is `mcp__ayrshare__list_media`. Omit `profileKey` to list the Business account's library (or rely on the `AYRSHARE_PROFILE_KEY` env default). Use this to reuse an existing URL instead of re-uploading.

## Verify a media URL before posting

```json
{ "mediaUrl": "https://cdn.example.com/launch-hero.png" }
```

This is `mcp__ayrshare__verify_media`. Run it BEFORE referencing the URL in a post — it catches unreachable URLs and unsupported formats early instead of failing at publish time.

## Resize an image for a specific platform

```json
{
  "mediaUrl": "https://cdn.example.com/launch-hero.png",
  "platform": "instagram"
}
```

This is `mcp__ayrshare__resize_media`. Resize is PER-PLATFORM. For a post going to twitter + instagram + linkedin with conflicting dimension rules, resize once per platform and attach the matching URL to each. See `limits.md` for the dimensions.

## Then attach the confirmed URL(s) to a post

Feed the verified/resized URL into `mcp__ayrshare__create_post` (see `../../ayrshare-mcp-posts/SKILL.md` — and validate first):

```json
{
  "post": "Big news — read the announcement.",
  "platforms": ["twitter", "facebook", "instagram", "linkedin"],
  "mediaUrls": ["https://cdn.ayrshare.com/.../resized-launch-hero.jpg"]
}
```

Note: field names for the media URL/file input (`file`, `mediaUrl`) follow the Ayrshare media endpoints; if the implemented MCP server names them differently, match the server's tool schema. On any error, call `mcp__ayrshare__explain_error` and surface the explanation rather than auto-retrying a 4xx.
