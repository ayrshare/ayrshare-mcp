---
name: profiles
model: claude-sonnet-4-6
effort: high
description: |
  Account-level profile management for the Ayrshare MCP server — create, list, JWT-link, and delete client/customer profiles under a Business account. Use whenever someone wants to onboard a new client, set up a customer's social accounts, "add a profile", "create a workspace for a client", generate a connect/OAuth link for someone to link their social networks, list existing profiles, recover a lost `profileKey`, or remove/offboard a client. Trigger when calling tools named `mcp__ayrshare__create_profile`, `mcp__ayrshare__generate_jwt`, `mcp__ayrshare__list_profiles`, or `mcp__ayrshare__delete_profile`, and even when the user doesn't say "Ayrshare" — if they're managing multiple clients' social accounts through an AI assistant, agency/white-label social setup, or asking "how do I connect a client's accounts", this is the skill. For the shared auth model and retry rules, see `../getting-started/SKILL.md`.
---

# Ayrshare MCP — Profiles

Profile management is the **agency / multi-client layer** of Ayrshare. A *profile* is one client (or customer workspace) under your Business account; each owns its own set of connected social networks and its own `profileKey`. These four tools create, link, list, and delete profiles. They are the front half of the client onboarding sequence — see the onboarding sequence in `../getting-started/SKILL.md`.

## Functions

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__create_profile` | Create a new client profile; returns its `profileKey` | `POST /profiles/profile` | No (account-level) | `title` | — |
| `mcp__ayrshare__generate_jwt` | Generate a browser URL for a profile's user to OAuth their social accounts | `POST /profiles/generateJWT` | No (account-level) | `profileKey`, `domain` | — |
| `mcp__ayrshare__list_profiles` | List all profiles under the Business account | `GET /profiles` | No (account-level) | — | — |
| `mcp__ayrshare__delete_profile` | Permanently delete a profile | `DELETE /profiles/profile` | No (account-level) | `profileKey` | — |

Full input schemas and example payloads/responses are in [`references/schemas.md`](references/schemas.md).

## Auth

All four tools are **account-level**: they authenticate with the **Business API key** only — the `Authorization: Bearer ${AYRSHARE_API_KEY}` header the MCP server sends, configured via `/ayrshare:setup`. You never supply a `profileKey` as the *auth* key here.

**The asymmetry worth internalizing:** `mcp__ayrshare__generate_jwt` and `mcp__ayrshare__delete_profile` take a `profileKey` *as a body parameter* — but that is **data, not authentication**. It names *which* profile to link or delete; the request is still authenticated by the Business key. So a `profileKey` appearing in the input does not make the tool profile-scoped. Contrast this with the profile-scoped tools (analytics, history, post, etc.), where a profile key (via `AYRSHARE_PROFILE_KEY` or a per-call `profileKey`) swaps the acting identity. Full two-layer model: `../getting-started/SKILL.md`.

These tools require a **Business plan**. A Launch/free-trial key will fail them even though it is otherwise valid.

## Usage guidance

- **Onboarding a client** runs in order: `create_profile` → `generate_jwt` → (user OAuths in browser) → verify with `mcp__ayrshare__get_history`. The dependency is hard: `generate_jwt` needs the `profileKey` that `create_profile` returns, so never call it first. The full four-step sequence (including the verification step, which lives in the History skill) is documented in `../getting-started/SKILL.md`.
- **Capture the `profileKey`** from `create_profile` immediately — downstream posting, analytics, and history all need it.
- **Lost a `profileKey`?** `list_profiles` is the recovery path. It returns every profile with its key; don't create a duplicate profile just because a key was misplaced.
- **`generate_jwt`'s `domain`** is the redirect target after the user finishes OAuth; the integration must handle that redirect to know linking is done. The actual account-linking happens in the user's browser — you hand them the URL and wait.

## Gotchas

- **Business key only — no `profileKey` as auth.** These are account-level tools. Passing a profile key as the authenticating key is wrong; the only `profileKey` that belongs here is the *body parameter* on `generate_jwt`/`delete_profile` identifying the target profile.
- **`profileKey` here is data, not the key.** It selects which profile to act on. It does not change who you're authenticated as (still the Business account). This trips people who've used the profile-scoped tools where a profile key *does* swap the acting identity.
- **`delete_profile` is destructive and irreversible.** It permanently removes the profile and unlinks its social accounts. Confirm with the user first, and never auto-retry it on a 4xx (a 4xx means bad key/permission, not a transient failure) — call `mcp__ayrshare__explain_error` and surface the explanation.
- **`generate_jwt` requires a `profileKey` first.** If `create_profile` errored, stop — do not call `generate_jwt` with an empty or guessed key. See the onboarding sequence in `../getting-started/SKILL.md`.
- **`list_profiles` is the recovery path for a lost key**, not a reason to re-create a profile.
- **Requires a Business plan.** Profiles, JWT generation, and multi-client onboarding are Business-only. A valid Launch/trial key still fails here.
- **Never auto-retry `create_profile` or `delete_profile` on a 4xx.** Call `mcp__ayrshare__explain_error`, surface it, and stop. (Mirrors the global retry-safety rule in `../getting-started/SKILL.md`; 429 gets at most one retry.)
