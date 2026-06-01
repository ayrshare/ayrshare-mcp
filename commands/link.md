---
description: Generate a branded short link using your custom domain via Ayrshare
---

Generate a branded short link via Ayrshare.

## Prerequisites

This command requires two additional environment variables:
- `AYRSHARE_PRIVATE_KEY` — your RSA private key for link signing
- `AYRSHARE_DOMAIN` — your custom short link domain

If either is missing, stop and explain what is needed. The user can configure these at https://app.ayrshare.com under Link Shortener settings.

## Steps

1. Check that AYRSHARE_PRIVATE_KEY and AYRSHARE_DOMAIN are set. If not, explain what is required and stop.

2. If no URL was provided as an argument, ask for the URL to shorten.

3. Call the Ayrshare link MCP tool with the URL, domain, and signing credentials.

4. Display the generated short link. If analytics tracking is included in the response, show the tracking URL as well.

## Notes
- Short links are tied to the AYRSHARE_DOMAIN — make sure the domain is verified in your Ayrshare account before using this command.
