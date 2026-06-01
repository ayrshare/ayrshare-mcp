---
name: getting-started
model: claude-sonnet-4-6
effort: high
description: |
  Foundation skill for the Ayrshare MCP server — auth model, installation, client onboarding, and retry safety. Use this whenever someone is installing, configuring, or wiring up the Ayrshare MCP plugin/server in Claude Code; whenever an Ayrshare MCP tool call returns 401/403 or "unauthorized"; whenever there's confusion about WHICH key to pass ("which key do I use", "do I need a profileKey here", Business key vs profile key); when onboarding a new client/customer/profile or generating a JWT/connect URL; or when a user has no Ayrshare account, no API key, or an unset AYRSHARE_API_KEY. Trigger even if the user doesn't say "Ayrshare" by name — if they're calling tools named `mcp__ayrshare__*`, setting up an MCP server for social posting, or asking how to connect a client's social accounts through an AI assistant, this is the skill. Other Ayrshare MCP skills (post, comments, analytics, media, profiles, user) cross-link here for the shared auth and retry rules.
---

# Ayrshare MCP — Getting Started

The single home for the cross-cutting model behind the Ayrshare MCP server: the **two-layer auth scheme**, the **client onboarding sequence**, and the **retry-safety rules**. Every other Ayrshare MCP skill points here instead of repeating it. If you only read one Ayrshare MCP skill, read this one — most failures are auth-layer mistakes, not tool bugs.

- Transport: **HTTP MCP server** at `https://api.ayrshare.com/mcp`, authenticated by the header `Authorization: Bearer ${AYRSHARE_API_KEY}`.
- Tools are named `mcp__ayrshare__<action>` (e.g. `mcp__ayrshare__create_profile`).
- Full install instructions (Claude Code plugin, MCP-only, env-var/CI) live in `references/install.md`. The summary below is enough to get running.

## Two-layer authentication — the #1 failure mode

Ayrshare has **two distinct keys**. Using the wrong one for a given tool is the most common cause of 401/403 and of acting on the wrong account. They are not interchangeable.

**Layer 1 — Business API key.** Account-level. This is the **HTTP Bearer token** the MCP server sends as `Authorization: Bearer ${AYRSHARE_API_KEY}`. It is configured once via `/ayrshare:setup` (or the `AYRSHARE_API_KEY` env var), **not** passed as a per-call argument. Requires a **Business plan**. This key authenticates the *account-level* tools and is the default identity for any profile-scoped tool when no `profileKey` is supplied.

Account-level tools (NEVER pass a `profileKey` as the auth key to these):
- `mcp__ayrshare__create_profile`
- `mcp__ayrshare__generate_jwt`
- `mcp__ayrshare__list_profiles`
- `mcp__ayrshare__delete_profile`
- `mcp__ayrshare__get_user`

**Layer 2 — profileKey.** Per-profile. Returned by `mcp__ayrshare__create_profile`. Identifies one client/customer profile and its connected social accounts. There are **two ways to supply it**:

1. **`AYRSHARE_PROFILE_KEY` env var** — fixes a **default** Business profile applied to *all* requests. Set it when you work primarily with one client and don't want to pass the key every time.
2. **Per-call `profileKey` parameter** — overrides the env-var default for a single request. Profile-scoped tools accept an optional `profileKey`; when provided, the server uses it instead of both the env-var default and the bare Business key for that one request.

Profile-scoped tools (use `AYRSHARE_PROFILE_KEY` and/or a per-call `profileKey` to act on a client; omit both to act as the Business account itself):
- History: `mcp__ayrshare__get_history`
- Analytics: `mcp__ayrshare__get_post_analytics`, `mcp__ayrshare__get_social_analytics`
- Posts: `mcp__ayrshare__create_post`, `mcp__ayrshare__validate_post`, `mcp__ayrshare__get_post`, `mcp__ayrshare__update_post`, `mcp__ayrshare__delete_post`, `mcp__ayrshare__retry_post`
- Comments: `mcp__ayrshare__get_comments`, `mcp__ayrshare__post_comment`, `mcp__ayrshare__reply_comment`, `mcp__ayrshare__delete_comment`
- Media: `mcp__ayrshare__upload_media`, `mcp__ayrshare__list_media`, `mcp__ayrshare__verify_media`, `mcp__ayrshare__resize_media`

**The rule in one line:** account-level Profiles/user tools → Business key only, never a `profileKey` as auth. Profile-scoped tools → supply a profile key (env default and/or per-call override) to operate on a specific client, or intentionally omit it to operate on the Business account directly. "Intentionally" matters: with no `AYRSHARE_PROFILE_KEY` set and no per-call `profileKey`, a profile-scoped post silently posts under the Business account, not the client you meant.

## AYRSHARE_API_KEY requirement

`AYRSHARE_API_KEY` is the **account-level Business plan API key**, obtained from the Ayrshare dashboard ([app.ayrshare.com](https://app.ayrshare.com) → Settings → API Key). The MCP server sends it as the HTTP Bearer token, loaded **at session start** — it is not passed per-call. A **Business plan is required** for the Profiles / multi-profile features (create profile, generate JWT, etc.). If the key is missing or wrong, the server cannot authenticate any tool — see *Missing credentials* below.

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

> **Verification gotcha:** do NOT verify the key by calling a tool in the *same* session where you set it. The key loads at session start, so a freshly-set key always returns 403 until you **restart Claude Code**. Restart first, then run `mcp__ayrshare__get_user` to confirm.

## Canonical client onboarding sequence

Onboarding a new client connects their social accounts to a profile under your Business account. The order matters because each step feeds the next.

1. **`mcp__ayrshare__create_profile`** (account-level, Business key) — returns the `profileKey`. Capture it; everything downstream needs it.
2. **`mcp__ayrshare__generate_jwt`** (account-level, Business key) — pass the `profileKey` from step 1 plus a redirect `domain`. Returns a URL. **Never call this before you have a profileKey** — without it there is nothing to generate a token for.
3. **User opens the JWT URL in a browser** and OAuths their social accounts. This happens outside the tools; you can't do it for them. Hand them the URL and wait.
4. **`mcp__ayrshare__get_history`** with that `profileKey` (profile-scoped) — verifies the connection succeeded and shows the profile's posts.

Don't over-railroad this — a user may already have a profileKey from a prior session, in which case skip to step 2 or 3. The hard rule is the dependency: no `generate_jwt` without a `profileKey`.

## Retry safety (global — referenced by every group skill)

The server fails fast and surfaces errors. Your job is to **not paper over them**.

- **When a tool call fails, call `mcp__ayrshare__explain_error`** on the error to translate the raw API error into plain language, then surface that explanation to the user. Do **not** silently retry.
- **Never auto-retry writes/deletes on any 4xx.** These tools must surface the error (via `explain_error`) instead of retrying: `mcp__ayrshare__create_post`, `mcp__ayrshare__update_post`, `mcp__ayrshare__delete_post`, `mcp__ayrshare__post_comment`, `mcp__ayrshare__reply_comment`, `mcp__ayrshare__delete_comment`, `mcp__ayrshare__delete_profile`. A 4xx means bad input, wrong key, or missing permission — a retry won't fix it and a delete/post retry can duplicate or destroy.
- **429 (rate limit):** at most **one** retry, after a short delay. No tight loops, no unbounded backoff.
- **Pre-flight validation:** `mcp__ayrshare__validate_post` lets you check content for platform-specific issues *before* publishing. Use it ahead of `create_post` — detail lives in the Posts skill.
- **Onboarding step failure:** if `mcp__ayrshare__create_profile` (or any onboarding step) fails — wrong plan, invalid key, etc. — **STOP the sequence and explain** (via `explain_error`). Do not proceed to `mcp__ayrshare__generate_jwt` with a missing/empty `profileKey`.

## Missing credentials / free-trial guidance

When the user has **no Ayrshare account or API key**, when **`AYRSHARE_API_KEY` is unset/wrong**, or when the API returns **401/403**, surface this signup link for a **28-day free trial of the Ayrshare Launch plan**:

```
https://billing.ayrshare.com/b/9B6bJ15Oidr9fz615u1Nu0h?utm_source=claude
```

The `?utm_source=claude` query parameter MUST be preserved exactly — it is signup attribution. Do not alter, shorten, URL-encode differently, or drop it. Note that the *Launch* trial does not include Profiles; the Profiles/onboarding tools still require a **Business** plan.

## Gotchas

- **Wrong key layer.** Passing a `profileKey` as the *auth* for an account-level Profiles/user tool, or expecting a profile-scoped post to "just know" the client with neither `AYRSHARE_PROFILE_KEY` nor a per-call `profileKey` set. Account-level tools use the Business key only; profile-scoped tools need a profile key to target a client.
- **`generate_jwt` before a profileKey exists.** Step 2 depends on step 1's output. Calling it first (or with an empty `profileKey`) fails — and if an earlier onboarding step errored, stop, don't push forward.
- **Verifying in the same session you set the key.** The HTTP Bearer token loads at session start. A key set via `/ayrshare:setup` won't activate until you **restart Claude Code** — verifying before restart always returns 403.
- **Auto-retrying writes/deletes.** Never retry `create_post`, `update_post`, `delete_post`, comment writes/deletes, or `delete_profile` on a 4xx. Call `mcp__ayrshare__explain_error` and surface it. 429 gets exactly one retry.
- **Assuming a non-Business plan works for Profiles.** Profiles, JWT generation, and multi-profile onboarding require a Business plan. A Launch/free-trial key will fail these even though the key is valid for single-account posting.
- **Dropping `utm_source=claude`.** The trial link's query param is attribution; keep it byte-for-byte.
- **Silently acting on the Business account.** Omitting a profile key on a profile-scoped write is legal and posts under the Business account. If you meant a client, that's a silent mis-post — only omit it on purpose.
- **`AYRSHARE_PROFILE_KEY` is a sticky default.** Once set, it applies to *every* profile-scoped request until overridden by a per-call `profileKey`. If you switch clients, either change the env var (and restart) or pass `profileKey` explicitly on each call.
