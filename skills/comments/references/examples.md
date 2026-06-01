# Example payloads — Ayrshare MCP comments

Inputs passed to the MCP tools. `id` is the post id returned by `mcp__ayrshare__create_post`. `commentId` is a comment id returned by `mcp__ayrshare__get_comments`.

## Read the comments on a post

```json
{ "id": "POST_ID_RETURNED_BY_CREATE_POST" }
```

For a specific client profile, add `profileKey`. The response includes each comment's id (use it as `commentId` for replies/deletes) and text.

## Add a NEW top-level comment to a post

```json
{
  "id": "POST_ID_RETURNED_BY_CREATE_POST",
  "comment": "Thanks everyone for the great feedback on this launch!",
  "platforms": ["twitter", "facebook"]
}
```

This is `mcp__ayrshare__post_comment`. Use when you want a comment ON THE POST. `platforms` is optional and only relevant when the post spans multiple networks and you want to scope the comment.

## Reply to an EXISTING comment

```json
{
  "commentId": "COMMENT_ID_FROM_GET_COMMENTS",
  "comment": "Great question — yes, dark mode is available on all plans."
}
```

This is `mcp__ayrshare__reply_comment`. Use when responding to a specific person/comment. Get the `commentId` from `mcp__ayrshare__get_comments` first — don't guess it.

## Reply on behalf of a client profile

```json
{
  "commentId": "COMMENT_ID_FROM_GET_COMMENTS",
  "comment": "Appreciate you reaching out! DMing you now.",
  "profileKey": "PROFILE_KEY_FROM_CREATE_PROFILE"
}
```

`profileKey` here overrides any `AYRSHARE_PROFILE_KEY` env default.

## Delete a comment

```json
{ "commentId": "COMMENT_ID_FROM_GET_COMMENTS" }
```

Add `profileKey` to delete a comment under a specific client profile. Not every platform supports comment deletion; a 4xx here may mean the platform doesn't allow it or the comment is already gone — call `mcp__ayrshare__explain_error` and surface the explanation, don't retry.
