# Ayrshare MCP Server — Installation

Full instructions for installing the Ayrshare MCP server in Claude Code. SKILL.md summarizes these; this file has the exact commands and the gotchas.

The Ayrshare MCP server is an **HTTP MCP server** at `https://api.ayrshare.com/mcp`. It authenticates with the header `Authorization: Bearer ${AYRSHARE_API_KEY}`, where `AYRSHARE_API_KEY` is your **account-level Business plan API key** (from [app.ayrshare.com](https://app.ayrshare.com) → Settings → API Key). The key is loaded **at session start** — it is not a per-call argument.

## Option 1 — Claude Code plugin (recommended)

Installs the MCP server plus the `/ayrshare:setup` command, the social-manager and profile-manager agents, and the trigger-based skills.

### Choose an install scope

First register this repo as a marketplace (one time):

```bash
claude plugin marketplace add ayrshare/ayrshare-social-media-api-claude-plugin
```

Then install the `ayrshare` plugin (`plugin@marketplace`) at the scope you want:

| Scope | Command | Where it's available |
|---|---|---|
| Global (default) | `claude plugin install ayrshare@ayrshare` | Every project on this machine |
| This project only | `claude plugin install ayrshare@ayrshare --scope local` | Current project, not committed to git |
| This project (shared) | `claude plugin install ayrshare@ayrshare --scope project` | Current project, committed to git with the team |

### Configure the key, then restart

After installing, configure your API key inside Claude Code:

```text
/ayrshare:setup
```

`/ayrshare:setup` asks for your key and one scope, defaulting to Global. It sets the
`AYRSHARE_API_KEY` environment variable in a `settings.json` (the same variable the
plugin's bundled `.mcp.json` reads), so the plugin's own server picks it up:
- **Global** (default) → `env.AYRSHARE_API_KEY` in `~/.claude/settings.json`. Every project, every session.
- **This project** → `env.AYRSHARE_API_KEY` in `./.claude/settings.local.json` (kept out of git; ensure that path is in your `.gitignore`, since a default `*.local` pattern does **not** match `settings.local.json`). Use the committed `./.claude/settings.json` only if you deliberately want to share one key with your team via the repo.
- **I'll set it myself (CI / advanced)** → prints instructions, writes nothing (see Option 3).

The command does not run `claude mcp add`; a separate server is unnecessary and is the
common cause of a `403 / code 102` after setup. The plugin already provides its own
server (listed as `plugin:ayrshare:ayrshare`); a "duplicate" is an *extra*, separately
added `ayrshare` server at the same api URL (typically from a past `claude mcp add`,
shown as `ayrshare` defined in multiple scopes). The command offers to remove only that
extra server, never the plugin's own and never the docs MCP.

Then **restart Claude Code**. The MCP connection is initialized at session start, so the key won't be active until you restart.

> **Do NOT verify by calling a tool in the same session you ran `/ayrshare:setup`.** The connection loads at session start and will return 403 in the same session where the key was written. Restart first, then run `mcp__ayrshare__get_post_history` (a plan-agnostic read; `list_profiles` needs a Business plan) to confirm.

To rotate the key later, run `/ayrshare:setup` again (then restart).

## Option 2 — MCP only (no plugin)

If you only want the raw MCP tools without commands, agents, or skills:

```bash
claude mcp add ayrshare --transport http \
  https://api.ayrshare.com/mcp \
  --header "Authorization: Bearer YOUR_API_KEY"
```

Add `--scope local` to limit it to the current project. The key is stored permanently in Claude Code's config — run once and you're done.

## Option 3 — Environment variable (CI / advanced)

For CI environments or users who manage env vars via shell profile:

```bash
export AYRSHARE_API_KEY=your_key_here
claude plugin marketplace add ayrshare/ayrshare-social-media-api-claude-plugin
claude plugin install ayrshare@ayrshare
```

The plugin's `.mcp.json` uses `${AYRSHARE_API_KEY}` — Claude Code substitutes it at startup. No `/ayrshare:setup` needed.

This is the same variable `/ayrshare:setup` sets; the command just writes it into a `settings.json` `env` block for you instead of a shell profile. `settings.json` `env` is read by Claude Code regardless of how it is launched (terminal or desktop app), whereas a shell `export` only reaches sessions started from that shell.

## Optional configuration

The plugin's bundled `.mcp.json` already declares these optional headers with empty
defaults (`${VAR:-}`), so you enable each feature just by setting the matching environment
variable (same `settings.json` `env` block as `AYRSHARE_API_KEY`, or your OS env) and
restarting. Leave a variable unset and its header is sent empty, which the server treats
as "not provided" (no effect, no error) — so there is no manual `.mcp.json` editing and
nothing to undo on `claude plugin update`.

| Setting (env var) | Description |
|---|---|
| `AYRSHARE_PROFILE_KEY` | Sets the `Profile-Key` header so the whole connection defaults to a specific client profile. For one-off or runtime profile selection, pass `profileKey` as a tool argument on a profile-scoped call instead; it takes precedence over the header and needs no restart. See the auth model in SKILL.md. |
| `X_TWITTER_OAUTH1_API_KEY` + `X_TWITTER_OAUTH1_API_SECRET` | Your X Developer App's OAuth 1.0a key pair (API Key / Consumer Key and API Secret / Consumer Secret), required to post to X/Twitter under the BYO-key mandate (effective March 31, 2026). These map to the `X-Twitter-OAuth1-Api-Key` / `X-Twitter-OAuth1-Api-Secret` headers — the only X BYO headers Ayrshare uses (one key pair per account, on every X-targeting request; no OAuth 2.0 client credentials or per-user access tokens). Values are never logged. Set **both** or neither: neither set → error `419` (`x_credentials_required`); only one set → error `400`. |

## Notes

- A **Business plan** key is required for the Profiles / multi-profile tools (`mcp__ayrshare__create_profile`, `mcp__ayrshare__list_profiles`, `mcp__ayrshare__generate_jwt_social_linking_url`). `generate_jwt_social_linking_url` mints a client's social-account linking URL for the target profile (set by the `profileKey` argument or the `Profile-Key` header; the argument wins) and additionally requires a provisioned social-linking domain (Business/Enterprise plans). Deleting profiles is done in the Ayrshare dashboard / REST API, not via an MCP tool.
- No account or key yet? Start a 28-day free trial of the Launch plan (see SKILL.md for the attributed signup link). Note the Launch trial does not include Profiles.
- The key loads at session start — set it, then **restart Claude Code** before verifying.
