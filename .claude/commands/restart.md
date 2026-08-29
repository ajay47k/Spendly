---
description: Exit this session and resume the same conversation in a new window
allowed-tools: Bash(powershell:*)
---

Restart the session. Run this single Bash command and nothing else — do not
explain first, do not ask for confirmation, do not run any other tool:

```
powershell -NoProfile -File .claude/scripts/restart.ps1
```

`.claude/scripts/restart.ps1` does the work:

1. Resolves the current session id by finding the newest `.jsonl` transcript
   under `~/.claude/projects/<slug-of-cwd>/` — the filename is the id.
2. Finds the claude process hosting this session by walking up the parent
   chain from PowerShell.
3. Opens a new Windows Terminal window in the same directory, which waits 3
   seconds and then runs `claude --resume <session-id>`.
4. Kills the current session.

It pins the exact session id rather than using `--continue`, so another
session writing to the same directory cannot steal the resume. If the id
cannot be resolved it falls back to `--continue`. If the claude process
cannot be found it aborts and kills nothing.

This session ends mid-command, so expect no output and no summary. The new
window is where the conversation continues.
