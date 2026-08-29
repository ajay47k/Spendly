---
description: Stage, commit with an auto-generated message, and push to origin
allowed-tools: Bash(git:*), Read
---

Ship the current work in one go: stage everything, write the commit
message yourself from the diff, and push to `origin`.

Optional user note: $ARGUMENTS
If present, treat it as a steer on emphasis or wording, not as the message.

## Step 1 — Commit
Follow `.claude/commands/commit.md` end to end — the safety scan, the
staging, reading the cached diff, and the message rules all live there.
Read that file and apply it; do not invent a different message format.

Stop where it says to stop. Nothing to commit, a stray `.db` or `.env`
in the status, or a failing hook all mean no push happens either.

One difference: skip its final "Not pushed" line — you are about to push.

## Step 2 — Find the upstream
```
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

The second command failing means the branch has no upstream yet.

## Step 3 — Push
With an upstream:
```
git push origin <branch>
```

Without one:
```
git push -u origin <branch>
```

Never `--force`, never `--force-with-lease`, never `--no-verify`.

## Step 4 — Handle a rejected push
A rejection means `origin/<branch>` moved on since you last fetched.
Do not rebase, merge, or force anything on your own. The commit is
already safe locally. Stop and say:

"Push rejected — origin/<branch> has commits you do not have.
Your commit <short-sha> is safe locally. Run /load to fast-forward,
then push again."

DO NOT CONTINUE.

## Step 5 — Report
```
Branch:  <branch>
Commit:  <short-sha> <subject>
Files:   <n> changed, +<x> -<y>
Pushed:  origin/<branch> <-- <short-sha>
```
