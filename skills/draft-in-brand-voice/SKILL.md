---
name: draft-in-brand-voice
description: |
  Draft social posts that match a brand's established voice for the Ayrshare MCP server: first pull the profile's own past posts (history) to read tone, format, and what performed, then write platform-appropriate copy in that voice and validate it before anything publishes. Use whenever someone wants on-brand content rather than generic copy: "write a post the way we usually post", "draft this in our brand voice", "match our tone", "write like our LinkedIn", or any time content is created for a profile whose established style should be matched. Trigger even without the word "Ayrshare": if the user wants content that sounds like an existing account, this is the skill. It pulls history (`get_post_history` / `get_platform_history`), optionally `get_post_analytics` for what worked, drafts via `generate_post` or your own copy, then checks with `validate_post`. It produces DRAFTS only and never publishes; publishing is the explicit `create_post` step in `../post/SKILL.md`.
---

# Ayrshare MCP — Draft in Brand Voice

A workflow skill, not a single tool. It turns "write me a post" into "write me a post that sounds like **this** brand" by grounding the draft in the profile's actual posting history before a word is written. The wedge: an agent that learns voice from real past posts beats one that guesses a tone from the topic alone.

This skill **drafts only**. It never publishes. The output is copy for the user to review; publishing is the separate, explicit `validate_post` → confirm → `create_post` step documented in `../post/SKILL.md`.

## The tools it orchestrates

- `mcp__ayrshare__get_platform_history` — native posts on a platform, **including ones not made through Ayrshare**. This is the broadest, most honest sample of how the brand actually writes. Start here for voice. (See `../history/SKILL.md`.)
- `mcp__ayrshare__get_post_history` — posts sent **via Ayrshare** (with status/notes). Useful for recent voice plus any internal notes already attached.
- `mcp__ayrshare__get_post_analytics` / `mcp__ayrshare__get_post_analytics_by_social_id` — optional, but this is the "optimize on history" half: pull metrics on past posts to see which voice/format actually performed, and bias the draft toward that. (See `../analytics/SKILL.md`.)
- `mcp__ayrshare__generate_post` — optional AI drafting from a topic/brief. Brief it with the voice you observed; it returns draft text only and never publishes. (See `../generate/SKILL.md`.)
- `mcp__ayrshare__validate_post` — dry-run the finished draft against each target platform's rules before you hand it back as "ready to post."

These are profile-scoped: choose the profile with the optional `profileKey` argument on each call or the connection's `Profile-Key` header (the argument wins when both are set). (`generate_post` is the exception: it takes no `profileKey` argument; see `../generate/SKILL.md`.) The voice you match is the voice of whichever profile you target, so settle that first and use it consistently across the calls.

## Workflow

1. **Pick the profile and platform(s).** Voice is per profile (and often per platform, the same brand writes differently on LinkedIn vs X). Confirm which profile you're drafting for: pass its `profileKey` argument on each call, or set the `Profile-Key` connection header (see `../getting-started/SKILL.md`); if the user has several profiles and none is given, ask which client this is for rather than guessing.
2. **Pull the voice sample.** Call `mcp__ayrshare__get_platform_history` for each target platform (and/or `mcp__ayrshare__get_post_history` for recent Ayrshare-sent posts). Aim for a representative recent set, not one post.
3. **Read the voice.** From the sample, characterize: tone (formal/playful/technical), sentence length and rhythm, emoji and hashtag habits, link/CTA patterns, formatting (line breaks, lists), and recurring vocabulary. Note differences per platform.
4. **(Optional) Find what worked.** If the goal is performance, not just consistency, pull analytics that **match the history source**: use `mcp__ayrshare__get_post_analytics` for the Ayrshare Post IDs from `get_post_history`, and `mcp__ayrshare__get_post_analytics_by_social_id` for the native Social Post IDs surfaced by `get_platform_history` (native posts have no Ayrshare Post ID). Weight the draft toward the formats/voice that engaged best. This is the "train on voice + optimize on history" pairing — say so to the user when you use it.
5. **Draft in that voice, per platform.** Either write the copy yourself in the observed voice, or brief `mcp__ayrshare__generate_post` with an explicit voice description (tone, length, emoji/hashtag rules) and refine its output. Produce a platform-appropriate variant for each network rather than one string posted everywhere.
6. **Validate, then hand off.** Run `mcp__ayrshare__validate_post` on each variant to catch platform-rule issues (length, media, format) before calling it ready. Present the drafts for review. To publish, continue with the post pipeline in `../post/SKILL.md` (`validate_post` → confirm → `create_post`) — this skill stops at the validated draft.

## Usage guidance

- **History is the voice source — use it, don't skip to generation.** The whole point is grounding the draft in real past posts. If you cannot read any history (a brand-new profile with zero posts, or no platform history available), say so and draft from whatever brief the user gives instead of pretending to match a voice that has no sample.
- **`get_platform_history` is the better voice sample** because it includes native posts not made through Ayrshare. `get_post_history` is narrower (Ayrshare-sent only) but carries status and `notes`. Use both when you can.
- **Match voice per platform.** A brand's LinkedIn voice is usually not its X voice. Pull and analyze each platform separately and write distinct variants; do not reuse one draft across networks.
- **`generate_post` is a drafting aid, not a voice oracle.** It generates from the brief you give it. The brand-voice matching is *your* analysis of the history shaping that brief (and your edits afterward) — feeding it only the topic produces generic copy. It returns text only; it never publishes.
- **Always validate before declaring a draft ready.** `validate_post` is a dry run; running it on the final variants catches over-limit text or unsupported media before the user tries to post.
- **This skill never publishes.** Do not call `create_post` from here. Drafting and publishing are deliberately separate so the user reviews on-brand copy before anything goes live.

## Gotchas

- **No history, no voice match.** A fresh profile has no posts to learn from. Don't fabricate a "house voice" — fall back to the user's brief and say the voice could not be sampled.
- **Voice is profile-scoped, like everything else.** The history you read and the draft you tune come from whichever profile you target: the `profileKey` argument (per call) or the `Profile-Key` header. Drafting for the wrong client is an auth-layer mistake, not a content one, so settle the profile first and use it consistently. (`generate_post` takes no `profileKey` argument; the history/analytics/validate tools do.)
- **Generated drafts still need validation.** `generate_post` output is not pre-validated against platform rules. Run `validate_post` before treating it as postable.
- **Don't claim performance you didn't check.** Only invoke the "optimized on what worked" framing if you actually pulled analytics (step 4). Otherwise you matched voice, not performance — describe it as such.
- **On any tool failure, call `mcp__ayrshare__explain_error`, then surface it — don't loop.** A missing TikTok link (for `recommend_hashtags`), unreachable media, or an empty history won't fix itself on retry. (Mirrors the global retry-safety rule in `../getting-started/SKILL.md`.)
