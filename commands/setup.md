---
description: Configure or rotate the Ayrshare API key after the plugin is installed
---

Configure the Ayrshare API key for Claude Code. Run this after installing the plugin.

The plugin's bundled MCP server reads the key from the `AYRSHARE_API_KEY`
environment variable (its `.mcp.json` sends `Authorization: Bearer ${AYRSHARE_API_KEY}`).
This command's job is to set that one variable in the right `settings.json` so the
plugin's own server picks it up. Do not create a separate MCP server with
`claude mcp add`; that produces a second server the plugin does not use and is the
classic cause of a `403 / code 102` after setup.

## Steps

1. **Get the key.** If the user did not include their API key as an argument, ask:
   "Please paste your Ayrshare API key. You can get one at https://app.ayrshare.com under Settings → API Key."

2. **Choose scope.** Ask one question, defaulting to Global:

   "Where should this key be available?
   - **Global (default)** — every project and session on this machine. Stored in `~/.claude/settings.json`.
   - **This project** — only this repo (still persists across sessions). Stored in `./.claude/settings.json`.
   - **I'll set it myself (CI / advanced)** — print instructions, write nothing."

3. **Write the variable** based on the answer. In every write case you are adding
   or updating `env.AYRSHARE_API_KEY` in a `settings.json` file. Read the file if it
   exists, parse it as JSON, set `env.AYRSHARE_API_KEY` to the key, and write it back
   preserving every other field. Create the file (and its directory) if missing.

   **Global:** target `~/.claude/settings.json` — your home directory on every OS (`~/.claude/settings.json` on macOS/Linux, `%USERPROFILE%\.claude\settings.json` on Windows).

   **This project:** target `./.claude/settings.json` (the current working directory).
   Remind the user that `.claude/settings.json` is normally committed; if they do not
   want the key in git, use `.claude/settings.local.json` instead (same `env` shape).
   A default `.gitignore` does **not** ignore `settings.local.json` (a `*.local`
   pattern does not match `*.local.json`), so explicitly tell the user to add
   `.claude/settings.local.json` to their `.gitignore` and confirm `git status` does
   not list it before committing.

   The resulting file should look like (other keys preserved):
   ```json
   {
     "env": {
       "AYRSHARE_API_KEY": "THE_KEY"
     }
   }
   ```

   **I'll set it myself:** write nothing. Tell the user to define the `AYRSHARE_API_KEY`
   environment variable with their platform's own mechanism, so it is present in the
   environment **before** Claude Code launches:
   - macOS / Linux: `export AYRSHARE_API_KEY=...` in a shell profile (`~/.zshrc`, `~/.bashrc`, ...), or a CI secret.
   - Windows: `setx AYRSHARE_API_KEY "..."` (or `$env:AYRSHARE_API_KEY="..."` in PowerShell), or set it under System Environment Variables.

   The plugin's `.mcp.json` substitutes `${AYRSHARE_API_KEY}` at session start on every OS.
   The `settings.json` `env` approach (the Global / This project options above) is the most
   portable choice: Claude Code reads it identically on macOS, Linux, and Windows, and it
   also works where there is no launching shell (e.g. the Claude desktop app). Prefer it
   unless the user specifically wants OS-managed environment variables.

4. **Offer to clean up a stale duplicate server.** Older versions of this command
   created a separate `ayrshare` MCP server (via `claude mcp add`) with the key in a
   header. That extra server shadows or collides with the plugin and should be removed.
   Run `claude mcp list` and identify it carefully:
   - The **plugin's own** server is the one to keep. The plugin provides it from the
     bundled `.mcp.json`, and Claude Code lists it namespaced as
     `plugin:ayrshare:ayrshare` (URL `https://api.ayrshare.com/mcp`). **Never remove this one.**
   - A **stale duplicate** is a *separately added* server listed as plain `ayrshare`
     (no `plugin:` prefix) at `https://api.ayrshare.com/mcp` — i.e. an `ayrshare`
     entry that exists *in addition to* the plugin's, often flagged as "defined in
     multiple scopes" by `claude mcp list`. Only this one should be offered for removal,
     with `claude mcp remove ayrshare` (add `--scope user` or `--scope local` to match where it lives).
   - **Never remove an `ayrshare` server whose URL is the docs endpoint**
     (`https://www.ayrshare.com/docs/mcp`). That is the separate Ayrshare documentation
     MCP, not a duplicate; leave it untouched.
   - If the only `ayrshare`-related server is the plugin's own (`plugin:ayrshare:ayrshare`),
     there is nothing to clean up; do not prompt for removal.

5. **Tell the user to restart.**
   - "Setup complete. **Restart Claude Code** to activate the connection. The MCP server is initialized at session start, so the key won't be active until you restart."

## Notes
- One mechanism, one variable: every scope sets `AYRSHARE_API_KEY`, which is exactly what the plugin's bundled server reads. No duplicate servers.
- **Optional credential variables (same `env` block, all empty by default).** The plugin's `.mcp.json` also interpolates three optional variables you set the same way (`settings.json` `env`, or your OS env):
  - `AYRSHARE_PROFILE_KEY` — act as a specific client profile by default (instead of passing `profileKey` per call).
  - `X_TWITTER_OAUTH1_API_KEY` and `X_TWITTER_OAUTH1_API_SECRET` — your X/Twitter app's OAuth 1.0a consumer key and secret, required to post to X under the BYO-key mandate.

  Each uses `${VAR:-}`, so when you leave it unset the header is sent empty and the server treats it as not provided (no effect, no error). Set it to turn the feature on. Restart Claude Code after changing any of them.
- To rotate the key, run `/ayrshare:setup` again and pick the same scope; it overwrites the variable in place.
- Do NOT verify by calling any MCP tool after setup. The connection loads at session start and will return 401/403 in the same session where the key was written. Restart first.
