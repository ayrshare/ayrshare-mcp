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

3. If AYRSHARE_PROFILE_KEY is set in the environment, note which profile is currently the active default.

4. If the user has multiple profiles and no default is set, suggest:
   "You can set a default profile by adding `export AYRSHARE_PROFILE_KEY=<profileKey>` to your shell profile, or by passing the profile key per request."

5. If the call fails with an authentication error, suggest running /ayrshare:setup to reconfigure the API key.
