#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Provides GitHub PAT to git when it asks for a password (via GIT_ASKPASS)
.DESCRIPTION
    This script is called by git when it needs credentials for HTTPS operations.
    It returns the PAT token stored in ProjectSecrets/PAT.txt
    
    Usage: Set environment variable GIT_ASKPASS to this script path
    Example:
        $env:GIT_ASKPASS = "G:\repos\AI\RoadTrip\scripts\git-pass-provider.ps1"
        git push origin main
#>

param(
    [string]$Prompt = ""
)

# Only respond to git's password prompt, ignore other prompts
if ($Prompt -like "*password*" -or $Prompt -like "*pass*") {
    $patFile = "G:\repos\AI\RoadTrip\ProjectSecrets\PAT.txt"
    
    if (Test-Path $patFile) {
        $pat = (Get-Content $patFile -Raw).Trim()
        Write-Host $pat
    } else {
        Write-Error "PAT file not found: $patFile" -ErrorAction Stop
    }
} else {
    # For other prompts (username, etc), don't respond
    exit 1
}
