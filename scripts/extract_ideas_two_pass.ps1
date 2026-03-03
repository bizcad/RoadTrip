param(
    [string[]]$Projects = @('G:\repos\AI\RoadTrip', 'G:\repos\AI\ControlPlane'),
    [string]$OutputDir = 'G:\repos\AI\RoadTrip\analysis\idea_extraction',
    [string[]]$IncludeExtensions = @('.md', '.txt'),
    [double]$SimilarityThreshold = 0.58
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-ExcludedPath {
    param([string]$Path)
    $excluded = @(
        '\\.git\\', '\\bin\\', '\\obj\\', '\\node_modules\\', '\\__pycache__\\',
        '\\.venv\\', '\\venv\\', '\\dist\\', '\\build\\'
    )
    foreach ($pattern in $excluded) {
        if ($Path -match $pattern) { return $true }
    }
    return $false
}

function Normalize-TranscriptText {
    param([string]$Text)

    $normalized = $Text -replace "`r`n", "`n"
    $normalized = $normalized -replace "(?m)^\s*\d{1,2}:\d{2}(?::\d{2})?\s*[-–—]?\s*", ''
    $normalized = $normalized -replace "(?m)^\s*\[\d{1,2}:\d{2}(?::\d{2})?\]\s*", ''
    $normalized = $normalized -replace "(?m)^\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->.*$", ''
    $normalized = $normalized -replace "(?m)^\s*<!--.*?-->\s*$", ''
    return $normalized
}

function Get-CandidateChunks {
    param([string]$Text)

    $paragraphs = $Text -split "\n\s*\n"
    $chunks = New-Object System.Collections.Generic.List[string]

    foreach ($p in $paragraphs) {
        $clean = ($p -replace "\s+", ' ').Trim()
        if ($clean.Length -ge 30 -and $clean.Length -le 1200) {
            $chunks.Add($clean)
        }
    }

    return $chunks
}

function Get-IdeaIntent {
    param([string]$Text)
    $t = $Text.ToLowerInvariant()

    if ($t -match '\b(decide|decision|chosen|we will|finalize|agreed)\b') { return 'decision' }
    if ($t -match '\b(question|should we|how do we|what if|unclear|unknown)\b') { return 'question' }
    if ($t -match '\b(risk|issue|problem|blocker|constraint|limitation)\b') { return 'problem' }
    return 'idea'
}

function Get-IdeaTheme {
    param([string]$Text)
    $t = $Text.ToLowerInvariant()

    if ($t -match '\b(memory|context|prompt|session log|transcript|knowledge|state)\b') { return 'memory-and-context' }
    if ($t -match '\b(agent|orchestr|workflow|automation|tooling|pipeline|mcp|skill)\b') { return 'agent-workflow' }
    if ($t -match '\b(spec|architecture|design|system|component|interface)\b') { return 'architecture-and-spec' }
    if ($t -match '\b(test|evaluation|benchmark|metrics|quality|validation)\b') { return 'evaluation-and-quality' }
    if ($t -match '\b(ui|dashboard|window|view|xaml|ux)\b') { return 'ui-and-experience' }
    if ($t -match '\b(road trip|flight|itinerary|travel|route|hotel|airport)\b') { return 'travel-domain' }
    return 'general'
}

function Get-Tokens {
    param([string]$Text)

    $stop = @(
        'the','a','an','and','or','but','if','then','else','for','to','of','in','on','at','by','with','from',
        'is','are','was','were','be','been','being','it','this','that','these','those','as','we','you','i',
        'our','your','their','they','he','she','them','his','her','not','do','does','did','can','could','would',
        'should','may','might','will','just','into','over','under','about','after','before','during','than'
    )

    $clean = ($Text.ToLowerInvariant() -replace '[^a-z0-9\s]', ' ' -replace '\s+', ' ').Trim()
    if (-not $clean) { return @() }

    $tokens = $clean.Split(' ') | Where-Object { $_.Length -ge 3 -and -not ($stop -contains $_) }
    return @($tokens)
}

function Get-Jaccard {
    param([string[]]$A, [string[]]$B)

    if ($A.Count -eq 0 -or $B.Count -eq 0) { return 0.0 }

    $setA = [System.Collections.Generic.HashSet[string]]::new([string[]]$A)
    $setB = [System.Collections.Generic.HashSet[string]]::new([string[]]$B)

    $intersection = [System.Collections.Generic.HashSet[string]]::new($setA)
    $intersection.IntersectWith($setB)

    $union = [System.Collections.Generic.HashSet[string]]::new($setA)
    $union.UnionWith($setB)

    if ($union.Count -eq 0) { return 0.0 }
    return [double]$intersection.Count / [double]$union.Count
}

function Estimate-Priority {
    param([string]$Text, [int]$Mentions, [int]$SourceCount)

    $t = $Text.ToLowerInvariant()
    $impact = 2
    if ($t -match '\b(architecture|system|platform|pipeline|automation|spec|evaluation)\b') { $impact = 4 }
    if ($t -match '\b(core|critical|foundational|must)\b') { $impact = 5 }

    $urgency = 2
    if ($t -match '\b(next|todo|need to|should|priority|urgent|blocker)\b') { $urgency = 4 }
    if ($t -match '\b(now|immediately)\b') { $urgency = 5 }

    $signal = [Math]::Min(5, 1 + [Math]::Ceiling(($Mentions + $SourceCount) / 3.0))
    $score = [Math]::Round((($impact * 0.45) + ($urgency * 0.25) + ($signal * 0.30)), 2)
    return $score
}

$ideaPattern = '(?i)\b(idea|plan|should|could|need to|next step|todo|build|create|implement|improve|automate|evaluate|design|spec|workflow|system|problem|challenge|approach|proposal|option|consider|we can|let''s|goal|priority|roadmap)\b'

$candidates = New-Object System.Collections.Generic.List[object]
$fileCount = 0

foreach ($project in $Projects) {
    if (-not (Test-Path -LiteralPath $project)) { continue }

    $files = Get-ChildItem -LiteralPath $project -Recurse -File -Force |
        Where-Object {
            ($IncludeExtensions -contains $_.Extension.ToLowerInvariant()) -and
            (-not (Test-ExcludedPath -Path $_.FullName))
        }

    foreach ($file in $files) {
        $fileCount += 1
        $raw = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if ([string]::IsNullOrWhiteSpace($raw)) { continue }

        $normalized = Normalize-TranscriptText -Text $raw
        $chunks = Get-CandidateChunks -Text $normalized

        foreach ($chunk in $chunks) {
            if ($chunk -notmatch $ideaPattern) { continue }

            $intent = Get-IdeaIntent -Text $chunk
            $theme = Get-IdeaTheme -Text $chunk
            $tokens = @(Get-Tokens -Text $chunk)
            if ($tokens.Count -lt 5) { continue }

            $confidence = 0.55
            if ($chunk -match '(?i)\b(need to|should|must|next|todo|plan|we can|let''s|build|implement)\b') { $confidence += 0.20 }
            if ($chunk -match '(?i)\b(architecture|spec|workflow|evaluation|automation|memory|context)\b') { $confidence += 0.15 }
            if ($confidence -gt 0.95) { $confidence = 0.95 }

            $projectName = if ($file.FullName.StartsWith('G:\repos\AI\RoadTrip', [System.StringComparison]::OrdinalIgnoreCase)) { 'RoadTrip' } else { 'ControlPlane' }

            $candidates.Add([pscustomobject]@{
                project = $projectName
                file_path = $file.FullName
                file_name = $file.Name
                ext = $file.Extension.ToLowerInvariant()
                excerpt = $chunk
                intent = $intent
                theme = $theme
                confidence = [Math]::Round($confidence, 2)
                tokens = ($tokens -join ' ')
            })
        }
    }
}

$clusters = New-Object System.Collections.Generic.List[object]

foreach ($candidate in $candidates) {
    $candTokens = $candidate.tokens.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
    $bestIndex = -1
    $bestScore = 0.0

    for ($i = 0; $i -lt $clusters.Count; $i++) {
        $clusterTokens = $clusters[$i].rep_tokens
        $score = Get-Jaccard -A $candTokens -B $clusterTokens
        if ($score -gt $bestScore) {
            $bestScore = $score
            $bestIndex = $i
        }
    }

    if ($bestIndex -ge 0 -and $bestScore -ge $SimilarityThreshold) {
        $clusters[$bestIndex].members.Add($candidate)
        if ($candidate.excerpt.Length -gt $clusters[$bestIndex].canonical.Length) {
            $clusters[$bestIndex].canonical = $candidate.excerpt
            $clusters[$bestIndex].rep_tokens = $candTokens
        }
    }
    else {
        $members = New-Object System.Collections.Generic.List[object]
        $members.Add($candidate)
        $clusters.Add([pscustomobject]@{
            canonical = $candidate.excerpt
            rep_tokens = $candTokens
            members = $members
        })
    }
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$ideaRegister = New-Object System.Collections.Generic.List[object]
$ideaEvidence = New-Object System.Collections.Generic.List[object]
$themeRows = New-Object System.Collections.Generic.List[object]

$clusterId = 0
foreach ($cluster in $clusters) {
    $clusterId += 1
    $ideaId = ('IDEA-{0:D4}' -f $clusterId)

    $members = $cluster.members
    $mentions = $members.Count
    $sourceFiles = $members.file_path | Sort-Object -Unique
    $sourceCount = @($sourceFiles).Count

    $themeTop = ($members | Group-Object theme | Sort-Object Count -Descending | Select-Object -First 1).Name
    $intentTop = ($members | Group-Object intent | Sort-Object Count -Descending | Select-Object -First 1).Name

    $priority = Estimate-Priority -Text $cluster.canonical -Mentions $mentions -SourceCount $sourceCount
    $status = 'open'
    if ($cluster.canonical -match '(?i)\b(done|completed|shipped|resolved)\b') { $status = 'implemented' }

    $sampleSources = ($sourceFiles | Select-Object -First 3) -join ' | '

    $ideaRegister.Add([pscustomobject]@{
        idea_id = $ideaId
        idea_text = $cluster.canonical
        theme = $themeTop
        intent = $intentTop
        priority_score = $priority
        status = $status
        mentions = $mentions
        source_count = $sourceCount
        sample_sources = $sampleSources
    })

    foreach ($m in $members) {
        $ideaEvidence.Add([pscustomobject]@{
            idea_id = $ideaId
            project = $m.project
            file_path = $m.file_path
            file_name = $m.file_name
            ext = $m.ext
            confidence = $m.confidence
            theme = $m.theme
            intent = $m.intent
            excerpt = $m.excerpt
        })
    }
}

$themeAgg = $ideaRegister | Group-Object theme | Sort-Object Count -Descending
foreach ($t in $themeAgg) {
    $rows = $ideaRegister | Where-Object { $_.theme -eq $t.Name }
    $avgPriority = [Math]::Round((($rows | Measure-Object -Property priority_score -Average).Average), 2)
    $themeRows.Add([pscustomobject]@{
        theme = $t.Name
        idea_count = $t.Count
        avg_priority = $avgPriority
    })
}

$ideaRegister = $ideaRegister | Sort-Object @{Expression='priority_score'; Descending=$true}, @{Expression='mentions'; Descending=$true}
$ideaEvidence = $ideaEvidence | Sort-Object idea_id, confidence -Descending

$ideaRegisterPath = Join-Path $OutputDir 'idea_register.csv'
$ideaEvidencePath = Join-Path $OutputDir 'idea_evidence.csv'
$ideaThemesPath = Join-Path $OutputDir 'idea_themes.csv'
$runSummaryPath = Join-Path $OutputDir 'run_summary.csv'

$ideaRegister | Export-Csv -Path $ideaRegisterPath -NoTypeInformation -Encoding UTF8
$ideaEvidence | Export-Csv -Path $ideaEvidencePath -NoTypeInformation -Encoding UTF8
$themeRows | Export-Csv -Path $ideaThemesPath -NoTypeInformation -Encoding UTF8

[pscustomobject]@{
    projects = ($Projects -join '; ')
    files_scanned = $fileCount
    candidates_found = $candidates.Count
    idea_clusters = @($ideaRegister).Count
    output_dir = $OutputDir
} | Export-Csv -Path $runSummaryPath -NoTypeInformation -Encoding UTF8

Write-Output "Completed two-pass extraction."
Write-Output "- $ideaRegisterPath"
Write-Output "- $ideaEvidencePath"
Write-Output "- $ideaThemesPath"
Write-Output "- $runSummaryPath"
