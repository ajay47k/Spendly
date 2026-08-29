# Restart this Claude Code session: resume the SAME conversation in a new window.
#
# The new window must be a separate process - a child of the session being
# killed would die with it and would have no TTY of its own.

$ErrorActionPreference = 'Stop'
$cwd = (Get-Location).Path

# Claude Code stores transcripts under a slug of the cwd, with ':', '\', '/',
# '_' and '.' all folded to '-'. The transcript's filename is the session id.
$slug = $cwd.Replace(':', '-').Replace('\', '-').Replace('/', '-').Replace('_', '-').Replace('.', '-')
$projectDir = Join-Path $env:USERPROFILE ".claude\projects\$slug"

$sessionId = $null
if (Test-Path $projectDir) {
    $newest = Get-ChildItem $projectDir -Filter *.jsonl -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($newest) { $sessionId = $newest.BaseName }
}

# Pin the exact session when we can; fall back to "most recent" if not.
if ($sessionId) {
    $resume  = "claude --resume $sessionId"
    $label   = "resuming session $sessionId"
} else {
    $resume  = "claude --continue"
    $label   = "session id not resolved - falling back to --continue"
}

# Walk up from this process to find the claude that hosts the session.
$p = $PID
$claudePid = $null
for ($i = 0; $i -lt 12; $i++) {
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $p" -ErrorAction SilentlyContinue
    if (-not $proc) { break }
    if ($proc.Name -like 'claude*') { $claudePid = $proc.ProcessId; break }
    $p = $proc.ParentProcessId
}
if (-not $claudePid) {
    Write-Output "Could not find the claude process in the parent chain. Aborting - nothing was killed."
    exit 1
}

Write-Output $label
Write-Output "Opening new window, then killing PID $claudePid."

# 3s delay so the old session is gone before the new one attaches.
Start-Process wt -ArgumentList '-d', $cwd, 'powershell', '-NoExit', '-Command', "Start-Sleep -Seconds 3; $resume"
Start-Sleep -Seconds 1
Stop-Process -Id $claudePid -Force
