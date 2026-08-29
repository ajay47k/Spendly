---
description: Pull the latest origin/main, only when local work is safely pushed
allowed-tools: Bash(git:*)
---

Load the latest `origin/main`. Only safe when nothing local can be lost —
so verify that first, and refuse otherwise.

## Step 1 — Fetch
Run `git fetch origin`.

## Step 2 — Everything committed?
Run `git status --short`. If anything is listed — modified, staged, or
untracked — stop and say:

"Uncommitted changes. Commit them first, then run /load again."

DO NOT CONTINUE.

## Step 3 — Everything pushed?
Run `git rev-list --count origin/main..main`. If the result is not `0`,
those commits exist only locally. Stop and say:

"N commit(s) not on origin. Push them first:
  git push origin main
Then run /load again."

DO NOT CONTINUE. Do not offer to discard them.

## Step 4 — Load
Both checks passed, so local work is already safe on origin and nothing
can be lost. Fast-forward:

```
git merge --ff-only origin/main
```

Use `--ff-only`, never `git pull` — a plain pull can create a merge commit.

## Step 5 — Report
```
Now at:  <short-sha> <subject>
Status:  <already up to date | pulled N commit(s)>
```
