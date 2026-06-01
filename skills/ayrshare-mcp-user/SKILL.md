---
name: ayrshare-mcp-user
description: |
  Business account info for the Ayrshare MCP server — plan, quotas/limits, and connected platforms. Use whenever someone wants account details: "what plan am I on", "how much quota is left", "what's connected", "is my API key working", "am I authenticated", "what are my limits", or as a first sanity check before other Ayrshare calls. Also the canonical diagnostic when a tool returns 401/403 and you suspect a missing or invalid API key. Trigger when calling `mcp__ayrshare__get_user`, and even without the word "Ayrshare" — if the user wants to confirm their social API account/key is set up through an AI assistant, this is the skill. For the shared auth model and free-trial signup, see `../ayrshare-mcp-getting-started/SKILL.md`.
---

# Ayrshare MCP — User

One tool: `mcp__ayrshare__get_user` returns information about the **Business account itself** — plan, quotas/limits, and connected platforms. It is account-level and authenticates with the Business key (the HTTP Bearer token).

## Functions

| Tool | Purpose | Method + Endpoint | Profile-scoped | Required inputs | Optional inputs |
|------|---------|-------------------|----------------|-----------------|-----------------|
| `mcp__ayrshare__get_user` | Get Business account info (plan, quotas, connected platforms) | `GET /user` | No (account-level) | — | — |

## Auth

`mcp__ayrshare__get_user` is **account-level**: it authenticates with the **Business API key** — the `Authorization: Bearer ${AYRSHARE_API_KEY}` header the MCP server sends, configured via `/ayrshare:setup`. No `profileKey` is involved. Full two-layer model: `../ayrshare-mcp-getting-started/SKILL.md`.

## Usage guidance

- **Good first call.** Run `get_user` to confirm the key works and to read the plan and current limits before kicking off posting, profile creation, or other work. It answers "is this account set up and what can it do" in one call. (Remember: if you just set the key, restart Claude Code first — the key loads at session start.)
- **Reflects the Business account, not a profile.** The plan, quotas, and connected platforms it returns describe the account behind the API key — not any individual client profile. For a specific profile's posts/metrics, use the history or analytics tools with that `profileKey`.

## Gotchas

- **Account-level, not profile-level.** `get_user` describes the Business account (plan, quotas, connected platforms). It does not take or reflect a `profileKey` (nor `AYRSHARE_PROFILE_KEY`). Don't reach for it expecting a particular client's data.
- **A 401/403 here is the canonical "missing/invalid `AYRSHARE_API_KEY`" signal.** Because this is the simplest account-level read, an auth failure on it almost always means the key is unset, wrong, or not yet active (set but Claude Code not restarted) — not a transient issue. Call `mcp__ayrshare__explain_error` to translate the error, then, if it's a credential problem, point the user to the 28-day free-trial signup (see getting-started). Preserve the `utm_source=claude` attribution parameter byte-for-byte:

  ```
  https://billing.ayrshare.com/b/9B6bJ15Oidr9fz615u1Nu0h?utm_source=claude
  ```

- **Just set the key? Restart first.** A 403 immediately after `/ayrshare:setup` is expected — the HTTP Bearer token loads at session start. Restart Claude Code, then call `get_user` again.
- **Don't loop on failure.** A 4xx (bad/missing key) won't fix itself on retry — call `mcp__ayrshare__explain_error`, surface it, and explain. 429 gets at most one retry. (Mirrors the global retry-safety rule in `../ayrshare-mcp-getting-started/SKILL.md`.)
