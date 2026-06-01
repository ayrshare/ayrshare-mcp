---
name: messages
description: |
  Direct messages (DMs) for the Ayrshare MCP server — read conversations and messages, send a DM, and manage the account's DM auto-responder. Use whenever someone wants to work with private/direct messages on Facebook, Instagram, or Twitter/X: "read my Instagram DMs", "show our Facebook conversations", "what messages came in on X", "reply to that DM", "send a direct message to this person", "DM them this link/photo", "answer the latest message in this conversation". Also the skill for auto-reply settings: "set up an auto-reply for DMs", "turn on the DM auto-responder", "change the auto-reply message", "how long does it wait before auto-replying", "what's our auto-responder set to", "turn off auto-replies". Trigger when calling `mcp__ayrshare__get_messages`, `mcp__ayrshare__send_message`, `mcp__ayrshare__get_auto_response`, or `mcp__ayrshare__set_auto_response`, and even without the word "Ayrshare" — if the user wants to read or send social DMs, or configure a DM auto-reply, through an AI assistant, this is the skill. DMs exist ONLY on Facebook, Instagram, and Twitter/X. For the shared auth model and retry rules, see `../getting-started/SKILL.md`.
---

# Ayrshare MCP — Messages (DMs)

Four tools, split into two jobs — moving messages, and the account-level auto-responder:

- `mcp__ayrshare__get_messages` — read conversations and messages for one platform. Its conversation/message ids feed `send_message`.
- `mcp__ayrshare__send_message` — send a DM (text and/or media) to a recipient or into an existing conversation.
- `mcp__ayrshare__get_auto_response` — read the account's DM auto-reply settings.
- `mcp__ayrshare__set_auto_response` — change the account's DM auto-reply settings.

**DMs are ONLY on Facebook, Instagram, and Twitter/X.** No other network (LinkedIn, TikTok, YouTube, etc.) has a messaging surface here. `get_messages` and `send_message` are platform-scoped and accept exactly one of `facebook`, `instagram`, `twitter`. The two auto-response tools are **account-level** — they take no `platform` and govern the whole account's DM auto-reply.

All four are profile-scoped via the connection's `Profile-Key` header (see Auth) — none takes a `profileKey` argument.

## Functions

| Tool | Purpose | Method + Endpoint | Required inputs | Optional inputs |
|------|---------|-------------------|-----------------|-----------------|
| `mcp__ayrshare__get_messages` | Read conversations / messages for one platform | `GET /messages/:platform` | `platform` (`facebook`\|`instagram`\|`twitter`) | `conversationsOnly` (bool), `conversationId`, `status` (`active`\|`archived`), `limit` (1-100, **X/Twitter only**), `next` (cursor, **X only**) |
| `mcp__ayrshare__send_message` | Send a DM (text and/or media) | `POST /messages/:platform` | `platform` (`facebook`\|`instagram`\|`twitter`); **`message` OR `mediaUrls`**; **`recipientId` OR `conversationId`** | — (none beyond the above) |
| `mcp__ayrshare__get_auto_response` | Read the account's DM auto-reply settings | `GET /messages/autoresponse` | — (no params) | — |
| `mcp__ayrshare__set_auto_response` | Update the account's DM auto-reply settings | `POST /messages/autoresponse` | at least one of `autoResponseActive` (bool), `autoResponseMessage` (string), `autoResponseWaitSeconds` (int) | — (none beyond the above) |

Full input schemas and example payloads/responses are in [`references/schemas.md`](references/schemas.md).

## Auth

All four tools are **profile-scoped via the connection's `Profile-Key` header**, not a per-call argument. The header is set in the MCP client config (`.mcp.json` headers): include `Profile-Key: <profileKey>` to act as one client profile; omit it to act on the account's primary/Business profile. To switch profiles you reconfigure the connection header — you do **not** pass a `profileKey` parameter to any tool. Full two-layer model: `../getting-started/SKILL.md`.

This applies to the auto-response tools too: they are account-level (no `platform`), but still scoped to whichever profile the connection's `Profile-Key` selects. Different connections → different DM auto-reply settings.

## Usage guidance

- **Pick the platform first.** `get_messages` and `send_message` are `:/platform` calls; pass exactly one of `facebook`, `instagram`, `twitter`. There is no "all platforms" mode — to scan three networks, make three calls.
- **Read before you reply.** Call `get_messages` to pull conversations/messages, find the right conversation, then reply with `send_message`. Use `conversationsOnly: true` for a lightweight list of threads (no message bodies) when you just need to pick a conversation; drop it (or pass a `conversationId`) to read the messages within one thread.
- **`send_message` needs two things: content AND a target.**
  - **Content:** supply `message` (text), `mediaUrls` (an array of URLs), or both. At least one is required — an empty message with no media is rejected.
  - **Target:** supply `recipientId` (the person/page-scoped user id) **or** `conversationId` (an existing thread). At least one is required.
- **Facebook and Instagram REQUIRE `recipientId`.** On FB/IG you must address the message to a `recipientId`; a bare `conversationId` is not enough. On Twitter/X you can reply into a `conversationId` or send to a `recipientId`. When in doubt, include `recipientId` — it's the universally accepted target.
- **Where ids come from.** `recipientId` and `conversationId` come out of `get_messages`. Read first to obtain them; don't guess or hand-construct ids.
- **Messaging windows are real.** Each platform enforces a window in which you may DM a user — e.g. Facebook/Instagram generally allow a reply only within **24 hours** of the user's last message to you. Outside the window the API returns a clear error. **Don't retry it** — translate it via `mcp__ayrshare__explain_error` and tell the user the window has closed (the customer must message first to reopen it). See the global retry rule in `../getting-started/SKILL.md`.
- **`limit` and `next` are Twitter/X-only.** `limit` (1-100) caps results and `next` is the pagination cursor — both apply to X only on `get_messages`. Don't pass them for Facebook or Instagram.
- **Auto-responder is account-level and partial-update.** `get_auto_response` takes no params and returns `autoResponseActive`, `autoResponseMessage`, `autoResponseWaitSeconds`. `set_auto_response` accepts any subset of those three — send only the field(s) you're changing; omitted fields are left as-is. Sending `autoResponseMessage: ""` (empty string) **resets the message to the Ayrshare default**, it does not blank it out.

## Gotchas

- **DMs are only FB / IG / X.** `get_messages` and `send_message` reject any other platform. Don't try LinkedIn/TikTok/YouTube/etc. DMs through these tools — there is no messaging surface for them.
- **Scope comes from the connection, not a parameter.** Whose DMs you read/send, and whose auto-responder you read/set, is fixed by the connection's `Profile-Key` header. There is no `profileKey` argument on any of these four tools. Confirm you're on the right connection before reading or sending.
- **`send_message` needs content AND target.** Missing either side fails: you must give `message` OR `mediaUrls`, **and** `recipientId` OR `conversationId`. FB/IG additionally require `recipientId` specifically — a `conversationId` alone won't do.
- **`mediaUrls` is an array of URLs.** Media is referenced by reachable URL, same as posts — there is no upload step here. Validate a media URL with `mcp__ayrshare__validate_media` (see the Media skill) before sending if you're unsure it's reachable.
- **Auto-response empty string resets, not clears.** `autoResponseMessage: ""` reverts to the Ayrshare default reply; it does not produce an empty auto-reply. To stop auto-replying entirely, set `autoResponseActive: false`.
- **Auto-response is not platform-scoped.** `get_auto_response`/`set_auto_response` hit `/messages/autoresponse` with no `platform`; they govern the whole account's (profile's) DM auto-reply across FB/IG/X at once. Don't expect a per-platform toggle here.
- **On failure, call `mcp__ayrshare__explain_error`, then surface it — don't loop.** `send_message` is a write: never auto-retry it on a 4xx. A closed messaging window, a bad/expired `recipientId`, or an unsupported platform won't fix itself on retry, and a blind resend can double-send. Translate the error via `mcp__ayrshare__explain_error` and present it; 429 gets at most one retry. (Mirrors the global retry-safety rule.)
