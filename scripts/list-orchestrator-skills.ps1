#!/usr/bin/env pwsh
<#
.SYNOPSIS
List all discovered orchestrator skills

.DESCRIPTION
Shows all skills that the orchestrator has discovered and can load.
Displays skill name, version, and description.

.EXAMPLE
.\scripts\list-orchestrator-skills.ps1
Shows available skills in pretty format
#>

param()

$pythonExe = 'C:\Users\bizca\AppData\Local\Programs\Python\Python313\python.exe'
$srcPath = Join-Path (Get-Location) 'src'

$env:PYTHONPATH = $srcPath

Write-Host ""
Write-Host "Orchestrator Skills Inventory" -ForegroundColor Cyan
Write-Host "=" * 60

& $pythonExe "$srcPath\list_skills.py"

Write-Host ""
Write-Host "To run a skill workflow, use:" -ForegroundColor Gray
Write-Host "  python src/orchestrator.py" -ForegroundColor Gray
Write-Host ""
