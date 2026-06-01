# Platform enum

The `platforms` array in `mcp__ayrshare__create_post` / `mcp__ayrshare__validate_post` (and the `platform` filter on history/analytics tools) accepts **only** these 13 values, verbatim: `twitter, facebook, instagram, linkedin, tiktok, youtube, pinterest, reddit, telegram, gmb, bluesky, snapchat, threads`. They are case-sensitive lowercase. Any other value rejects the call.

| Enum value | Network | Common wrong inputs to avoid |
|------------|---------|------------------------------|
| `twitter` | X / Twitter | `x`, `X`, `tweet` |
| `facebook` | Facebook Page | `fb`, `meta` |
| `instagram` | Instagram | `ig`, `insta` |
| `linkedin` | LinkedIn | `li`, `linked_in` |
| `tiktok` | TikTok | `tik_tok` |
| `youtube` | YouTube | `yt`, `youtube_shorts` |
| `pinterest` | Pinterest | `pin` |
| `reddit` | Reddit | — |
| `telegram` | Telegram | `tg` |
| `gmb` | Google Business Profile | `google`, `google_business`, `googlebusiness`, `gbp` |
| `bluesky` | Bluesky | `bsky` |
| `snapchat` | Snapchat | `snap` |
| `threads` | Threads | — |

## Notes

- `platforms` is always an **array**, even for a single network: `["twitter"]`, not `"twitter"`.
- The Google Business Profile value is `gmb`, **not** `googlebusiness`.
- A post targets every platform in the array in one call. One invalid value fails the whole request. Run `mcp__ayrshare__validate_post` first to catch this and other per-platform issues early.
- In example payloads, prioritize `twitter`, `facebook`, `instagram`, `linkedin` — the most common targets.
- Each network has its own content rules (character limits, media requirements). Media is referenced by URL via `mediaUrls`; check a URL is reachable with `mcp__ayrshare__validate_media` — see `../../ayrshare-mcp-media/SKILL.md`.
