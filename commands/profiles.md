---
description: List and inspect all connected social media profiles
---

List and inspect connected social media profiles via Ayrshare.

## Steps

1. Call mcp__ayrshare__list_profiles to fetch all connected profiles.

2. Display results as a table:

   | Profile Name | Platforms | Profile Key |
   |---|---|---|
   | (name) | (comma-separated list) | (key or "default") |

3. If the MCP connection has a `Profile-Key` header configured (e.g. templated from `AYRSHARE_PROFILE_KEY`), note which profile is currently active.

4. If the user has multiple profiles and none is currently selected, explain how to act as a specific profile: add a `Profile-Key` header to the MCP server config set to that profile's key (you can template it as `${AYRSHARE_PROFILE_KEY}` and export the env var), then restart. There is NO per-request `profileKey` argument on any tool.

5. If the call fails with an authentication error, suggest running /ayrshare:setup to reconfigure the API key.
