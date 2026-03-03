# GEPA Prompt/Response Logging MVP

This folder contains a lightweight scaffold to log GEPA-style prompt optimization trials with provenance metadata.

## What it logs
Each run captures:
- timestamp
- prompt_id
- parent_prompt_id
- model
- response_id
- response_hash
- gepa_score
- pass_fail
- cost_usd
- latency_ms

The run writes:
- session log entry with YAML header + prompt/response blocks
- JSON artifact per trial
- JSONL line for analytics

## Files
- `PRD.md` - product requirements for this MVP
- `PLAN.md` - implementation plan
- `run_gepa_trial.py` - main logger script
- `gepa-run.ps1` - PowerShell wrapper
- `mvp_config.example.yaml` - sample config
- `samples/` - sample prompt/response inputs
- `artifacts/` - output folder (created at runtime)

## Quick start (Windows / PowerShell)
Run from repo root:

```powershell
pwsh -File .\evaluation\gepa_mvp\gepa-run.ps1 \
  -PromptId "prompt_v1" \
  -ParentPromptId "" \
  -Model "claude-sonnet-4.5" \
  -ResponseId "rsp_v1" \
  -GepaScore 0.82 \
  -PassFail pass \
  -CostUsd 0.031 \
  -LatencyMs 1520 \
  -PromptFile ".\evaluation\gepa_mvp\samples\prompt.txt" \
  -ResponseFile ".\evaluation\gepa_mvp\samples\response.txt"
```

Or call Python directly:

```powershell
py .\evaluation\gepa_mvp\run_gepa_trial.py \
  --prompt-id prompt_v1 \
  --parent-prompt-id "" \
  --model claude-sonnet-4.5 \
  --response-id rsp_v1 \
  --gepa-score 0.82 \
  --pass-fail pass \
  --cost-usd 0.031 \
  --latency-ms 1520 \
  --prompt-file .\evaluation\gepa_mvp\samples\prompt.txt \
  --response-file .\evaluation\gepa_mvp\samples\response.txt
```

## Session log behavior
By default, entries append to:
- `PromptTracking/Session Log YYYYMMDD.md`

Override with:
- `-SessionLogPath` in PowerShell wrapper
- `--session-log-path` in Python script

## Notes
- This MVP does not run GEPA optimization itself; it records trial outcomes from your GEPA/model pipeline.
- Designed to be compatible with your existing `PromptTracking` workflow.
