# ============================================================================
# Testing Profile - Test Automation & QA
# ============================================================================
# Testing-focused functions and utilities
# Loaded exclusively in TESTING mode
# ============================================================================

$ProjectRoot = if ($ProjectRoot) { $ProjectRoot } else { (Get-Item .).FullName }

# ============================================================================
# Test Discovery
# ============================================================================

function test-discover {
    <#
    .SYNOPSIS
    Discover available tests in the project
    #>
    Write-Host "🔍 Discovering tests..." -ForegroundColor Cyan
    
    $testDirs = @("tests", "test", "spec", "specs")
    $found = $false
    
    foreach ($dir in $testDirs) {
        $testPath = Join-Path $ProjectRoot $dir
        if (Test-Path $testPath) {
            Write-Host "Found: $testPath" -ForegroundColor Green
            Get-ChildItem $testPath -Filter "test_*.py" -o -Filter "*_test.py" -Recurse | 
            ForEach-Object { Write-Host "  • $($_.FullName)" -ForegroundColor Gray }
            $found = $true
        }
    }
    
    if (-not $found) {
        Write-Host "No test directories found" -ForegroundColor Yellow
    }
}

# ============================================================================
# Python Test Runners (if pytest is available)
# ============================================================================

function test-check-pytest {
    <#
    .SYNOPSIS
    Check if pytest is available
    #>
    try {
        $result = py -m pytest --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pytest available: $result" -ForegroundColor Green
            return $true
        }
    }
    catch { }
    
    Write-Host "❌ pytest not found. Install with: py -m pip install pytest pytest-cov" -ForegroundColor Red
    return $false
}

function test-verbose {
    <#
    .SYNOPSIS
    Run tests with verbose output
    #>
    if (Test-Path ".\tests") {
        python -m pytest .\tests -vv --tb=short
    } else {
        Write-Host "Tests directory not found" -ForegroundColor Yellow
    }
}

function test-markers {
    <#
    .SYNOPSIS
    List available pytest markers
    #>
    python -m pytest --markers
}

# ============================================================================
# Test Reporting
# ============================================================================

function test-report {
    <#
    .SYNOPSIS
    Show latest test report
    #>
    $reportPath = Join-Path $ProjectRoot ".test-results\latest.xml"
    
    if (Test-Path $reportPath) {
        Write-Host "📊 Latest Test Results:" -ForegroundColor Cyan
        (Get-Content $reportPath | Select-String "tests|failures|errors" | head -10)
    } else {
        Write-Host "No test report found" -ForegroundColor Yellow
    }
}

function test-coverage-html {
    <#
    .SYNOPSIS
    Generate and open HTML coverage report
    #>
    Write-Host "📊 Generating coverage report..." -ForegroundColor Yellow
    python -m pytest .\tests --cov=src --cov-report=html
    
    if (Test-Path ".\htmlcov\index.html") {
        Write-Host "✅ Coverage report generated" -ForegroundColor Green
        Start-Process ".\htmlcov\index.html"
    }
}

# ============================================================================
# Helper Aliases
# ============================================================================

Set-Alias -Name discover-tests -Value test-discover -Force
Set-Alias -Name td -Value test-discover -Force

Write-Host "✓ Testing profile loaded" -ForegroundColor Green
