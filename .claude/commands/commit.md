---
description: Stage everything and commit with an auto-generated message
allowed-tools: Bash(git:*)
---

Stage all changes and commit them with a message you write yourself from
the diff. The user gives you nothing — read the work and describe it.

Optional user note: $ARGUMENTS
If present, treat it as a steer on emphasis or wording, not as the message.

## Step 1 — Look before staging
Run `git status --short`.

If it is empty, stop and say: "Nothing to commit."

Scan the list for things that must never be committed:
- `expense_tracker.db` or any `*.db` / `*.sqlite` file
- `venv/`, `__pycache__/`, `.pytest_cache/`
- `.env`, or any file that looks like it holds a key or password

If any appear, stop, name them, and say they belong in `.gitignore`.
DO NOT CONTINUE.

## Step 2 — Stage
```
git add .
```

## Step 3 — Read the actual change
Run these, and read the output properly — the message comes from here,
not from memory of the conversation:
```
git diff --cached --stat
git diff --cached
git log --oneline -5
git branch --show-current
```

If the diff is very large, still read the stat and the diff of the files
that carry the intent (routes, schema, logic) rather than the noise.

## Step 4 — Write the message
Match this repository's existing style exactly — check `git log` above.

**Subject line**
- Imperative mood: "Add", "Implement", "Fix", never "Added" or "Adds"
- No conventional-commit prefixes (`feat:`, `chore:`) — this repo has none
- 50 characters or fewer, no trailing period
- Names the change, not the files: "Implement Step 1: SQLite database setup"

**Body** (skip only for a genuinely trivial one-line change)
- Blank line after the subject, wrapped at 72 characters
- One short paragraph saying what the change does overall
- Then bullets for the parts worth calling out
- Explain *why* wherever the reason is not obvious from the code —
  the non-obvious decision is the thing worth recording
- Never list files that the diff already shows

**Roadmap awareness**
If the change implements one of the numbered steps in `CLAUDE.md`, say so
in the subject: "Implement Step N: <what>".

**Trailers**
End the message with the `Co-Authored-By` and `Claude-Session` trailers
that this session's git instructions specify, using this session's own
URL — never one copied from an earlier commit.

## Step 5 — Commit
Pass the message on stdin so multi-line text survives the shell:
```
git commit -F - <<'EOF'
<subject>

<body>
EOF
```

Never use `--no-verify` and never `--amend` an existing commit.
If a hook rejects the commit, report what it said and stop — fix the
cause, do not bypass it.

## Step 6 — Report
```
Branch:  <branch>
Commit:  <short-sha> <subject>
Files:   <n> changed, +<x> -<y>
```

Then say: "Not pushed. Run /commit-push to commit and push in one go."
