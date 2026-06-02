---
name: profiles
description: |
  Account-level profile management for the Ayrshare MCP server — create profiles, list profiles, and generate social-account linking URLs for client/customer profiles under a Business account. Use whenever someone wants to onboard a new client, set up a customer's social accounts, "add a profile", "create a workspace for a client", list existing profiles, recover a lost `profileKey`, or get a link a client opens to connect their own social networks. Trigger when calling tools named `mcp__ayrshare__create_profile`, `mcp__ayrshare__list_profiles`, or `mcp__ayrshare__generate_jwt`, and even when the user doesn't say "Ayrshare" — if they're managing multiple clients' social accounts through an AI assistant, agency/white-label social setup, or asking "how do I connect a client's accounts" / "send my client a link to link their socials", this is the skill. `mcp__ayrshare__generate_jwt` mints the single sign-on linking URL the client opens to connect their networks; the OAuth itself still completes in their browser. For the shared auth model and retry rules, see `../getting-started/SKILL.md`.
---

# Ayrshare MCP — Profiles

Profile management is the **agency / multi-client layer** of Ayrshare. A *profile* is one client (or customer workspace) under your Business account; each owns its own set of connected social networks and its own `profileKey`. These three tools create profiles, list them, and mint the social-account linking URL a client opens to connect their networks. Together they cover client onboarding — see the onboarding sequence in `../getting-started/SKILL.md`.

## Functions

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__create_profile` | Create a new client profile; returns its `profileKey` | `POST /profiles` | No (account-level) | `title` | `messagingActive`, `hideTopHeader`, `hideLogo`, `topHeader`, `subHeader`, `disableSocial`, `team` (requires `email`), `email`, `tags` |
| `mcp__ayrshare__list_profiles` | List all profiles under the Business account and their linked platforms | `GET /profiles` | No (account-level) | — | `title`, `refId`, `hasActiveSocialAccounts`, `includesActiveSocialAccounts`, `isByokLinked`, `actionLog`, `limit`, `cursor`, `include` |
| `mcp__ayrshare__generate_jwt` | Mint a single sign-on social-account **linking URL** for one profile — the link a client opens to connect their own networks | `POST /profiles/generateJWT` | No (account-level; targets the `profileKey` **argument**, not the connection header) | `profileKey` (the target sub-profile) | `logout`, `redirect`, `allowedSocial`, `verify`, `expiresIn` (Max Pack), `email` (Max Pack) |

Full input schemas and example payloads/responses are in [`references/schemas.md`](references/schemas.md).

> `mcp__ayrshare__generate_jwt` mints the single sign-on linking URL a client opens to connect their social accounts; it does **not** run the OAuth flow itself (the client completes that in their browser) and it does **not** link anything on its own. There is still **no MCP tool to delete a profile**. See *Linking a client's social accounts* below.

## Auth

`create_profile` and `list_profiles` are **account-level**: they authenticate with the **Business API key** only — the `Authorization: Bearer ${AYRSHARE_API_KEY}` header the MCP server sends, configured via `/ayrshare:setup`. You never supply a `profileKey` as the *auth* key, and neither of those two takes a `profileKey` argument. (`generate_jwt`, the third tool in this skill, is the exception — it takes a *target* `profileKey` **argument**; see below.)

**How profile scoping actually works.** `create_profile` and `list_profiles` take no `profileKey` parameter and **ignore the `Profile-Key` header** — they are account-level. To *act as* a specific client profile — post, fetch analytics, pull history under that client — you set the **`Profile-Key` connection header** in the MCP client config (the `headers` block of `.mcp.json`), not a per-call argument. Omit the header to act as the account's primary/Business profile. The `profileKey` that `create_profile` returns is the value you place in that header. (`generate_jwt` is the lone tool that takes a `profileKey` *argument* — covered next.) Full two-layer model: `../getting-started/SKILL.md`.

**`generate_jwt` is the one exception to the no-`profileKey`-argument rule.** It takes a `profileKey` **argument** naming the sub-profile to mint the link *for*: you stay authenticated as the Primary Profile (the API key) and generate a linking URL for that specific client. The connection's `Profile-Key` header is ignored by this tool. `generate_jwt` additionally needs the account's JWT signing credentials, supplied as **connection headers** (never arguments): `X-Ayrshare-Private-Key` (your `private.key`, base64-encoded) and `X-Ayrshare-Domain` (your onboarding domain), env-substituted in `.mcp.json` exactly like the API key. The tool injects them into the request server-side and never logs them. The private key is a **high-value secret** (it can mint linking URLs for every profile under the account) — keep it out of version control, source it from an env var / secret store rather than a literal in a committed file, and treat the whole config like a credential. This header-based model is interim; see *Linking a client's social accounts* below.

`create_profile` / `list_profiles` require a **Business plan**. A Launch/free-trial key will fail them even though it is otherwise valid.

## Linking a client's social accounts

Creating a profile does **not** link any social networks to it — a fresh profile has zero connected platforms. To connect a client's accounts you generate a **single sign-on linking URL** and the client opens it to OAuth their own networks.

- **`mcp__ayrshare__generate_jwt` (in-MCP).** Pass the client's `profileKey` and get back a hosted `url` (valid 5 minutes by default, or `expiresIn` on the Max Pack). Hand that URL to the client; they open it in a browser and link their accounts. Requires the `X-Ayrshare-Private-Key` (base64) and `X-Ayrshare-Domain` connection headers (see *Auth* above). `generate_jwt` only *mints* the link — the OAuth itself happens in the client's browser, not via any MCP tool.
- **Ayrshare dashboard** (Social Accounts → link), or the **REST API** (`POST /profiles/generateJWT`) directly — equivalent alternatives to `generate_jwt` if you are not driving it through the MCP.

After the client's accounts are linked, point the MCP connection at that profile by setting its `Profile-Key` header (above) and verify with the History tools (`mcp__ayrshare__get_post_history` / `mcp__ayrshare__get_platform_history`).

## Usage guidance

- **Onboarding a client** runs in order: `create_profile` → capture the returned `profileKey` → `generate_jwt` with that `profileKey` to mint the linking URL → hand the URL to the client to OAuth their accounts → set the `Profile-Key` connection header to that key → verify with the History tools. See the full sequence in `../getting-started/SKILL.md`.
- **Capture the `profileKey`** from `create_profile` immediately — it is sensitive, shown once (the API cannot return it again), and is what you put in the `Profile-Key` header to operate as that client. Treat it like a credential.
- **Lost a `profileKey`?** It cannot be recovered through the API — `list_profiles` does **not** return profile keys (the `GET /profiles` call omits them for security). Retrieve a lost key from the **Ayrshare dashboard**; don't create a duplicate profile just because a key was misplaced.
- **`team` profiles** require an `email`: set `team: true` only together with the team member's `email`, or the call fails.
- **`disableSocial`** takes an array of network names to disable for that profile; `topHeader`/`subHeader`/`hideTopHeader`/`hideLogo` control the white-label linking-page chrome.

## Gotchas

- **`profileKey` as auth vs as a target.** `create_profile` / `list_profiles` are account-level (Business key) and take **no** `profileKey` parameter — profile scoping is the `Profile-Key` connection header. The one exception is `generate_jwt`, which takes a `profileKey` **argument** to name the sub-profile it mints the link for (the connection's `Profile-Key` header is ignored there). No tool ever uses a `profileKey` as the *auth* key.
- **`generate_jwt` mints the link; it does not link accounts itself.** A new profile starts empty. `generate_jwt` returns the URL a client opens to OAuth their networks — the actual linking happens in the client's browser, not via any MCP tool. (The dashboard and REST `POST /profiles/generateJWT` are equivalent alternatives.) `generate_jwt` needs the `X-Ayrshare-Private-Key` / `X-Ayrshare-Domain` connection headers.
- **No delete tool.** The MCP cannot delete or offboard a profile. If a user asks to remove a profile, tell them it must be done in the Ayrshare dashboard or via the REST API — do not claim an MCP tool can do it.
- **`team` without `email` fails.** If `team: true`, `email` is required.
- **`profileKey` is sensitive.** `create_profile` returns it once and the API never returns it again. Capture it, store it like a secret, and never echo it back in plain logs. A lost key is recoverable only from the Ayrshare dashboard.
- **`list_profiles` returns `title`/`refId`/linked platforms — not `profileKey`.** The `GET /profiles` call omits keys for security, so `list_profiles` cannot recover a lost key (use the dashboard for that). Use it to find a profile or its `refId`, not as a reason to re-create a profile.
- **Requires a Business plan.** Profiles and multi-client management are Business-only. A valid Launch/trial key still fails here.
- **Never auto-retry `create_profile` on a 4xx.** Call `mcp__ayrshare__explain_error`, surface it, and stop. (Mirrors the global retry-safety rule in `../getting-started/SKILL.md`; 429 gets at most one retry.)
