# Platform enum

The `platforms` array in `mcp__ayrshare__create_post` / `mcp__ayrshare__validate_post` (and the `platform` filter on history/analytics tools) accepts **only** these 13 values. They are case-sensitive lowercase. Any other value rejects the call.

| Enum value | Network | Common wrong inputs to avoid |
|------------|---------|------------------------------|
| `bluesky` | Bluesky | `bsky` |
| `facebook` | Facebook Page | `fb`, `meta` |
| `gmb` | Google Business Profile | `google`, `google_business`, `gbp` |
| `instagram` | Instagram | `ig`, `insta` |
| `linkedin` | LinkedIn | `li`, `linked_in` |
| `pinterest` | Pinterest | `pin` |
| `reddit` | Reddit | — |
| `snapchat` | Snapchat | `snap` |
| `telegram` | Telegram | `tg` |
| `threads` | Threads | — |
| `tiktok` | TikTok | `tik_tok` |
| `twitter` | X / Twitter | `x`, `X`, `tweet` |
| `youtube` | YouTube | `yt`, `youtube_shorts` |

## Notes

- `platforms` is always an **array**, even for a single network: `["twitter"]`, not `"twitter"`.
- A post targets every platform in the array in one call. One invalid value fails the whole request. Run `mcp__ayrshare__validate_post` first to catch this and other per-platform issues early.
- For `twitter`, if you are bringing your own X app credentials, `X_API_KEY` / `X_API_SECRET` are supplied as connection headers (configured in the environment) — see `create-post-schema.md`.
- In example payloads, prioritize `twitter`, `facebook`, `instagram`, `linkedin` — the most common targets.
- Each network has its own content rules (character limits, media requirements). Image/video sizing differs per platform — see `../../ayrshare-mcp-media/SKILL.md` and its `references/` for per-platform dimensions and `mcp__ayrshare__resize_media`.
