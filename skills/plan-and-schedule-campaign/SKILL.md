---
name: plan-and-schedule-campaign
description: |
  Plan a multi-post, multi-platform social campaign and schedule it across networks via the Ayrshare MCP server — adapting copy and timing per platform, validating each post before it is scheduled, and confirming with the user before anything goes live. Use whenever someone wants more than one scheduled post: "plan a content calendar", "schedule a week of posts", "set up our product-launch sequence", "queue these announcements across LinkedIn and X", "space these out over the next two weeks", or any multi-post / multi-day / multi-platform scheduling request. Trigger even without the word "Ayrshare" — if the user wants a planned, scheduled run of posts rather than one immediate post, this is the skill. It orchestrates `mcp__ayrshare__validate_post` → `mcp__ayrshare__create_post` (with a per-post `scheduleDate`) for each post, optionally `mcp__ayrshare__generate_post` / `mcp__ayrshare__recommend_hashtags` for drafting, and `mcp__ayrshare__get_post` / `mcp__ayrshare__update_post` to manage the scheduled queue afterward. There is **no bulk/campaign endpoint** — a campaign is many individual scheduled posts, each validated and confirmed. For the shared auth model and retry rules, see `../getting-started/SKILL.md`; for the single-post mechanics, see `../post/SKILL.md`.
---

# Ayrshare MCP — Plan & Schedule a Campaign

A workflow skill that turns "schedule a week of launch posts" into a concrete, validated, scheduled set. There is **no dedicated campaign or bulk tool**: a campaign is a series of individual `create_post` calls, each with its own `scheduleDate`, each validated first. This skill is the planning and orchestration layer on top of `../post/SKILL.md`.

It is built on the suggest-and-approve pattern: draft and validate everything, show the user the full plan, and only schedule after explicit confirmation.

## The tools it orchestrates

- `mcp__ayrshare__validate_post` — dry-run each planned post against its platforms' rules **before** scheduling, so an over-limit caption or unsupported media is caught at planning time, not publish time.
- `mcp__ayrshare__create_post` — schedules one post by including a future `scheduleDate` (ISO 8601 UTC). Omitting `scheduleDate` posts immediately, so for a campaign every post carries one. Returns an `id` per post — capture them.
- `mcp__ayrshare__get_post` / `mcp__ayrshare__update_post` — inspect or edit a scheduled (pending) post afterward: reschedule, approve, or adjust. (See `../post/SKILL.md`.)
- `mcp__ayrshare__generate_post` / `mcp__ayrshare__recommend_hashtags` — optional drafting aids for the copy (drafts only; they never publish). For on-brand copy, pair with `../draft-in-brand-voice/SKILL.md`.

All are profile-scoped by the connection's `Profile-Key` header — there is **no per-call `profileKey` argument**. The whole campaign schedules under whichever profile that header selects, so confirm the connection before scheduling anything.

## Scheduling fields (from the post schema)

Per-post timing/workflow controls (full schema in `../post/references/create-post-schema.md`):

- `scheduleDate` (ISO 8601 UTC, e.g. `2026-07-08T12:30:00Z`) — the future publish time. The core of every campaign post. Convert relative dates ("next Tuesday 9am") to an absolute UTC timestamp yourself.
- `autoSchedule` (`{ schedule: true, title? }`) — publish into a **named auto-schedule's** next open slot instead of a fixed time. **Cannot be combined with `scheduleDate`** — pick one timing model per post.
- `autoRepost` (`{ repeat: 1-10, days: >=2, startDate? }`) — recurring/evergreen reposting (paid plan). Also **cannot be combined with `scheduleDate`**.
- `requiresApproval` (bool) — hold each post in `awaiting approval` until approved via `update_post` (`approved: true`). Useful when a human must sign off each calendar item.
- `validateScheduled` (bool, default `true`) — pre-validate scheduled posts at submission so errors surface immediately rather than at publish time. Keep it on.
- `idempotencyKey` (string) — unique per post so a retried submission does not create a duplicate. Worth setting when scheduling many posts in a loop.

## Workflow

1. **Confirm the profile.** A campaign schedules under the profile the `Profile-Key` connection header selects. If several profiles exist and none is set, ask which client this is for (see `../getting-started/SKILL.md`).
2. **Build the plan.** Lay out the posts: for each, the message, the target platform(s), the media (if any), and the intended time. Adapt copy per platform (char limits, format) rather than reusing one string — use per-platform option objects where needed (e.g. `youTubeOptions.title`, `redditOptions.title` + `subreddit`). For drafting help, use `../generate/SKILL.md` or, for on-brand copy, `../draft-in-brand-voice/SKILL.md`.
3. **Convert every time to ISO 8601 UTC.** Turn "Friday 9am" into an absolute `scheduleDate`. Never pass a human phrase or an empty string. Decide one timing model per post: a fixed `scheduleDate`, OR `autoSchedule`, OR `autoRepost` — never two at once.
4. **Validate every post.** Call `mcp__ayrshare__validate_post` on each planned post (same inputs as `create_post`). Surface any per-platform issues and fix them before scheduling.
5. **Show the full plan and get explicit confirmation.** Present the calendar (each post: platforms, time, preview). Wait for the user to approve before scheduling anything. This is a write step — do not auto-schedule.
6. **Schedule, one post at a time.** For each approved post call `mcp__ayrshare__create_post` with its `scheduleDate` (set `idempotencyKey`). Capture the returned `id` for every post — that is how you manage it later.
7. **Track and adjust.** Use `mcp__ayrshare__get_post` to check status and `mcp__ayrshare__update_post` to reschedule/approve/edit a pending post. To recover a post that failed at publish time, use `mcp__ayrshare__retry_post` (once, only if retryable) — never a second `create_post`, which would duplicate.

## Usage guidance

- **A campaign is N individual posts.** There is no bulk endpoint. You loop validate → create per post; the "campaign" is your plan plus the captured `id`s, not a single API object. Keep a running list of `{ time, platforms, id }` so you can manage the queue.
- **Validate before scheduling, not after.** `validate_post` at planning time is the whole safety win — it turns publish-time rejections into planning-time fixes. Keep `validateScheduled: true` as well so scheduled posts are re-checked at submission.
- **Confirm the whole calendar before any write.** Show the user every post and time, get one explicit approval, then schedule. Suggest-and-approve, not fire-and-forget.
- **One timing model per post.** `scheduleDate`, `autoSchedule`, and `autoRepost` are mutually exclusive on a single post. Choose deliberately: fixed time for a calendar, `autoSchedule` for "next open slot", `autoRepost` for evergreen.
- **Adapt copy per platform.** Char limits and required fields differ (YouTube needs a title; Reddit needs title + subreddit). Build per-platform variants and validate each, rather than scheduling one identical string everywhere.
- **Capture every `id`.** Rescheduling, approving, editing, and status checks all key off the post `id` returned by `create_post`.
- **Set `idempotencyKey` when scheduling in a loop.** It prevents a retried submission from creating a duplicate scheduled post.

## Gotchas

- **No bulk/campaign tool exists.** Don't look for one. Each post is its own `validate_post` + `create_post`. If you skip the per-post loop you'll under-deliver the plan.
- **`scheduleDate` must be ISO 8601 UTC, future.** e.g. `2026-07-08T12:30:00Z`. A human phrase, an empty string, or a past time fails or posts immediately. Convert relative times yourself.
- **`scheduleDate` + `autoSchedule`/`autoRepost` is invalid.** They are mutually exclusive — combining them on one post is rejected. Pick one timing model.
- **Scheduling is a write — never schedule without confirmation.** Present the full calendar first. Don't auto-retry a failed schedule on a 4xx; a closed window, bad media, or wrong platform won't fix itself, and a blind resend can duplicate. Use `idempotencyKey` to be safe.
- **Profile scoping is the connection header.** The whole campaign schedules under the profile the `Profile-Key` header selects; there is no `profileKey` argument. Confirm the connection before scheduling for a client.
- **Recover failures with `retry_post`, not a second `create_post`.** A second create duplicates on platforms that already succeeded. `retry_post` re-attempts a failed post once, only if retryable.
- **On any tool failure, call `mcp__ayrshare__explain_error`, then surface it.** Translate the error to plain language for the user; a 429 gets at most one retry after a short delay. (Mirrors the global retry-safety rule in `../getting-started/SKILL.md`.)
