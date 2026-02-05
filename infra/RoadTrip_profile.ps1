# ProjectRoot PowerShell Profile
# This automatically loads when PowerShell starts in this workspace

$ProjectRoot = "G:\repos\AI\RoadTrip"

# Optional PowerShell Profile Configuration for ProjectRoot Development
# Add these aliases and functions to your PowerShell profile to enable Unix-style commands
#
# To use:
# 1. Open PowerShell
# 2. Run: $PROFILE (shows path to your profile file)
# 3. Open that file in your editor (create it if it doesn't exist)
# 4. Add the contents of this file to your profile
# 5. Reload: . $PROFILE
#
# Then you can use Unix-style commands like:
#   dotnet test ... | head -30
#   dotnet test ... | tail -20
#   (Get-Content file) | wc -l

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

# ========== RoadTrip Git Push Wrapper ==========
# Comprehensive git push script with auto-generated commit messages
function gpush {
    param(
        [Parameter(Position=0)]
        [string]$Message = $null,
        
        [switch]$DryRun,
        [switch]$Log
    )
    
    $scriptPath = Join-Path $ProjectRoot "scripts\git_push.ps1"
    if (-not (Test-Path $scriptPath)) {
        Write-Host "Error: git_push.ps1 not found at $scriptPath" -ForegroundColor Red
        return
    }
    
    $args = @("-DryRun:$DryRun")
    if ($Message) { $args += "-Message", $Message }
    if ($Log) { $args += "-LogFile", (Join-Path $ProjectRoot "logs\push.log") }
    if ($VerbosePreference -eq "Continue") { $args += "-Verbose" }
    
    & $scriptPath @args
}

# Convenience alias: dry-run with verbose output
function gpush-dry {
    gpush -DryRun -Verbose
}

# Convenience alias: push with logging enabled
function gpush-log {
    gpush -Log -Verbose
}

# Write confirmation message
Write-Host "✓ RoadTrip development aliases loaded" -ForegroundColor Green
Write-Host "  Available commands: head, tail, wc, grep, gpush, gpush-dry, gpush-log" -ForegroundColor Cyan

# Load session logging
# Only load if we're in the ProjectRoot directory
if ((Get-Location).Path -like "*RoadTrip*") {
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
