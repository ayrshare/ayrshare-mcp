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

   **Global:** target `~/.claude/settings.json`.

   **This project:** target `./.claude/settings.json` (the current working directory).
   Remind the user that `.claude/settings.json` is normally committed; if they do not
   want the key in git, use `.claude/settings.local.json` instead (same `env` shape)
   and ensure it is gitignored.

   The resulting file should look like (other keys preserved):
   ```json
   {
     "env": {
       "AYRSHARE_API_KEY": "THE_KEY"
     }
   }
   ```

   **I'll set it myself:** write nothing. Print:
   ```bash
   export AYRSHARE_API_KEY=your_key_here   # add to ~/.zshenv, CI secret, etc.
   ```
   and note the plugin's `.mcp.json` substitutes `${AYRSHARE_API_KEY}` at session start.

4. **Offer to clean up a stale duplicate server.** Older versions of this command
   created a separate `ayrshare` MCP server with the key in a header. If one exists it
   shadows or collides with the plugin and should be removed. Run `claude mcp list` and
   look for a server named `ayrshare` whose URL is `https://api.ayrshare.com/mcp`.
   - If found, tell the user it is a leftover duplicate and offer to remove it with
     `claude mcp remove ayrshare` (add `--scope user` or `--scope local` to match where it lives).
   - **Never remove an `ayrshare` server whose URL is the docs endpoint**
     (`https://www.ayrshare.com/docs/mcp`). That is the separate Ayrshare documentation
     MCP, not a duplicate; leave it untouched.

5. **Tell the user to restart.**
   - "Setup complete. **Restart Claude Code** to activate the connection. The MCP server is initialized at session start, so the key won't be active until you restart."

## Notes
- One mechanism, one variable: every scope sets `AYRSHARE_API_KEY`, which is exactly what the plugin's bundled server reads. No duplicate servers.
- To rotate the key, run `/ayrshare:setup` again and pick the same scope; it overwrites the variable in place.
- Do NOT verify by calling any MCP tool after setup. The connection loads at session start and will return 401/403 in the same session where the key was written. Restart first.
