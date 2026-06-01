# Ayrshare MCP for Claude Code

Publish, schedule, and analyze social media across 10+ platforms directly from Claude Code — powered by the [Ayrshare](https://www.ayrshare.com) API.

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
| Global (default) | `claude plugin install github:ayrshare/ayrshare-mcp` | Every project on this machine |
| This project only | `claude plugin install github:ayrshare/ayrshare-mcp --scope local` | Current project, not committed to git |
| This project (shared) | `claude plugin install github:ayrshare/ayrshare-mcp --scope project` | Current project, committed to git with the team |

After installing, configure your API key:

```
/ayrshare:setup
```

`/ayrshare:setup` will ask for your key and where to store it — choose the option that matches how you installed the plugin.

---

### Detailed walkthroughs

#### Global — available in all your projects

```bash
# 1. Install the plugin globally (this is the default)
claude plugin install github:ayrshare/ayrshare-mcp

# 2. Configure your API key (stored in ~/.claude/)
# Run inside Claude Code:
/ayrshare:setup   # choose "Global" when asked
```

Commands, agents, and skills are available in every project. The key is stored in `~/.claude/` — no project files are modified.

---

#### This project only — local, not committed

```bash
# 1. Install scoped to the current project (not committed to git)
claude plugin install github:ayrshare/ayrshare-mcp --scope local

# 2. Configure your API key (stored in .mcp.json in the project directory)
# Run inside Claude Code:
/ayrshare:setup   # choose "This project" when asked
```

Commands, agents, and skills only appear in this project. The key is written to `.mcp.json` in the project root. Add `.mcp.json` to `.gitignore` to keep the key out of version control.

---

#### This project — committed with the team

```bash
# 1. Install scoped to the project (committed to git)
claude plugin install github:ayrshare/ayrshare-mcp --scope project

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
  https://us-central1-ayrshare-dev.cloudfunctions.net/mcp \
  --header "Authorization: Bearer YOUR_API_KEY"
```

Add `--scope local` to limit it to the current project. The key is stored permanently in Claude Code's config — run once and you are done.

---

### Environment variable (CI / advanced)

For CI environments or users who manage env vars via shell profile:

```bash
export AYRSHARE_API_KEY=your_key_here
claude plugin install github:ayrshare/ayrshare-mcp
```

The plugin's `.mcp.json` uses `${AYRSHARE_API_KEY}` — Claude Code substitutes it at startup. No setup command needed.

---

## Commands

| Command | Description |
|---|---|
| `/ayrshare:setup` | Configure or rotate your API key |
| `/ayrshare:post` | Publish a post to one or more platforms |
| `/ayrshare:analytics` | Fetch engagement and performance stats |
| `/ayrshare:profiles` | List connected social media profiles |
| `/ayrshare:link` | Generate a branded short link |

---

## Skills

| Skill | Description |
|---|---|
| `/ayrshare:list-profiles` | List profiles as a formatted table |

---

## Optional Configuration

| Environment Variable | Description |
|---|---|
| `AYRSHARE_PROFILE_KEY` | Fix a default Business profile for all requests |
| `AYRSHARE_PRIVATE_KEY` | RSA private key — required for `/ayrshare:link` |
| `AYRSHARE_DOMAIN` | Custom short link domain — required for `/ayrshare:link` |
| `X_API_KEY` | X/Twitter API key (BYO credentials) |
| `X_API_SECRET` | X/Twitter API secret (BYO credentials) |

---

## Supported Platforms

Facebook, Instagram, LinkedIn, X (Twitter), TikTok, YouTube, Pinterest, Reddit, Telegram, Threads, and more — depending on your Ayrshare plan and connected profiles.

---

## Resources

- [Ayrshare API Docs](https://docs.ayrshare.com)
- [Ayrshare Dashboard](https://app.ayrshare.com)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)
