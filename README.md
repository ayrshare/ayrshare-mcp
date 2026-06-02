# Ayrshare MCP for Claude Code

The unified social media API for AI agents. Publish, schedule, and analyze across 13+ networks directly from Claude Code, with post-history retrieval and per-platform content validation before you publish. Powered by the [Ayrshare](https://www.ayrshare.com) API.

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- An Ayrshare account with an API key — get one at [app.ayrshare.com](https://app.ayrshare.com) under **Settings → API Key**

---

## Installation

### Plugin installation scopes

The plugin scope controls where commands, agents, and skills are available. Choose one:

| Scope | Command | Where it's available |
|---|---|---|
| Global (default) | `claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin` | Every project on this machine |
| This project only | `claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin --scope local` | Current project, not committed to git |
| This project (shared) | `claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin --scope project` | Current project, committed to git with the team |

After installing, configure your API key:

```text
/ayrshare:setup
```

`/ayrshare:setup` will ask for your key and where to store it — choose the option that matches how you installed the plugin.

---

### Detailed walkthroughs

#### Global — available in all your projects

```bash
# 1. Install the plugin globally (this is the default)
claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin

# 2. Configure your API key (stored in ~/.claude/)
# Run inside Claude Code:
/ayrshare:setup   # choose "Global" when asked
```

Commands, agents, and skills are available in every project. The key is stored in `~/.claude/` — no project files are modified.

---

#### This project only — local, not committed

```bash
# 1. Install scoped to the current project (not committed to git)
claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin --scope local

# 2. Configure your API key (stored in .mcp.json in the project directory)
# Run inside Claude Code:
/ayrshare:setup   # choose "This project" when asked
```

Commands, agents, and skills only appear in this project. The key is written to `.mcp.json` in the project root. Add `.mcp.json` to `.gitignore` to keep the key out of version control.

---

#### This project — committed with the team

```bash
# 1. Install scoped to the project (committed to git)
claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin --scope project

# 2. Configure your API key (stored in .mcp.json in the project directory)
# Run inside Claude Code:
/ayrshare:setup   # choose "This project" when asked
```

The plugin is committed to the repo so the whole team gets it automatically. Each developer runs `/ayrshare:setup` individually to configure their own API key. Add `.mcp.json` to `.gitignore` so keys are never committed.

---

### MCP only (no plugin)

If you only want the raw MCP tools without commands, agents, or skills:

```bash
claude mcp add ayrshare --transport http \
  https://api.ayrshare.com/mcp \
  --header "Authorization: Bearer YOUR_API_KEY"
```

Add `--scope local` to limit it to the current project. The key is stored permanently in Claude Code's config — run once and you are done.

---

### Environment variable (CI / advanced)

For CI environments or users who manage env vars via shell profile:

```bash
export AYRSHARE_API_KEY=your_key_here
claude plugin install github:ayrshare/ayrshare-social-media-api-claude-plugin
```

The plugin's `.mcp.json` uses `${AYRSHARE_API_KEY}` — Claude Code substitutes it at startup. No setup command needed.

---

## Commands

| Command | Description |
|---|---|
| `/ayrshare:setup` | Configure or rotate your API key |

The former `/ayrshare:post`, `/ayrshare:analytics`, and `/ayrshare:profiles` commands were consolidated into the **social-manager** and **profile-manager** agents and the trigger-based skills below.

---

## Skills

Trigger-based skills activate automatically on intent (even when you don't name Ayrshare) and teach Claude how to drive the MCP tools correctly: the auth model (API key + optional `Profile-Key` header), retry safety, and platform quirks. They cover all 27 of the server's tools. **Start with `getting-started`** — every group skill cross-links to it.

| Skill | Tools | Use when |
|---|---|---|
| `getting-started` | (cross-cutting) | Installing/configuring the plugin, any 401/403, "which credential do I use", onboarding a client, or missing `AYRSHARE_API_KEY`. Home of the auth model (API key + `Profile-Key` header), onboarding sequence, retry/`explain_error` rules, and the free-trial link. |
| `post` | `create_post`, `validate_post`, `get_post`, `update_post`, `retry_post` | Validating, posting, scheduling, editing, fetching, or retrying social content. |
| `history` | `get_post_history`, `get_platform_history` | Listing posts sent via Ayrshare, or native posts (incl. ones not made via Ayrshare) and finding native Social Post IDs. |
| `analytics` | `get_post_analytics`, `get_post_analytics_by_social_id`, `get_social_network_analytics` | Per-post analytics (by Ayrshare or native Social Post ID) or account/network analytics (followers, reach, impressions). |
| `comments` | `get_comments`, `add_comment`, `reply_comment` | Reading, adding, or replying to comments on a post. |
| `messages` | `get_messages`, `send_message`, `get_auto_response`, `set_auto_response` | Reading/sending direct messages (Facebook, Instagram, X) or configuring the DM auto-responder. |
| `profiles` | `list_profiles`, `create_profile`, `generate_jwt` | Creating or listing client profiles, or minting a client's social-account linking URL (account-level, Business plan). |
| `media` | `validate_media` | Checking a media URL is reachable before posting (media is referenced by URL; there is no upload/library/resize tool). |
| `generate` | `generate_post`, `recommend_hashtags` | Drafting AI post copy (never publishes) or suggesting hashtags for a keyword. |
| `webhooks` | `register_webhook`, `unregister_webhook`, `list_webhooks` | Subscribing to push notifications (e.g. when a scheduled post publishes) instead of polling. |
| `errors` | `explain_error` | Decoding an Ayrshare `Error <code>` into a plain-English cause + fix. |

Tool names follow the plugin's `mcp__ayrshare__<action>` convention (e.g. `mcp__ayrshare__create_post`).

---

## Optional Configuration

Both of these are configured by adding **connection headers** to the `ayrshare` server in `.mcp.json` (or via `claude mcp add --header`). There are no per-call `profileKey` or credential parameters on any tool.

### Act as a specific client profile (`Profile-Key`)

Add a `Profile-Key` header alongside `Authorization`:

```jsonc
"headers": {
  "Authorization": "Bearer ${AYRSHARE_API_KEY}",
  "Profile-Key": "${AYRSHARE_PROFILE_KEY}"   // optional; omit to act on the primary profile
}
```

Then set `AYRSHARE_PROFILE_KEY` and restart. With no header set, calls act on the account's primary profile.

### Generate client linking URLs (`generate_jwt`)

The `generate_jwt` tool mints the single sign-on URL a client opens to connect their own social accounts. It needs your account's JWT signing credentials, supplied as connection headers (env-substituted like the API key):

```jsonc
"headers": {
  "Authorization": "Bearer ${AYRSHARE_API_KEY}",
  "X-Ayrshare-Private-Key": "${AYRSHARE_PRIVATE_KEY}",   // your private.key, base64-encoded
  "X-Ayrshare-Domain": "${AYRSHARE_DOMAIN}"              // your onboarding domain
}
```

Encode the key with `cat private.key | base64` (a header cannot carry raw PEM newlines). The private key is a **high-value secret** — it can mint linking URLs for every profile under the account, so source it from an env var / secret store, never commit it, and keep `.mcp.json` out of version control. The tool injects these into the request server-side and never logs them; `generate_jwt` is the only tool that uses them. (This header-based model is interim; a server-side signing surface is planned.)

### Bring-your-own X/Twitter app (BYOK)

If you post to X/Twitter with your own developer app, the MCP server forwards a fixed allowlist of credential headers per request (values are never logged). Add the ones your app uses to the `ayrshare` server's `headers`:

- `X-Twitter-OAuth1-Api-Key`, `X-Twitter-OAuth1-Api-Secret`
- `X-Twitter-OAuth1-Access-Token`, `X-Twitter-OAuth1-Access-Token-Secret`
- `X-Twitter-OAuth2-Client-Id`, `X-Twitter-OAuth2-Client-Secret`

Without them, a BYOK X/Twitter account returns error `419` (`x_credentials_required`).

---

## Supported Platforms

Facebook, Instagram, LinkedIn, X (Twitter), TikTok, YouTube, Pinterest, Reddit, Telegram, Threads, Bluesky, Snapchat, and Google Business Profile — depending on your Ayrshare plan and connected profiles.

---

## Resources

- [Ayrshare API Docs](https://docs.ayrshare.com)
- [Ayrshare Dashboard](https://app.ayrshare.com)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)
