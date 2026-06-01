# Profiles — Input Schemas & Examples

All four tools run against the Ayrshare MCP server at `https://api.ayrshare.com/mcp` and authenticate with the Business API key (the `Authorization: Bearer ${AYRSHARE_API_KEY}` header). No `profileKey` is used as the auth key. Endpoints below are the underlying Ayrshare REST routes each tool maps to.

## `mcp__ayrshare__create_profile`

`POST /profiles/profile`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Display name for the profile (e.g. the client or company name) |

Example call:

```json
{ "title": "Acme Corp" }
```

The response contains the new profile's `profileKey` (and `refId`). **Capture the `profileKey`** — every profile-scoped operation downstream needs it (via `AYRSHARE_PROFILE_KEY` or a per-call `profileKey`), and `generate_jwt`/`delete_profile` need it as their body param.

## `mcp__ayrshare__generate_jwt`

`POST /profiles/generateJWT`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profileKey` | string | yes | The `profileKey` returned by `mcp__ayrshare__create_profile`. **Data, not auth** — identifies which profile to link. |
| `domain` | string | yes | Redirect URL after OAuth completes (e.g. `https://yourapp.com/callback`). The integration must handle this redirect to detect when linking is done. |

Example call:

```json
{
  "profileKey": "PROFILE_KEY_FROM_STEP_1",
  "domain": "https://yourapp.com/callback"
}
```

Returns a URL. The user opens it in a browser, OAuths their social networks, and is redirected to `domain`. This linking step happens outside the tools.

## `mcp__ayrshare__list_profiles`

`GET /profiles`

No inputs. Returns all profiles under the Business account, each with its `title` and `profileKey`. This is the recovery path when a `profileKey` has been lost.

## `mcp__ayrshare__delete_profile`

`DELETE /profiles/profile`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profileKey` | string | yes | The `profileKey` of the profile to delete. **Data, not auth.** |

Example call:

```json
{ "profileKey": "PROFILE_KEY_TO_DELETE" }
```

**Destructive and irreversible** — permanently deletes the profile and unlinks its social accounts. Confirm with the user before calling, and never auto-retry on a 4xx (call `mcp__ayrshare__explain_error` instead).
