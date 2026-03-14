param(
    [string]$SourceUrl,
    [string]$DestinationPath,
    $PreferRaw,
    $LocalizeImages,
    [switch]$FromClipboard
)

function ConvertTo-NullableBoolean {
    param($Value)

    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace("$Value")) {
        return $null
    }
    if ($Value -is [bool]) {
        return $Value
    }

    switch -Regex ("$Value".Trim().ToLowerInvariant()) {
        '^(1|true|t|y|yes)$' { return $true }
        '^(0|false|f|n|no)$' { return $false }
        default { throw "Invalid boolean value: $Value. Use true/false, yes/no, or 1/0." }
    }
}

function Read-BooleanWithDefault {
    param([string]$Prompt, [bool]$DefaultValue)

    $suffix = if ($DefaultValue) { 'Y/n' } else { 'y/N' }
    while ($true) {
        $value = Read-Host "$Prompt [$suffix]"
        if ([string]::IsNullOrWhiteSpace($value)) {
            return $DefaultValue
        }
        switch -Regex ($value.Trim().ToLowerInvariant()) {
            '^(y|yes)$' { return $true }
            '^(n|no)$' { return $false }
            default { Write-Host 'Enter y or n.' }
        }
    }
}

function Get-SourceUrlFromClipboard {
    $clip = Get-Clipboard -Raw
    if ([string]::IsNullOrWhiteSpace($clip)) {
        throw 'Clipboard is empty.'
    }

    $match = [regex]::Match($clip.Trim(), 'https?://[^\s<>"'']+')
    if (-not $match.Success) {
        throw 'Clipboard does not contain an http/https URL.'
    }

    $candidate = $match.Value.Trim()
    $uri = $null
    if (-not [Uri]::TryCreate($candidate, [UriKind]::Absolute, [ref]$uri)) {
        throw "Clipboard URL is not a valid absolute URL: $candidate"
    }

    if (($uri.Scheme -ne 'http' -and $uri.Scheme -ne 'https') -or [string]::IsNullOrWhiteSpace($uri.Host)) {
        throw "Clipboard URL must use http/https and include a host: $candidate"
    }

    return $uri.AbsoluteUri
}

function Get-PageHtml {
    param([string]$Url)

    $headers = @{
        'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        'Accept' = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        'Accept-Language' = 'en-US,en;q=0.9'
    }

    $response = Invoke-WebRequest -Uri $Url -Headers $headers -ErrorAction Stop
    return $response.Content
}

function Remove-HtmlTags {
    param([string]$Text)

    $withoutTags = [regex]::Replace($Text, '<[^>]+>', ' ')
    return [System.Net.WebUtility]::HtmlDecode($withoutTags)
}

function ConvertTo-SafeFileStem {
    param([string]$Text, [string]$Fallback = 'scraped-page')

    $decoded = [System.Net.WebUtility]::HtmlDecode($Text)
    $clean = [regex]::Replace($decoded, '[^A-Za-z0-9]+', '_').Trim('_')
    if ([string]::IsNullOrWhiteSpace($clean)) {
        return $Fallback
    }
    return $clean
}

function Get-TitleFromHtmlOrUrl {
    param([string]$Html, [string]$Url)

    $h1 = [regex]::Match($Html, '<h1[^>]*>(.*?)</h1>', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($h1.Success) {
        $text = (Remove-HtmlTags -Text $h1.Groups[1].Value).Trim()
        if ($text) { return $text }
    }

    $title = [regex]::Match($Html, '<title[^>]*>(.*?)</title>', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($title.Success) {
        $text = (Remove-HtmlTags -Text $title.Groups[1].Value).Trim()
        if ($text) { return $text }
    }

    $uri = [Uri]$Url
    $segment = $uri.Segments[-1].Trim('/')
    if ([string]::IsNullOrWhiteSpace($segment)) {
        return $uri.Host
    }
    return $segment
}

function Get-AutoDestinationPath {
    param([string]$Url, [string]$Html, [string]$RepositoryRoot)

    $title = Get-TitleFromHtmlOrUrl -Html $Html -Url $Url
    $stem = ConvertTo-SafeFileStem -Text $title -Fallback 'scraped-page'
    return Join-Path (Join-Path $RepositoryRoot 'docs') ($stem + '.md')
}

$repoRoot = Split-Path -Parent $PSScriptRoot

if ($FromClipboard.IsPresent -and [string]::IsNullOrWhiteSpace($SourceUrl)) {
    try {
        $SourceUrl = Get-SourceUrlFromClipboard
        Write-Host "Using URL from clipboard: $SourceUrl" -ForegroundColor Yellow
    }
    catch {
        Write-Host "Clipboard does not contain a valid http/https URL. Copy a page URL, then run scrape-now again." -ForegroundColor Yellow
        return
    }
}

if ([string]::IsNullOrWhiteSpace($SourceUrl)) {
    $SourceUrl = Read-Host 'Source URL'
}

if ([string]::IsNullOrWhiteSpace($DestinationPath)) {
    $destinationInput = Read-Host 'Destination markdown path (blank = auto-generate under .\\docs)'
    if ([string]::IsNullOrWhiteSpace($destinationInput)) {
        $html = ''
        try {
            $html = Get-PageHtml -Url $SourceUrl
        }
        catch {
            Write-Host 'Could not fetch page HTML for title generation. Falling back to URL-based filename.' -ForegroundColor Yellow
        }
        $DestinationPath = Get-AutoDestinationPath -Url $SourceUrl -Html $html -RepositoryRoot $repoRoot
        Write-Host "Auto-generated destination: $DestinationPath" -ForegroundColor Yellow
    }
    else {
        $DestinationPath = $destinationInput
    }
}

$PreferRaw = ConvertTo-NullableBoolean -Value $PreferRaw
$LocalizeImages = ConvertTo-NullableBoolean -Value $LocalizeImages

if ($null -eq $PreferRaw) {
    $PreferRaw = Read-BooleanWithDefault -Prompt 'Prefer raw markdown endpoint if available?' -DefaultValue $true
}
if ($null -eq $LocalizeImages) {
    $LocalizeImages = Read-BooleanWithDefault -Prompt 'Localize images?' -DefaultValue $true
}

$scriptPath = Join-Path $repoRoot 'scripts\run_page_scrape.py'
if (-not (Test-Path $scriptPath)) {
    throw "Missing script: $scriptPath"
}

Push-Location $repoRoot
try {
    py $scriptPath --url $SourceUrl --output $DestinationPath --prefer-raw $PreferRaw --localize-images $LocalizeImages
}
finally {
    Pop-Location
}
