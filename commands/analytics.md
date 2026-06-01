---
description: Fetch social media analytics and engagement stats across connected platforms
---

Fetch social media analytics and engagement stats via Ayrshare.

## Steps

1. Determine scope:
   - If the user specified platforms, get analytics for those.
   - If not specified, call mcp__ayrshare__list_profiles and ask which platforms to analyze.

2. Call the Ayrshare analytics MCP tool for the requested platforms and time range.

3. Present results clearly:
   - Group by platform
   - Highlight key metrics: impressions, engagement rate, clicks, reach, follower growth
   - If post-level data is available, surface the top 3 performing posts

4. If profileKey is needed (Business account with multiple profiles), include it in the request.

## Notes
- If the user asks for a comparison (e.g. "this week vs last week"), call analytics for both periods and compute the delta.
- If a platform returns no data, note it explicitly rather than silently omitting it.
