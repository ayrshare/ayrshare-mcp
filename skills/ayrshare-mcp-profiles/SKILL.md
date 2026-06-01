---
name: ayrshare-mcp-profiles
description: |
  Account-level profile management for the Ayrshare MCP server — create and list client/customer profiles under a Business account. Use whenever someone wants to onboard a new client, set up a customer's social accounts, "add a profile", "create a workspace for a client", list existing profiles, or recover a lost `profileKey`. Trigger when calling tools named `mcp__ayrshare__create_profile` or `mcp__ayrshare__list_profiles`, and even when the user doesn't say "Ayrshare" — if they're managing multiple clients' social accounts through an AI assistant, agency/white-label social setup, or asking "how do I connect a client's accounts", this is the skill. Note: linking a client's social networks (OAuth/connect URL) is NOT done through these MCP tools — it happens in the Ayrshare dashboard or via the REST API directly. For the shared auth model and retry rules, see `../ayrshare-mcp-getting-started/SKILL.md`.
---

# Ayrshare MCP — Profiles

Profile management is the **agency / multi-client layer** of Ayrshare. A *profile* is one client (or customer workspace) under your Business account; each owns its own set of connected social networks and its own `profileKey`. These two tools create and list profiles. They are the front half of client onboarding — see the onboarding sequence in `../ayrshare-mcp-getting-started/SKILL.md`.

## Functions

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__create_profile` | Create a new client profile; returns its `profileKey` | `POST /profiles` | No (account-level) | `title` | `messagingActive`, `hideTopHeader`, `hideLogo`, `topHeader`, `subHeader`, `disableSocial`, `team` (requires `email`), `email`, `tags`, `passthrough` |
| `mcp__ayrshare__list_profiles` | List all profiles under the Business account and their linked platforms | `GET /profiles` | No (account-level) | — | — |

Full input schemas and example payloads/responses are in [`references/schemas.md`](references/schemas.md).

> There is **no MCP tool to generate a connect/JWT/OAuth link** and **no MCP tool to delete a profile**. The profile MCP tools only *create* and *list*. See *Linking a client's social accounts* below.

## Auth

Both tools are **account-level**: they authenticate with the **Business API key** only — the `Authorization: Bearer ${AYRSHARE_API_KEY}` header the MCP server sends, configured via `/ayrshare:setup`. You never supply a `profileKey` as the *auth* key here, and there is **no `profileKey` argument** on either tool.

**How profile scoping actually works.** No Ayrshare MCP tool takes a `profileKey` parameter. To *act as* a specific client profile — post, fetch analytics, pull history under that client — you set the **`Profile-Key` connection header** in the MCP client config (the `headers` block of `.mcp.json`), not a per-call argument. Omit the header to act as the account's primary/Business profile. The `profileKey` that `create_profile` returns is the value you place in that header. Full two-layer model: `../ayrshare-mcp-getting-started/SKILL.md`.

These tools require a **Business plan**. A Launch/free-trial key will fail them even though it is otherwise valid.

## Linking a client's social accounts

Creating a profile does **not** link any social networks to it — a fresh profile has zero connected platforms. Linking a client's accounts (the OAuth/connect step) is **outside these MCP tools**. There is no MCP tool that generates a connect link or runs the OAuth flow. Do it via:

- the **Ayrshare dashboard** (Social Accounts → link, optionally on the client's behalf with their `profileKey`), or
- the **Ayrshare REST API directly** (e.g. the JWT/SSO link generation endpoints), outside the MCP surface.

After the client's accounts are linked, point the MCP connection at that profile by setting its `Profile-Key` header (above) and verify with the History tools (`mcp__ayrshare__get_post_history` / `mcp__ayrshare__get_platform_history`).

## Usage guidance

- **Onboarding a client** runs in order: `create_profile` → capture the returned `profileKey` → link the client's social accounts *outside* the MCP (dashboard or REST API) → set the `Profile-Key` connection header to that key → verify with the History tools. See the full sequence in `../ayrshare-mcp-getting-started/SKILL.md`.
- **Capture the `profileKey`** from `create_profile` immediately — it is sensitive, shown once, and is what you put in the `Profile-Key` header to operate as that client. Treat it like a credential.
- **Lost a `profileKey`?** `list_profiles` is the recovery path. It returns every profile with its linked platforms (and key); don't create a duplicate profile just because a key was misplaced.
- **`team` profiles** require an `email`: set `team: true` only together with the team member's `email`, or the call fails.
- **`disableSocial`** takes an array of network names to disable for that profile; `topHeader`/`subHeader`/`hideTopHeader`/`hideLogo` control the white-label linking-page chrome.

## Gotchas

- **Business key only — no `profileKey` as auth, and no `profileKey` argument anywhere.** These are account-level tools authenticated by the Business key. Neither tool accepts a `profileKey` parameter; profile scoping is the `Profile-Key` connection header, set in `.mcp.json`, not a per-call value. `passthrough` cannot carry it either (credential keys are dropped).
- **`create_profile` does not link any accounts.** A new profile starts empty. The OAuth/connect step is done in the dashboard or via the REST API — there is no MCP tool for it. Don't promise the user a "connect link" from these tools.
- **No delete tool.** The MCP cannot delete or offboard a profile. If a user asks to remove a profile, tell them it must be done in the Ayrshare dashboard or via the REST API — do not claim an MCP tool can do it.
- **`team` without `email` fails.** If `team: true`, `email` is required.
- **`profileKey` is sensitive.** `create_profile` returns it once. Capture it, store it like a secret, and never echo it back in plain logs. `list_profiles` is the recovery path if it's lost.
- **`list_profiles` is the recovery path for a lost key**, not a reason to re-create a profile.
- **Requires a Business plan.** Profiles and multi-client management are Business-only. A valid Launch/trial key still fails here.
- **Never auto-retry `create_profile` on a 4xx.** Call `mcp__ayrshare__explain_error`, surface it, and stop. (Mirrors the global retry-safety rule in `../ayrshare-mcp-getting-started/SKILL.md`; 429 gets at most one retry.)
