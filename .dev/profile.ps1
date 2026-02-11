# ============================================================================
# RoadTrip Workspace Profile - Entry Point with Mode Switching
# ============================================================================
# This is the auto-loaded workspace profile for RoadTrip development.
#
# Setup Instructions:
# 1. Add this to your global $PROFILE (usually Microsoft.VSCode_profile.ps1):
#    $devProfile = ".\.dev\profile.ps1"
#    if (Test-Path $devProfile) { . $devProfile }
#
# 2. Store secrets in Windows Credential Manager:
#    cmdkey /add:github_pat /user:github /pass:"your_token"
#    cmdkey /add:openai_key /user:openai /pass:"your_key"
#
# 3. Available modes: use-mode coding | testing | content
#
# ============================================================================

# Detect project root
$ProjectRoot = if ((Test-Path ".\RoadTrip.code-workspace") -and (Test-Path ".\scripts\git_push.ps1")) {
    (Get-Item .).FullName
} elseif ((Test-Path "..\RoadTrip.code-workspace") -and (Test-Path "..\scripts\git_push.ps1")) {
    (Get-Item ..).FullName
} else {
    $null
}

if (-not $ProjectRoot) {
    Write-Host "⚠️  Not in RoadTrip workspace - skipping initialization" -ForegroundColor Gray
    return
}

# Global mode state
$script:CurrentMode = "coding"
$script:AvailableModes = @("coding", "testing", "content")
$script:ProjectDefaultModel = "claude-3-5-sonnet"
$script:ImageModel = "gpt-4-vision"

# ============================================================================
# Load Shared Utilities (always available)
# ============================================================================
. (Join-Path $ProjectRoot "infra\common-profile.ps1")

# ============================================================================
# Load Secrets Securely
# ============================================================================
. (Join-Path $ProjectRoot "infra\load-secrets.ps1")

# ============================================================================
# Mode Switching Infrastructure
# ============================================================================

function use-mode {
    param(
        [Parameter(Position=0)]
        [string]$Mode,
        
        [switch]$List
    )
    
    if ($List) {
        Write-Host "Available modes:" -ForegroundColor Cyan
        foreach ($m in $script:AvailableModes) {
            $indicator = if ($m -eq $script:CurrentMode) { "→" } else { " " }
            Write-Host "  $indicator $m" -ForegroundColor Green
        }
        return
    }
    
    if (-not $Mode) {
        Write-Host "Current mode: $($script:CurrentMode)" -ForegroundColor Cyan
        Write-Host "Usage: use-mode coding | testing | content" -ForegroundColor Gray
        return
    }
    
    if ($Mode -notin $script:AvailableModes) {
        Write-Host "❌ Unknown mode: $Mode" -ForegroundColor Red
        Write-Host "Available: $($script:AvailableModes -join ', ')" -ForegroundColor Gray
        return
    }
    
    # Load new mode
    $modeFile = Join-Path $ProjectRoot ".dev\modes\$Mode.ps1"
    if (-not (Test-Path $modeFile)) {
        Write-Host "❌ Mode file not found: $modeFile" -ForegroundColor Red
        return
    }
    
    . $modeFile
    $script:CurrentMode = $Mode
}

function show-current-mode {
    Write-Host "📍 Current Mode: $($script:CurrentMode)" -ForegroundColor Cyan
    Write-Host "   Model: $($script:ProjectDefaultModel)" -ForegroundColor Gray
    if ($script:ImageModel) {
        Write-Host "   Image: $($script:ImageModel)" -ForegroundColor Gray
    }
}

# ============================================================================
# Quick Navigation
# ============================================================================

function cdp { Set-Location $ProjectRoot }
function cd-dev { Set-Location (Join-Path $ProjectRoot ".dev") }
function cd-infra { Set-Location (Join-Path $ProjectRoot "infra") }
function cd-src { Set-Location (Join-Path $ProjectRoot "src") }
function cd-scripts { Set-Location (Join-Path $ProjectRoot "scripts") }
function cd-prompts { Set-Location (Join-Path $ProjectRoot "PromptTracking") }

Set-Alias -Name cdprj -Value cdp -Force
Set-Alias -Name cdd -Value cd-dev -Force

# ============================================================================
# Initialize Default Mode (directly, not through use-mode function)
# ============================================================================

# Load default mode (coding) directly to avoid scope issues
$defaultModeFile = Join-Path $ProjectRoot ".dev\modes\coding.ps1"
if (Test-Path $defaultModeFile) {
    . $defaultModeFile
} else {
    Write-Host "❌ Default mode file not found: $defaultModeFile" -ForegroundColor Red
}

Write-Host ""
Write-Host "💡 Quick commands:" -ForegroundColor Cyan
Write-Host "   use-mode -List        # Show available modes" -ForegroundColor Gray
Write-Host "   use-mode testing      # Switch to testing mode" -ForegroundColor Gray
Write-Host "   use-mode content      # Switch to content mode" -ForegroundColor Gray
Write-Host "   show-current-mode     # Show current configuration" -ForegroundColor Gray
Write-Host "   cdp, cd-dev, cd-src   # Navigation shortcuts" -ForegroundColor Gray
Write-Host ""
