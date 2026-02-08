<#
.SYNOPSIS
    Invoke the commit-message skill to generate a semantic commit message.

.DESCRIPTION
    Calls the commit_message.py skill to generate a commit message using
    Tier 1→2→3 strategy (deterministic → LLM fallback → user override).
    
    The skill stages are:
    - Tier 1 ($0): Deterministic heuristics (90% of commits)
    - Tier 2 (~$0.001-0.01): Claude API fallback (10% of commits)
    - Tier 3 ($0): User override with -Message parameter
    
    Output can be copied and passed to git_push.ps1 -Message "..."

.PARAMETER StagedFiles
    List of file paths to include in message generation.
    Supports wildcards (e.g., "src/*.py").
    
.PARAMETER DiffFile
    Path to a unified diff file (optional).
    Helps Tier 2 LLM generate more accurate messages.

.PARAMETER UserMessage
    User-provided commit message (Tier 3 override).
    If provided, bypasses Tier 1 and 2 entirely.

.PARAMETER Config
    Path to commit-strategy.yaml. Default: config/commit-strategy.yaml

.PARAMETER DryRun
    Do not call external APIs; show what would happen.
    Useful for testing without incurring costs.

.PARAMETER AsJson
    Output result as JSON instead of plain text.

.PARAMETER Verbose
    Show detailed output including reasoning and costs.

.EXAMPLE
    .\invoke-commit-message.ps1 -StagedFiles "src/auth.py", "src/models.py"
    Generates message for two source files.

.EXAMPLE
    .\invoke-commit-message.ps1 -StagedFiles "docs/*.md"
    Generates message for all modified .md files in docs.

.EXAMPLE
    .\invoke-commit-message.ps1 -StagedFiles "src" -DryRun -Verbose
    Shows what would happen without calling APIs.

.EXAMPLE
    .\invoke-commit-message.ps1 -UserMessage "feat: custom message"
    Uses explicit message (Tier 3 override).

.EXAMPLE
    .\invoke-commit-message.ps1 -StagedFiles "src/" -DiffFile ./changes.patch -AsJson
    Generates message with diff context, outputs as JSON.

.OUTPUTS
    Plain text commit message (or JSON if -AsJson)
    Messages can be copied and used with:
      .\git_push.ps1 -Message "the generated message"

.NOTES
    Requires:
      - Python 3.8+
      - PyYAML: pip install pyyaml
      - anthropic (optional, for Tier 2): pip install anthropic
    
    The skill is immutable; git_push.ps1 is untouched.
    Integration testing happens when you manually verify the message.

#>

[CmdletBinding()]
param(
    [Parameter(Position=0, ValueFromRemainingArguments=$true, HelpMessage='File paths to include')]
    [string[]]$StagedFiles = @(),
    
    [Parameter(HelpMessage='Path to unified diff file')]
    [string]$DiffFile = $null,
    
    [Parameter(HelpMessage='User-provided message (Tier 3 override)')]
    [string]$UserMessage = $null,
    
    [Parameter(HelpMessage='Path to commit-strategy.yaml')]
    [string]$Config = 'config/commit-strategy.yaml',
    
    [Parameter(HelpMessage='Do not call external APIs')]
    [switch]$DryRun,
    
    [Parameter(HelpMessage='Output as JSON')]
    [switch]$AsJson
)

# ============================================================================
# Validation
# ============================================================================

if (@($StagedFiles).Count -eq 0 -and [string]::IsNullOrWhiteSpace($UserMessage)) {
    Write-Host "Error: Must provide -StagedFiles or -UserMessage" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\invoke-commit-message.ps1 -StagedFiles src/*.py"
    Write-Host "  .\invoke-commit-message.ps1 -UserMessage 'feat: custom message'"
    Write-Host "  .\invoke-commit-message.ps1 -StagedFiles src/ -DryRun"
    exit 1
}

# Get repo root (parent of scripts directory)
$repoRoot = Split-Path -Path $PSScriptRoot -Parent

# Check skill file exists
$skillPath = Join-Path $repoRoot 'src' 'skills' 'commit_message.py'
if (-not (Test-Path $skillPath)) {
    Write-Host "Error: Skill not found at $skillPath" -ForegroundColor Red
    exit 1
}
$pythonCmd = $null
foreach ($py in @('py', 'python3', 'python', 'python.exe')) {
    try {
        $version = & $py --version 2>$null
        if ($version) {
            $pythonCmd = $py
            break
        }
    }
    catch { }
}

if ([string]::IsNullOrWhiteSpace($pythonCmd)) {
    Write-Host "Error: Python not found on PATH" -ForegroundColor Red
    Write-Host "Install Python 3.8+ from https://www.python.org/"
    exit 1
}

# ============================================================================
# Build Python Command
# ============================================================================

$pythonArgs = @($skillPath)

# Add staged files
if (@($StagedFiles).Count -gt 0) {
    $pythonArgs += '--staged-files'
    $pythonArgs += $StagedFiles
}

# Add user message if provided
if (-not [string]::IsNullOrWhiteSpace($UserMessage)) {
    $pythonArgs += '--user-message'
    $pythonArgs += $UserMessage
}

# Add config path
$pythonArgs += '--config'
$pythonArgs += $Config

# Add flags
if ($DryRun) {
    $pythonArgs += '--dry-run'
}

if ($AsJson) {
    $pythonArgs += '--json'
}

# ============================================================================
# Execute Skill
# ============================================================================

Write-Verbose "Invoking: $pythonCmd $($pythonArgs -join ' ')"

try {
    & $pythonCmd @pythonArgs
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        exit $exitCode
    }
}
catch {
    Write-Host "Error executing skill: $_" -ForegroundColor Red
    exit 1
}
