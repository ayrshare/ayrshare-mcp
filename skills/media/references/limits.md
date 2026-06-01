# Per-platform media constraints to check before posting

Values compiled from Ayrshare's published media guidelines as a convenience reference — **not a contract**. Platforms change these often; verify against the live Ayrshare media guidelines docs before relying on a specific number. **The MCP does not validate these limits**: `mcp__ayrshare__validate_media` only HEAD-checks that a URL is reachable and reports its content type. An out-of-spec asset is rejected by the platform at post time, not by `validate_media`. There is also **no resize or upload tool**: supply media already hosted at a public URL and already sized for each target platform, then confirm the URL is reachable with `mcp__ayrshare__validate_media` before posting.

## Hosting (no upload tool)

- Media is referenced by **public URL** in a post's `mediaUrls` — the MCP does not store or upload media. Host it on your own CDN, S3, or any public host.
- A SCHEDULED post will fail to publish if the media URL becomes unreachable before the scheduled time. Keep the URL live until the post sends.
- Confirm the URL is reachable and the right content type with `mcp__ayrshare__validate_media` before posting.

## Per-platform image requirements (priority networks first)

| Platform | Max image size | Formats | Recommended / key dimensions |
|----------|----------------|---------|------------------------------|
| `twitter` (X) | 5 MB | JPG, PNG, GIF, Animated GIF, WEBP | Single image 1200 x 675 px; aspect 16:9. Dimensions 4x4–8192x8192 px. Up to 4 images. |
| `facebook` | 10 MB | JPEG, BMP, PNG, Animated GIF, TIFF | Recommended 1200 x 630 px. Max 2048 x 2048 px. |
| `instagram` | 8 MB (Story; feed similar) | JPEG | Width ≥ 1080 px; feed aspect 1.91:1 to 4:5; Story aspect 9:16 (e.g. 1080 x 1920). sRGB. Strictly enforced — out-of-range aspect errors. |
| `linkedin` | 5 MB | JPG, GIF, Animated GIF, PNG | Recommended 1200 x 627 px. Must be < 36,152,320 total pixels. |
| `pinterest` | 20 MB | BMP, JPEG, PNG, TIFF, GIF, Animated GIF, WEBP | Recommended 1000 x 1500 px; aspect 2:3. Min 600 x 900, max 2000 x 3000 px. |
| `bluesky` | 1 MB | JPG, Animated GIF, PNG | Recommended 1200 x 627 px. Animated GIF sent as video; one per post. |
| `threads` | 8 MB | JPEG, PNG | Aspect limit 10:1. Width 320–1440 px. sRGB. |
| `telegram` | 5 MB | JPG, PNG, GIF, Animated GIF, WEBP | Width+height ≤ 10,000 total; ratio ≤ 20. |
| `gmb` (Google Business) | 10 KB – 5 MB | JPG, PNG | Recommended 720 x 720 px; min 250 x 250 px. Landscape preferred (portrait/multiframe may error). |
| `tiktok` (image posts) | 20 MB/image | JPG, JPEG, WEBP (no PNG) | Up to 35 images; rate-limited (6/min, 15/day). |
| `reddit` | varies by subreddit | JPG, PNG, GIF | Follow subreddit rules. |
| `snapchat` | varies | per Snapchat spec | Story-style 9:16. |
| `youtube` | video-first | video formats | Thumbnails per YouTube spec. |

## Why these constraints matter — and why there's no resize step

The table shows the conflict directly: Instagram wants width ≥ 1080 px with a 1.91:1–4:5 aspect, X recommends 1200 x 675 (16:9), Pinterest wants a 2:3 portrait, GBP wants landscape ~720x720. A single asset cannot satisfy all of them. Because the MCP has **no resize tool**, the agent must supply a correctly-sized asset per platform: host the right variant at a public URL for each network, validate each URL with `mcp__ayrshare__validate_media`, and attach the matching URL to each platform's post.

## Notes

- Limits change as networks update their APIs; treat this as a working reference, not a contract. For the live spec, see Ayrshare's media guidelines docs.
- Video has separate size/duration/codec limits per platform not enumerated here — check the per-network media guidelines when posting video.
