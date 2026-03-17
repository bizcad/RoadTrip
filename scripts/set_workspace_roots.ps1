param(
    [ValidateSet('full', 'roadtrip-only')]
    [string]$Mode = 'full',

    [string]$WorkspaceFile = (Join-Path $PSScriptRoot '..\RoadTrip.code-workspace')
)

if (-not (Test-Path $WorkspaceFile -PathType Leaf)) {
    throw "Workspace file not found: $WorkspaceFile"
}

$workspace = Get-Content -Path $WorkspaceFile -Raw | ConvertFrom-Json

$fullFolders = @(
    [pscustomobject]@{ path = '.' },
    [pscustomobject]@{ path = '../scratchpad' },
    [pscustomobject]@{ path = '../rockbot' },
    [pscustomobject]@{ path = '../thepopebot-main' },
    [pscustomobject]@{ path = '../PPA' }
)

$roadTripOnlyFolders = @(
    [pscustomobject]@{ path = '.' }
)

switch ($Mode) {
    'full' {
        $workspace.folders = $fullFolders
    }
    'roadtrip-only' {
        $workspace.folders = $roadTripOnlyFolders
    }
}

$updatedJson = $workspace | ConvertTo-Json -Depth 20
Set-Content -Path $WorkspaceFile -Value $updatedJson -Encoding utf8

Write-Host "Updated workspace roots: $Mode" -ForegroundColor Green
Write-Host "File: $WorkspaceFile" -ForegroundColor Cyan
Write-Host "Reload the VS Code window to apply changes in Source Control." -ForegroundColor Yellow