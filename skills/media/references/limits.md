# Media size/format limits and per-platform image dimensions

Values from Ayrshare's media guidelines. Platforms are network requirements that Ayrshare enforces — an out-of-spec asset is rejected at upload or at post time. Resize per platform with `mcp__ayrshare__resize_media`.

## Upload limits (Ayrshare `/media/upload`)

- **Max file size: 30 MB** through `mcp__ayrshare__upload_media`. For larger files, host externally (e.g. S3) and pass the URL in the post's `mediaUrls` instead of uploading.
- **Retention: uploaded files are stored 90 days.** Already-published posts are unaffected, but a SCHEDULED post that references expired media will fail to publish. Don't schedule far-future posts against soon-to-expire uploads.
- Externally hosted media (your own URL) skips the upload step entirely — often faster.

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

## Why resize is per-platform

The table above shows the conflict directly: Instagram wants width ≥ 1080 px with a 1.91:1–4:5 aspect, X recommends 1200 x 675 (16:9), Pinterest wants a 2:3 portrait, GBP wants landscape ~720x720. A single asset cannot satisfy all of them. When a post targets multiple networks, run `mcp__ayrshare__resize_media` once per platform and attach the right URL to each.

## Notes

- Limits change as networks update their APIs; treat this as a working reference, not a contract. For the live spec, see Ayrshare's media guidelines docs.
- Video has separate size/duration/codec limits per platform not enumerated here — check the per-network media guidelines when posting video.
