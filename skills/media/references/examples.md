# Example payloads — Ayrshare MCP media (validation)

Inputs passed to the MCP tool. There is only one media tool: `validate_media`. The reliable order is: obtain a publicly hosted URL (at the right dimensions) → `validate_media` → attach to a post's `mediaUrls`. There is **no** upload, list, or resize tool — media is referenced by public URL.

## Validate a media URL before posting

```json
{ "mediaUrl": "https://cdn.example.com/launch-hero.png" }
```

This is `mcp__ayrshare__validate_media` (POST `/media/urlExists`). It HEAD-checks that the URL is reachable and reports the content type. Run it BEFORE referencing the URL in a post — it catches unreachable URLs and wrong/unexpected content types early instead of failing at publish time. `mediaUrl` is a single URL string; the only optional input is `passthrough`.

## There is no upload / list / resize tool

The Ayrshare MCP does not store media. To use an image or video in a post:

1. Host it at a **public URL** yourself (your CDN, S3, or any public host), sized correctly for each target platform — see `limits.md`. There is no resize tool, so the asset must already meet each network's dimension/aspect rules.
2. Validate the URL with `mcp__ayrshare__validate_media` (above).
3. Pass the validated URL into the post's `mediaUrls`.

If a user asks to "upload", "store in a library", or "resize for Instagram", there is no MCP tool for it — route them to supply a hosted URL at the correct dimensions.

## Then attach the validated URL(s) to a post

Feed the validated URL into `mcp__ayrshare__create_post` (see `../../post/SKILL.md` — and validate the post first):

```json
{
  "post": "Big news — read the announcement.",
  "platforms": ["twitter", "facebook", "instagram", "linkedin"],
  "mediaUrls": ["https://cdn.example.com/launch-hero.png"]
}
```

For a post going to several networks with conflicting dimension rules (see `limits.md`), host a correctly-sized variant per platform and attach the matching URL to each — the MCP cannot resize for you.

Note: on any error, call `mcp__ayrshare__explain_error` and surface the explanation rather than auto-retrying a 4xx (an unreachable or wrong-type URL won't fix itself on retry).
