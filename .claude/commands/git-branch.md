---
description: Create a feature branch off the latest main, only when nothing is uncommitted
argument-hint: "Feature name e.g. registration or login and logout"
allowed-tools: Bash(git:*)
---

Start work on a new feature. Branch off an up-to-date `main`, but only
once the current work is safely committed — a branch switch carries
uncommitted changes with it, and that is how work ends up on the wrong
branch.

Feature name: $ARGUMENTS

## Step 1 — Require a feature name
If $ARGUMENTS is empty, stop and say:

"Usage: /git-branch <feature name>
Example: /git-branch registration"

DO NOT CONTINUE.

## Step 2 — Everything committed?
Run `git status --short`. If anything is listed — modified, staged, or
untracked — stop and say:

"Uncommitted changes:
<the list>

Commit them first with /commit, then run /git-branch again."

DO NOT CONTINUE. Do not stash, do not commit them yourself, and do not
offer to discard them — the user decides where that work belongs.

## Step 3 — Build the branch name
From the feature name derive `feature_slug`:
- Lowercase, kebab-case
- Only `a-z`, `0-9` and `-`
- Maximum 40 characters
- "registration" → `registration`, "Login and Logout" → `login-logout`

The branch is `feature/<feature_slug>`.

If the user's argument already starts with `feature/`, do not double the
prefix — slugify what follows it.

## Step 4 — Check the name is free
Run `git branch --list` and `git branch -r --list`.

If `feature/<feature_slug>` already exists locally or on the remote,
append a two-digit counter until it is free:
`feature/registration-01`, `feature/registration-02`, and so on.
Say in the report that you did this and why.

## Step 5 — Get main up to date
```
git checkout main
git fetch origin
git merge --ff-only origin/main
```

Use `--ff-only`, never a plain `git pull` — a pull can create a merge
commit on main.

If the fast-forward is refused, local `main` has diverged from origin.
Stop, say so, and point at /load. DO NOT CONTINUE — branching from a
diverged main just spreads the problem.

Unpushed commits on `main` are not a blocker. They are committed, so
nothing is at risk; the new branch simply includes them. Note the count
in the report.

## Step 6 — Create the branch
```
git checkout -b feature/<feature_slug>
```

## Step 7 — Report
```
Branch:  feature/<feature_slug>
Base:    <short-sha> <subject>
Main:    <up to date with origin | N commit(s) ahead of origin>
```

If this feature is one of the numbered steps in `CLAUDE.md`, mention
which one, and that `/create-spec <n> <feature>` will write the spec for
it.
