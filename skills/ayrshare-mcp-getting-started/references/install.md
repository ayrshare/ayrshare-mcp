# Ayrshare MCP Server — Installation

Full instructions for installing the Ayrshare MCP server in Claude Code. SKILL.md summarizes these; this file has the exact commands and the gotchas.

The Ayrshare MCP server is an **HTTP MCP server** at `https://us-central1-ayrshare-dev.cloudfunctions.net/mcp`. It authenticates with the header `Authorization: Bearer ${AYRSHARE_API_KEY}`, where `AYRSHARE_API_KEY` is your **account-level Business plan API key** (from [app.ayrshare.com](https://app.ayrshare.com) → Settings → API Key). The key is loaded **at session start** — it is not a per-call argument.

## Option 1 — Claude Code plugin (recommended)

Installs the MCP server plus the bundled commands (`/ayrshare:setup`, `/ayrshare:post`, …), the social-manager agent, and skills.

### Choose an install scope

| Scope | Command | Where it's available |
|---|---|---|
| Global (default) | `claude plugin install github:ayrshare/ayrshare-mcp` | Every project on this machine |
| This project only | `claude plugin install github:ayrshare/ayrshare-mcp --scope local` | Current project, not committed to git |
| This project (shared) | `claude plugin install github:ayrshare/ayrshare-mcp --scope project` | Current project, committed to git with the team |

### Configure the key, then restart

After installing, configure your API key inside Claude Code:

```
/ayrshare:setup
```

`/ayrshare:setup` asks for your key and where to store it — choose the option that matches your install scope:
- **Global** → key stored in `~/.claude/`.
- **This project** (`--scope local` or `--scope project`) → key written to `.mcp.json` in the project root. Add `.mcp.json` to `.gitignore` so the key is never committed.

Then **restart Claude Code**. The MCP connection is initialized at session start, so the key won't be active until you restart.

> **Do NOT verify by calling a tool in the same session you ran `/ayrshare:setup`.** The connection loads at session start and will return 403 in the same session where the key was written. Restart first, then run `mcp__ayrshare__list_profiles` (a no-argument read) to confirm.

To rotate the key later, run `/ayrshare:setup` again (then restart).

## Option 2 — MCP only (no plugin)

If you only want the raw MCP tools without commands, agents, or skills:

```bash
claude mcp add ayrshare --transport http \
  https://us-central1-ayrshare-dev.cloudfunctions.net/mcp \
  --header "Authorization: Bearer YOUR_API_KEY"
```

Add `--scope local` to limit it to the current project. The key is stored permanently in Claude Code's config — run once and you're done.

## Option 3 — Environment variable (CI / advanced)

For CI environments or users who manage env vars via shell profile:

```bash
export AYRSHARE_API_KEY=your_key_here
claude plugin install github:ayrshare/ayrshare-mcp
```

The plugin's `.mcp.json` uses `${AYRSHARE_API_KEY}` — Claude Code substitutes it at startup. No `/ayrshare:setup` needed.

## Optional configuration

| Environment Variable | Description |
|---|---|
| `AYRSHARE_PROFILE_KEY` | Value for an optional `Profile-Key` connection header — set this to act as a specific client profile. **Only takes effect if you add a `Profile-Key` header to the MCP server config** (the default config sends only the API key); there is no per-call `profileKey` parameter. See the auth model in SKILL.md. |
| `AYRSHARE_PRIVATE_KEY` | RSA private key — required for `/ayrshare:link` (branded short links). |
| `AYRSHARE_DOMAIN` | Custom short-link domain — required for `/ayrshare:link`. |
| `X_API_KEY` / `X_API_SECRET` | X/Twitter API credentials (bring-your-own). |

## Notes

- A **Business plan** key is required for the Profiles / multi-profile tools (`mcp__ayrshare__create_profile`, `mcp__ayrshare__list_profiles`). Linking a client's social accounts and deleting profiles are done in the Ayrshare dashboard / REST API, not via MCP tools.
- No account or key yet? Start a 28-day free trial of the Launch plan (see SKILL.md for the attributed signup link). Note the Launch trial does not include Profiles.
- The key loads at session start — set it, then **restart Claude Code** before verifying.
