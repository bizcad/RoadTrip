# Escalation Operating Model (Fast Thinking)

## Reframed question
The issue is not "no escalation contract." The issue is "which escalation mode is correct for this workload and what budget governs it?"

## Core principles
- Escalation can be productive when explicitly bounded.
- SLA acts as a budget constraint (time + attention + cost), not just a minimum availability metric.
- Workloads require different contracts: user-on-demand, nightly maintenance, and always-on services.

## Mode selection
- `social_loop_bounded`: preferred when quality, judgment, or policy interpretation needs human/agent iteration.
- `hard_stop_handoff`: preferred when safety/policy checks fail and further automation increases risk.
- `autonomous_retry_then_handoff`: preferred for transient/runtime failures with low blast radius.

## Service tiers
- `interactive_critical`: user waiting now; prioritize responsiveness and minimal hops.
- `interactive_standard`: user task with moderate urgency.
- `scheduled_maintenance`: nightly memory reorg, backup alignment, cleanup, and compaction windows.
- `continuous_24x7`: capabilities that must be available regardless of local machine state.

## Budget contract fields
- response target (minutes)
- max escalation hops
- allowed automation depth
- owner and backup owner
- stop condition and containment path

## Metrics
- on_time_handoff_rate by tier
- escalation_hop_distribution
- budget_overrun_rate
- overnight_job_completion_slo
- user_wait_time_p95 for interactive tiers

## Guardrails
- No escalation without an assigned owner.
- No unlimited social loop; enforce hop cap by tier.
- No tierless incident; every event must declare service tier.
- If tier metadata is missing, default to `interactive_standard` and emit policy warning.
