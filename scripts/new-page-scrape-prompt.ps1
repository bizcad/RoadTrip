param(
    [string]$SourceUrl,
    [string]$DestinationPath,
    $PreferRaw,
    $LocalizeImages,
    [switch]$FromClipboard,
    [switch]$CopyToClipboard
)

$target = Join-Path (Split-Path -Parent $PSScriptRoot) 'infra\new-page-scrape-prompt.ps1'
& $target @PSBoundParameters
