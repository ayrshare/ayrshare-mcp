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
   - If AYRSHARE_PROFILE_KEY is set, note which profile is currently the active default.
   - If there are multiple profiles and no default is set, suggest: "Set a default profile by exporting AYRSHARE_PROFILE_KEY=<profileKey>."

4. If the tool call fails with an authentication error, suggest the user run /ayrshare:setup to configure their API key.
