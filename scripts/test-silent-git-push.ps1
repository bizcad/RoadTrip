<#
.SYNOPSIS
    Test harness: Validate silent Git push end-to-end.

.DESCRIPTION
    This harness script validates the complete silent authentication chain:
    
    1. Remote is HTTPS (required for token-based auth)
    2. Token can be resolved via token_resolver.py
    3. Token fingerprint is computed (SHA-256, first 16 hex chars)
    4. invoke-git-push-with-token.ps1 -DryRun runs without interactive prompts
    
    This script assumes:
    - token_resolver.py is in the scripts folder
    - invoke-git-push-with-token.ps1 is in the scripts folder
    - Repo root is one level up from scripts folder
    - GitHub PAT is already configured (via setup-github-credentials.ps1)

    To validate NON-INTERACTIVE behavior, run this script from an automation
    context where no console/UI is available (e.g., scheduled task, agent).

.PARAMETER Verbose
    Enable verbose output (Git trace, but token is never exposed).

.EXAMPLE
    .\test-silent-git-push.ps1
    Runs validation in interactive mode (good for local testing).

.EXAMPLE
    .\test-silent-git-push.ps1 -Verbose
    Runs with Git tracing enabled (shows detailed auth sequence).

.NOTES
    Exit codes:
    0 = All validation checks passed
    1 = Validation failed (see output for details)
    
    For full non-interactive validation, run this from a scheduled task
    or automation agent without user session.
#>

param(
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = 'INFO'
    )
    $ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
    Write-Host "[$ts][$Level] $Message"
}

function Get-TokenFingerprint {
    param([string]$Token)

    $bytes = [Text.Encoding]::UTF8.GetBytes($Token)
    $hash  = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    $hex   = [Convert]::ToHexString($hash)
    return $hex.Substring(0, 16)
}

# ============================================================================
# Setup
# ============================================================================

$scriptRoot = $PSScriptRoot
$repoRoot   = Resolve-Path (Join-Path $scriptRoot "..")
$tokenResolver = Join-Path $repoRoot "src\skills\token_resolver.py"
$invokePush    = Join-Path $scriptRoot "invoke-git-push-with-token.ps1"

Write-Log "Starting silent Git push test harness."
Write-Log "Repo root: $repoRoot"
Write-Host ""

# ============================================================================
# Validation Checks
# ============================================================================

# Check 1: git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Log "git not found on PATH." 'ERROR'
    Write-Log "Please install git or add it to your PATH." 'ERROR'
    exit 1
}
Write-Log "✓ git is available on PATH"

# Check 2: Python is available (py launcher for Windows)
$pythonCmd = $null
foreach ($cmd in @("py", "python3", "python")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}
if (-not $pythonCmd) {
    Write-Log "Python not found. Install Python 3.6+ or add to PATH." 'ERROR'
    exit 1
}
Write-Log "✓ Python is available on PATH ($pythonCmd)"

# Check 3: token_resolver.py exists
if (-not (Test-Path $tokenResolver)) {
    Write-Log "token_resolver.py not found at $tokenResolver" 'ERROR'
    exit 1
}
Write-Log "✓ token_resolver.py found"

# Check 4: invoke-git-push-with-token.ps1 exists
if (-not (Test-Path $invokePush)) {
    Write-Log "invoke-git-push-with-token.ps1 not found at $invokePush" 'ERROR'
    exit 1
}
Write-Log "✓ invoke-git-push-with-token.ps1 found"

Write-Host ""

# ============================================================================
# Repo Checks
# ============================================================================

Push-Location $repoRoot
try {
    # Check 5: Inside a git repository
    $gitDir = & git rev-parse --git-dir 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Not inside a git repository" 'ERROR'
        exit 1
    }
    Write-Log "✓ Inside a git repository"

    # Check 6: Remote is HTTPS
    $remotes = & git remote -v
    Write-Log "Git remotes:"
    $remotes | ForEach-Object { Write-Log "  $_" }
    
    if ($remotes -notmatch 'https://') {
        Write-Log "Remote does not use HTTPS. Silent PAT auth requires HTTPS." 'ERROR'
        Write-Log "Configure your remote using: git remote set-url origin https://..." 'ERROR'
        exit 1
    }
    Write-Log "✓ Remote uses HTTPS"

    # Check 7: Token can be resolved
    Write-Log "Resolving GitHub token via token_resolver.py..."
    $token = & $pythonCmd $tokenResolver 2>$null
    
    if ($LASTEXITCODE -ne 0 -or -not $token) {
        Write-Log "token_resolver.py failed to return a token." 'ERROR'
        Write-Log "Run setup-github-credentials.ps1 to configure credentials." 'ERROR'
        exit 1
    }

    $fingerprint = Get-TokenFingerprint -Token $token
    Write-Log "✓ Token resolved"
    Write-Log "  Fingerprint (SHA-256, first 16 hex chars): $fingerprint"
    
    # Immediately clear token from memory
    $token = $null

    Write-Host ""

    # Check 8: Dry-run push via wrapper (no actual push)
    Write-Log "Running invoke-git-push-with-token.ps1 -DryRun (no actual push)..."
    Write-Log "This validates the silent auth chain without modifying the repo."
    Write-Host ""

    # Build arguments for child PowerShell process
    $args = @('-File', $invokePush, '-DryRun')
    if ($Verbose) {
        $args += '-Verbose'
    }

    # Use a child PowerShell process to mimic automation context better
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = (Get-Process -Id $PID).Path
    $psi.Arguments = $args -join ' '
    $psi.WorkingDirectory = $repoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true

    # Pass all environment variables to child process
    # Child process doesn't automatically inherit parent environment
    $currentEnv = [System.Environment]::GetEnvironmentVariables([System.EnvironmentVariableTarget]::Process)
    foreach ($key in $currentEnv.Keys) {
        if (-not $psi.EnvironmentVariables.ContainsKey($key)) {
            [void]$psi.EnvironmentVariables.Add($key, $currentEnv[$key])
        }
    }

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    [void]$proc.Start()
    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    Write-Host $stdout
    if ($stderr) {
        Write-Host $stderr
    }

    if ($proc.ExitCode -ne 0) {
        Write-Log "invoke-git-push-with-token.ps1 -DryRun failed with exit code $($proc.ExitCode)." 'ERROR'
        exit $proc.ExitCode
    }

    Write-Host ""
    Write-Log "✓ Dry-run silent push completed successfully"
    Write-Log "  No interactive prompts appeared"
    Write-Host ""

    Write-Log "VALIDATION PASSED" 'INFO'
    Write-Log "The silent authentication chain is working correctly." 'INFO'
    Write-Host ""
    Write-Log "Next steps:" 'INFO'
    Write-Log "  1. Test a real push: .\invoke-git-push-with-token.ps1 -Message 'test: silent auth validation'" 'INFO'
    Write-Log "  2. For full non-interactive validation, run this harness from a scheduled task" 'INFO'
    Write-Host ""
}
finally {
    Pop-Location
}
