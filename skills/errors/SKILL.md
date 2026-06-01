---
name: errors
description: |
  Error explanation for the Ayrshare MCP server — translate an Ayrshare error code into a plain-English cause, a classification, and a fix. Use whenever a code or numeric error needs decoding: "what does Ayrshare error 156 mean", "why did that post fail with code 272", "explain this error", "what's error code 110 on Instagram", "how do I fix this Ayrshare error". Trigger when calling `mcp__ayrshare__explain_error`, and even without the word "Ayrshare" — if the user surfaces a social-posting error code and wants to know what it means or how to fix it, this is the skill. CRITICAL: whenever ANY OTHER Ayrshare MCP tool returns a structured `Error <code>: ...`, look the code up here and explain/fix it rather than echoing the raw error back. For the shared auth model and the global retry-safety rule, see `../getting-started/SKILL.md`.
---

# Ayrshare MCP — Errors

One tool, the canonical way to decode any Ayrshare error code:

- `mcp__ayrshare__explain_error` — looks up an error `code` in the Ayrshare error catalog and returns a plain-English cause, a classification, and a short resolution hint.

It is the cross-cutting helper every other group skill points to: when a tool call fails with a structured `Error <code>: ...`, translate it here before surfacing anything to the user.

## Functions

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__explain_error` | Explain an Ayrshare error code from the canonical error catalog | `GET /error-explainer` | `code` (string of digits, or a number) | `platform` (a platform identifier) |

The response gives three things:

- **Cause** — a plain-English description of what went wrong.
- **Classification** — one of `developer-fix` (your code/config/input is wrong), `user-action` (the end user or their linked account must act, e.g. re-auth, permissions, content rules), or `network` (a transient/platform-side issue).
- **Resolution hint** — a short suggested fix.

## Auth

This tool is reached over the same authenticated connection as every other Ayrshare MCP tool. Profile context, where relevant, comes from the connection's `Profile-Key` header, not a per-call argument — there is **no** `profileKey` parameter, and `passthrough` cannot carry one (it is a blocked credential key). Full two-layer model: `../getting-started/SKILL.md`.

## Usage guidance

- **This is the first stop after ANY failed tool call.** When `create_post`, `add_comment`, `get_platform_history`, or any other Ayrshare MCP tool returns a structured `Error <code>: ...`, call `explain_error` with that `code` (pass the failing `platform` if you have it) and surface the explanation. Do **not** echo the raw error or guess at the meaning.
- **Pass `platform` when you have it.** The same numeric code can mean different things per network; supplying the `platform` identifier (e.g. the platform that the failed call targeted) sharpens the cause and fix.
- **`code` accepts a string of digits or a number.** Pass the bare code from the error (e.g. `156`, `"272"`). Strip any surrounding text.
- **Act on the classification:**
  - `developer-fix` → the input/config/code is wrong; fix it before retrying (do not blindly re-call the failing tool).
  - `user-action` → the end user or their linked social account must do something (re-authenticate, grant a permission, change content); relay the resolution hint to them.
  - `network` → transient/platform-side; a single retry after a short delay is reasonable (matching the global 429/transient rule), but don't loop.
- **It does not fix the underlying call.** `explain_error` only decodes the code. After understanding it, address the root cause and re-run the original tool deliberately — don't auto-retry the failed write.

## Gotchas

- **Don't echo raw error codes at the user.** A bare `Error 272` is unhelpful. Always run it through `explain_error` and present the cause + fix.
- **The classification drives whether a retry is even sensible.** A `developer-fix` or `user-action` error will not resolve on retry — only `network`-class errors warrant the single transient retry. Never auto-retry a failed write on a 4xx just because you decoded it.
- **Provide `platform` for accuracy.** Omitting it still works but may give a more generic explanation when the code is platform-specific.
- **Scope (where it applies) comes from the connection, not a parameter.** There is no `profileKey` argument on this or any Ayrshare MCP tool.
- **`explain_error` is itself a read.** If the lookup call fails (rare), surface it plainly; don't loop. (Mirrors the global retry-safety rule in `../getting-started/SKILL.md`.)
