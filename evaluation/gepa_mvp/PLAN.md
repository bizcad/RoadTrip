# PLAN: GEPA Prompt/Response Logging MVP

## Phase 1: Scaffold (this change)
- Create MVP docs (`PRD.md`, this plan).
- Create Python logger script to:
  - validate metadata inputs
  - compute response hash
  - write JSON artifact + JSONL
  - append YAML-headed entry to daily session log
- Create PowerShell wrapper (`gepa-run.ps1`) for easy local usage.
- Add sample prompt/response files and sample config.

## Phase 2: Adoption
- Add aliases in `PromptTracking/log-aliases.ps1` (optional integration):
  - `gepa-run`
  - `gepa-log-help`
- Add convenience command to ingest GEPA optimizer outputs directly.
- Add small parser script to summarize pass rate and top-scoring prompt variants.

## Phase 3: Optimization Loop
- Connect script to actual GEPA candidate generation outputs.
- Add ranking logic and automatic winner promotion proposal.
- Add threshold-based gating for model-selection updates.

## MVP CLI Contract
`run_gepa_trial.py` should accept:
- `--prompt-id` (required)
- `--parent-prompt-id` (optional)
- `--model` (required)
- `--response-id` (optional)
- `--gepa-score` (required)
- `--pass-fail` (`pass|fail`, required)
- `--cost-usd` (optional)
- `--latency-ms` (optional)
- `--prompt-file` or `--prompt-text` (one required)
- `--response-file` or `--response-text` (one required)
- `--session-log-path` (optional; defaults to today’s file in `PromptTracking`)

## Output Guarantees
- One markdown section appended to a session log with YAML metadata.
- One JSON artifact per trial.
- One JSONL append for analytics-friendly history.

## Manual Test Checklist
1. Run sample command.
2. Confirm session log entry includes YAML + prompt + response.
3. Confirm `trials.jsonl` append exists.
4. Confirm per-trial JSON artifact exists.
5. Confirm script fails fast on missing required fields.
