# PRD: GEPA Prompt/Response Provenance MVP

## Overview
Build a lightweight MVP that captures GEPA-optimized prompt/response trials with structured metadata and appends them to the daily session log in `PromptTracking`.

This MVP is designed for dogfooding a self-improving workflow where prompt optimization and model-selection optimization can be measured, compared, and traced.

## Problem
Prompt optimization experiments are high value but difficult to reproduce and compare unless every trial is logged with:
- prompt lineage
- model used
- response identity
- score and pass/fail outcomes
- operational metrics (cost/latency)

Without this, improvements are anecdotal and difficult to promote into stable workflows.

## Goals
- Log each prompt/response trial with a YAML metadata header.
- Append trial summaries to the same daily session log used today.
- Keep full trial artifacts in JSON for programmatic analysis.
- Support quick local usage from PowerShell and `py`.

## Non-Goals (MVP)
- Running a full GEPA algorithm internally.
- Calling proprietary model APIs directly.
- Auto-capturing Copilot Chat prompts/responses from the VS Code UI.
- CI orchestration and model hosting.

## Users
- Primary: repo owner/developer running eval and prompt-optimization experiments.
- Secondary: future agent workflows that need reproducible trial history.

## Functional Requirements
1. Accept a prompt and response payload (file- or text-based).
2. Capture metadata fields:
   - `timestamp`
   - `prompt_id`
   - `parent_prompt_id`
   - `model`
   - `response_id`
   - `response_hash`
   - `gepa_score`
   - `pass_fail`
   - `cost_usd`
   - `latency_ms`
3. Append a markdown session-log entry containing:
   - YAML header block
   - prompt section
   - response section
4. Persist machine-readable records to JSONL and per-trial JSON artifact files.
5. Provide PowerShell wrapper command for ergonomic execution.

## Session Log Entry Format
Each entry should include a YAML block for metadata, then prompt/response bodies.

Example:

```markdown
## GEPA Trial 2026-02-26 14:45:10

```yaml
entry_type: gepa_trial
timestamp: 2026-02-26T14:45:10Z
trial_id: 20260226-144510-abc123
prompt_id: prompt_v7
parent_prompt_id: prompt_v6
model: claude-sonnet-4.5
response_id: rsp_9f2d
response_hash: 9f2d4...
gepa_score: 0.87
pass_fail: pass
cost_usd: 0.042
latency_ms: 1830
```

### Prompt
<!--Start Prompt-->
...prompt text...
<!--End Prompt-->

### Response
<!--Start Response-->
...response text...
<!--End Response-->
```

## Data Artifacts
- `evaluation/gepa_mvp/artifacts/trials.jsonl`
- `evaluation/gepa_mvp/artifacts/YYYYMMDD/<trial_id>.json`

## Success Criteria
- A single command can append a valid YAML-headed prompt/response trial to the current session log.
- Artifacts are queryable via JSONL.
- Required metadata fields are always present.

## Risks
- Manual score entry can be inconsistent.
- Users may omit metadata without guardrails.
- Session log size may grow quickly.

## Mitigations
- Validate required inputs in script.
- Provide sample command and config.
- Keep full payload in artifacts; keep log human-readable.
