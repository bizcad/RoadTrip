# Evaluation Model (Fast Thinking)

## Reframed problem
"Success" is not a scalar. It is context + consequence.

## Why benchmark-style success can fail users
- Benchmarks often reward average-case correctness, not high-cost edge misses.
- Public-score optimization can overweight what looks good and underweight what protects users.
- Aesthetic quality (for example "lovely photos") is valid, but only in tasks where aesthetic output is the purpose.

## Purpose-first metric stack
Every workflow is scored on four independent axes:
1. Utility outcome: did the task achieve the user’s real objective?
2. Harm avoidance: did we avoid high-cost misses?
3. User trust: would the user delegate this again?
4. Aesthetic quality: did output quality match task expectations?

## Asymmetric risk rule
For critical-signal workflows (doctor, bank, legal, safety):
- One critical miss outweighs many routine successes.
- Gate by `critical_miss_rate` and `harm_weighted_error`, not aggregate pass rate.

## Suggested formulas
- `purpose_score = 0.45*utility + 0.35*harm_avoidance + 0.15*trust + 0.05*aesthetic`
- `harm_weighted_error = sum(error_count_i * impact_weight_i)`

Where impact weights increase with severity, for example:
- cosmetic miss = 1
- operational miss = 5
- critical signal miss = 25

## Tier-specific gate examples
- `critical_signal`: require critical_miss_rate = 0 in validation window.
- `operational`: allow low miss rate with bounded correction latency.
- `cosmetic`: prioritize quality preference and user taste alignment.

## Human factors note
"Good taste" has no universal metric. Treat taste as preference alignment:
- explicit user style profile,
- satisfaction feedback,
- consistency with declared intent.

## Guardrails
- No go/no-go decision from one vanity metric.
- No model benchmark score accepted as production safety proxy.
- Always report score decomposition by axis and by tier.
