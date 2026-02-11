# ============================================================================
# CODING MODE - Development & Implementation
# ============================================================================
# Optimized for daily development work
# - Model: Claude 3.5 Sonnet (fast, accurate code generation)
# - Skills: All available (commit, blog, session logging, etc.)
# - Focus: Git workflows, code quality, skill discovery

$script:ProjectDefaultModel = "claude-3-5-sonnet"
$script:ImageModel = "gpt-4-vision"

# Load development-focused profiles
. (Join-Path $ProjectRoot "infra\git-push-profile.ps1")
. (Join-Path $ProjectRoot "infra\blog-publishing-profile.ps1")
. (Join-Path $ProjectRoot "infra\skills-registry.ps1")

# ============================================================================
# Coding Mode Aliases
# ============================================================================

function show-skills {
    Write-Host "📚 Available Skills:" -ForegroundColor Cyan
    list-skills
}

function show-models {
    Write-Host "🤖 AI Models:" -ForegroundColor Cyan
    Write-Host "  Primary: $script:ProjectDefaultModel" -ForegroundColor Green
    Write-Host "  Image:   $script:ImageModel" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Switch with: use-model 'model-name'" -ForegroundColor Gray
}

function show-coding-help {
    Write-Host "🧑‍💻 CODING MODE - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "GIT & PUSH:" -ForegroundColor Yellow
    Write-Host "  gpush              # Push with auto-generated commit message" -ForegroundColor Gray
    Write-Host "  gpush-dry          # Dry run (see what would be pushed)" -ForegroundColor Gray
    Write-Host "  gpush-log          # Push and log to file" -ForegroundColor Gray
    Write-Host ""
    Write-Host "BLOGGING:" -ForegroundColor Yellow
    Write-Host "  bpublish (bp)      # Publish blog post" -ForegroundColor Gray
    Write-Host ""
    Write-Host "SKILLS & AI:" -ForegroundColor Yellow
    Write-Host "  show-skills        # List available Python skills" -ForegroundColor Gray
    Write-Host "  show-models        # Show available AI models" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NAVIGATION:" -ForegroundColor Yellow
    Write-Host "  cdp                # Go to project root" -ForegroundColor Gray
    Write-Host "  cd-src             # Go to src folder" -ForegroundColor Gray
    Write-Host "  cd-scripts         # Go to scripts folder" -ForegroundColor Gray
    Write-Host ""
    Write-Host "SWITCHING:" -ForegroundColor Yellow
    Write-Host "  use-mode testing   # Switch to testing mode" -ForegroundColor Gray
    Write-Host "  use-mode content   # Switch to content mode" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# Mode Startup
# ============================================================================

Write-Host ""
Write-Host "🧑‍💻 CODING MODE ACTIVATED" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  Model:    $script:ProjectDefaultModel" -ForegroundColor Green
Write-Host "  Focus:    Development, git workflows, skills" -ForegroundColor Green
Write-Host "  Commands: gpush, bpublish, show-skills" -ForegroundColor Green
Write-Host "  Help:     show-coding-help" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
