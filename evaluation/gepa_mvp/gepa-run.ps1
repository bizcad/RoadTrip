param(
    [Parameter(Mandatory = $true)]
    [string]$PromptId,

    [string]$ParentPromptId = "",

    [Parameter(Mandatory = $true)]
    [string]$Model,

    [string]$ResponseId = "",

    [Parameter(Mandatory = $true)]
    [double]$GepaScore,

    [Parameter(Mandatory = $true)]
    [ValidateSet('pass','fail')]
    [string]$PassFail,

    [double]$CostUsd = 0,

    [int]$LatencyMs = 0,

    [string]$PromptFile,
    [string]$PromptText,
    [string]$ResponseFile,
    [string]$ResponseText,

    [string]$SessionLogPath,
    [string]$ProjectRoot
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir 'run_gepa_trial.py'

if (-not (Test-Path $runner)) {
    throw "Missing script: $runner"
}

$args = @(
    $runner,
    '--prompt-id', $PromptId,
    '--parent-prompt-id', $ParentPromptId,
    '--model', $Model,
    '--response-id', $ResponseId,
    '--gepa-score', $GepaScore,
    '--pass-fail', $PassFail,
    '--cost-usd', $CostUsd,
    '--latency-ms', $LatencyMs
)

if ($PromptFile) { $args += @('--prompt-file', $PromptFile) }
if ($PromptText) { $args += @('--prompt-text', $PromptText) }
if ($ResponseFile) { $args += @('--response-file', $ResponseFile) }
if ($ResponseText) { $args += @('--response-text', $ResponseText) }
if ($SessionLogPath) { $args += @('--session-log-path', $SessionLogPath) }
if ($ProjectRoot) { $args += @('--project-root', $ProjectRoot) }

py @args
