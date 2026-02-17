# Coding Plan: Self-Improvement Memory System

**Workflow:** 010-memory-for-self-improvement  
**Date:** 2026-02-16  
**Status:** Ready to execute  
**Source of truth:** `PDR-self-improvement.md` + `ADR-self-improvement.md`

---

## 1) Execution Rules (Non-Negotiable)

1. No irreversible mistakes:
   - block/escalate destructive actions unless safeguards are present.
2. Deterministic-first implementation:
   - probabilistic components advise, deterministic gates decide.
3. Testing is mandatory:
   - integration, adversarial, performance, security evidence required.
4. Telemetry-gated release decisions:
   - missing telemetry on blocking metrics = No-Go.
5. Version provenance required:
   - trusted artifact versions must match fingerprint/provenance records.

---

## 2) Preflight (Must Pass Before Build)

## Gate G1: H2 Validation
- Execute manual consolidation audit protocol and capture decision record.
- Required: utility and no-harm thresholds met.

## Gate G2-G8: Readiness Confirmation
- Safety non-negotiables accepted.
- Cost + capacity guardrails approved.
- Mutation perimeter approved.
- Timeline/resources accepted.
- Mandatory testing gate criteria defined.
- Version-provenance gate criteria defined.
- Irreversible-risk gate criteria defined.

**Output artifacts:**
- H2 decision record
- preflight checklist signed (single-page)

---

## 3) Implementation Workstreams

## WS-A: Memory Foundation
**Goal:** Implement continuity and retrieval primitives.

Tasks:
1. Session Bootstrap scaffold (`recent_failures`, `active_skills`, `pending_reminders`).
2. Episodic Index scaffold (SQLite FTS5 over telemetry).
3. Retrieval trigger policy (deterministic gating path).

Done when:
- deterministic retrieval path works,
- baseline telemetry is queryable,
- no side-effect behavior in retrieval path.

## WS-B: Consolidation + Safety
**Goal:** Implement offline consolidation with complete safety stack.

Tasks:
1. Deterministic clustering/normalization pipeline.
2. Multi-criteria promotion gate (frequency/time/source/confidence).
3. Safety gate stack including semantic harm detection.
4. Quarantine path + decision telemetry.

Done when:
- harmful candidate patterns are blocked/escalated,
- safe patterns are promoted with provenance,
- gate outcomes are fully auditable.

## WS-C: Reliability Guardrails
**Goal:** Prevent catastrophic drift or irreversible failures.

Tasks:
1. Hard memory ceiling + deterministic pruning.
2. Rollback + burned-pattern cooldown.
3. Irreversible operation safeguards (pre-checks + explicit policy/confirmation).

Done when:
- ceiling breaches do not proceed silently,
- rollback prevents oscillation,
- irreversible operations require safeguards or block.

## WS-D: Trust + Version Provenance
**Goal:** Bind trusted artifact versioning to runtime verification.

Tasks:
1. Enforce version metadata presence for trusted Skills/MCP/MPC artifacts.
2. Include version fields in fingerprint/provenance inputs.
3. Add consistency checks for spec version ↔ fingerprinted artifact version.

Done when:
- provenance package verifies without drift,
- mismatches fail release gate.

---

## 4) Testing Plan (Mandatory)

## T1 Integration Tests
- End-to-end goal → selection → execution → telemetry → consolidation decision.

## T2 Adversarial Tests
- Prompt injection, goal drift, confused deputy, memory poisoning, irreversible-action attempts.

## T3 Performance Tests
- Latency, throughput, error rate on expected workload envelope.

## T4 Security Tests
- Unauthorized access attempts, trust-event tampering, fingerprint/provenance tampering.

**Pass requirement:** all mandatory suites pass with evidence attached.

---

## 5) Evidence and Release Control

Use:
- `PDR-self-improvement.md` section 10.3 Release Evidence Index
- `VERSION-PROVENANCE-PACKAGE-CHECKLIST.md`
- `ISSUE-REPRO-AND-VERIFICATION-TEMPLATE.md`

Release decision policy:
- Missing blocking telemetry/evidence = No-Go.
- Advisory gaps require explicit risk acceptance + remediation date.

---

## 6) Safe Commit Breakpoints (Solo Mode)

Use `gpush` only at stable checkpoints.

Checkpoint A — Preflight complete:
- H2 record done
- gates confirmed

Checkpoint B — Foundation stable:
- WS-A implemented + integration baseline green

Checkpoint C — Safety complete:
- WS-B + WS-C safeguards and tests green

Checkpoint D — Trust/version complete:
- WS-D checks green

Checkpoint E — Release candidate:
- full test/evidence package complete

**Commit trigger rule:**
- good compile/build and relevant test slice green,
- no unresolved critical failures,
- no irreversible-risk safeguard regressions.

---

## 7) Suggested First Sprint (Concrete)

1. Build WS-A scaffolds and deterministic retrieval gate.
2. Add WS-B deterministic clustering + promotion gate.
3. Implement semantic harm gate and quarantine telemetry.
4. Add T1 integration tests for the above.
5. Commit at Checkpoint B only when tests pass.

---

## 8) Blockers and Escalation

Stop and escalate immediately if:
- irreversible operation safeguards are bypassed,
- telemetry attribution for blocking metrics is missing,
- version provenance mismatch is detected,
- mandatory test suite cannot be executed.

---

## 9) Handoff Notes

This plan is optimized for solo execution with minimal ceremony and strict safety.
It is intentionally checkpoint-driven to preserve momentum while preventing irreversible mistakes.
