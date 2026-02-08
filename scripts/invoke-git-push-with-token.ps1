<#
.SYNOPSIS
    Authenticated git push wrapper (silently uses stored GitHub PAT).

.DESCRIPTION
    Resolves GitHub PAT from Windows Credential Manager and calls git_push.ps1
    with the token available in the environment. This enables silent git operations
    without interactive authentication prompts.

    The token is retrieved during the script run and not logged or persisted after
    the script completes.

    This wrapper maintains the immutability of git_push.ps1 while providing
    credential handling at the orchestration layer.

.PARAMETER Message
    Commit message. If omitted, git_push.ps1 auto-generates one.

.PARAMETER DryRun
    Dry run: show what would be done without performing git operations.

.PARAMETER LogFile
    Optional path to append execution log.

.PARAMETER Force
    If GitHub token is not found in Windows Credential Manager, fall back to
    interactive authentication (requires manual auth prompt). Without -Force,
    missing token will fail the operation.

.EXAMPLE
    .\invoke-git-push-with-token.ps1
    Uses stored GitHub PAT to push all staged changes.

.EXAMPLE
    .\invoke-git-push-with-token.ps1 -Message "feat: add new feature"
    Pushes with explicit message.

.EXAMPLE
    .\invoke-git-push-with-token.ps1 -DryRun -Verbose
    Shows what would be committed without performing git operations.

.NOTES
    Requires:
      - GitHub PAT stored via setup-github-credentials.ps1
      - Python 3.6+ (for token_resolver.py)
      - git installed and on PATH

    The token is retrieved fresh each time (no caching between runs).
    Token is not logged or exposed in output.

#>

[CmdletBinding()]
param(
    [Parameter(Position=0, HelpMessage='Commit message. If omitted, auto-generated from staged changes.')]
    [string]$Message = $null
    ,
    [Parameter(HelpMessage='Dry run: show message without pushing')]
    [switch]$DryRun
    ,
    [Parameter(HelpMessage='Optional path to append execution log')]
    [string]$LogFile = $null
    ,
    [Parameter(HelpMessage='Allow fallback to interactive auth if token not found')]
    [switch]$Force
)

# ============================================================================
# Configuration
# ============================================================================

$SkillsDir = Join-Path (Split-Path -Parent $PSScriptRoot) "src\skills"
$TokenResolverScript = Join-Path $SkillsDir "token_resolver.py"
$GitPushScript = Join-Path $PSScriptRoot "git_push.ps1"
$TokenName = "github_pat"

function Write-Log([string]$msg, [string]$level = "INFO") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [$level] $msg" -ForegroundColor $(
        if ($level -eq "ERROR") { "Red" }
        elseif ($level -eq "WARN") { "Yellow" }
        elseif ($level -eq "INFO") { "Cyan" }
        else { "Gray" }
    )
    
    if ($LogFile -and -not [string]::IsNullOrWhiteSpace($LogFile)) {
        $logTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$logTimestamp] [$level] $msg" | Add-Content -Path $LogFile -Encoding UTF8 -ErrorAction SilentlyContinue
    }
}

function Resolve-Token {
    <#
    .SYNOPSIS
      Call token_resolver.py to get the GitHub PAT.
    #>
    Write-Log "Resolving GitHub token..."
    
    # Find Python interpreter
    $pythonCmd = $null
    foreach ($cmd in @("py", "python3", "python", "python.exe")) {
        try {
            $test = & $cmd --version 2>$null
            if ($test) {
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
    
    # Check token resolver script exists
    if (-not (Test-Path $TokenResolverScript)) {
        Write-Log "Token resolver script not found: $TokenResolverScript" "ERROR"
        return $null
    }
    
    try {
        # Call Python skill to resolve token
        # The skill outputs just the token on success, error on stderr
        $token = & $pythonCmd $TokenResolverScript --token-name $TokenName --resolve 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $token) {
            Write-Log "Token resolved successfully (from environment or Windows Credential Manager)"
            return $token
        } else {
            Write-Log "Failed to resolve token (exit code: $LASTEXITCODE)" "ERROR"
            if (-not $Force) {
                Write-Log "Use -Force to allow interactive authentication" "WARN"
            }
            return $null
        }
    } catch {
        Write-Log "Exception while resolving token: $_" "ERROR"
        return $null
    }
}

function Invoke-GitPush([string]$token, [string]$message) {
    <#
    .SYNOPSIS
      Call git_push.ps1 with token available in environment.
    #>
    # Set token in environment for git credential helper to use
    # GitHub's git credential helpers check GIT_TOKEN or similar
    $env:GITHUB_TOKEN = $token
    
    # Also set GIT_TRACE for debugging if verbose
    if ($VerbosePreference -eq "Continue") {
        $env:GIT_TRACE = "1"
    }
    
    try {
        # Build arguments for git_push.ps1
        $args = @()
        if ($Message) {
            $args += '-Message'
            $args += $Message
        }
        if ($DryRun) {
            $args += '-DryRun'
        }
        if ($LogFile) {
            $args += '-LogFile'
            $args += $LogFile
        }
        
        # Invoke git_push.ps1
        Write-Log "Invoking git_push.ps1..."
        & $GitPushScript @args
        
        $exitCode = $LASTEXITCODE
        return $exitCode
    } finally {
        # Clean up environment
        Remove-Item env:GITHUB_TOKEN -ErrorAction SilentlyContinue
        Remove-Item env:GIT_TRACE -ErrorAction SilentlyContinue
    }
}

# ============================================================================
# Main Flow
# ============================================================================

Write-Log "Starting authenticated git push..."

# Validate git_push.ps1 exists
if (-not (Test-Path $GitPushScript)) {
    Write-Log "git_push.ps1 not found at: $GitPushScript" "ERROR"
    exit 1
}

# Resolve GitHub token
$token = Resolve-Token
if (-not $token) {
    if ($Force) {
        Write-Log "Token not found; falling back to interactive authentication" "WARN"
        Write-Log "Running git_push.ps1 without token (will prompt for auth)"
        & $GitPushScript -Message $Message -DryRun:$DryRun -LogFile $LogFile
        exit $LASTEXITCODE
    } else {
        Write-Log "Token resolution failed. Run setup-github-credentials.ps1 to configure." "ERROR"
        exit 1
    }
}

# Invoke git push with token
$exitCode = Invoke-GitPush -token $token -message $Message

if ($exitCode -eq 0) {
    Write-Log "Git push completed successfully" "INFO"
} else {
    Write-Log "Git push failed with exit code: $exitCode" "ERROR"
}

exit $exitCode
