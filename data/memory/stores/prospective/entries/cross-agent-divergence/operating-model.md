# Cross-Agent Divergence — Operating Model (Fast Thinking)

## Core principle
Fixing an error is not equivalent to preserving intent.

## Decision model
1. Intent check first: did the change satisfy the original objective?
2. Side-effect check second: what broke adjacent behavior?
3. Trust check third: was the change policy-compliant and auditable?

## Retry budget policy (proposal)
- Default loop budget: 2 attempts.
- Attempts 3-5: only with explicit escalation reason and narrowed blast radius.
- Above 5: disallowed without human approval and SME review.
- Hard stop if intent confidence decreases after a retry.

## Communication modes
- supportive_consensus (default): cooperative drafting and convergence.
- adversarial_review: challenge assumptions and hidden failure modes.
- independent_judge: final arbitration when modes disagree.

## Schema governance rule
- If agent schemas differ, neither is implicitly authoritative.
- Resolve using compatibility contract:
  - required fields intersection
  - transformation mapping with tests
  - versioned schema decision record

## Specialist strategy
- Use mission-based specialist cells, not fixed department org charts.
- A cell forms around a specific problem/opportunity, then dissolves when done.
- Cells can mix domains (for example: accounting + workflow + UX) when the mission requires it.
- Not all cells are temporary: recurring process cells are valid (for example nightly memory management jobs).
- Every specialist/cell requires:
  - objective
  - success metric
  - expiry/retirement condition
  - recall trigger (what event should wake it again)
- Prune specialists with low value or stale usage to control complexity.

## Operating modes: job-cost vs process-cost
- Job-cost mode (discrete mission): one-off or finite objective, then dissolve.
- Process-cost mode (recurring pipeline): stable repeated flow with scheduled execution and continuous improvement.
- Both modes should coexist under one governance layer.
- Cron-style workloads (for example memory hygiene) belong in process-cost mode.

## Cell lifecycle model (proposal)
1. Spawn: open a cell when baseline workflow underperforms or a new opportunity appears.
2. Operate: run bounded experiments with explicit intent-preservation checks.
3. Package: when solved, persist playbook + tests + interface contract.
4. Cold store: deactivate active scheduling/routing for dormant capabilities.
5. Warm recall: reactivate when trigger conditions match (provider, domain, risk profile).
6. Re-certify: run smoke checks before full routing.

## Example implications
- "GitHub push" capability can be cold-stored when not needed.
- If push target changes to Bitbucket, trigger warm recall of push-specialist cell or spawn a new provider-specific cell.
- "Bank deposit accounting" and "trade show operations" should be separate mission cells with distinct metrics and retirement criteria.
- "YouTube scripting/presenting" and "YouTube publishing" should usually be separate specialists; forcing one agent to do both increases coupling and coordination risk.

## SOLID-style capability boundaries
- Single responsibility: each specialist owns one coherent capability surface.
- Open/closed: extend with new specialists or wrappers, avoid rewriting stable cells.
- Liskov-style substitution: replacement specialists must preserve intent contract and outputs.
- Interface segregation: keep contracts narrow so consumers depend only on needed fields.
- Dependency inversion: workflows depend on capability interfaces, not concrete agent implementations.

## Multi-instance evolution (per-user adaptation)
- Different project instances should evolve differently for different user contexts.
- Keep a shared core (safety policy, trust gates, telemetry schema), but allow local specialization.
- Treat each deployment as a profile with its own:
  - priorities and risk tolerance
  - specialist mix
  - retry/escalation thresholds
  - retention/TTL defaults
- Portability rule: share patterns and interfaces, not forced identical behavior.
- Governance rule: instance-specific overrides must remain auditable and reversible.

## SME escalation contract
Escalate when:
- retry budget exceeded,
- intent confidence below threshold,
- security/compliance risk detected,
- schema conflict unresolved.

## Minimal metrics
- intent_preservation_rate
- post_fix_regression_rate
- retries_per_task
- escalation_rate
- specialist_roi

## Fast-to-slow promotion criteria
Promote to slow-thinking implementation only after:
- >=3 real observations,
- measurable improvement trend,
- rollback path defined,
- governance owner identified.
