<#
.SYNOPSIS
    Authenticated git push wrapper with silent, non-interactive token resolution.

.DESCRIPTION
    This wrapper enables silent git operations without interactive authentication prompts.
    
    It implements GitHub's recommended pattern for non-interactive authentication:
    1. Resolves GitHub PAT from multiple sources (env → CredMan → .env)
    2. Sets Git environment variables to force non-interactive mode
    3. Wires up a credential helper (git-askpass) to provide the token
    4. Calls git push with the token available but unexposed in logs
    5. Cleans up all sensitive environment variables after completion

    The original git_push.ps1 remains immutable; this wrapper only sets environment
    and calls it. Token is never logged or exposed in output.

    ** Silent Authentication Pattern **
    
    Key Git environment variables (set per-invocation):
    - GITHUB_TOKEN / GH_TOKEN: carry PAT to askpass helper
    - GIT_ASKPASS: path to git-askpass-env.cmd (credential helper)
    - GIT_TERMINAL_PROMPT=0: never prompt on terminal
    - GCM_INTERACTIVE=Never: disable Git Credential Manager UI
    - credential.helper="": disable other helpers for this invocation
    
    This ensures Git never opens dialogs, never prompts interactively,
    and uses only the environment-based credential helper.

.PARAMETER Message
    Commit message. If omitted, git_push.ps1 auto-generates one.

.PARAMETER DryRun
    Dry run: show what would be committed without performing git push.

.EXAMPLE
    .\invoke-git-push-with-token.ps1
    Uses stored GitHub PAT to push all staged changes silently.

.EXAMPLE
    .\invoke-git-push-with-token.ps1 -Message "feat: add new feature"
    Pushes with explicit message.

.EXAMPLE
    .\invoke-git-push-with-token.ps1 -DryRun -Verbose
    Shows what would be pushed without performing git operations.

.NOTES
    Architecture:
    - token_resolver.py: Retrieves PAT from env/CredMan/.env
    - git-askpass-env.cmd: Credential helper (reads GITHUB_TOKEN env var)
    - This wrapper: Orchestrates env setup and calls git_push.ps1
    
    Requires:
    - GitHub PAT stored via setup-github-credentials.ps1
    - Python 3.6+ (for token_resolver.py)
    - git installed and on PATH
    
    Token is retrieved fresh each invocation (no caching between runs).
    Token is cleared from environment immediately after use.
#>

[CmdletBinding()]
param(
    [Parameter(Position=0, HelpMessage='Commit message. If omitted, auto-generated.')]
    [string]$Message = $null,
    
    [Parameter(HelpMessage='Dry run: show what would be pushed without performing git operations')]
    [switch]$DryRun
    # Note: -Verbose is provided automatically by PowerShell via [CmdletBinding()]
    # Access via $VerbosePreference -eq "Continue" or Write-Verbose
)

$ErrorActionPreference = 'Stop'

# ============================================================================
# Helpers
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = 'INFO'
    )
    $timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
    Write-Host "[$timestamp][$Level] $Message"
}

function Get-TokenFingerprint {
    param([string]$Token)
    
    $bytes = [Text.Encoding]::UTF8.GetBytes($Token)
    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    $hex = [System.BitConverter]::ToString($hash).Replace('-', '').ToLower()
    # Return first 16 hex chars
    return $hex.Substring(0, 16)
}

function Get-GitHubToken {
    <#
    .SYNOPSIS
      Call token_resolver.py to get the GitHub PAT.
    #>
    Write-Log "Resolving GitHub token..."
    
    # Find Python interpreter
    $pythonCmd = $null
    foreach ($cmd in @("py", "python3", "python", "python.exe")) {
        try {
            $null = & $cmd --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = $cmd
                break
            }
        } catch {
            # Continue to next option
        }
    }
    
    if (-not $pythonCmd) {
        Write-Log "Python interpreter not found on PATH" "ERROR"
        return $null
    }
    
    # Find token resolver script
    $resolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "src\skills\token_resolver.py"
    if (-not (Test-Path $resolverPath)) {
        Write-Log "Token resolver script not found: $resolverPath" "ERROR"
        return $null
    }
    
    try {
        # Call Python skill to resolve token
        # Outputs only the token to stdout on success
        $token = & $pythonCmd $resolverPath 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $token) {
            Write-Log "Token resolved successfully"
            return $token
        } else {
            Write-Log "Failed to resolve token (exit code: $LASTEXITCODE)" "ERROR"
            return $null
        }
    } catch {
        Write-Log "Exception while resolving token: $_" "ERROR"
        return $null
    }
}

# ============================================================================
# Main
# ============================================================================

Write-Log "Starting invoke-git-push-with-token.ps1 (DryRun=$DryRun, Verbose=$($VerbosePreference -eq 'Continue'))"

# Validate git_push.ps1 exists
$gitPushScript = Join-Path $PSScriptRoot "git_push.ps1"
if (-not (Test-Path $gitPushScript)) {
    Write-Log "git_push.ps1 not found at: $gitPushScript" "ERROR"
    exit 1
}

# Validate git-askpass-env.cmd exists
$askPassScript = Join-Path $PSScriptRoot "git-askpass-env.cmd"
if (-not (Test-Path $askPassScript)) {
    Write-Log "git-askpass-env.cmd not found at: $askPassScript" "ERROR"
    exit 1
}

# Resolve GitHub token
$token = Get-GitHubToken
if (-not $token) {
    Write-Log "Token resolution failed. Run setup-github-credentials.ps1 to configure." "ERROR"
    exit 1
}

$fingerprint = Get-TokenFingerprint -Token $token
Write-Log "Token fingerprint (SHA-256, first 16 hex chars): $fingerprint"

# Save original env so we can restore
$originalEnv = @{
    GITHUB_TOKEN       = $env:GITHUB_TOKEN
    GH_TOKEN           = $env:GH_TOKEN
    GIT_ASKPASS        = $env:GIT_ASKPASS
    GIT_TERMINAL_PROMPT = $env:GIT_TERMINAL_PROMPT
    GCM_INTERACTIVE    = $env:GCM_INTERACTIVE
    GIT_TRACE          = $env:GIT_TRACE
    GIT_CURL_VERBOSE   = $env:GIT_CURL_VERBOSE
}

try {
    # Set token in environment for git-askpass-env.cmd to consume
    $env:GITHUB_TOKEN = $token
    $env:GH_TOKEN = $token  # Some tools also check GH_TOKEN
    
    # Force non-interactive behavior
    $env:GIT_TERMINAL_PROMPT = '0'
    $env:GCM_INTERACTIVE = 'Never'
    
    # Wire up our askpass helper
    $env:GIT_ASKPASS = $askPassScript
    
    # Disable any configured credential helper for this invocation
    # (This is local-only; won't persist after the process exits)
    git config --local credential.helper "" 2>$null | Out-Null
    
    if ($VerbosePreference -eq "Continue") {
        $env:GIT_TRACE = '1'
        $env:GIT_CURL_VERBOSE = '1'
        Write-Log "Verbose tracing enabled"
        Write-Log "Git environment configured for silent authentication"
    }
    
    # Change to repo root for git operations
    $repoRoot = & git rev-parse --show-toplevel 2>$null
    if (-not $repoRoot) {
        Write-Log "Not in a git repository" "ERROR"
        exit 1
    }
    
    Push-Location $repoRoot
    try {
        if ($DryRun) {
            Write-Log "DRY-RUN: Executing 'git push --dry-run'"
            git push --dry-run
            $exitCode = $LASTEXITCODE
        } else {
            Write-Log "Invoking git_push.ps1 (immutable prototype)"
            if ($Message) {
                & $gitPushScript -Message $Message
            } else {
                & $gitPushScript
            }
            $exitCode = $LASTEXITCODE
        }
        
        if ($exitCode -eq 0) {
            Write-Log "Git push completed successfully"
        } else {
            Write-Log "Git push failed with exit code: $exitCode" "ERROR"
        }
        
        exit $exitCode
    } finally {
        Pop-Location
    }
} catch {
    # Never log the token; only log metadata and generic error info
    Write-Log "Exception during git push. Token fingerprint: $fingerprint. Error: $($_.Exception.Message)" "ERROR"
    exit 1
} finally {
    # Clear sensitive environment variables
    $env:GITHUB_TOKEN = $null
    $env:GH_TOKEN = $null
    
    # Restore other env vars
    $env:GIT_ASKPASS = $originalEnv.GIT_ASKPASS
    $env:GIT_TERMINAL_PROMPT = $originalEnv.GIT_TERMINAL_PROMPT
    $env:GCM_INTERACTIVE = $originalEnv.GCM_INTERACTIVE
    $env:GIT_TRACE = $originalEnv.GIT_TRACE
    $env:GIT_CURL_VERBOSE = $originalEnv.GIT_CURL_VERBOSE
    
    Write-Log "Environment cleaned; token removed from process environment"
}
