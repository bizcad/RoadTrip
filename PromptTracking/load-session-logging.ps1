# Load Session Logging - Run this to initialize session logging in current terminal
# Usage: . .\PromptTracking\load-session-logging.ps1

Write-Host "🔄 Loading session logging system..." -ForegroundColor Cyan

# Get the script directory and navigate to project root
$scriptDir = $PSScriptRoot
$projectRoot = Split-Path -Parent $scriptDir

# Change to project root
Push-Location $projectRoot

try {
    # Load session logging system
    $sessionLogPath = ".\PromptTracking\session-log.ps1"
    $aliasesPath = ".\PromptTracking\log-aliases.ps1"

    if (Test-Path $sessionLogPath) {
        Write-Host "📝 Loading session logging functions..." -ForegroundColor Yellow

        # Load main session logging functions
        . $sessionLogPath

        # Load command aliases
        if (Test-Path $aliasesPath) {
            . $aliasesPath
            Write-Host ""
            Write-Host "✅ Session logging system loaded successfully!" -ForegroundColor Green
            Write-Host "💡 Try 'log-help' to see all available commands!" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️  Session log aliases not found at: $aliasesPath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Session log script not found at: $sessionLogPath" -ForegroundColor Yellow
        Write-Host "   Make sure the PromptTracking folder contains session-log.ps1" -ForegroundColor Gray
    }
}
finally {
    # Return to original location
    Pop-Location
}
