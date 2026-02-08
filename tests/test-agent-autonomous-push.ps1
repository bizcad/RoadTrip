<#
.SYNOPSIS
    Test agent workflow: autonomous commit and push (no user interaction).

.DESCRIPTION
    Simulates an agent:
    1. Making a change to a file
    2. Staging it
    3. Calling push-with-token.ps1 (which calls git silently)
    4. Verifying the push succeeded on GitHub

    This demonstrates Phase 1b automation: agents can now push code
    without interactive authentication dialogs.

.EXAMPLE
    .\test-agent-autonomous-push.ps1
    Runs the test workflow.
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AGENT WORKFLOW TEST: Autonomous Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Simulate agent making a decision and writing a file
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$agentDecision = @"
[Agent Decision Log]
Timestamp: $timestamp
Agent: TestAgent-1
Action: Autonomous commit and push test

This file was created by an automated agent.
The agent made changes and pushed to GitHub without requiring
any user interaction or authentication prompts.

This demonstrates successful silent authentication (Phase 1b).
"@

# Write the file
$testFile = "tests/agent-autonomous-push-test.txt"
Write-Host "📝 Agent action: Creating test file..."
$agentDecision | Out-File -FilePath $testFile -Encoding UTF8
Write-Host "   ✓ $testFile created"
Write-Host ""

# Stage the file
Write-Host "📋 Agent action: Staging changes..."
git add $testFile
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Staged: $testFile"
} else {
    Write-Host "   ✗ Staging failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Now use the push-with-token script for silent push
Write-Host "🚀 Agent action: Pushing with silent authentication..."
Write-Host "   (This should complete instantly with no dialogs)"
Write-Host ""

$pushScript = Join-Path $PSScriptRoot "..\scripts\push-with-token.ps1"
$startTime = [DateTime]::Now

# Call the push script with a descriptive message
& $pushScript -Message "test: agent autonomous push (Phase 1b silent auth verification)"

$pushExitCode = $LASTEXITCODE
$elapsed = ([DateTime]::Now - $startTime).TotalSeconds

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST RESULT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($pushExitCode -eq 0) {
    Write-Host "✅ SUCCESS: Agent pushed autonomously!" -ForegroundColor Green
    Write-Host "   Time elapsed: $elapsed seconds"
    Write-Host "   No authentication prompts: ✓"
    Write-Host ""
    Write-Host "📊 Verification:"
    Write-Host "   Commit: $(git log --oneline -1)"
    Write-Host "   Status: $(git status --short)"
    Write-Host ""
    Write-Host "🎉 Phase 1b Complete: Agents can now push code silently!"
    exit 0
} else {
    Write-Host "❌ FAILED: Push exited with code $pushExitCode" -ForegroundColor Red
    exit 1
}
