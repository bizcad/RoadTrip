# ADR: Self-Improvement Memory System

**Document ID:** ADR-self-improvement  
**Date:** 2026-02-16  
**Status:** Proposed for acceptance (intended to become binding for implementation)  
**Scope:** RoadTrip Personal Assistant memory, consolidation, and self-improvement loop

---

## Decision Summary

This ADR establishes the binding architecture and governance decisions for implementing self-improvement memory in RoadTrip.

### Binding Outcomes
1. Use a local-first, file-based memory architecture with deterministic controls.
2. Treat probabilistic reasoning as advisory, never as an unguarded execution authority.
3. Require pre-implementation H2 validation as a hard gate.
4. Enforce safety and cost controls as non-negotiable release criteria.
5. Permit minimal topology learning metadata, but prohibit autonomous topology rewiring in this phase.
6. Enforce mandatory testing and inspection gates before coding-plan approval and release.
7. Enforce versioned trust artifacts and bind version metadata into fingerprint/provenance verification.
8. Enforce irreversible-operation safeguards as a blocking safety constraint.

---

## Context

RoadTrip evolved from a travel app into a personal assistant platform with explicit principles:
- conservative defaults,
- deterministic code for reliability,
- security-first behavior,
- auditability and recoverability.

The PRD iterations define a strong direction but remain split across multiple documents. This ADR resolves decision ambiguity and codifies implementation boundaries.

---

## Architectural Decisions

## ADR-001: Local-First Memory Architecture
**Status:** Accepted  
**Decision:** Memory remains local and human-readable with file artifacts as primary state.

**Rationale:**
- preserves observability,
- enables manual recovery,
- aligns with deterministic governance,
- avoids opaque vendor-managed memory loops.

**Consequences:**
- Pros: transparency, git traceability, low lock-in.
- Cons: additional local orchestration complexity.

---

## ADR-002: Deterministic-First Control Plane
**Status:** Accepted  
**Decision:** Execution control remains deterministic. Probabilistic components may propose but cannot bypass deterministic gates.

**Rationale:**
- consistent with “deterministic correctness creates reliability,”
- reduces unsafe variance in autonomous behavior.

**Consequences:**
- Pros: repeatability, testability, safer automation.
- Cons: less flexibility in novel edge cases unless explicitly escalated.

---

## ADR-003: Three Operational Components + Consolidation Bridge
**Status:** Accepted  
**Decision:** Standardize component naming to reduce ambiguity:
- Memory Core (always-on memory),
- Session Bootstrap (predictive context loading),
- Episodic Index (searchable telemetry history),
- Consolidation Engine (offline sleep cycle bridge).

**Rationale:**
- removes layer-number drift,
- creates direct mapping to implementation workstreams.

**Consequences:**
- Pros: cleaner decomposition, clearer ownership.
- Cons: requires migration of wording from prior PRD docs.

---

## ADR-004: Preflight Gate Is Mandatory (H2 Validation First)
**Status:** Accepted  
**Decision:** Coding does not start until H2 validation passes defined thresholds.

**Rationale:**
- avoids building automation on low-signal telemetry,
- reduces wasted implementation effort.

**Pass criteria (binding):**
- hit-rate threshold met,
- multi-rule activation threshold met,
- zero harm events,
- minimum rule coverage met.

**Consequences:**
- Pros: evidence-based go/no-go.
- Cons: delays build start when signal is weak.

---

## ADR-005: Safety Controls Are Non-Negotiable
**Status:** Accepted  
**Decision:** Consolidation updates must pass all safety gates, including semantic harm detection and policy checks.

**Rationale:**
- prompt/data poisoning is a known realistic failure mode,
- synthetic rules are high-impact artifacts and must be constrained.

**Consequences:**
- Pros: safer self-improvement loop.
- Cons: may reduce promotion throughput.

---

## ADR-006: Hard Ceiling and Deterministic Pruning
**Status:** Accepted  
**Decision:** Memory size has hard limits with deterministic pruning and archive rules.

**Rationale:**
- prevents context saturation and cognitive drift,
- enforces long-term maintainability.

**Consequences:**
- Pros: bounded memory growth and predictable costs.
- Cons: requires explicit retention governance and archival hygiene.

---

## ADR-007: Cost Guardrails With Model Enforcement
**Status:** Accepted  
**Decision:** Consolidation uses an explicitly allowed low-cost model profile and logs cost per run.

**Rationale:**
- prevents silent cost escalation,
- aligns with low-cost continuous operation goals.

**Consequences:**
- Pros: stable monthly spend.
- Cons: potentially lower synthesis richness in edge cases.

---

## ADR-008: Rollback + Cooldown Anti-Oscillation Policy
**Status:** Accepted  
**Decision:** Rolled-back patterns enter cooldown and cannot be immediately re-promoted.

**Rationale:**
- prevents retry/revert loops,
- preserves stability after incident response.

**Consequences:**
- Pros: better operational resilience.
- Cons: slower re-introduction of corrected variants.

---

## ADR-009: Minimal DyTopo in This Phase
**Status:** Accepted with constraint  
**Decision:** Allow metadata-level topology learning only; disallow autonomous graph rewiring and auto-invocation changes.

**Rationale:**
- captures useful learning without destabilizing control flow,
- respects deterministic governance in current maturity stage.

**Consequences:**
- Pros: incremental capability gain with bounded risk.
- Cons: full dynamic orchestration value is deferred.

---

## ADR-010: Human Escalation Model for “No Interference” Goal
**Status:** Accepted  
**Decision:** Interpret “without my interference” as routine autonomy with safety escalation boundaries.

**Autonomy ladder:**
1. Auto-execute: low-risk, high-confidence deterministic path.
2. Auto-block: explicit policy/safety violation.
3. Manual-review queue: ambiguous high-impact actions or low-confidence risky updates.

**Rationale:**
- balances autonomy with safety,
- prevents hidden operational assumptions.

**Consequences:**
- Pros: clear intervention semantics.
- Cons: occasional review burden remains by design.

---

## ADR-011: Testing Is Mandatory and Non-Negotiable
**Status:** Accepted  
**Decision:** The program requires mandatory testing evidence across integration, adversarial, performance, and security categories as a precondition for coding-plan readiness and release readiness.

**Rationale:**
- reliability is earned by inspection, not expectation,
- trust architecture requires continuous verification under normal and hostile conditions,
- deterministic claims must be validated with reproducible evidence.

**Consequences:**
- Pros: stronger confidence in autonomous operation and safer rollout.
- Cons: increased up-front verification effort and longer readiness cycles.

---

## ADR-012: Versioned Trust Artifacts and Fingerprint Binding
**Status:** Accepted  
**Decision:** Trusted Skill and MCP/MPC artifacts must carry explicit version metadata (including front matter where used), and those version values must be included in fingerprint/provenance inputs used for trust and release verification.

**Rationale:**
- ensures traceability from specification artifact to executable trust boundary,
- prevents version drift between docs and verified runtime artifacts,
- strengthens reproducibility and rollback confidence.

**Consequences:**
- Pros: stronger artifact integrity and auditability in trusted execution paths.
- Cons: tighter release discipline required for version updates.

---

## ADR-013: Irreversible Mistake Prevention by Design
**Status:** Accepted  
**Decision:** High-impact irreversible actions must be guarded by deterministic checks, explicit confirmation/policy authorization, and auditable decision traces; missing safeguards result in block or escalation.

**Rationale:**
- irreversible mistakes are costliest and hardest to recover,
- solo operation requires defaults that fail safe without relying on constant attention,
- trust in autonomous behavior depends on proving non-execution under unsafe conditions.

**Consequences:**
- Pros: materially lower risk of catastrophic operator-impacting failures.
- Cons: additional friction on destructive operations by design.

---

## Rejected Alternatives

1. Use black-box managed orchestration loop as primary control plane.
   - Rejected due to observability and intervention limitations.

2. Full probabilistic autonomous orchestration in this phase.
   - Rejected due to safety and reliability uncertainty.

3. Immediate full dynamic topology rewiring.
   - Rejected due to change-risk and verification burden.

---

## Compliance and Governance Requirements

To be considered compliant with this ADR, the implementation spec must include:
- one canonical source-of-truth requirements doc,
- explicit preflight go/no-go criteria,
- requirement-to-evidence verification mapping,
- release gates for safety, reliability, and cost,
- rollback and incident response procedures.

---

## Supersession Rule

This ADR supersedes ambiguous or conflicting guidance across earlier PRD iterations for architecture and governance decisions in this workflow.

Any future change to these decisions requires an ADR update section with:
- change proposal,
- rationale,
- risk impact,
- acceptance authority.

---

## Approval Block

- Product Owner: ____________________  Date: __________
- Technical Reviewer: _______________  Date: __________
- Safety Reviewer: __________________  Date: __________
