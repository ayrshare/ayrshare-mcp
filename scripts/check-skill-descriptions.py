#!/usr/bin/env python3
"""Validate every skills/*/SKILL.md frontmatter `description` against the
constraints the claude.ai Cowork / community-marketplace plugin validator
enforces but `claude plugin validate` does NOT:

  - at most 1024 characters
  - no angle brackets ('<' or '>'), which the validator treats as XML tags

This exists so a future skill edit cannot silently reintroduce the failure that
blocked the Cowork org upload (see PR #13). Run from anywhere in the repo; it
resolves paths relative to its own location. Exits non-zero and lists every
offender on failure.
"""
import glob
import os
import re
import sys

MAX_LEN = 1024


def extract_description(text):
    """Return the logical description string from a SKILL.md, or None."""
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not fm_match:
        return None
    frontmatter = fm_match.group(1)

    # Block scalar form:  description: |   (or >)   followed by indented lines.
    block = re.search(
        r"^description:[ \t]*[|>][-+0-9]*[ \t]*\n((?:[ \t].*\n?)*)",
        frontmatter,
        re.M,
    )
    if block and block.group(1).strip():
        lines = [ln.strip() for ln in block.group(1).splitlines()]
        return " ".join(ln for ln in lines if ln)

    # Inline form:  description: some text   (optionally quoted).
    inline = re.search(r"^description:[ \t]*(.+)$", frontmatter, re.M)
    if inline:
        return inline.group(1).strip().strip("\"'")

    return None


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))
    if not paths:
        print("error: no skills/*/SKILL.md found", file=sys.stderr)
        return 1

    failures = []
    for path in paths:
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as fh:
            desc = extract_description(fh.read())
        if desc is None:
            failures.append(f"{rel}: no frontmatter 'description' found")
            continue
        length = len(desc)
        if length > MAX_LEN:
            failures.append(f"{rel}: description is {length} chars (max {MAX_LEN})")
        brackets = sorted({c for c in desc if c in "<>"})
        if brackets:
            failures.append(
                f"{rel}: description contains {brackets} (validator rejects XML tags)"
            )

    if failures:
        print("SKILL.md description validation FAILED:", file=sys.stderr)
        for failure in failures:
            print("  - " + failure, file=sys.stderr)
        print(
            "\nKeep each skill's frontmatter description at most "
            f"{MAX_LEN} characters and free of '<' or '>'.",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: {len(paths)} skill descriptions, all <= {MAX_LEN} chars "
        "and free of angle brackets."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
