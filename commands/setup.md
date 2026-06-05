---
description: Configure or rotate your Ayrshare API key (and optional Profile-Key / X BYOK) after installing the plugin
---

Configure your Ayrshare credentials for Claude Code. Run this after installing the plugin.

The plugin's bundled MCP server reads its credentials from environment variables (its `.mcp.json` sends `Authorization: Bearer ${AYRSHARE_API_KEY}` plus optional `${AYRSHARE_PROFILE_KEY:-}` and `${X_TWITTER_OAUTH1_API_KEY:-}` / `${X_TWITTER_OAUTH1_API_SECRET:-}` headers). This command puts those variables where the plugin's own server reads them. Do not create a separate MCP server with `claude mcp add`; that produces a second server the plugin does not use and is the classic cause of a `403 / code 102` after setup.

Only `AYRSHARE_API_KEY` is required. Profile-Key and X BYOK are optional.

## Steps

1. **Ask how the user wants to provide secrets.** Do this first, before asking for any key:

   "Two ways to set this up:
   - **Paste here:** quickest. You paste your key(s) and I write them to a `settings.json` for you. Heads-up: anything you paste enters this chat's context and is sent to the model provider.
   - **I'll add them myself:** for when you would rather not put a secret in chat (e.g. org policy). I show you the exact file (or env var) and a fill-in-the-blanks snippet, and you add the real values yourself. I write and see nothing."

   If the user already passed a key as an argument, treat that as "paste here."

2. **If "I'll add them myself":** ask where they want the credentials, give the matching fill-in instructions, write nothing, and skip to step 5.
   - **Global** (all projects and sessions) is `~/.claude/settings.json` (their home directory; `%USERPROFILE%\.claude\settings.json` on Windows). **This project** is `./.claude/settings.local.json` (kept out of git; have them gitignore it, since a `*.local` pattern does not match `settings.local.json`). For either, give them this `env` block to merge in, preserving any keys already present:
     ```json
     {
       "env": {
         "AYRSHARE_PROFILE_KEY": "<optional: a default client profile; delete this line for your primary profile>",
         "X_TWITTER_OAUTH1_API_KEY": "<optional: your X app Consumer Key; delete if you don't post to X>",
         "X_TWITTER_OAUTH1_API_SECRET": "<optional: your X app Consumer Secret; delete if you don't post to X>",
         "AYRSHARE_API_KEY": "<required: your key from app.ayrshare.com, Settings then API Key>"
       }
     }
     ```
     The required `AYRSHARE_API_KEY` is intentionally **last** so that deleting any optional line above it leaves valid JSON (no dangling trailing comma). If the user keeps an optional line, every entry except the last needs its trailing comma.
   - **OS environment variables** (CI / advanced): set the same variable names before launching Claude Code (macOS/Linux: `export VAR=...` in a shell profile or a CI secret; Windows: `setx VAR "..."` then relaunch, or System Environment Variables).

   Tell them: only `AYRSHARE_API_KEY` is required; delete the optional lines they don't need; the X pair is both or neither; save, then restart. The `settings.json` route is the more portable one (Claude Code reads it identically on every OS and however it is launched, not only from the shell that set it).

3. **If "paste here": write the API key.** First ask the scope:
   - **Global (default):** `~/.claude/settings.json` (home directory; `%USERPROFILE%\.claude\settings.json` on Windows).
   - **This project:** `./.claude/settings.local.json`, kept out of git. Have them add `.claude/settings.local.json` to `.gitignore` and confirm `git status` does not list it (a `*.local` pattern does not match `settings.local.json`, which ends in `.json`). Use the committed `./.claude/settings.json` only to deliberately share one key with a team.

   Then ask them to paste the key (from https://app.ayrshare.com, Settings then API Key). Read the chosen file if it exists, parse it as JSON, set `env.AYRSHARE_API_KEY`, and write it back preserving every other field (create the file and its directory if missing). Result: `{ "env": { "AYRSHARE_API_KEY": "THE_KEY" } }`, with other keys intact.

4. **If "paste here": offer the two optional credentials.** Present each as a **neutral** choice driven by the user's use case. Do **not** mark either option as "(Recommended)" or "(default)": the right answer depends entirely on how the user works, and labeling one as recommended misleads the others. For each, the user may paste the value, or (to keep it out of chat) add the variable to the same settings file themselves, exactly like step 2.

   a. **Default client profile (optional).** Ask whether they want the connection to default to one client profile. If **not** (or unsure), they provide nothing and calls act on the account's **primary** profile (this is just the no-Profile-Key behavior, not a recommendation), and they can still target any client per call via the `profileKey` tool argument. If they **do** want a fixed default client, set `env.AYRSHARE_PROFILE_KEY` from a pasted Profile Key. The per-call argument always supersedes the connection default, so a pinned key never locks the user out of other profiles (remove the variable and restart to return to primary).

   b. **X/Twitter (BYOK), required for any X/Twitter call.** This is **not** a skip-by-default choice: anyone who will make **any** X/Twitter call must provide their own X Developer App OAuth 1.0a key pair, or every X call fails with `419`. Ask plainly: "Do you post to X/Twitter?" (Frame it on X usage, and do not present skipping as recommended.) If **yes**, set BOTH `env.X_TWITTER_OAUTH1_API_KEY` and `env.X_TWITTER_OAUTH1_API_SECRET` from the pasted X **API Key** (Consumer Key) and X **API Secret** (Consumer Secret). If **no** (they don't use X), skip. Both or neither: with only one set an X call fails with `400`, with neither it fails with `419` (non-X networks are unaffected). This pair is **account-level** and rides on **every** X-targeting request alongside the API key, independent of any Profile-Key (a set Profile-Key just targets that profile's linked X account).

5. **Offer to clean up a stale duplicate server.** Older versions of this command created a separate `ayrshare` MCP server (via `claude mcp add`) with the key in a header. That extra server shadows or collides with the plugin and should be removed. Run `claude mcp list` and identify it carefully:
   - The **plugin's own** server is the one to keep. The plugin provides it from the bundled `.mcp.json`, and Claude Code lists it namespaced as `plugin:ayrshare:ayrshare` (URL `https://api.ayrshare.com/mcp`). **Never remove this one.**
   - A **stale duplicate** is a *separately added* server listed as plain `ayrshare` (no `plugin:` prefix) at `https://api.ayrshare.com/mcp`, i.e. an `ayrshare` entry that exists *in addition to* the plugin's, often flagged as "defined in multiple scopes" by `claude mcp list`. Only this one should be offered for removal, with `claude mcp remove ayrshare` (add `--scope user` or `--scope local` to match where it lives).
   - **Never remove an `ayrshare` server whose URL is the docs endpoint** (`https://www.ayrshare.com/docs/mcp`). That is the separate Ayrshare documentation MCP, not a duplicate; leave it untouched.
   - If the only `ayrshare`-related server is the plugin's own (`plugin:ayrshare:ayrshare`), there is nothing to clean up; do not prompt for removal.

6. **Tell the user to restart, and how to use it afterward.**
   - "Setup complete. **Restart Claude Code** to activate the connection. The MCP server is initialized at session start, so your credentials won't be active until you restart."
   - Then set expectations on invocation: after restart, the tools are used by **asking in plain English** (e.g. "show my recent Instagram posts", "post this to LinkedIn"), not by typing a slash command. `/ayrshare:setup` is the **only** slash command; the other tools fire on intent (the trigger-skills route them), so `/ayrshare:get_post_history` and similar will read as "unknown command."

## Notes
- One mechanism: every path sets the same env vars (`AYRSHARE_API_KEY` required; `AYRSHARE_PROFILE_KEY`, `X_TWITTER_OAUTH1_API_KEY`, `X_TWITTER_OAUTH1_API_SECRET` optional), which is exactly what the plugin's bundled `.mcp.json` reads. No duplicate servers.
- The optional vars use `${VAR:-}` in the bundled config, so leaving one unset sends an empty header that the server treats as not provided (no effect, no error). Set it to turn the feature on.
- To rotate any credential, run `/ayrshare:setup` again and pick the same destination (it overwrites in place), or edit the settings file directly. Restart after any change.
- Do NOT verify by calling any MCP tool after setup. The connection loads at session start and will return 401/403 in the same session where the key was written. Restart first.
