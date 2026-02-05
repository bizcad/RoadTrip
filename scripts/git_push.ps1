<#
.SYNOPSIS
    Stage, commit, and push repository changes to the current branch's origin.

.DESCRIPTION
    Stages, commits, and pushes repository changes to `origin/<current-branch>`.

    If `-Message` is provided, that message is used for the commit. If `-Message`
    is omitted, the script auto-generates a descriptive commit subject and body
    from the staged changes (when running normally) or from the working-tree
    status (when using `-DryRun`). Use `-DryRun` to print the generated message
    without performing any git operations.

    Exit codes:
      0   Success
      2   git not installed or not on PATH
      3   Current folder is not a git repository
      4   git add failed
      5   git commit failed
      6   git push failed
      7   Validation failed (missing origin remote)

.PARAMETER Message
    Commit message to use. If omitted, a descriptive message is auto-generated
    from the staged changes (or working-tree when -DryRun). Default: $null

.PARAMETER DryRun
    Do not perform git operations; print the generated commit message and exit.
    Useful for testing message generation.



.PARAMETER LogFile
    Optional path to append execution log. If omitted, console output only.
    Log includes timestamp, command description, changes summary, and result.

.EXAMPLE
    .\git_push.ps1 -Message "Add feature X"
    Commits all staged changes with the message "Add feature X" and pushes.

.EXAMPLE
    .\git_push.ps1
    Auto-generates a commit message from staged changes and pushes.

.EXAMPLE
    .\git_push.ps1 -DryRun -Verbose
    Prints the generated commit message with detailed output without performing
    any git operations.

.EXAMPLE
    .\git_push.ps1 -LogFile "./logs/push.log"
    Commits and pushes, appending execution details to the log file.

.OUTPUTS
    None. Exit codes indicate success or failure.

.NOTES
    Requires git to be installed and accessible on the system PATH.
    Ensures origin remote exists before attempting push.
    Cleanup of temporary files is verified; failures are logged as warnings.

#>

[CmdletBinding()]
param(
    [Parameter(Position=0, HelpMessage = 'Commit message. If omitted, a descriptive message is auto-generated from staged changes (or working-tree when -DryRun).')]
    [string]$Message = $null
    ,
    [Parameter(HelpMessage = 'Do not perform git operations; print the generated commit message and exit.')]
    [switch]$DryRun
    ,
    [Parameter(HelpMessage = 'Optional path to append execution log (timestamp, command, result).')]
    [string]$LogFile = $null
)

# ============================================================================
# Helper Functions
# ============================================================================

function Fail([string]$msg, [int]$code = 1) {
    Write-Host $msg -ForegroundColor Red
    Log-Event "ERROR: $msg (exit $code)"
    exit $code
}

function Log-Event([string]$msg) {
    if ([string]::IsNullOrWhiteSpace($LogFile)) { return }
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $msg" | Add-Content -Path $LogFile -Encoding UTF8 -ErrorAction SilentlyContinue
}

function GenerateCommitMessage([string[]]$statusLines, [bool]$useNameStatus = $false) {
    <#
    .SYNOPSIS
      Parse git status output and generate a descriptive commit message.

    .PARAMETER statusLines
      Lines from `git status --porcelain` or `git diff --cached --name-status`.

    .PARAMETER useNameStatus
      If $true, parse git diff --cached --name-status format (tab-separated codes+paths).
      If $false, parse git status --porcelain format (two-char code + space + path).
      Handles multi-char codes (e.g., R100 for rename with similarity percentage).

    .OUTPUTS
      A string with the generated commit message (subject + optional body).
    #>
    $added = @()
    $modified = @()
    $deleted = @()
    $renamed = @()
    $copied = @()

    foreach ($line in $statusLines) {
        $trim = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trim)) { continue }

        if ($useNameStatus) {
            # Format: "A\tpath", "M\tpath", "R100\told\tnew"
            $parts = $trim -split "\t"
            $code = $parts[0]
            if ($code -match '^R[0-9]*$') {
                # Rename: code is R or R<percentage>
                $renamed += "$($parts[1]) -> $($parts[2])"
            } elseif ($code.StartsWith('A')) {
                $added += $parts[1]
            } elseif ($code.StartsWith('M')) {
                $modified += $parts[1]
            } elseif ($code.StartsWith('D')) {
                $deleted += $parts[1]
            } elseif ($code.StartsWith('C')) {
                $copied += $parts[1]
            } else {
                # Fallback: assume modification
                $modified += $parts[-1]
            }
        } else {
            # Format: " M path", "A  path", "R  old -> new"
            # Handle multi-char codes (e.g., "R100", "AM", "MD")
            if ($trim -match '^([A-Z]+[0-9]*?)\s+(.*)$') {
                $code = $Matches[1]
                $rest = $Matches[2]
                if ($rest -match '->') {
                    $renamed += $rest.Trim()
                } elseif ($code.Contains('A')) {
                    $added += $rest
                } elseif ($code.Contains('M')) {
                    $modified += $rest
                } elseif ($code.Contains('D')) {
                    $deleted += $rest
                } elseif ($code.Contains('C')) {
                    $copied += $rest
                } else {
                    $modified += $rest
                }
            }
        }
    }

    $total = ($added.Count + $modified.Count + $deleted.Count + $renamed.Count + $copied.Count)

    # Single-file case: short message
    if ($total -eq 1) {
        if ($added.Count -eq 1) { return "Add: $($added[0])" }
        if ($deleted.Count -eq 1) { return "Remove: $($deleted[0])" }
        if ($renamed.Count -eq 1) { return "Rename: $($renamed[0])" }
        return "Update: $($modified[0])"
    }

    # Multi-file case: subject + body with categorized lists
    $subject = "chore: update $total files (+$($added.Count) ~$($modified.Count) -$($deleted.Count))"
    $sections = @()

    if ($added.Count -gt 0) {
        $sections += "Added:`n$([string]::Join("`n", ($added | ForEach-Object { "- $_" })))"
    }
    if ($modified.Count -gt 0) {
        $sections += "Modified:`n$([string]::Join("`n", ($modified | ForEach-Object { "- $_" })))"
    }
    if ($renamed.Count -gt 0) {
        $sections += "Renamed:`n$([string]::Join("`n", ($renamed | ForEach-Object { "- $_" })))"
    }
    if ($deleted.Count -gt 0) {
        $sections += "Deleted:`n$([string]::Join("`n", ($deleted | ForEach-Object { "- $_" })))"
    }
    if ($copied.Count -gt 0) {
        $sections += "Copied:`n$([string]::Join("`n", ($copied | ForEach-Object { "- $_" })))"
    }

    $body = [string]::Join("`n`n", $sections)
    return $subject + "`n`n" + $body
}


# ============================================================================
# Main Script
# ============================================================================

# Refresh environment variables to ensure git is available (especially after fresh installs)
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Validate git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail 'git is not installed or not on PATH.' 2
}

# Ensure we are in a git repository
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    Fail 'Current folder is not inside a git repository.' 3
}

Set-Location $repoRoot.Trim()

Write-Verbose "Repository root: $repoRoot"
Log-Event "Starting push workflow in $(Get-Location)"

# Check for any changes in the working tree
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host 'No changes to commit.' -ForegroundColor Yellow
    Log-Event 'No changes to commit; exiting.'
    exit 0
}

Write-Verbose "Found changes to commit"

# ============================================================================
# Dry-Run Mode: Print message without staging/committing
# ============================================================================

if ($DryRun) {
    Write-Verbose "DryRun mode: analyzing working-tree changes without staging"
    $statusLines = $status -split "`n"
    $gen = if ($Message) { $Message } else { GenerateCommitMessage $statusLines -useNameStatus $false }
    Write-Host "`n--- Dry Run: Generated commit message ---" -ForegroundColor Cyan
    Write-Host $gen
    Write-Host "--- End generated message ---`n" -ForegroundColor Cyan
    Log-Event "DryRun: generated message without performing git operations."
    exit 0
}


# ============================================================================
# Normal Mode: Stage, Commit, and Push
# ============================================================================

Write-Host "Staging all changes..."
Write-Verbose "Running: git add -A"
git add -A
if ($LASTEXITCODE -ne 0) { Fail 'git add failed.' 4 }
Write-Verbose "✓ Staging complete"
Log-Event 'Staged all changes with git add -A'

# Generate commit message if not provided
if (-not $Message) {
    Write-Verbose "Generating commit message from staged changes..."
    $stagedRaw = git diff --cached --name-status
    if (-not $stagedRaw) {
        Fail 'No staged changes available to describe.' 5
    }
    $stagedLines = $stagedRaw -split "`n"
    $Message = GenerateCommitMessage $stagedLines -useNameStatus $true
    Write-Verbose "✓ Message generated: $($Message.Split("`n")[0])"
}

# Commit with the message
Write-Verbose "Committing changes..."
$tempFile = [System.IO.Path]::GetTempFileName()
try {
    Set-Content -Path $tempFile -Value $Message -Encoding UTF8
    Write-Verbose "Running: git commit -F <temp-file>"
    Write-Host "Committing: $($Message.Split("`n")[0])"
    Log-Event "Committing with message: $($Message.Split("`n")[0])"
    git commit -F $tempFile
    if ($LASTEXITCODE -ne 0) { Fail 'git commit failed (no changes staged or commit aborted).' 5 }
    Write-Verbose "✓ Commit successful"
} finally {
    # Ensure temporary file is cleaned up
    if (Test-Path $tempFile -ErrorAction SilentlyContinue) {
        try {
            Remove-Item $tempFile -Force -ErrorAction Stop
            Write-Verbose "✓ Temporary commit message file cleaned up"
        } catch {
            Write-Host "  ⚠ Warning: Could not delete temporary file: $tempFile" -ForegroundColor Yellow
            Log-Event "Warning: temp file cleanup failed: $_"
        }
    }
}

# Determine target branch
Write-Verbose "Determining target branch..."
$branch = git rev-parse --abbrev-ref HEAD 2>$null
if ($branch -eq 'HEAD' -or -not $branch) {
    # Detached HEAD; try to infer from remote
    $branch = git symbolic-ref refs/remotes/origin/HEAD 2>$null | ForEach-Object { $_ -replace 'refs/remotes/origin/', '' }
    if (-not $branch) {
        $branch = 'main'
    }
    Write-Verbose "Detached HEAD; using remote default: $branch"
} else {
    Write-Verbose "Current branch: $branch"
}

# Pre-check: verify origin remote exists (only needed for push)
if (-not (git remote get-url origin 2>$null)) {
    Fail 'origin remote does not exist or is not accessible.' 7
}
Write-Verbose "✓ origin remote found"
Log-Event "Validated origin remote exists."

# Push to origin
Write-Host "Pushing to origin/$branch..."
Write-Verbose "Running: git push origin $branch (with 5s connection timeout)"
Log-Event "Pushing to origin/$branch..."
git -c http.connectTimeout=5 push origin $branch --quiet
if ($LASTEXITCODE -ne 0) { Fail 'git push failed.' 6 }
Write-Verbose "✓ Push successful"

Write-Host 'Push complete.' -ForegroundColor Green
Log-Event 'Push complete successfully.'
exit 0
