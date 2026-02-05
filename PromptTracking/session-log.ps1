<#
Session Log Appender
Usage:  
  pwsh -File .\PromptTracking\session-log.ps1            # Append clipboard to today's log
  pwsh .\PromptTracking\session-log.ps1 -CodeBlock         # Wrap clipboard in fenced block
  pwsh .\PromptTracking\session-log.ps1 -Title "Spec Sync" -Section
  pwsh .\PromptTracking\session-log.ps1 -Path .\PromptTracking\Session\ Custom.md
Parameters:
  -Path <string>    Explicit file path (otherwise Session Log yyyyMMdd.md in PromptTracking)
  -Section          Create a heading for this entry (defaults to H2; use -H1 for H1)
  -Title <string>   Custom section title (requires -Section)
  -CodeBlock        Wrap clipboard content in ``` fences
  -H1               Use H1 (#) instead of H2 (##) for -Section headings
  -Markers <enum>   Surround content with HTML comment markers.
                    Values: None|Prompt|Response|Note (default: None)
  -GuardLargeClipboard  Enable clipboard size guard (requires -MaxClipboardChars > 0)
  -MaxClipboardChars    Maximum allowed clipboard characters before blocking (default 0 = no limit)
  -AutoTruncate         If guard triggers, truncate to MaxClipboardChars instead of aborting
  -DayStart             Insert a day-start HTML marker before the entry
  -DayEnd               Insert a day-end HTML marker before the entry
  -Quiet            Suppress confirmation output
#>
param(
  [string]$Path,
  [switch]$Section,
  [string]$Title,
  [switch]$CodeBlock,
  [switch]$H1,
  [ValidateSet('None','Prompt','Response','Note')]
  [string]$Markers = 'None',
  [switch]$GuardLargeClipboard,
  [int]$MaxClipboardChars = 0,
  [switch]$AutoTruncate,
  [switch]$DayStart,
  [switch]$DayEnd,
  [switch]$Quiet
)

function Get-SessionLogPath {
  param([string]$Explicit)
  if ($Explicit) { return (Resolve-Path -LiteralPath $Explicit -ErrorAction SilentlyContinue) ?? $Explicit }
  $dir = Join-Path $PSScriptRoot '.'
  $date = Get-Date -Format 'yyyyMMdd'
  return Join-Path $dir "Session Log $date.md"
}

$target = Get-SessionLogPath -Explicit $Path
$content = Get-Clipboard -Raw
if (-not $content) { Write-Warning 'Clipboard empty – nothing appended.'; exit 1 }

# Optional clipboard size guard
if ($GuardLargeClipboard -and $MaxClipboardChars -gt 0) {
  $len = $content.Length
  if ($len -gt $MaxClipboardChars) {
    if ($AutoTruncate) {
      $content = $content.Substring(0, [Math]::Min($MaxClipboardChars, $len)) + "`n... (truncated from $len characters)"
      if (-not $Quiet) { Write-Warning "Clipboard truncated to $MaxClipboardChars chars (was $len)." }
    }
    else {
      Write-Warning "Clipboard length $len exceeds MaxClipboardChars=$MaxClipboardChars. Use -AutoTruncate or increase the limit. Aborting append."
      exit 2
    }
  }
}

$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$headingToken = if ($H1) { '#' } else { '##' }
$header = if ($Section) {
  if ($Title) { "`n$headingToken $Title ($timestamp)`n" } else { "`n$headingToken Entry $timestamp`n" }
} else { "`n[$timestamp]`n" }

# Optional day boundary markers
$dayMarker = ""
if ($DayStart -and $DayEnd) {
  $dayMarker = "`n<!--Day Start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')-->`n<!--Day End $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')-->`n"
}
elseif ($DayStart) { $dayMarker = "`n<!--Day Start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')-->`n" }
elseif ($DayEnd)   { $dayMarker = "`n<!--Day End $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')-->`n" }

if ($CodeBlock) { $content = "``````n$content`n``````" }

# Optional content markers for easier parsing
switch ($Markers) {
  'Response' {
    $content = "<!--Start Response-->`n$content`n<!--End Response-->"
  }
  'Prompt' {
    $content = "<!--Start Prompt-->`n$content`n<!--End Prompt-->"
  }
  'Note' {
    $content = "<!--Start Note-->`n$content`n<!--End Note-->"
  }
  default { }
}

if (-not (Test-Path $target)) {
  "# Session Log $(Get-Date -Format 'yyyy-MM-dd')`n" | Out-File $target -Encoding UTF8
}
Add-Content -Path $target -Value ($dayMarker + $header + $content + "`n") -Encoding UTF8

if (-not $Quiet) { Write-Host "Appended clipboard to $target" -ForegroundColor Green }
