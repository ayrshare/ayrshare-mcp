---
description: List all connected Ayrshare social media profiles as a formatted table
---

List all connected Ayrshare social media profiles.

## Steps

1. Call mcp__ayrshare__list_profiles to fetch all profiles.

2. Format the output as a table:

   | Profile Name | Platforms | Profile Key |
   |---|---|---|
   | (name) | (comma-separated platforms) | (key, or "default" if it is the main account) |

3. After displaying the table:
   - If the connection has a `Profile-Key` header configured (e.g. from `AYRSHARE_PROFILE_KEY`), note which profile is currently active.
   - If there are multiple profiles and none is configured, explain that acting as a specific profile requires setting that profile's `Profile-Key` header on the MCP connection — there is no per-call `profileKey` argument.

4. If the tool call fails with an authentication error, suggest the user run /ayrshare:setup to configure their API key.
