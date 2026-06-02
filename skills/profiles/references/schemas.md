# Profiles — Input Schemas & Examples

These tools run against the Ayrshare MCP server at `https://api.ayrshare.com/mcp` and authenticate with the Business API key (the `Authorization: Bearer ${AYRSHARE_API_KEY}` header). `create_profile` and `list_profiles` are account-level and take **no `profileKey` argument** — to act as a specific profile you set the `Profile-Key` connection header in the MCP client config, not a per-call parameter. `generate_jwt` is the exception: it takes a `profileKey` **argument** (the sub-profile to mint a linking URL for) and reads its signing credentials from the `X-Ayrshare-Private-Key` / `X-Ayrshare-Domain` connection headers (see its section below). No `profileKey` is ever used as the auth key. Endpoints below are the underlying Ayrshare REST routes each tool maps to.

## `mcp__ayrshare__create_profile`

`POST /profiles`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Display name for the profile (e.g. the client or company name). Must be unique. |
| `messagingActive` | boolean | no | Enable messaging (DMs) for this profile. Messaging must first be enabled for the account. |
| `hideTopHeader` | boolean | no | Hide the top header on the white-label linking page. |
| `hideLogo` | boolean | no | Hide the logo on the white-label linking page. |
| `topHeader` | string | no | Custom top-header text on the linking page. |
| `subHeader` | string | no | Custom sub-header text on the linking page. |
| `disableSocial` | array of strings | no | Social networks to disable for this profile. Values: bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube. |
| `team` | boolean | no | Create a team profile. **If `true`, `email` is required.** |
| `email` | string | no | Team member email. Required when `team` is `true`. |
| `tags` | array of strings | no | Tags to attach to the profile. |

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

The response contains the new profile's sensitive `profileKey` (and `refId`). **Capture the `profileKey`** — it is shown once and the API cannot return it again (a lost key is recoverable only from the Ayrshare dashboard), and it is what you place in the `Profile-Key` connection header to operate as this profile downstream (posting, analytics, history). Treat it like a credential.

## `mcp__ayrshare__list_profiles`

`GET /profiles`

Lists the User Profiles under the caller's Primary Profile (which is not itself included). All inputs are optional filters/pagination.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | no | Return only the profile with this (URL-encoded) title. |
| `refId` | string | no | Return only the profile with this refId. |
| `hasActiveSocialAccounts` | boolean | no | `true` = only profiles with at least one connected social account; `false` = only profiles with none. |
| `includesActiveSocialAccounts` | array of strings | no | Filter to profiles whose active social accounts contain ALL of the listed platforms. |
| `isByokLinked` | boolean | no | Filter by BYOK migration status. `true` = completed; `false` = eligible but not migrated. Omit for all. (Currently applies to X/Twitter BYOK.) |
| `actionLog` | boolean \| number | no | Return the create/delete action log and active-user billing count. `true` = 60 days (default), or a number of days (1-365). |
| `limit` | number | no | Max profiles to return. Default and maximum is 5000. |
| `cursor` | string | no | Pagination cursor. When `hasMore` is true, pass the returned `nextCursor` here for the next page. |
| `include` | string \| array | no | Return extended profile data (requires `refId`). Values: `suspension`, `socialHealth`, `linkingErrors`, `activity`, `quota`, `unlinkHistory`, `actionLog`. |

Returns the profiles under the Business account — each with its `title`, `refId`, and the social platforms currently linked to it. For security the `GET /profiles` call does **not** return `profileKey`, so `list_profiles` cannot recover a lost key — retrieve that from the Ayrshare dashboard. Use `list_profiles` to find a profile or its `refId`, not to work around a misplaced key.

Examples:

```jsonc
// All profiles (default)
{}
```

```jsonc
// Only profiles that already have a linked TikTok and Instagram
{ "includesActiveSocialAccounts": ["tiktok", "instagram"] }
```

```jsonc
// One profile by refId, with extended quota + activity data
{ "refId": "ABCD1234", "include": ["quota", "activity"] }
```

## `mcp__ayrshare__generate_jwt`

`POST /profiles/generateJWT`

Mints a single sign-on **social-account linking URL** for one User Profile, so a client can connect their own social networks. This is the onboarding step after `create_profile`: hand the returned `url` to the client, who opens it in a browser to OAuth their accounts. The URL is valid for 5 minutes by default (or `expiresIn` on the Max Pack).

**Credentials (connection headers, not arguments).** Unlike every other profiles tool, `generate_jwt` needs the account's JWT signing credentials, supplied as connection headers and env-substituted in `.mcp.json`:

| Header | Value |
|--------|-------|
| `X-Ayrshare-Private-Key` | Your `private.key`, **base64-encoded** (`cat private.key \| base64`). A header cannot carry raw PEM newlines, so it is transported base64-encoded and decoded server-side. |
| `X-Ayrshare-Domain` | Your exact onboarding domain. |

The tool injects these into the request server-side and never logs them. The private key is a high-value secret (it can mint linking URLs for every profile) — keep it out of version control and source it from a secret store / env var, not a literal in a committed file.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profileKey` | string | yes | The User Profile Key of the **sub-profile** to mint the linking URL for (from `create_profile`). The account API key is NOT valid here. Drives both profile resolution and the signed token; the connection's `Profile-Key` header is ignored. |
| `logout` | boolean | no | Auto-log-out the current profile session when the URL is opened. Not recommended in production. |
| `redirect` | string (URL) | no | Where to send the user after they click "Done" / the logo. Automatically shortened in the returned URL. |
| `allowedSocial` | array of strings | no | Restrict which networks appear on the linking page (overrides the account's Social Networks config). Values: bluesky, facebook, gmb, instagram, linkedin, pinterest, reddit, snapchat, telegram, threads, tiktok, twitter, youtube. |
| `verify` | boolean | no | Verify the generated token is valid before returning. Non-production only. |
| `expiresIn` | number | no | Token longevity in **minutes** (1-2880; default 5). **Requires the Max Pack.** |
| `email` | object | no | Send a Connect Accounts email with the link directly to the user. **Requires the Max Pack.** Fields: `to` (required), `bcc`, `termsUrl`, `privacyUrl`, `company`, `contactEmail`. |

Note: `privateKey`/`domain` are taken from the connection headers above (not request fields), and the MCP sets `base64: true` automatically since the key is base64-encoded in transit.

Example call (minimal — just the target profile):

```json
{ "profileKey": "PROFILE_KEY" }
```

Example call (restricted networks, 1-hour link, custom redirect):

```json
{
  "profileKey": "PROFILE_KEY",
  "allowedSocial": ["facebook", "instagram", "linkedin", "tiktok"],
  "expiresIn": 60,
  "redirect": "https://acme.example/onboarding/done"
}
```

The response contains the hosted linking `url` (and the signed `token`). Hand the `url` to the client; the OAuth completes in their browser. The private key is never echoed back.
