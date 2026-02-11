# RoadTrip Workspace-Aware PowerShell Profile
# Dynamically detects when you're in the RoadTrip repo and loads workspace-specific functions
# Safe to include in your global $PROFILE - gracefully skips if not in RoadTrip repo

# Try to detect project root dynamically
$ProjectRoot = if ((Test-Path ".\RoadTrip.code-workspace") -and (Test-Path ".\scripts\git_push.ps1")) {
    (Get-Item .).FullName  # Current directory is RoadTrip root
} elseif ((Test-Path "..\RoadTrip.code-workspace") -and (Test-Path "..\scripts\git_push.ps1")) {
    (Get-Item ..).FullName  # Parent directory is RoadTrip root
} else {
    $null  # Not in RoadTrip workspace
}

# Optional PowerShell Profile Configuration for RoadTrip Development
# 
# **IMPORTANT:** Add this to your global $PROFILE file:
#   $roadTripProfile = "G:\repos\AI\RoadTrip\infra\RoadTrip_profile.ps1"
#   if (Test-Path $roadTripProfile) { . $roadTripProfile }
#
# This is SAFE to include in your global profile because:
# - It automatically detects when you're in the RoadTrip workspace
# - It gracefully disables RoadTrip-specific functions in other workspaces
# - Unix-style commands (head, tail, wc, grep) always load
#
# To use:
# 1. Open PowerShell
# 2. Run: $PROFILE (shows path to your profile file)
# 3. Open that file in your editor (create it if it doesn't exist, usually:
#    E:\OneDrive - Personal\OneDrive\Documents\PowerShell\Microsoft.VSCode_profile.ps1)
# 4. Add the code block above
# 5. Reload: . $PROFILE
#
# Then you can use Unix-style commands like:
#   dotnet test ... | head -30
#   dotnet test ... | tail -20
#   (Get-Content file) | wc -l
#   ls | grep pattern
#
# And RoadTrip-specific commands when in RoadTrip workspace:
#   gpush, gpush-dry, gpush-log, bpublish (bp)

# ========== Shell Command Functions ==========
# Equivalent to Unix 'head' command - shows first 10 lines
# Usage: command | head
function head {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [object]$InputObject
    )
    
    $input | Select-Object -First 10
}

# Equivalent to Unix 'tail' command - shows last 10 lines
# Usage: command | tail
function tail {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [object]$InputObject
    )
    
    $input | Select-Object -Last 10
}

# Equivalent to Unix 'wc -l' command - counts lines
# Usage: command | wc
function wc {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [object]$InputObject
    )
    
    @($input) | Measure-Object -Line | Select-Object -ExpandProperty Lines
}

# grep alias - PowerShell equivalent using Select-String
function grep {
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string]$Pattern,
        
        [Parameter(ValueFromPipeline=$true, ValueFromRemainingArguments=$true)]
        [string[]]$InputObject
    )
    
    begin {
        $allInput = @()
    }
    
    process {
        if ($InputObject) {
            $allInput += $InputObject
        }
    }
    
    end {
        if ($allInput) {
            # Try to treat as files first, then as pipeline input
            $files = @()
            $lines = @()
            
            foreach ($item in $allInput) {
                if (Test-Path $item -PathType Leaf) {
                    $files += $item
                } else {
                    $lines += $item
                }
            }
            
            if ($files) {
                Get-Content $files | Select-String -Pattern $Pattern
            } elseif ($lines) {
                $lines | Select-String -Pattern $Pattern
            }
        } else {
            Write-Host "Usage: grep 'pattern' [files]" -ForegroundColor Yellow
            Write-Host "Usage: command | grep 'pattern'" -ForegroundColor Yellow
        }
    }
}

# ========== ProjectRoot Specific Functions ==========
# Quick navigation to project root
function cdqm {
    Set-Location "G:\repos\ProjectRoot"
}

# Quick test commands
function test-fast {
    dotnet test ProjectRoot.slnx --filter "Category!=E2E"
}

function test-e2e {
    dotnet test ProjectRoot.slnx --filter "TestCategory=Smoke"
}

function test-build {
    dotnet build ProjectRoot.slnx -clp:Summary
}

# ========== RoadTrip-Specific Functions (only if in RoadTrip workspace) ==========
if ($ProjectRoot) {
    # Comprehensive git push script with auto-generated commit messages
    function gpush {
        param(
            [Parameter(Position=0)]
            [string]$Message = $null,
            
            [switch]$DryRun,
            [switch]$Log
        )
        
        Push-Location $ProjectRoot
        try {
            $invokeArgs = @()
            if ($Message) { $invokeArgs += $Message }
            if ($DryRun) { $invokeArgs += "-DryRun" }
            if ($Log) { $invokeArgs += "-LogFile"; $invokeArgs += (Join-Path $ProjectRoot "logs\push.log") }
            if ($VerbosePreference -eq "Continue") { $invokeArgs += "-Verbose" }
            
            & ".\scripts\git_push.ps1" @invokeArgs
        }
        finally {
            Pop-Location
        }
    }

    # Convenience wrappers using global scriptblocks to avoid PSUseApprovedVerbs warnings
    # (SuppressMessageAttribute doesn't work on non-Verb-Noun function names)
    $global:gpushdry = { gpush -DryRun -Verbose }
    $global:gpushlog = { gpush -Log -Verbose }
    function gpush-dry { & $global:gpushdry }
    function gpush-log { & $global:gpushlog }

    # Load bpublish function for one-button blog publishing
    $bpublishPath = Join-Path $ProjectRoot "scripts\bpublish-function.ps1"
    if (Test-Path $bpublishPath) {
        . $bpublishPath
    }

    Write-Host "✓ RoadTrip development aliases loaded" -ForegroundColor Green
    Write-Host "  Available commands: head, tail, wc, grep, gpush, gpush-dry, gpush-log, bpublish (bp)" -ForegroundColor Cyan
} else {
    Write-Host "ℹ Not in RoadTrip workspace - RoadTrip-specific commands disabled" -ForegroundColor Gray
}

# Load session logging (workspace-aware)
if ($ProjectRoot) {
    try {
        Push-Location $ProjectRoot
        
        # Load session logging quietly
        if (Test-Path ".\PromptTracking\session-log.ps1") {
            . ".\PromptTracking\session-log.ps1"
            
            if (Test-Path ".\PromptTracking\log-aliases.ps1") {
                . ".\PromptTracking\log-aliases.ps1"
                
                Write-Host "✅ Session logging ready! Try: " -NoNewline -ForegroundColor Green
                Write-Host "log-help" -ForegroundColor Cyan
            }
        }
    }
    finally {
        Pop-Location
    }
}
