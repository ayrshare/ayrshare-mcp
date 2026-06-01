---
description: Publish a post to one or more social media platforms via Ayrshare
---

Publish a post to one or more social media platforms via Ayrshare.

## Steps

1. If the user did not provide post content, ask what they want to post.

2. If the user did not specify platforms, call mcp__ayrshare__list_profiles to show connected platforms, then ask which ones to target.

3. Before posting, call mcp__ayrshare__validate_post with the content and platforms to check for platform-specific issues (character limits, unsupported media, etc.). If issues are found, explain them and ask how the user wants to proceed.

4. Ask for confirmation: show a summary of the content and target platforms, then ask "Publish this post?" — do not call create_post until confirmed.

5. Call mcp__ayrshare__create_post with:
   - `post`: the text content
   - `platforms`: array of platform identifiers (e.g. `["twitter", "instagram", "linkedin"]`)
   - `profileKey`: include if AYRSHARE_PROFILE_KEY is set in the environment, or if the user specified a profile

6. Report the result per platform. For any platform that failed, call mcp__ayrshare__explain_error on the error and show a human-readable explanation.

## Optional parameters
- **Schedule**: if the user wants to schedule the post, include `scheduleDate` in ISO 8601 format (e.g. `2025-12-31T10:00:00Z`)
- **X/Twitter BYO credentials**: if X_API_KEY and X_API_SECRET are set, pass them as connection headers
