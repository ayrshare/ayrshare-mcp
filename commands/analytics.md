---
description: Fetch social media analytics and engagement stats across connected platforms
---

Fetch social media analytics and engagement stats via Ayrshare.

## Steps

1. Determine scope:
   - If the user specified platforms, get analytics for those.
   - If not specified, call mcp__ayrshare__list_profiles and ask which platforms to analyze.

2. Call the right analytics tool for the request:
   - Account/network stats (followers, impressions, reach, demographics): `mcp__ayrshare__get_social_network_analytics` — required `platforms`; optional `quarters` (1-4), `daily`, `period60Days`.
   - One specific post's metrics: `mcp__ayrshare__get_post_analytics` (by Ayrshare Post `id`) or `mcp__ayrshare__get_post_analytics_by_social_id` (by native Social Post `id` + single `platform`).
   These tools do not take an arbitrary date range; scope is via `quarters`/`daily` (account analytics) or the post id (post analytics).

3. Present results clearly:
   - Group by platform
   - Highlight key metrics: impressions, engagement rate, clicks, reach, follower growth
   - If post-level data is available, surface the top 3 performing posts

4. To analyze a specific client profile, the MCP connection must carry that profile's `Profile-Key` header (set in the MCP config). There is no per-call `profileKey` argument on any analytics tool.

## Notes
- If the user asks for a comparison (e.g. "this week vs last week"), call analytics for both periods and compute the delta.
- If a platform returns no data, note it explicitly rather than silently omitting it.
