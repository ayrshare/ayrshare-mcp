# Contributing

## This is a public repository

Anything committed here is visible to the world the moment it is pushed. A leaked
credential is compromised instantly and **cannot be un-leaked** by deleting the commit
(push events and the API have already exposed it). Treat secret prevention as a
local, pre-push concern, not something CI can fix after the fact.

Never commit:

- API keys, bearer tokens, or `Authorization` header values with real keys
- Private keys (the Ayrshare account private key can mint linking URLs for every
  profile under the account)
- `.env` files (already covered by `.gitignore`)

Use placeholders in committed files: `${AYRSHARE_API_KEY}`, `Bearer KEY`, etc.

## Enable local secret scanning (one-time, per clone)

We use [TruffleHog](https://github.com/trufflesecurity/trufflehog) to catch secrets
before they are committed. After cloning:

```sh
brew install trufflehog          # or see TruffleHog docs for your OS
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

The `pre-commit` hook scans your staged changes and blocks the commit if it finds a
verified secret. If TruffleHog is not installed, the hook warns and lets the commit
through, CI is the backstop in that case.

## CI backstop

Every push and pull request runs the **TruffleHog Secret Scanning** workflow
(`.github/workflows/trufflehog.yml`) over the full git history. A verified finding
fails the check. This check should be marked **required** in branch protection for
`main`, so a red PR cannot be merged.

If a secret ever does land on a branch: **rotate the key first** (it is already
exposed), then scrub the history.
