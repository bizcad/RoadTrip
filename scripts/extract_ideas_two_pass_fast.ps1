param(
    [string[]]$Projects = @('G:\repos\AI\RoadTrip', 'G:\repos\AI\ControlPlane'),
    [string]$OutputDir = 'G:\repos\AI\RoadTrip\analysis\idea_extraction',
    [string[]]$IncludeExtensions = @('.md', '.txt')
)

$ErrorActionPreference = 'Stop'

function Test-ExcludedPath {
    param([string]$Path)
    $excludedParts = @('\.git\','\bin\','\obj\','\node_modules\','\__pycache__\','\.venv\','\venv\','\dist\','\build\')
    foreach ($p in $excludedParts) {
        if ($Path -match $p) { return $true }
    }
    return $false
}

function Normalize-Text {
    param([string]$Text)
    $t = $Text -replace "`r`n", "`n"
    $t = $t -replace '(?m)^\s*\d{1,2}:\d{2}(?::\d{2})?\s*[-–—]?\s*', ''
    $t = $t -replace '(?m)^\s*\[\d{1,2}:\d{2}(?::\d{2})?\]\s*', ''
    $t = $t -replace '(?m)^\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->.*$', ''
    $t = $t -replace '(?m)^\s*<!--.*?-->\s*$', ''
    return $t
}

function Get-Theme {
    param([string]$Text)
    $t = $Text.ToLowerInvariant()
    if ($t -match '\b(memory|context|session|transcript|knowledge|state)\b') { return 'memory-and-context' }
    if ($t -match '\b(agent|workflow|automation|pipeline|tool|mcp|skill)\b') { return 'agent-workflow' }
    if ($t -match '\b(spec|architecture|design|system|component|interface)\b') { return 'architecture-and-spec' }
    if ($t -match '\b(test|evaluation|metric|quality|validate|benchmark)\b') { return 'evaluation-and-quality' }
    if ($t -match '\b(ui|dashboard|xaml|window|view|ux)\b') { return 'ui-and-experience' }
    if ($t -match '\b(road trip|flight|itinerary|travel|route|hotel|airport)\b') { return 'travel-domain' }
    return 'general'
}

function Get-Intent {
    param([string]$Text)
    $t = $Text.ToLowerInvariant()
    if ($t -match '\b(decide|decision|finalize|agreed|chosen)\b') { return 'decision' }
    if ($t -match '\b(question|should we|how do we|what if|unknown|unclear)\b') { return 'question' }
    if ($t -match '\b(problem|risk|issue|blocker|constraint|limitation)\b') { return 'problem' }
    return 'idea'
}

function Get-Tokens {
    param([string]$Text)
    $stop = @('the','a','an','and','or','but','if','then','else','for','to','of','in','on','at','by','with','from','is','are','was','were','be','been','being','it','this','that','these','those','as','we','you','i','our','your','their','they','them','his','her','not','do','does','did','can','could','would','should','may','might','will','into','over','under','about','after','before','during','than')
    $clean = ($Text.ToLowerInvariant() -replace '[^a-z0-9\s]', ' ' -replace '\s+', ' ').Trim()
    if (-not $clean) { return @() }
    $tokens = $clean.Split(' ') | Where-Object { $_.Length -ge 3 -and -not ($stop -contains $_) }
    return @($tokens)
}

function Get-IdeaKey {
    param([string[]]$Tokens)
    if (-not $Tokens -or $Tokens.Count -eq 0) { return '' }
    $head = @($Tokens | Select-Object -First 14)
    return ($head -join ' ')
}

$ideaPattern = '(?i)\b(idea|plan|should|could|need to|next step|todo|build|create|implement|improve|automate|evaluate|design|spec|workflow|system|problem|challenge|approach|proposal|option|consider|we can|goal|priority|roadmap)\b'

$candidates = New-Object System.Collections.Generic.List[object]
$filesScanned = 0

foreach ($project in $Projects) {
    if (-not (Test-Path -LiteralPath $project)) { continue }
    $files = Get-ChildItem -LiteralPath $project -Recurse -File -Force | Where-Object {
        ($IncludeExtensions -contains $_.Extension.ToLowerInvariant()) -and (-not (Test-ExcludedPath -Path $_.FullName))
    }

    foreach ($file in $files) {
        $filesScanned++
        $raw = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if ([string]::IsNullOrWhiteSpace($raw)) { continue }

        $text = Normalize-Text -Text $raw
        $parts = $text -split "\n\s*\n"
        $chunkCount = 0

        foreach ($part in $parts) {
            if ($chunkCount -ge 100) { break }
            $chunk = ($part -replace '\s+', ' ').Trim()
            if ($chunk.Length -lt 35 -or $chunk.Length -gt 1200) { continue }
            if ($chunk -notmatch $ideaPattern) { continue }

            $tokens = @(Get-Tokens -Text $chunk)
            if ($tokens.Count -lt 6) { continue }

            $key = Get-IdeaKey -Tokens $tokens
            if (-not $key) { continue }

            $conf = 0.55
            if ($chunk -match '(?i)\b(need to|should|must|next|todo|plan|we can|build|implement|priority)\b') { $conf += 0.20 }
            if ($chunk -match '(?i)\b(architecture|spec|workflow|evaluation|automation|memory|context)\b') { $conf += 0.15 }
            if ($conf -gt 0.95) { $conf = 0.95 }

            $projectName = if ($file.FullName.StartsWith('G:\repos\AI\RoadTrip', [System.StringComparison]::OrdinalIgnoreCase)) { 'RoadTrip' } else { 'ControlPlane' }

            $candidates.Add([pscustomobject]@{
                idea_key = $key
                excerpt = $chunk
                project = $projectName
                file_path = $file.FullName
                file_name = $file.Name
                ext = $file.Extension.ToLowerInvariant()
                theme = (Get-Theme -Text $chunk)
                intent = (Get-Intent -Text $chunk)
                confidence = [Math]::Round($conf, 2)
            })

            $chunkCount++
        }
    }
}

$byIdea = @{}
foreach ($c in $candidates) {
    if (-not $byIdea.ContainsKey($c.idea_key)) {
        $byIdea[$c.idea_key] = [pscustomobject]@{
            canonical = $c.excerpt
            mentions = 0
            sources = New-Object System.Collections.Generic.HashSet[string]
            themeCounts = @{}
            intentCounts = @{}
            evidences = New-Object System.Collections.Generic.List[object]
        }
    }

    $bucket = $byIdea[$c.idea_key]
    $bucket.mentions++
    [void]$bucket.sources.Add($c.file_path)
    $bucket.evidences.Add($c)

    if ($c.excerpt.Length -gt $bucket.canonical.Length) { $bucket.canonical = $c.excerpt }

    if (-not $bucket.themeCounts.ContainsKey($c.theme)) { $bucket.themeCounts[$c.theme] = 0 }
    $bucket.themeCounts[$c.theme]++

    if (-not $bucket.intentCounts.ContainsKey($c.intent)) { $bucket.intentCounts[$c.intent] = 0 }
    $bucket.intentCounts[$c.intent]++
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$ideaRegister = New-Object System.Collections.Generic.List[object]
$ideaEvidence = New-Object System.Collections.Generic.List[object]
$id = 0

foreach ($kv in $byIdea.GetEnumerator()) {
    $id++
    $ideaId = ('IDEA-{0:D4}' -f $id)
    $b = $kv.Value

    $themeTop = ($b.themeCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
    $intentTop = ($b.intentCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key

    $sourceCount = $b.sources.Count
    $mentions = $b.mentions

    $impact = 2
    if ($b.canonical -match '(?i)\b(architecture|system|platform|pipeline|automation|spec|evaluation)\b') { $impact = 4 }
    if ($b.canonical -match '(?i)\b(core|critical|foundational|must)\b') { $impact = 5 }

    $urgency = 2
    if ($b.canonical -match '(?i)\b(next|todo|need to|should|priority|urgent|blocker)\b') { $urgency = 4 }

    $signal = [Math]::Min(5, 1 + [Math]::Ceiling(($mentions + $sourceCount) / 3.0))
    $priority = [Math]::Round((($impact * 0.45) + ($urgency * 0.25) + ($signal * 0.30)), 2)

    $status = 'open'
    if ($b.canonical -match '(?i)\b(done|completed|shipped|resolved)\b') { $status = 'implemented' }

    $sampleSources = (@($b.sources | Select-Object -First 3) -join ' | ')

    $ideaRegister.Add([pscustomobject]@{
        idea_id = $ideaId
        idea_text = $b.canonical
        theme = $themeTop
        intent = $intentTop
        priority_score = $priority
        status = $status
        mentions = $mentions
        source_count = $sourceCount
        sample_sources = $sampleSources
    })

    foreach ($ev in $b.evidences) {
        $ideaEvidence.Add([pscustomobject]@{
            idea_id = $ideaId
            project = $ev.project
            file_path = $ev.file_path
            file_name = $ev.file_name
            ext = $ev.ext
            confidence = $ev.confidence
            theme = $ev.theme
            intent = $ev.intent
            excerpt = $ev.excerpt
        })
    }
}

$ideaRegister = $ideaRegister | Sort-Object @{Expression='priority_score'; Descending=$true}, @{Expression='mentions'; Descending=$true}
$ideaEvidence = $ideaEvidence | Sort-Object idea_id, @{Expression='confidence'; Descending=$true}

$themeRows = $ideaRegister | Group-Object theme | Sort-Object Count -Descending | ForEach-Object {
    $rows = $ideaRegister | Where-Object { $_.theme -eq $_.Name }
    [pscustomobject]@{
        theme = $_.Name
        idea_count = $_.Count
        avg_priority = [Math]::Round((($rows | Measure-Object -Property priority_score -Average).Average), 2)
    }
}

$ideaRegisterPath = Join-Path $OutputDir 'idea_register.csv'
$ideaEvidencePath = Join-Path $OutputDir 'idea_evidence.csv'
$ideaThemesPath = Join-Path $OutputDir 'idea_themes.csv'
$runSummaryPath = Join-Path $OutputDir 'run_summary.csv'

$ideaRegister | Export-Csv -Path $ideaRegisterPath -NoTypeInformation -Encoding UTF8
$ideaEvidence | Export-Csv -Path $ideaEvidencePath -NoTypeInformation -Encoding UTF8
$themeRows | Export-Csv -Path $ideaThemesPath -NoTypeInformation -Encoding UTF8

[pscustomobject]@{
    projects = ($Projects -join '; ')
    files_scanned = $filesScanned
    candidates_found = $candidates.Count
    idea_clusters = @($ideaRegister).Count
    output_dir = $OutputDir
} | Export-Csv -Path $runSummaryPath -NoTypeInformation -Encoding UTF8

Write-Output "Completed two-pass extraction."
Write-Output "- $ideaRegisterPath"
Write-Output "- $ideaEvidencePath"
Write-Output "- $ideaThemesPath"
Write-Output "- $runSummaryPath"
