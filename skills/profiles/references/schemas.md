# Profiles — Input Schemas & Examples

Both tools run against the Ayrshare MCP server at `https://api.ayrshare.com/mcp` and authenticate with the Business API key (the `Authorization: Bearer ${AYRSHARE_API_KEY}` header). No `profileKey` is used as the auth key, and **neither tool takes a `profileKey` argument** — to act as a specific profile you set the `Profile-Key` connection header in the MCP client config, not a per-call parameter. Endpoints below are the underlying Ayrshare REST routes each tool maps to.

## `mcp__ayrshare__create_profile`

`POST /profiles`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Display name for the profile (e.g. the client or company name) |
| `messagingActive` | boolean | no | Enable messaging (DMs) for this profile |
| `hideTopHeader` | boolean | no | Hide the top header on the white-label linking page |
| `hideLogo` | boolean | no | Hide the logo on the white-label linking page |
| `topHeader` | string | no | Custom top-header text on the linking page |
| `subHeader` | string | no | Custom sub-header text on the linking page |
| `disableSocial` | array of strings | no | Social networks to disable for this profile |
| `team` | boolean | no | Create a team profile. **If `true`, `email` is required.** |
| `email` | string | no | Team member email. Required when `team` is `true`. |
| `tags` | array of strings | no | Tags to attach to the profile |
| `passthrough` | object | no | Advanced/undocumented API params, flattened onto the request top level. Credential/identity keys (`profileKey`, `apiKey`, `uid`, etc.) are dropped — `passthrough` **cannot** carry a `profileKey`. |

Example call (minimal):

```json
{ "title": "Acme Corp" }
```

Example call (team profile with white-label chrome):

```json
{
  "title": "Acme Corp",
  "team": true,
  "email": "social@acme.com",
  "messagingActive": true,
  "topHeader": "Acme Social",
  "disableSocial": ["telegram", "reddit"],
  "tags": ["agency-client", "enterprise"]
}
```

The response contains the new profile's sensitive `profileKey` (and `refId`). **Capture the `profileKey`** — it is shown once and is what you place in the `Profile-Key` connection header to operate as this profile downstream (posting, analytics, history). Treat it like a credential.

## `mcp__ayrshare__list_profiles`

`GET /profiles`

No inputs. Returns all profiles under the Business account — each with its `title`, `refId`, and the social platforms currently linked to it. This is the recovery path when a `profileKey` has been lost; do not create a duplicate profile to recover a key.
