---
description: Configure or rotate the Ayrshare API key after the plugin is installed
---

Configure the Ayrshare API key for Claude Code. Run this after installing the plugin.

## Steps

1. If the user did not include their API key as an argument, ask:
   "Please paste your Ayrshare API key. You can get one at https://app.ayrshare.com under Settings → API Key."

2. Ask where to store the key — this should match the scope used when installing the plugin:

   "Where do you want to store the API key?
   - **This project** — writes the key to `.mcp.json` in the current project directory (use if you installed the plugin with `--scope local` or `--scope project`)
   - **Global** — stores the key in `~/.claude/` for all projects (use if you installed the plugin globally — the default)"

3. Based on the answer:

   **This project:**
   - Create or update `.mcp.json` in the current working directory. If the file already exists, update only the `Authorization` header under the `ayrshare` server and preserve all other entries.
     ```json
     {
       "mcpServers": {
         "ayrshare": {
           "type": "http",
           "url": "https://api.ayrshare.com/mcp",
           "headers": {
             "Authorization": "Bearer KEY"
           }
         }
       }
     }
     ```
   - Remind the user to add `.mcp.json` to `.gitignore` if they do not want the key committed to git.

   **Global:**
   - Run `claude mcp remove ayrshare --scope user` (ignore errors if none exists)
   - Run `claude mcp add ayrshare --transport http https://api.ayrshare.com/mcp --header "Authorization: Bearer KEY" --scope user`

4. After writing the key, inform the user:
   - "Setup complete. **Restart Claude Code** to activate the connection — the MCP server is initialized at session start, so the key won't be active until you restart."
   - If project scope was chosen, remind them to add `.mcp.json` to `.gitignore` to avoid committing the key.

## Notes
- To rotate the key at any time, run /ayrshare:setup again.
- The key scope should match the plugin installation scope so commands and MCP access are consistent.
- Do NOT attempt to verify by calling any MCP tool after setup — the connection is loaded at session start and will always return 403 in the same session where the key was written.
