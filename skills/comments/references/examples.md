# Example payloads — Ayrshare MCP comments

Inputs passed to the MCP tools. `id` is the post id returned by `mcp__ayrshare__create_post`. `commentId` is a comment id returned by `mcp__ayrshare__get_comments`. Profile scoping is the optional `profileKey` argument or the connection's `Profile-Key` header (the argument wins when both are set); see `../../getting-started/SKILL.md`.

## Read the comments on a post

```json
{ "id": "POST_ID_RETURNED_BY_CREATE_POST" }
```

The response includes each comment's id (use it as `commentId` for replies) and text.

To read by a native Social Post/Comment ID instead of an Ayrshare id, set `searchPlatformId` and supply the single platform:

```json
{
  "id": "NATIVE_SOCIAL_POST_ID",
  "searchPlatformId": true,
  "platform": "linkedin"
}
```

Add `commentId: true` alongside `searchPlatformId` when the `id` is a native Social Comment ID rather than a post id.

## Add a NEW top-level comment to a post

```json
{
  "id": "POST_ID_RETURNED_BY_CREATE_POST",
  "comment": "Thanks everyone for the great feedback on this launch!",
  "platforms": ["twitter", "facebook"]
}
```

This is `mcp__ayrshare__add_comment`. Use when you want a comment ON THE POST. `platforms` is optional (a subset of `add_comment`'s networks: bluesky, facebook, instagram, linkedin, reddit, tiktok, twitter, youtube) and only relevant when the post spans multiple networks and you want to scope the comment. To attach media, add `mediaUrls` with exactly one URL — supported only on Facebook, LinkedIn, and X (twitter).

## Reply to an EXISTING comment

```json
{
  "commentId": "COMMENT_ID_FROM_GET_COMMENTS",
  "comment": "Great question — yes, dark mode is available on all plans.",
  "platforms": ["linkedin"]
}
```

This is `mcp__ayrshare__reply_comment` (POST `/comments/reply`). Use when responding to a specific person/comment. Get the `commentId` from `mcp__ayrshare__get_comments` first — don't guess it.

## Reply to a TikTok comment by its native Social Comment ID

```json
{
  "commentId": "NATIVE_SOCIAL_COMMENT_ID",
  "comment": "Appreciate you reaching out!",
  "platforms": ["tiktok"],
  "searchPlatformId": true,
  "videoId": "TIKTOK_VIDEO_ID"
}
```

With `searchPlatformId`, `commentId` is a native Social Comment ID and exactly one platform must be supplied. TikTok Social-Comment-ID replies additionally require `videoId`.

## Acting as a specific client profile

To reply on behalf of a client profile, pass its `profileKey` as a tool argument (it wins over the `Profile-Key` connection header), or set that header; see `../../getting-started/SKILL.md`.
