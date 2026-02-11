# ============================================================================
# TESTING MODE - QA & Test Automation
# ============================================================================
# Optimized for testing and quality assurance
# - Model: GPT-4 (more deterministic for automated testing)
# - Skills: Testing-focused only
# - Focus: Test execution, CI/CD simulation, regression testing

$script:ProjectDefaultModel = "gpt-4"
$script:ImageModel = $null  # Not needed for testing

# Load testing-focused profiles
. (Join-Path $ProjectRoot "infra\testing-profile.ps1")

# ============================================================================
# Testing Mode Aliases
# ============================================================================

function show-test-config {
    Write-Host "📋 Test Configuration:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Model:           $script:ProjectDefaultModel" -ForegroundColor Green
    Write-Host "  Test Framework:  Python unittest" -ForegroundColor Green
    Write-Host "  Coverage:        Enabled" -ForegroundColor Green
    Write-Host ""
}

function show-testing-help {
    Write-Host "🧪 TESTING MODE - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "TEST EXECUTION:" -ForegroundColor Yellow
    Write-Host "  test-unit          # Run unit tests only" -ForegroundColor Gray
    Write-Host "  test-integration   # Run integration tests" -ForegroundColor Gray
    Write-Host "  test-e2e           # Run end-to-end tests" -ForegroundColor Gray
    Write-Host "  test-all           # Run all tests" -ForegroundColor Gray
    Write-Host ""
    Write-Host "COVERAGE & REPORTING:" -ForegroundColor Yellow
    Write-Host "  test-coverage      # Generate coverage report" -ForegroundColor Gray
    Write-Host "  test-report        # Show latest test report" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NAVIGATION:" -ForegroundColor Yellow
    Write-Host "  cdp                # Go to project root" -ForegroundColor Gray
    Write-Host "  cd-scripts         # Go to scripts folder" -ForegroundColor Gray
    Write-Host ""
    Write-Host "SWITCHING:" -ForegroundColor Yellow
    Write-Host "  use-mode coding    # Switch to coding mode" -ForegroundColor Gray
    Write-Host "  use-mode content   # Switch to content mode" -ForegroundColor Gray
    Write-Host ""
}

# Test command placeholders (update paths to match your test structure)
function test-unit {
    Write-Host "🧪 Running unit tests..." -ForegroundColor Yellow
    if (Test-Path ".\tests\unit") {
        python -m pytest .\tests\unit -v
    } else {
        Write-Host "⚠️  Unit tests not found in .\tests\unit" -ForegroundColor Gray
    }
}

function test-integration {
    Write-Host "🧪 Running integration tests..." -ForegroundColor Yellow
    if (Test-Path ".\tests\integration") {
        python -m pytest .\tests\integration -v
    } else {
        Write-Host "⚠️  Integration tests not found in .\tests\integration" -ForegroundColor Gray
    }
}

function test-e2e {
    Write-Host "🧪 Running end-to-end tests..." -ForegroundColor Yellow
    if (Test-Path ".\tests\e2e") {
        python -m pytest .\tests\e2e -v
    } else {
        Write-Host "⚠️  E2E tests not found in .\tests\e2e" -ForegroundColor Gray
    }
}

function test-all {
    Write-Host "🧪 Running all tests..." -ForegroundColor Yellow
    if (Test-Path ".\tests") {
        python -m pytest .\tests -v --cov=src
    } else {
        Write-Host "⚠️  Tests folder not found" -ForegroundColor Gray
    }
}

function test-coverage {
    Write-Host "📊 Generating coverage report..." -ForegroundColor Yellow
    python -m pytest .\tests --cov=src --cov-report=html --cov-report=term
    Write-Host "✅ Coverage report generated in htmlcov/index.html" -ForegroundColor Green
}

# ============================================================================
# Mode Startup
# ============================================================================

Write-Host ""
Write-Host "🧪 TESTING MODE ACTIVATED" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  Model:    $script:ProjectDefaultModel" -ForegroundColor Green
Write-Host "  Focus:    QA, test automation, regression testing" -ForegroundColor Green
Write-Host "  Commands: test-unit, test-integration, test-e2e, test-all" -ForegroundColor Green
Write-Host "  Help:     show-testing-help" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
