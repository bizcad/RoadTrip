# Test Framework for Autonomous Git-Push Skill
# Phase 1 Validation Testing

[CmdletBinding()]
param(
    [ValidateSet('all', 'discovery', 'auth', 'rules', 'decision', 'telemetry')]
    [string]$TestSuite = 'all'
)

# Configuration
$SkillsRoot = "$(Split-Path $PSScriptRoot)\skills"
$TestResultsDir = "$(Split-Path $PSScriptRoot)\tests\results"
$TestLogFile = Join-Path $TestResultsDir "test-run-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

if (-not (Test-Path $TestResultsDir)) {
    New-Item -ItemType Directory -Path $TestResultsDir | Out-Null
}

# Utilities
function Write-TestLog {
    param([string]$Message, [string]$Level = 'INFO')
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $TestLogFile -Value $logEntry
}

function Start-TestSuite {
    param([string]$Name)
    Write-TestLog "========== TEST SUITE: $Name ==========" WARN
    Write-Host ""
}

function Test-SkillFileExists {
    param([string]$SkillName, [string]$FileName)
    if ($SkillName -eq ".") {
        $path = Join-Path $SkillsRoot $FileName
    } else {
        $path = Join-Path -Path $SkillsRoot -ChildPath $SkillName | Join-Path -ChildPath $FileName
    }
    $exists = Test-Path $path
    if ($exists) {
        Write-TestLog "  [PASS] $SkillName/$FileName exists"
    }
    else {
        Write-TestLog "  [FAIL] $SkillName/$FileName missing" FAIL
    }
    return $exists
}

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if ($Condition) {
        Write-TestLog "    [PASS] $Message"
        return $true
    }
    else {
        Write-TestLog "    [FAIL] $Message" FAIL
        return $false
    }
}

# TEST SUITE 1: Discovery
function Invoke-DiscoveryTests {
    Start-TestSuite "Skill Discovery"
    
    $allPass = $true
    
    Write-Host "Root Documentation:"
    $allPass = (Test-SkillFileExists "." "CLAUDE.md") -and $allPass
    
    Write-Host "`ngit-push-autonomous Skill:"
    $allPass = (Test-SkillFileExists "git-push-autonomous" "SKILL.md") -and $allPass
    $allPass = (Test-SkillFileExists "git-push-autonomous" "CLAUDE.md") -and $allPass
    $allPass = (Test-SkillFileExists "git-push-autonomous" "safety-rules.md") -and $allPass
    $allPass = (Test-SkillFileExists "git-push-autonomous" "decision-tree.md") -and $allPass
    $allPass = (Test-SkillFileExists "git-push-autonomous" "examples.md") -and $allPass
    
    Write-Host "`nSpecialist Skills:"
    $allPass = (Test-SkillFileExists "auth-validator" "SKILL.md") -and $allPass
    $allPass = (Test-SkillFileExists "auth-validator" "CLAUDE.md") -and $allPass
    $allPass = (Test-SkillFileExists "rules-engine" "SKILL.md") -and $allPass
    $allPass = (Test-SkillFileExists "rules-engine" "CLAUDE.md") -and $allPass
    $allPass = (Test-SkillFileExists "telemetry-logger" "SKILL.md") -and $allPass
    $allPass = (Test-SkillFileExists "telemetry-logger" "CLAUDE.md") -and $allPass
    
    Write-Host ""
    return $allPass
}

# TEST SUITE 2: Auth Validator
function Invoke-AuthValidatorTests {
    Start-TestSuite "Auth Validator Logic"
    
    $allPass = $true
    
    Write-Host "Test: Git is installed"
    $gitExists = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    $allPass = (Assert-True $gitExists "git command found") -and $allPass
    
    Write-Host "`nTest: Git user.name configured"
    $userName = & git config user.name 2>$null
    $hasUserName = -not [string]::IsNullOrWhiteSpace($userName)
    $allPass = (Assert-True $hasUserName "user.name is set") -and $allPass
    
    Write-Host "`nTest: Git user.email configured"
    $userEmail = & git config user.email 2>$null
    $hasUserEmail = -not [string]::IsNullOrWhiteSpace($userEmail)
    $allPass = (Assert-True $hasUserEmail "user.email is set") -and $allPass
    
    Write-Host "`nTest: Git repository found"
    $repoRoot = & git rev-parse --show-toplevel 2>$null
    $isRepo = $LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($repoRoot)
    $allPass = (Assert-True $isRepo "Inside a git repository") -and $allPass
    
    if ($isRepo) {
        Write-Host "`nTest: Origin remote exists"
        $origin = & git remote get-url origin 2>$null
        $hasOrigin = $LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($origin)
        $allPass = (Assert-True $hasOrigin "origin remote configured") -and $allPass
    }
    
    Write-Host ""
    return $allPass
}

# TEST SUITE 3: Rules Engine
function Invoke-RulesEngineTests {
    Start-TestSuite "Rules Engine Logic"
    
    $allPass = $true
    $safetyRulesPath = Join-Path -Path $SkillsRoot -ChildPath "git-push-autonomous" | Join-Path -ChildPath "safety-rules.md"
    
    if (Test-Path $safetyRulesPath) {
        $content = Get-Content $safetyRulesPath -Raw
        
        Write-Host "Test: Exclusion patterns defined"
        $hasBlocked = $content -match 'blocked_files|blocked_patterns'
        $allPass = (Assert-True $hasBlocked "Exclusion rules are documented") -and $allPass
        
        Write-Host "`nTest: .env in blocked list"
        $hasEnvBlock = $content -match '\.env'
        $allPass = (Assert-True $hasEnvBlock ".env is blocked") -and $allPass
        
        Write-Host "`nTest: node_modules in blocked list"
        $hasNodeBlock = $content -match 'node_modules'
        $allPass = (Assert-True $hasNodeBlock "node_modules is blocked") -and $allPass
        
        Write-Host "`nTest: Size limits documented"
        $hasSizeLimit = $content -match 'size|Size|MB|mb'
        $allPass = (Assert-True $hasSizeLimit "File size limits documented") -and $allPass
    }
    else {
        Write-TestLog "ERROR: safety-rules.md not found" FAIL
        $allPass = $false
    }
    
    Write-Host ""
    return $allPass
}

# TEST SUITE 4: Decision Flow
function Invoke-DecisionFlowTests {
    Start-TestSuite "Decision Flow (Decision Tree)"
    
    $allPass = $true
    $decisionTreePath = Join-Path -Path $SkillsRoot -ChildPath "git-push-autonomous" | Join-Path -ChildPath "decision-tree.md"
    
    if (Test-Path $decisionTreePath) {
        $content = Get-Content $decisionTreePath -Raw
        
        Write-Host "Test: Decision tree has entry point"
        $hasStart = $content -match 'START|STEP 1'
        $allPass = (Assert-True $hasStart "Decision tree starts with STEP 1") -and $allPass
        
        Write-Host "`nTest: Auth validation step exists"
        $hasAuth = $content -match 'auth-validator|Auth'
        $allPass = (Assert-True $hasAuth "Decision tree calls auth-validator") -and $allPass
        
        Write-Host "`nTest: Rules validation step exists"
        $hasRules = $content -match 'rules-engine|Rules'
        $allPass = (Assert-True $hasRules "Decision tree calls rules-engine") -and $allPass
        
        Write-Host "`nTest: Telemetry logging step exists"
        $hasTelemetry = $content -match 'telemetry|Telemetry'
        $allPass = (Assert-True $hasTelemetry "Decision tree logs telemetry") -and $allPass
        
        Write-Host "`nTest: Exit codes documented"
        $hasExitCodes = $content -match 'exit|Exit|EXIT|code'
        $allPass = (Assert-True $hasExitCodes "Exit codes are documented") -and $allPass
    }
    else {
        Write-TestLog "ERROR: decision-tree.md not found" FAIL
        $allPass = $false
    }
    
    Write-Host ""
    return $allPass
}

# TEST SUITE 5: Telemetry
function Invoke-TelemetryTests {
    Start-TestSuite "Telemetry Logging Structure"
    
    $allPass = $true
    $telemetryPath = Join-Path -Path $SkillsRoot -ChildPath "telemetry-logger" | Join-Path -ChildPath "SKILL.md"
    
    if (Test-Path $telemetryPath) {
        $content = Get-Content $telemetryPath -Raw
        
        Write-Host "Test: Telemetry logs decisions"
        $logsDecisions = $content -match 'decision|Decision|approved|blocked'
        $allPass = (Assert-True $logsDecisions "Telemetry records decisions") -and $allPass
        
        Write-Host "`nTest: Telemetry includes confidence scores"
        $hasConfidence = $content -match 'confidence|Confidence'
        $allPass = (Assert-True $hasConfidence "Telemetry includes confidence") -and $allPass
        
        Write-Host "`nTest: Telemetry log format defined"
        $hasFormat = $content -match 'JSON|json|format|Format|Input|Output'
        $allPass = (Assert-True $hasFormat "Log format is specified") -and $allPass
    }
    else {
        Write-TestLog "ERROR: telemetry-logger SKILL.md not found" FAIL
        $allPass = $false
    }
    
    Write-Host ""
    return $allPass
}

# MAIN EXECUTION
Write-TestLog "======== AUTONOMOUS GIT-PUSH SKILL: PHASE 1 VALIDATION ========" WARN
Write-TestLog "Test Framework Start: $(Get-Date)" WARN

$results = @{
    discovery = $false
    auth = $false
    rules = $false
    decision = $false
    telemetry = $false
}

switch ($TestSuite) {
    'all' {
        $results.discovery = Invoke-DiscoveryTests
        $results.auth = Invoke-AuthValidatorTests
        $results.rules = Invoke-RulesEngineTests
        $results.decision = Invoke-DecisionFlowTests
        $results.telemetry = Invoke-TelemetryTests
    }
    'discovery' { $results.discovery = Invoke-DiscoveryTests }
    'auth' { $results.auth = Invoke-AuthValidatorTests }
    'rules' { $results.rules = Invoke-RulesEngineTests }
    'decision' { $results.decision = Invoke-DecisionFlowTests }
    'telemetry' { $results.telemetry = Invoke-TelemetryTests }
}

# Summary
Write-TestLog "======== TEST SUMMARY ========" WARN
$passCount = ($results.Values | Where-Object { $_ -eq $true }).Count
$totalCount = $results.Count
$passRate = [math]::Round(($passCount / $totalCount) * 100, 1)

$summaryLevel = if ($passCount -eq $totalCount) { 'PASS' } else { 'WARN' }
Write-TestLog "Passed: $passCount / $totalCount ($passRate%)" $summaryLevel
Write-TestLog "Test Results Log: $TestLogFile" INFO

Write-Host ""
Write-Host "Results:" -ForegroundColor Cyan
foreach ($test in $results.GetEnumerator()) {
    $status = if ($test.Value) { "[PASS]" } else { "[FAIL]" }
    Write-Host "  $status $($test.Name)"
}

Write-TestLog "Test Framework End: $(Get-Date)" WARN
Write-Host ""
Write-Host "Full log saved to: $TestLogFile" -ForegroundColor Yellow

$exitCode = if ($passCount -eq $totalCount) { 0 } else { 1 }
exit $exitCode
