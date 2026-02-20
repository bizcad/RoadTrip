# Stale Fix Replay — Pros and Cons (Fast Thinking)

## Candidate strategy
Mark stale remediation entries as deprecated_in_favor_of, let them age out by lifecycle timeout, and treat not_found similar to deprecated at runtime with explicit telemetry.

## Pros
- Reduces repeated replay of obsolete fixes.
- Preserves historical trail while steering to current leaf entry.
- Supports deterministic handling for deprecated and missing entries.
- Enables gradual cleanup (timeout/pruning) without immediate hard deletion.

## Cons / Risks
- Redirect chains can loop or become too deep.
- Newer replacement can drift semantically from original intent.
- Auto-pointer updates can be unsafe for refactors.
- Missing target artifacts can create silent fallback masking if not fail-closed.

## Guardrails
- Max chain hop limit (3).
- Cycle detection (DAG requirement).
- Capability/intent parity check before redirect.
- Fail closed when target unresolved.
- Emit explicit telemetry on every redirect and not_found substitution.

## Evidence needed
- stale-hit count and post-hit success/failure trend.
- redirect-hop distribution and cycle detection count.
- % deprecated entries retired before SLA.
- unresolved target incidents and time-to-repair.
