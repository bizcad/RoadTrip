<#
.SYNOPSIS
    Direct git push using token embedded in URL (no credential manager).

.DESCRIPTION
    Simple wrapper that reads token from ProjectSecrets/PAT.txt
    and performs git push with token in the HTTPS URL.
    No credential manager dialog appears.

.PARAMETER Message
    Optional commit message. If provided, stages all and commits with this message before pushing.

.EXAMPLE
    .\push-with-token.ps1
    Pushes current branch silently with token.

.EXAMPLE
    .\push-with-token.ps1 -Message "feat: add new feature"
    Commits staged changes and pushes silently.
#>

param(
    [Parameter(Position=0)]
    [string]$Message = $null
)

$ErrorActionPreference = "Stop"

# Get token from ProjectSecrets (one level up from scripts directory)
$repoRoot = Split-Path -Parent $PSScriptRoot
$projSecretsPath = Join-Path $repoRoot "ProjectSecrets\PAT.txt"
if (-not (Test-Path $projSecretsPath)) {
    Write-Error "PAT.txt not found at: $projSecretsPath"
    exit 1
}

$token = (Get-Content $projSecretsPath -Raw).Trim()
if (-not $token) {
    Write-Error "Token is empty"
    exit 1
}

# Get current branch
$branch = (git rev-parse --abbrev-ref HEAD 2>$null).Trim()
if (-not $branch) {
    Write-Error "Not in a git repository"
    exit 1
}

# Commit if message provided
if ($Message) {
    Write-Host "Staging and committing..."
    git add -A
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Commit failed"
        exit $LASTEXITCODE
    }
}

# Push with token in URL (bypasses credential manager)
Write-Host "Pushing $branch with token..."
$pushUrl = "https://git:$token@github.com/bizcad/RoadTrip.git"
git push $pushUrl $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Push succeeded"
    exit 0
} else {
    Write-Host "✗ Push failed with exit code: $LASTEXITCODE"
    exit $LASTEXITCODE
}
