# Messages (DMs) — Input Schemas & Examples

The MCP server reaches the Ayrshare API through four messaging tools:

- `mcp__ayrshare__get_messages` (`GET /messages/:platform`) — read conversations / messages for one platform.
- `mcp__ayrshare__send_message` (`POST /messages/:platform`) — send a DM (text and/or media).
- `mcp__ayrshare__get_auto_response` (`GET /messages/autoresponse`) — read the account's DM auto-reply settings.
- `mcp__ayrshare__set_auto_response` (`POST /messages/autoresponse`) — update those settings.

**DMs are ONLY on Facebook, Instagram, and Twitter/X.** `get_messages` and `send_message` are platform-scoped (one of `facebook`, `instagram`, `twitter`). The two auto-response tools are **account-level** — no `platform`.

All four are **profile-scoped**: choose the profile with an optional `profileKey` tool argument or the `Profile-Key` connection header (the argument wins when both are set). With neither, calls act on the account's primary/Business profile.

`MESSAGE_PLATFORMS` enum (the only three with a DM surface):
`facebook, instagram, twitter`

## `mcp__ayrshare__get_messages`

`GET /messages/:platform`

Reads conversations and/or messages for a single platform. Returns conversations and messages whose ids (`conversationId`, `recipientId`) feed `send_message`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string (enum) | **yes** | The platform to read. One of `facebook`, `instagram`, `twitter`. |
| `conversationsOnly` | boolean | no | Return only the list of conversations (threads), without the messages inside them. Ignores `conversationId` when set. |
| `conversationId` | string | no | Restrict to one conversation/thread. Ignored when `conversationsOnly` is true. |
| `status` | string | no | Filter by conversation status: `active` (default) or `archived`. |
| `limit` | integer | no | Max results, 1-100. **Twitter/X only.** |
| `next` | string | no | Pagination cursor from a prior call. **Twitter/X only.** |

Examples:

```jsonc
// All recent Instagram conversations + messages (profile chosen by the connection's Profile-Key header)
{ "platform": "instagram" }
```

```jsonc
// Lightweight list of Facebook conversations only (no message bodies)
{ "platform": "facebook", "conversationsOnly": true }
```

```jsonc
// Read the messages inside one Instagram conversation
{ "platform": "instagram", "conversationId": "aWdfZGFf...thread" }
```

```jsonc
// Paginate Twitter/X messages (limit + next are X-only)
{ "platform": "twitter", "limit": 50, "next": "CURSOR_FROM_PRIOR_CALL" }
```

The returned `conversationId` and `recipientId` are exactly what `send_message` needs — read first, then reply.

## `mcp__ayrshare__send_message`

`POST /messages/:platform`

Sends a DM. You must supply **content** (`message` OR `mediaUrls`) **and** a **target** (`recipientId` OR `conversationId`). Facebook and Instagram additionally **require** `recipientId`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string (enum) | **yes** | The platform to send on. One of `facebook`, `instagram`, `twitter`. |
| `message` | string | conditional | Text body. Provide `message` OR `mediaUrls` (or both); at least one is required. Required on X/Twitter even when `mediaUrls` is provided. |
| `mediaUrls` | string[] (URLs) | conditional | Array of reachable media URLs (FB/IG accept multiple; X accepts one). Provide `mediaUrls` OR `message` (or both); at least one is required. |
| `recipientId` | string | conditional | Target user/page-scoped id. Provide `recipientId` OR `conversationId`; at least one is required. **Required on Facebook and Instagram.** |
| `conversationId` | string | conditional | Existing thread to send into. Provide `conversationId` OR `recipientId`; at least one is required. (On FB/IG you still need `recipientId`.) |

Constraints, in plain terms:

- **Content:** at least one of `message`, `mediaUrls`.
- **Target:** at least one of `recipientId`, `conversationId`.
- **Facebook / Instagram:** `recipientId` is mandatory (a bare `conversationId` is not enough).
- **Messaging window:** each platform allows DMs only within its window (FB/IG follow Meta's standard messaging-window policy, tied to the user's last inbound message). Outside the window the API returns a clear error — surface it via `mcp__ayrshare__explain_error`, don't retry.

Examples:

```jsonc
// Instagram text reply — FB/IG require recipientId
{ "platform": "instagram", "recipientId": "17841400000000000", "message": "Thanks for reaching out! How can we help?" }
```

```jsonc
// Facebook reply with an image (recipientId required on FB)
{
  "platform": "facebook",
  "recipientId": "9876543210",
  "message": "Here's the guide you asked about:",
  "mediaUrls": ["https://img.ayrshare.com/dm/guide.jpg"]
}
```

```jsonc
// Twitter/X reply into an existing conversation (X accepts conversationId)
{ "platform": "twitter", "conversationId": "1234567890-9876543210", "message": "Sent you the details!" }
```

```jsonc
// Media-only DM (no text) — content requirement satisfied by mediaUrls (FB/IG; X requires message text)
{ "platform": "facebook", "recipientId": "9876543210", "mediaUrls": ["https://img.ayrshare.com/dm/promo.png"] }
```

## `mcp__ayrshare__get_auto_response`

`GET /messages/autoresponse`

**No functional parameters** (an optional `profileKey` argument, or the `Profile-Key` header, selects the profile). Account-level (not platform-scoped). Returns that profile's DM auto-reply settings.

Request:

```json
{}
```

Returns (shape):

| Field | Type | Description |
|-------|------|-------------|
| `autoResponseActive` | boolean | Whether DM auto-reply is on. |
| `autoResponseMessage` | string | The auto-reply text currently in use. |
| `autoResponseWaitSeconds` | integer | Delay before the auto-reply is sent. |

## `mcp__ayrshare__set_auto_response`

`POST /messages/autoresponse`

Updates the profile's DM auto-reply settings. **At least one** of the three setting fields is required. Account-level (no `platform`).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `autoResponseActive` | boolean | conditional | Turn auto-reply on/off (default `false`). At least one of these three fields is required. |
| `autoResponseMessage` | string | conditional | The auto-reply text. **Empty string `""` resets to the Ayrshare default** (it does not blank the reply). At least one of these three fields is required. |
| `autoResponseWaitSeconds` | integer | conditional | Delay (seconds) before the auto-reply sends again to the same correspondent (default `86400`, i.e. 24 h). At least one of these three fields is required. |

Examples:

```jsonc
// Turn on auto-reply with a custom message and a 30s delay
{ "autoResponseActive": true, "autoResponseMessage": "Thanks for your message! We'll reply within a few hours.", "autoResponseWaitSeconds": 30 }
```

```jsonc
// Just turn it off
{ "autoResponseActive": false }
```

```jsonc
// Reset the message to the Ayrshare default (empty string = reset)
{ "autoResponseMessage": "" }
```

```jsonc
// Change only the wait time
{ "autoResponseWaitSeconds": 60 }
```

For the shared auth model and the global retry-safety rule (never auto-retry the `send_message` write on a 4xx; translate via `mcp__ayrshare__explain_error`; 429 gets one retry), see `../../getting-started/SKILL.md`.
