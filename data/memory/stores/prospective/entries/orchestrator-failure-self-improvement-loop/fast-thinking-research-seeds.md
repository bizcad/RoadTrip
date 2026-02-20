# Fast Thinking Research Seeds — Self-Improvement Loop

## Purpose
Generate low-cost experiments to evaluate whether orchestrator-failure routing improves reliability and learning velocity.

## Hypotheses

### H1: Failure packets with structured evidence increase fix quality
- Fast test: compare ad-hoc retries vs evidence-packed prospective entries.
- Measure: recurrence rate, time-to-fix, false-fix rate.

### H2: Hot-list + watch directory reduces remediation latency
- Fast test: enable watch trigger for one failure class.
- Measure: mean-time-to-first-attempt, queue age distribution.

### H3: Working-lane transitions reduce duplicate remediation attempts
- Fast test: enforce move to working on agent start.
- Measure: duplicate-attempt count and collision frequency.

### H4: Promotion with fingerprint+registry reduces repeated failures
- Fast test: run same workflow after promoted fix.
- Measure: pass-rate delta and regression incidence over N runs.

### H5: Sleep-cycle pull outperforms event-only solving under bursty failures
- Fast test: compare two modes for one week each:
	- mode A: event-only immediate solving,
	- mode B: event enqueue + bounded sleep-cycle pull.
- Measure: queue age, dropped/duplicated work, system stability, token budget adherence.

### H6: Effort-tier compression improves cost without quality loss
- Fast test: for one recurring task class, start expensive-first, then promote to fast-registry once confidence threshold is met.
- Measure: fast-lane win rate, escalation rate, cost per successful resolution, rollback rate.

### H7: History-aware routing reduces unnecessary expensive solves
- Fast test: add "seen-before + prior-cost" check before lane selection.
- Measure: expensive-lane invocation rate, mean tokens per resolved issue, quality regression rate.

### H8: HITL budget gate prevents instability during early rollout
- Fast test: require HITL approval for budget cap overrides and high-risk classes.
- Measure: budget breach count, incident rate, operator intervention load.

## One-Sprint Experiment Plan
1. Choose one non-security failure class.
2. Implement prospective entry creation with evidence bundle.
3. Simulate agent invocation (manual first) and move item prospective -> working.
4. Validate fix with predefined criteria.
5. Capture outcome and either promote or return to prospective with notes.
6. Run queueing A/B (event-only vs sleep-cycle pull).
7. Run effort-tier compression trial (expensive -> fast-registry).
8. Add history-aware routing check (seen-before + prior-cost) and compare against baseline.
9. Add HITL budget override gate and track stability/cost outcomes.

## Promotion Criteria to Working Design Proposal
Promote this concept if:
- >=2 independent replications show improved recurrence metrics,
- no safety policy regressions are observed,
- transition semantics (prospective/working/resolved) are deterministic and auditable.

## Additional Metrics to Capture
- fast_lane_win_rate
- escalation_rate
- cost_per_success_by_lane
- queue_overflow_incidents
- budget_breach_count (time/token/item caps)
- expensive_lane_invocation_rate
- mean_tokens_per_resolved_issue
- hitl_override_rate
