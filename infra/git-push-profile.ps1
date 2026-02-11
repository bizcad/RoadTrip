# ============================================================================
# Git Push Profile - Version Control Aliases
# ============================================================================
# Provides convenient wrappers for git push operations
# Part of CODING and TESTING modes
# ============================================================================

$ProjectRoot = if ($ProjectRoot) { $ProjectRoot } else { (Get-Item .).FullName }

# ============================================================================
# Git Push Functions
# ============================================================================

function gpush {
    <#
    .SYNOPSIS
    Push changes with auto-generated or custom commit message
    
    .PARAMETER Message
    Custom commit message (optional - auto-generated if not provided)
    
    .PARAMETER DryRun
    Show what would be pushed without actually pushing
    
    .PARAMETER Log
    Log the push operation to file
    #>
    
    param(
        [Parameter(Position=0)]
        [string]$Message,
        
        [switch]$DryRun,
        [switch]$Log
    )
    
    Push-Location $ProjectRoot
    try {
        # Build parameters explicitly for external script
        $scriptArgs = @()
        if ($Message) { $scriptArgs += $Message }
        if ($DryRun) { $scriptArgs += "-DryRun" }
        if ($Log) { $scriptArgs += "-Log" }
        
        if (Test-Path ".\scripts\git_push.ps1") {
            & ".\scripts\git_push.ps1" @scriptArgs
        } else {
            Write-Host "❌ Git push script not found at .\scripts\git_push.ps1" -ForegroundColor Red
        }
    }
    finally {
        Pop-Location
    }
}

# ============================================================================
# Convenience Wrappers
# ============================================================================

function gpush-dry {
    <#
    .SYNOPSIS
    Dry run - see what would be pushed without actually pushing
    #>
    gpush -DryRun -Verbose
}

function gpush-log {
    <#
    .SYNOPSIS
    Push and log to file
    #>
    gpush -Log -Verbose
}

# ============================================================================
# Git Status & Info
# ============================================================================

function git-status-quick {
    <#
    .SYNOPSIS
    Show quick git status summary
    #>
    Push-Location $ProjectRoot
    try {
        git status --short
    }
    finally {
        Pop-Location
    }
}

function git-log-recent {
    <#
    .SYNOPSIS
    Show recent commits
    #>
    param([int]$Count = 10)
    
    Push-Location $ProjectRoot
    try {
        git log --oneline -n $Count
    }
    finally {
        Pop-Location
    }
}

function git-branch-info {
    <#
    .SYNOPSIS
    Show current branch and remote tracking
    #>
    Push-Location $ProjectRoot
    try {
        $branch = git rev-parse --abbrev-ref HEAD
        $remote = git config branch.$branch.remote
        
        Write-Host "Current Branch:" -ForegroundColor Cyan
        Write-Host "  Local:  $branch" -ForegroundColor Green
        if ($remote) {
            Write-Host "  Remote: $remote" -ForegroundColor Green
            Write-Host "  Tracking: $remote/$branch" -ForegroundColor Green
        } else {
            Write-Host "  Remote: (not set up)" -ForegroundColor Yellow
        }
    }
    finally {
        Pop-Location
    }
}

Set-Alias -Name gs -Value git-status-quick -Force
Set-Alias -Name gl -Value git-log-recent -Force
Set-Alias -Name gb -Value git-branch-info -Force

Write-Host "✓ Git push profile loaded (gpush, gpush-dry, gpush-log)" -ForegroundColor Green
