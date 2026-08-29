---
description: Switch to main and pull the latest origin/main, only when local work is safely pushed
allowed-tools: Bash(git:*)
---

Switch to `main` and load the latest `origin/main`. Only safe when nothing
local can be lost — so verify that first, and refuse otherwise.

Run every check BEFORE switching branches, so a refusal leaves the repo
exactly as it was.

## Step 1 — Fetch
Run `git fetch origin`.

## Step 2 — Everything committed?
Run `git status --short`. If anything is listed — modified, staged, or
untracked — stop and say:

"Uncommitted changes. Commit them first, then run /load again."

DO NOT CONTINUE. Switching branches with a dirty tree drags the changes
along or fails outright.

## Step 3 — Everything on main pushed?
Run `git rev-list --count origin/main..main`. If the result is not `0`,
those commits exist only locally. Stop and say:

"N commit(s) on main not on origin. Push them first:
  git push origin main
Then run /load again."

DO NOT CONTINUE. Do not offer to discard them.

## Step 4 — Switch to main
Run `git branch --show-current`. If it is already `main`, skip this step.
Otherwise remember the branch name for the report and run:

```
git switch main
```

Leaving a feature branch does not lose its commits — the branch still
points at them. Nothing to warn about here.

## Step 5 — Load
Both checks passed, so local work is already safe on origin and nothing
can be lost. Fast-forward:

```
git merge --ff-only origin/main
```

Use `--ff-only`, never `git pull` — a plain pull can create a merge commit.

## Step 6 — Report
```
Branch:  main <(was <previous-branch>) if you switched>
Now at:  <short-sha> <subject>
Status:  <already up to date | pulled N commit(s)>
```
