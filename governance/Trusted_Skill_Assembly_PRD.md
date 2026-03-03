# Feature PRD: Trusted Skill Assembly and Secure Runner Supply Chain

## Document Metadata
- Product: RoadTrip
- Feature: Trusted Skill Assembly
- Date: 2026-02-25
- Source Conversation: PromptTracking/Session Log 20260225.md
- Status: Draft for implementation planning

## Governance Alignment (Existing Baselines)
This PRD extends and operationalizes governance already defined in this folder:
- `governance/README.md` (scope and default read-only principle)
- `governance/Controlled_Infrastructure_Policy.md` (safe defaults, mutation controls, wrapper rule)
- `governance/RBAC_Model.md` (role boundaries, deny-by-default mutation)
- `governance/Certification_Checklist.md` (promotion gate and evidence criteria)

Implementation decisions in this PRD should be interpreted as additive to those baselines, not replacements.

## 1) Executive Summary
RoadTrip should evolve from script-first skill execution toward a contract-first, registry-driven, multi-runtime assembly model. The core idea is to keep skill identity stable while allowing implementation migration (Python/PowerShell to C#) behind the same contractual interface. 

The main expected gain is not only per-skill runtime speed, but system-level improvements in reliability, diagnosability, governance, and Zero Trust posture. This feature defines how certified workflow assemblies, trusted execution paths, and normalized production incident feedback can create self-improving and secure operations.

## 2) Reasoning Captured from Conversation
The design reasoning progressed through these conclusions:

1. A skill can be reimplemented in another language without changing orchestration semantics if the contract remains stable.
2. For many skills, compiled performance gain is incremental; the larger gain is workflow-level performance and reliability.
3. Registry-driven runtime selection enables implementation upgrades while preserving skill behavior and compatibility.
4. Zero Trust alignment improves when execution is bound to signed artifacts, least-privilege RBAC, deterministic policy checks, and auditable provenance.
5. Certified workflow assemblies (composed from contractual skills) can form a trusted code supply chain.
6. Catch blocks should emit normalized incident objects and route to remediation mechanisms.
7. Incidents should create both human-readable and machine-readable GitHub issues for rapid triage and automated follow-up.
8. End-to-end attestation reduces silent hallucination risk by constraining execution to approved contracts and policies.

RoadTrip framing retained: problems create deterrents ("probs create deters").

## 3) Problem Statement
Current execution is primarily script-oriented and implementation-coupled. This can introduce:
- Runtime variability across environments.
- Weaker contract enforcement between orchestrator and skills.
- Limited provenance confidence for production incidents.
- Slower operational correction cycles due to inconsistent diagnostics.

RoadTrip needs a contract-centric execution architecture where implementation can evolve without destabilizing behavior, while security and traceability increase.

## 4) Goals and Non-Goals
### Goals
- Support multi-runtime skill implementations under one immutable skill identity.
- Introduce runner-based execution with normalized result and incident envelopes.
- Enable certified workflow assemblies with RBAC, fingerprinting, and provenance.
- Improve Zero Trust controls across source, build, artifact, and runtime.
- Implement closed-loop self-improvement via incident-to-fix workflows.

### Non-Goals
- Immediate full rewrite of all existing Python skills.
- Autonomous production auto-promotion without policy gates.
- Eliminating all failures; objective is bounded, diagnosable failures.

## 5) Functional Requirements
### FR-1 Skill Contract Stability
- Each skill has a stable skill_id.
- Multiple runtime variants may exist for one skill_id.
- Inputs/outputs follow versioned schemas.

### FR-2 Registry Runtime Variants
Registry entries must support at minimum:
- runtime
- entry_point
- contract_version
- deterministic flag
- idempotent flag
- artifact_type
- timeout
- checksum/fingerprint
- required_rbac_scope

### FR-3 Runner Process Model
- Orchestrator selects runtime variant by policy.
- Runner executes skill in isolated process.
- Runner returns normalized result object:
  - decision
  - success
  - artifact reference
  - errors/warnings
  - telemetry id
  - duration

### FR-4 Equivalence and Promotion
- New runtime variants run in shadow mode.
- Outputs are compared against baseline implementation.
- Promotion requires parity threshold and policy/test gates.

### FR-5 Certified Workflow Assembly
- Workflow is represented as assembly graph of contractual skills.
- Assembly artifact includes fingerprint, provenance, policy snapshot, and test evidence.
- Only certified assemblies are eligible for production execution.

### FR-6 Incident Normalization and GitHub Issue Emission
- On failure, emit normalized incident object with deterministic fingerprint.
- Incident pipeline de-duplicates by fingerprint and workflow context.
- Create/update GitHub issue with:
  - concise human summary
  - machine-readable JSON section
  - links to telemetry, logs, artifact identity, and run context

### FR-7 Self-Improving Remediation Wiring
- Catch paths route to typed remediation handlers (retry, quarantine, policy block, patch suggestion).
- Remediation outputs create candidate fixes and verification tasks.
- Production promotion remains gated until confidence and policy criteria pass.

## 6) Security and Zero Trust Requirements
- RBAC principal required for orchestrator and runner identities.
- Least privilege per skill capability and resource scope.
- Signed source tags/commits for promoted builds.
- Reproducible build requirements for certified runners.
- Artifact signing and hash verification before execution.
- SBOM generation and retention for certified artifacts.
- Immutable audit logs for run identity and policy decisions.
- Secret and PII redaction before issue creation.

### Baseline Mapping
- Read-only by default and explicit mutation intent requirements inherit from `governance/Controlled_Infrastructure_Policy.md`.
- Role boundaries and mutation authorization model inherit from `governance/RBAC_Model.md`.
- Promotion/certification evidence requirements inherit from `governance/Certification_Checklist.md`.
- Folder-level governance scope and controlled component coverage inherit from `governance/README.md`.

## 7) Architecture Overview
### Components
- Skill Registry: contract + runtime variant metadata.
- Orchestrator: policy-aware dispatcher.
- Runner Host: process isolation and normalization.
- Contract Validator: schema and version checks.
- Incident Pipeline: normalization, dedupe, issue publication.
- Certification Gate: tests, policy checks, provenance checks.

### Data Objects
- Skill Contract
- Assembly Manifest
- Normalized Result
- Normalized Incident
- Certification Record

## 8) Operational KPIs
- P95 skill execution latency.
- Mean time to remediation for production incidents.
- Policy violation rate per 1000 executions.
- Runtime parity drift rate (baseline vs candidate).
- Unauthorized capability attempts blocked.
- Certified assembly adoption rate.

## 9) Risk Model (Probs -> Deters)
- Prob: Runtime drift between Python and C#.
  - Deter: Contract tests, golden fixtures, shadow mode parity checks.
- Prob: Credential/prompt deadlock in automation.
  - Deter: Noninteractive auth policy and runner preflight checks.
- Prob: Unsafe side effects.
  - Deter: Idempotency metadata, preflight policy chain, scoped RBAC.
- Prob: Issue spam/noise from repeated failures.
  - Deter: Fingerprint-based dedupe and issue update strategy.
- Prob: Hallucinated remediation.
  - Deter: Deterministic evidence links and gated promotion.

## 10) Rollout Plan (MVP to Hardened)
### Phase 1: Contract and Runner MVP
- Add runtime variant schema to registry.
- Implement runner result envelope.
- Pilot with one deterministic skill (git_push_autonomous pathway).

### Phase 2: Incident and Issue Loop
- Emit normalized incidents from runner failures.
- Auto-create/update GitHub issues with dual-format payload.
- Add ownership routing and severity labels.

### Phase 3: Certification Pipeline
- Add parity gate, policy gate, and provenance gate.
- Produce certified assembly manifest artifacts.
- Enforce production-only certified execution.

### Phase 4: Self-Improvement Control Loop
- Connect typed remediation handlers.
- Auto-generate fix candidates and validation tasks.
- Keep promotion human-gated until confidence target is sustained.

## 11) Acceptance Criteria
- A skill_id can run with at least two runtime variants under one contract.
- Runner output is fully normalized and consumed by orchestrator.
- At least one failure path creates a de-duplicated GitHub issue with machine-readable payload.
- Assembly manifest includes fingerprint, provenance, and gate outcomes.
- Production execution rejects uncertified assembly artifacts.

## 12) Open Questions
- Should certification confidence thresholds vary by skill criticality tier?
- What is the minimum parity window before promoting a new runtime variant?
- Which fields in incident payload are mandatory for legal/compliance retention?

## 13) Reference
- PromptTracking/Session Log 20260225.md
- governance/README.md
- governance/Controlled_Infrastructure_Policy.md
- governance/RBAC_Model.md
- governance/Certification_Checklist.md
