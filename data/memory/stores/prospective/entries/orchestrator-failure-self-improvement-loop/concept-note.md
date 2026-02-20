# Concept Note — Orchestrator Failure -> Problem-Solving Agent Loop

## Status
- Classification: **interesting idea**
- Confidence: **promising, needs design + validation**
- Queue lane: **prospective**

## Core Idea
Close the self-improvement loop by routing orchestrator failures into a problem-solving flow that works prospective memory items and promotes validated fixes.

## Machine-Readable Draft
- `routing-policy-v0.yaml` captures the initial routing constraints and guardrails for future automation.

## Queueing Strategy (v0 Recommendation)
Use a **hybrid pull model** with bounded event assist:

1. **Primary path: sleep-cycle pull**
   - Process a capped batch from prospective during orchestrator idle/sleep windows.
   - Enforce strict budget (max items, max runtime, max token spend).
   - Advantage: avoids event storms and preserves deterministic pacing.

2. **Secondary path: event-assisted enqueue**
   - Failures append/update evidence packets immediately.
   - Do not auto-solve every event in real time; only mark priority/hot-list.
   - Advantage: no lost signal, while execution stays controlled.

3. **Entry state handling: minimal metadata first**
   - Keep only essential state (`status`, `attempt_count`, `priority`).
   - Avoid heavy state-machine complexity until repeat pain is observed.

This balances your three concerns: state complexity, event overload risk, and practical cadence.

## Routing Policy (v0): Urgency x Cost x History
Before invoking a problem-solving agent, route each item by:

1. **Urgency** (SLA/impact): low, medium, high.
2. **Budget envelope**: token cap + allowed spend for this cycle.
3. **Historical precedent**: have we seen this class before, and what did remediation cost?

### Decision heuristic
- If known class + high prior success in fast lane -> run registry lookup first.
- If unknown class but low urgency and low risk -> queue for sleep-cycle processing.
- If high urgency and high risk -> HITL triage first, then controlled execution.
- If budget cap would be breached -> defer to next cycle or escalate HITL for override.

### Cost-aware objective
Use the cheapest lane that satisfies safety and quality constraints:
`fast lookup -> medium effort -> expensive agentic solve`.

Escalate only when confidence drops or validation fails.

### Mental model
```csharp
$("go solve the problem addressed in data/memory/stores/prospective/entries/{entry}");
```

## Proposed Flow (v0)
1. **Orchestrator executes workflow**.
2. If success -> normal completion.
3. If failure -> create/update prospective entry with evidence packet.
4. Mark entry as hot-list/watch candidate.
5. Launch problem-solving agent using approved SDK + skills/MCP/workflows.
6. Move item to working lane while in progress.
7. On solved/validated:
   - fingerprint output,
   - register capability,
   - attach provenance + tests.
8. On unresolved:
   - return to prospective with new evidence and next-attempt strategy.

## Why this matters
- Replaces fixed one-retry failure pattern with evidence-driven remediation.
- Creates a repeatable path from failure -> candidate fix -> vetted capability.
- Enables structured autonomous self-improvement without bypassing safety gates.

## Guardrails
- No direct production mutation without policy checks.
- Require objective pass criteria before promotion to registry.
- Preserve auditable trace: failure evidence, agent actions, validations, fingerprint.
- Escalate to human review for security/auth/safety-sensitive failures.
- Enforce per-cycle token/time/item budgets; no uncapped autonomous loops.
- Prefer free/low-cost resources by default unless explicit override is approved.

## HITL-First Rollout Guidance
For early deployment, keep Human-In-The-Loop as the default for:
- budget overrides,
- high-urgency/high-risk failures,
- promotions into registry when evidence is borderline.

This keeps the system alive and controlled while policies mature.

## Candidate Data Model (minimum)
- `entry_id`
- `origin_workflow`
- `failure_class`
- `evidence_paths[]`
- `attempt_count`
- `status` (prospective|working|quarantine|resolved)
- `hot_list` (bool)
- `priority` (low|medium|high)
- `queued_at`
- `urgency`
- `token_budget_cap`
- `historical_cost_to_resolve`
- `historical_success_by_lane`
- `validation_result`
- `fingerprint_id` (optional)

## Additional Self-Improvement Vector: Metric-Driven Cost Compression
Another path beyond failure-handling is **effort-tier optimization**:

1. Start with expensive reasoning path for uncertain tasks.
2. Track when expensive path converges to stable, repeatable outcomes.
3. Promote these outcomes into fast-thinking registry lookups.
4. Route future similar tasks to fast lane by default, with fallback to medium/expensive on confidence drop.

### Target behavior
- Early phase: expensive path dominates.
- Mature phase: fast lookup dominates for recurring solved classes.
- Safety: confidence/risk gates can always escalate back up.

### Suggested Metrics
- `fast_lane_win_rate` = % tasks solved correctly via registry lookup.
- `escalation_rate` = % fast-lane attempts escalated to medium/expensive.
- `cost_per_success_by_lane` (fast vs medium vs expensive).
- `promotion_success_rate` = % promoted entries that remain stable without rollback.
- `confidence_drift_rate` = how often previously-fast classes regress.

## Open Design Questions
1. What failure classes are eligible for autonomous problem-solving vs mandatory human review?
2. What is the max autonomous attempts before quarantine/escalation?
3. Should hot-list be explicit flag, folder watch, or both?
4. What defines "solved" for promotion (tests, scenario holdouts, runtime success, rollback checks)?
5. How should working/prospective transitions be represented atomically?
6. What budget should sleep-cycle processing enforce per cycle (items/time/tokens)?
7. What confidence threshold triggers promotion from expensive path to fast-registry lane?
