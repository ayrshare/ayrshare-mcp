---
description: Generate a branded short link using a custom domain via Ayrshare
model: claude-sonnet-4-6
effort: high
---

Generate a branded short link via Ayrshare.

## Prerequisites

Requires two environment variables:
- `AYRSHARE_PRIVATE_KEY` — RSA private key for link signing
- `AYRSHARE_DOMAIN` — custom short link domain

If either is missing, stop and explain what is needed. The user can configure these at https://app.ayrshare.com under Link Shortener settings.

## Steps

1. Check that AYRSHARE_PRIVATE_KEY and AYRSHARE_DOMAIN are set. If not, explain what is required and stop.

2. If no URL was provided, ask for the URL to shorten.

3. Call the Ayrshare link MCP tool with the URL, domain, and signing credentials.

4. Display the generated short link. If analytics tracking is included in the response, show the tracking URL as well.

## Notes
- The short link domain must be verified in the Ayrshare account before use.
