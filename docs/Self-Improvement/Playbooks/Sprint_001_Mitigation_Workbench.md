# Sprint 001 — Mitigation Workbench (Draft)

## Goal

Process the "What could go wrong" list as a single sprint, identify common controls, and avoid one-off fixes.

## Working Method

- Treat each risk as a testable failure mode.
- Map to one or more shared mitigations.
- Prioritize mitigations that reduce multiple risks (Venn overlap).

## Risk-to-Control Matrix

| Risk | Control Family | Shared With | Priority | Owner | Status |
|---|---|---|---|---|---|
| Wrong-memory lock-in | Admission gate + TTL + quarantine | stale replay, policy bypass | P0 | TBD | Open |
| Stale fix replay | TTL + freshness check + revalidation | lock-in, success illusion | P0 | TBD | Open |
| Secret leakage | Redaction + denylist + safe logging | telemetry noise, policy bypass | P0 | TBD | Open |
| Retry amplification | Retry cap + blast-radius guard | wrong branch/push risks | P1 | TBD | Open |
| Cross-agent divergence | Shared schema + precedence rules | stale replay, lock-in | P1 | TBD | Open |

## Venn-Style Common Controls

### Control A — Memory Admission Policy
Covers:
- wrong-memory lock-in
- stale fix replay
- policy bypass

### Control B — Runtime Safety Guard
Covers:
- retry amplification
- success metric illusion
- false trust in registry

### Control C — Observability Hygiene
Covers:
- secret leakage
- telemetry noise
- cross-agent divergence

## Sprint Deliverables

1. Approved memory admission schema
2. Quarantine/demotion rules
3. Runtime retry + escalation contract
4. Redaction policy for all logs/memory
5. PDR + ADR for implementation handoff

## Definition of Done

- Every P0 risk has at least one implemented control.
- Controls are tested with failure-injection cases.
- Known solutions can be promoted, quarantined, and expired deterministically.
