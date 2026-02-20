# Controlled Infrastructure Policy

## Purpose

Protect critical system components from accidental or malicious mutation while enabling safe, auditable evolution.

## Policy Statement

All controlled-infrastructure components are **read-only by default** and **system-mutated by policy-controlled paths only**.

## Controlled Infrastructure

This policy applies to:

1. Registry and registry lifecycle tooling
2. Memory stores and memory transition tooling
3. Orchestrator and workflow runners
4. Guardrail/policy enforcement modules
5. Any script or skill that can mutate the above

## Core Requirements

### 1) Safe Defaults

- No-argument execution of infrastructure scripts must be read-only.
- Default output must be informational (`--info` equivalent) with no side effects.
- Destructive/mutating operations must require explicit opt-in flags (e.g., `--apply`, `--build --force`).

### 2) Mutation Controls

- Mutation requires explicit intent and authorized identity.
- Mutation paths must emit structured audit events.
- Mutation without policy authorization must fail closed.

### 3) Guardrail Testability

All controlled scripts/skills must have tests for:

- No-arg read-only behavior
- Blocked mutation without explicit opt-in
- Dry-run/read-only path availability
- Non-zero exit on blocked unsafe operations
- Clear safety messaging

### 4) Certification Gate

Candidate code artifacts (skill/script/workflow) are not promotable unless guardrail tests pass.

### 5) Wrapper Rule

If a candidate artifact lacks native guardrails, it must run behind an execution wrapper enforcing this policy.

## RBAC Alignment

See `RBAC_Model.md`.

## Break-Glass Exception

Emergency mutation path is allowed only when all are true:

- Incident ticket exists
- Dual approval is recorded
- Scope is minimized
- Full audit trail is captured
- Post-incident review is completed

## Human vs System Mutation

Default target model:

- Humans: specify intent/specs and approve changes
- System: executes controlled mutation paths

This maps to your architecture direction ("write specs, mutate through certified system paths").

## Self-Improvement Level (Proposed Level 6)

Level 6: **Self-improvement through governed evolution**.

Definition:

- The system evolves itself via policy-constrained, test-validated, auditable mutation pipelines.
- Human role shifts from direct code mutation to specification, approval, and governance review.

## Adoption Sequence

1. Label infrastructure scripts/skills
2. Enforce no-arg read-only contract
3. Add guardrail tests
4. Gate promotion on certification
5. Enable wrapper fallback for non-compliant candidates
6. Introduce RBAC and break-glass process
