# Session Log Aliases - Source this file to get simple commands
# Usage: . .\PromptTracking\log-aliases.ps1

# Simple function aliases for session logging
function log { 
    & "$PSScriptRoot\session-log.ps1" @args 
}

function logs { 
    & "$PSScriptRoot\session-log.ps1" -Section @args 
}

function logc { 
    & "$PSScriptRoot\session-log.ps1" -CodeBlock @args 
}

function logt([string]$title) { 
    & "$PSScriptRoot\session-log.ps1" -Section -Title $title 
}

function logp { 
    & "$PSScriptRoot\session-log.ps1" -Section -Title "Prompt:" -H1 -Markers Prompt 
}

function logr { 
    & "$PSScriptRoot\session-log.ps1" -Section -Title "Response:" -H1 -Markers Response 
}

# General note with markers (H1 + Note markers)
function logn {
    & "$PSScriptRoot\session-log.ps1" -Section -Title "Note:" -H1 -Markers Note
}

# Show available commands (approved verb)
function Show-LogHelp {
    Write-Host "Session Log Aliases:" -ForegroundColor Green
    Write-Host "  log          - Append clipboard with timestamp" -ForegroundColor Yellow
    Write-Host "  logs         - Append clipboard as section" -ForegroundColor Yellow  
    Write-Host "  logc         - Append clipboard as code block section" -ForegroundColor Yellow
    Write-Host "  logt 'title' - Append clipboard as section with custom title" -ForegroundColor Yellow
    Write-Host "  logp         - Append clipboard as 'Prompt:' section" -ForegroundColor Yellow
    Write-Host "  logr         - Append clipboard as 'Response:' section" -ForegroundColor Yellow
    Write-Host "  logn         - Append clipboard as 'Note:' section with markers" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  log" -ForegroundColor Cyan
    Write-Host "  logs" -ForegroundColor Cyan
    Write-Host "  logc" -ForegroundColor Cyan
    Write-Host "  logt 'Bug Fix'" -ForegroundColor Cyan
    Write-Host "  logp" -ForegroundColor Cyan
    Write-Host "  logr" -ForegroundColor Cyan
    Write-Host "  logn" -ForegroundColor Cyan
}

# Back-compat alias for previous helper name
Set-Alias -Name log-help -Value Show-LogHelp -Force