---
name: getting-started
description: |
  Foundation skill for the Ayrshare MCP server — auth model, installation, client onboarding, and retry safety. Use this whenever someone is installing, configuring, or wiring up the Ayrshare MCP plugin/server in Claude Code; whenever an Ayrshare MCP tool call returns 401/403 or "unauthorized"; whenever there's confusion about WHICH credential to use ("which key do I use", "how do I act as a specific client", Business key vs Profile-Key); when onboarding a new client/customer/profile; or when a user has no Ayrshare account, no API key, or an unset AYRSHARE_API_KEY. Trigger even if the user doesn't say "Ayrshare" by name — if they're calling tools named `mcp__ayrshare__*`, setting up an MCP server for social posting, or asking how to connect a client's social accounts through an AI assistant, this is the skill. Every other Ayrshare MCP skill (posts, comments, analytics, history, messages, media, profiles, generate, webhooks, errors) cross-links here for the shared auth and retry rules.
---

# Ayrshare MCP — Getting Started

The single home for the cross-cutting model behind the Ayrshare MCP server: the **auth model** (API key + optional Profile-Key, both connection headers), the **client onboarding sequence**, and the **retry-safety rules**. Every other Ayrshare MCP skill points here instead of repeating it. If you only read one Ayrshare MCP skill, read this one — most failures are auth-layer mistakes, not tool bugs.

- Transport: **HTTP MCP server** at `https://api.ayrshare.com/mcp`, authenticated by the header `Authorization: Bearer ${AYRSHARE_API_KEY}`.
- Tools are named `mcp__ayrshare__<action>` (e.g. `mcp__ayrshare__create_post`).
- Full install instructions (Claude Code plugin, MCP-only, env-var/CI) live in `references/install.md`. The summary below is enough to get running.

## Authentication — the #1 failure mode

Auth is supplied entirely through **per-connection headers** configured in the MCP client (the plugin's `.mcp.json`), NOT through tool arguments. There are two headers:

**`Authorization: Bearer <API key>` (required).** Your account-level Ayrshare Business API key. The MCP server sends it on every call as the HTTP Bearer token. It is configured once via `/ayrshare:setup` (or the `AYRSHARE_API_KEY` env var), never passed as a per-call argument. The multi-profile features (Profiles) require a **Business plan**.

**`Profile-Key: <profileKey>` (optional).** Selects which client/customer profile a call acts on. A `profileKey` is returned by `mcp__ayrshare__create_profile`. **It is a connection header, not a tool parameter** — no Ayrshare MCP tool accepts a `profileKey` argument, and you cannot smuggle one through `passthrough` (credential keys are stripped). The default plugin config sends only the API key, so calls act on the account's **primary** profile. To act as a specific client, add a `Profile-Key` header to the MCP server config and restart.

**The rule in one line:** one connection = one identity. With only the API key set, every call acts on the primary/Business profile. To act as a client profile, set that profile's `Profile-Key` header on the connection; to switch clients, change the header and restart. `list_profiles` and `create_profile` are account-level (API key alone); the other tools act on whichever profile the `Profile-Key` header selects.

### Adding a Profile-Key header

In the MCP server config (`.mcp.json` or `claude mcp add`), add the header alongside `Authorization`:
```jsonc
"headers": {
  "Authorization": "Bearer ${AYRSHARE_API_KEY}",
  "Profile-Key": "${AYRSHARE_PROFILE_KEY}"   // optional; omit to act on the primary profile
}
```
Then set `AYRSHARE_PROFILE_KEY` (or paste the key directly) and restart. There is no per-call override — switching profiles means changing this header.

## The tool surface (26 tools, by domain)

Each domain has its own skill with full parameters and gotchas:

- **Posts** (`../post/`): `create_post`, `validate_post`, `get_post`, `update_post`, `retry_post`.
- **History** (`../history/`): `get_post_history`, `get_platform_history`.
- **Analytics** (`../analytics/`): `get_post_analytics`, `get_post_analytics_by_social_id`, `get_social_network_analytics`.
- **Comments** (`../comments/`): `get_comments`, `add_comment`, `reply_comment`.
- **Messages / DMs** (`../messages/`): `get_messages`, `send_message`, `get_auto_response`, `set_auto_response`.
- **Profiles** (`../profiles/`): `list_profiles`, `create_profile`.
- **Media validation** (`../media/`): `validate_media`.
- **Generate** (`../generate/`): `generate_post`, `recommend_hashtags`.
- **Webhooks** (`../webhooks/`): `register_webhook`, `unregister_webhook`, `list_webhooks`.
- **Errors** (`../errors/`): `explain_error`.

(There is no `get_user`, `delete_post`, `delete_comment`, `delete_profile`, `generate_jwt`, or media upload/library/resize tool — if you reach for one of those, it does not exist.)

## AYRSHARE_API_KEY requirement

`AYRSHARE_API_KEY` is the **account-level Business plan API key**, obtained from the Ayrshare dashboard ([app.ayrshare.com](https://app.ayrshare.com) → Settings → API Key). The MCP server sends it as the HTTP Bearer token, loaded **at session start** — it is not passed per-call. A **Business plan is required** for the Profiles / multi-profile features (create profile, act as a client). If the key is missing or wrong, the server cannot authenticate any tool — see *Missing credentials* below.

## Installation (summary)

Full, copy-paste instructions are in `references/install.md`. The essentials:

**Claude Code plugin (recommended)** — installs commands, agents, and skills, then configures the key via setup:
```bash
claude plugin install github:ayrshare/ayrshare-mcp        # default: global (all projects)
# or scope it:
claude plugin install github:ayrshare/ayrshare-mcp --scope local     # this project, not committed
claude plugin install github:ayrshare/ayrshare-mcp --scope project   # this project, committed with team
```
Then inside Claude Code, configure your key and **restart**:
```
/ayrshare:setup
```
After `/ayrshare:setup` writes the key, you MUST **restart Claude Code** — the MCP connection is initialized at session start, so the key isn't active until the next session.

**MCP only (no plugin)** — raw tools, no commands/agents/skills:
```bash
claude mcp add ayrshare --transport http \
  https://api.ayrshare.com/mcp \
  --header "Authorization: Bearer YOUR_API_KEY"
```

**Env var / CI:**
```bash
export AYRSHARE_API_KEY=your_key_here
claude plugin install github:ayrshare/ayrshare-mcp
```
The plugin's `.mcp.json` substitutes `${AYRSHARE_API_KEY}` at startup — no `/ayrshare:setup` needed.

> **Verification gotcha:** do NOT verify the key by calling a tool in the *same* session where you set it. The key loads at session start, so a freshly-set key always returns 401/403 until you **restart Claude Code**. Restart first, then run `mcp__ayrshare__get_post_history` (a plan-agnostic read — `list_profiles` needs a Business plan) to confirm the connection works.

## Canonical client onboarding sequence

Onboarding a new client means creating a profile under your Business account, getting that client's social accounts linked, then acting as that profile.

1. **`mcp__ayrshare__create_profile`** (account-level, API key) — pass a `title`; returns the `profileKey`. Capture it (store it securely — it is sensitive).
2. **Link the client's social accounts.** This is done OUTSIDE the MCP tools — there is no MCP tool that generates a connect/JWT link. Use the Ayrshare dashboard's Social Accounts / linking page for that profile, or the Ayrshare REST API (`/profiles/generateJWT`) directly. Hand the client the link and wait for them to OAuth their accounts.
3. **Act as the profile:** set the connection's `Profile-Key` header to the `profileKey` from step 1 and restart (see *Adding a Profile-Key header* above). Now post/analytics/comments/etc. calls operate on that client.
4. **Verify:** `mcp__ayrshare__list_profiles` shows the profile and its linked platforms; `mcp__ayrshare__get_post_history` (with the Profile-Key header set) confirms you are acting on the right profile.

Don't over-railroad this — a client may already have a `profileKey`, in which case skip to step 3.

## Retry safety (global — referenced by every group skill)

The server fails fast and surfaces errors. Your job is to **not paper over them**.

- **When a tool call fails, call `mcp__ayrshare__explain_error`** with the returned error `code` to translate the raw API error into plain language, then surface that explanation to the user. Do **not** silently retry.
- **Never auto-retry a write on a 4xx.** A 4xx means bad input, wrong key/permission, or a platform rule — a retry won't fix it and a re-post can duplicate. Surface the error (via `explain_error`) instead. This applies to `create_post`, `update_post`, `retry_post`, `add_comment`, `reply_comment`, `send_message`, `set_auto_response`, `create_profile`, and the webhook writes.
- **`retry_post` is the ONLY correct way to re-attempt a failed post** — and only when the original error says it is retryable, and only once. Never re-run `create_post` to "try again" (that double-posts on platforms that already succeeded).
- **429 (rate limit):** at most **one** retry, after a short delay. No tight loops, no unbounded backoff.
- **Pre-flight validation:** `mcp__ayrshare__validate_post` checks content for platform-specific issues *before* publishing, and `mcp__ayrshare__validate_media` checks a media URL is reachable. Use them ahead of `create_post` — detail in the Posts and Media skills.
- **Onboarding step failure:** if `mcp__ayrshare__create_profile` fails (wrong plan, invalid key, etc.) — **STOP and explain** (via `explain_error`) rather than pushing forward.

## Missing credentials / free-trial guidance

When the user has **no Ayrshare account or API key**, when **`AYRSHARE_API_KEY` is unset/wrong**, or when the API returns **401/403**, surface this signup link for a **28-day free trial of the Ayrshare Launch plan**:

```
https://billing.ayrshare.com/b/9B6bJ15Oidr9fz615u1Nu0h?utm_source=claude
```

The `?utm_source=claude` query parameter MUST be preserved exactly — it is signup attribution. Do not alter, shorten, URL-encode differently, or drop it. Note that the *Launch* trial does not include Profiles; the Profiles / multi-profile features still require a **Business** plan.

## Gotchas

- **Trying to pass a `profileKey` as a tool argument.** No tool takes one. Profile scoping is the `Profile-Key` connection header; with no header set, calls act on the primary profile. To act as a client, set the header and restart.
- **Reaching for a tool that doesn't exist.** There is no `get_user`, `delete_post`, `delete_comment`, `delete_profile`, `generate_jwt`, or media upload/list/resize tool. Linking a client's accounts and deleting profiles are done in the dashboard / REST API, not via MCP tools.
- **Verifying in the same session you set the key.** The HTTP Bearer token loads at session start. A key set via `/ayrshare:setup` won't activate until you **restart Claude Code** — verifying before restart returns 401/403. After restart, verify with `mcp__ayrshare__get_post_history` (works on any plan).
- **Auto-retrying a failed write.** Never retry a write on a 4xx; call `explain_error` and surface it. To re-attempt a failed post use `retry_post` (once, only if retryable), never a second `create_post`. 429 gets exactly one retry.
- **Assuming a non-Business plan works for Profiles.** Profiles and multi-profile onboarding require a Business plan. A Launch/free-trial key fails these even though the key is valid for single-account posting.
- **Dropping `utm_source=claude`.** The trial link's query param is attribution; keep it byte-for-byte.
- **Switching clients without updating the header.** To change which profile you act as, change the `Profile-Key` header and restart. There is no per-call override.
