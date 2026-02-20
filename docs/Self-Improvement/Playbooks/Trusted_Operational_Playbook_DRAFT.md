# Trusted Operational Playbook (Draft)

## Purpose

Define how a candidate solution becomes a **trusted operational playbook** that can be executed deterministically by orchestrators.

## Practical Model

### Phase A — Discovery (Probabilistic Allowed)

Inputs:
- Session logs
- Telemetry failures
- Human notes
- Agent-generated proposals

Outputs:
- Candidate solution artifacts
- Assumptions and uncertainty list

### Phase B — Refinement (Structured)

Inputs:
- Candidate artifacts from Phase A
- Follow-up questions raised by reviewers

Outputs:
- Narrowed candidate set
- Explicit test plans

### Phase C — Validation & Scoring (Deterministic Gate)

Inputs:
- Refined candidates
- Objective tests

Required checks:
- Reproducible test pass
- Policy/safety pass
- Secret redaction pass
- Rollback/containment strategy documented

Outputs:
- Scored decision package

### Phase D — Promotion Decision

Decision options:
- **PROMOTE** → add to known solutions as operational playbook
- **QUARANTINE** → keep for observation, do not auto-apply
- **REJECT** → archive with rationale

## Admission Rules for Known Solutions

A known solution is eligible for promotion only when it has:

1. `deterministic_steps` (explicit executable sequence)
2. `validation_proof` (test run IDs or artifacts)
3. `confidence_score` (0.0–1.0)
4. `expires_at` (TTL)
5. `max_failures` before quarantine
6. `owner` and escalation contact

## Runtime Behavior

At execution time:

1. Resolve primary trusted skill from registry.
2. Execute and validate outcome.
3. On failure, lookup known solution by error code/pattern.
4. Retry once with the matched playbook.
5. If retry fails, **hard stop** and escalate.

## Non-Goals (for now)

- Autonomous code generation in production runtime
- Unlimited retries
- Silent self-modification without review
