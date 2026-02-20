# Pruning Governor (Fast Thinking)

## Core thesis
Complexity pruning must be policy-driven, automatic, and budget-constrained.

## Why this is hard
- The system can discover useful complexity before converging to simplicity.
- Humans and agents both over-retain (pack-rat behavior).
- Disk growth is finite; eventually resource pressure forces poor emergency decisions.

## Governance model
- Let complexity be explored in bounded sandbox lanes.
- Require every retained item to justify its cost.
- Enforce periodic pruning cycles regardless of human preference.

## Retention contract fields
Every retained artifact/control requires:
- owner
- purpose
- cost estimate (space/time/cognitive)
- expiry/TTL
- review cadence
- prune policy (auto, quarantine, review-required)

## Pruning modes
- `steady_prune`: nightly low-impact pruning of expired transient items.
- `pressure_prune`: aggressive pruning when warning threshold exceeded.
- `emergency_prune`: fail-safe mode at emergency threshold; only critical lane retained.

## Complexity score (example)
`complexity_score = active_controls + unresolved_exceptions + stale_artifacts + override_count`

Gate rules:
- if complexity_score rises 3 review windows in a row, block new feature controls.
- if storage percent > warning threshold, run pressure_prune.
- if storage percent > emergency threshold, run emergency_prune and alert owner.

## Human trust boundary
Humans may defer deletion emotionally. Policy must cap this with expiring overrides.

## Metrics
- retention_budget_utilization
- prune_yield_gb_per_day
- stale_artifact_ratio
- override_expiry_compliance
- complexity_score_trend

## Guardrails
- No indefinite override.
- No orphan retention (missing owner/purpose).
- No new control admitted without retirement candidate.
