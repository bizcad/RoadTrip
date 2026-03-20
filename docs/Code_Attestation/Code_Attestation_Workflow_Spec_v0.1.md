# Code Attestation Workflow Specification

Project: RoadTrip / PPA control plane planning
Version: 0.1-draft
Date: 2026-03-18
Status: Planning specification (no implementation yet)

---

## 1. Purpose

Define a deterministic, evidence-based workflow that decides whether code selected by the orchestrator is trusted enough for the requested action.

This specification addresses completion bias, reasoning-output drift, and false confidence from non-independent verification.

Core principle:

- Trust executable evidence, not explanation chains.
- No model grades its own homework.

---

## 2. Problem Statement

Three failure modes must be controlled:

1. Completion bias in the author model
- The generator can produce tests that mirror its own implementation and still miss real defects.

2. Logic chain vs recommendation drift
- Model rationale can sound coherent while output is incorrect.
- Reasoning text is not accepted as correctness evidence.

3. Attestation without independence
- Fingerprint and signature prove integrity and origin.
- They do not prove behavior against workflow intent.

---

## 3. Independence Requirement

Correctness verification must be independent of artifact generation.

Policy requirement:

- Evaluator identity must differ from generator identity.
- Prefer evaluator family/provider difference for higher-risk tiers.
- Deterministic verifiers (compiler, proof checker, policy engine) are first-class independent checks.

---

## 4. Trust Ladder

The orchestrator consumes trust_level as a deterministic field produced by verification pipeline outputs.

1. untrusted
- Artifact exists.
- No accepted verification evidence.

2. basic
- Compiler/type checks pass.
- Minimal static hygiene checks pass.

3. verified
- basic requirements pass.
- Independent adversarial testing passes.
- mutation_score_pct meets threshold.
- Evaluator is not the generator.
- Security gates pass.
- Proof gate passes when postconditions are declared for proof-eligible code.

4. attested
- verified requirements pass.
- Human SME signs off.
- Identity-backed sign-off captured (Entra principal or equivalent).

---

## 5. Fragment Front Matter Additions

Add two sections to fragment schema: postconditions and attestation.

## 5.1 Postconditions Section

Postconditions are contract-level intent statements consumed by:

- Formal proof flow (Lean/Leanstral + checker)
- Independent adversarial test generation

Example schema:

```yaml
postconditions:
  contract_version: "1.0"
  statements:
    - id: "pc-001"
      text: "For valid principal scope, returned SecretBundle contains only keys within that scope."
      severity_if_violated: "critical"
    - id: "pc-002"
      text: "Function returns deterministic result for same inputs and same vault state snapshot."
      severity_if_violated: "high"
  proof_required: true
```

## 5.2 Attestation Section

Attestation is an evidence bundle stored as node metadata and front matter.

```yaml
attestation:
  provenance:
    generator_model: "claude-sonnet-4-6"
    generator_model_version: "20250514"
    prompt_hash: "sha256:{prompt-hash}"
    toolchain_hash: "sha256:{toolchain-hash}"
    build_reproducible: true
    signed: true
    signature_method: "cosign"
    provenance_level: "slsa-2"
    sbom_hash: "sha256:{sbom-hash}"

  correctness:
    test_pass: true
    test_coverage_pct: 94
    mutation_score_pct: 91
    metamorphic_tests_pass: true
    postcondition_tests_pass: true
    lean_proof_status: "pass"  # pass | fail | not-required | not-run

  independence:
    evaluator_model: "claude-haiku-4-5"
    evaluator_model_family: "anthropic"
    evaluator_differs_from_generator: true

  security:
    sast_clean: true
    dependency_scan_clean: true
    secret_scan_clean: true
    coderabbit_severity_max: 0

  operations:
    canary_result: "pass"      # pass | fail | not-run
    rollback_artifact_id: "rb-2026-03-18-001"
    error_budget_impact: "low" # low | medium | high

  computed:
    confidence_score: 0.94
    risk_tier: "medium"
    trust_level: "verified"
    policy_version: "attest-policy-v1"
```

Notes:

- confidence_score is policy-computed only.
- confidence_score is never model self-reported.
- trust_level is policy-derived from evidence and cannot be set manually.

---

## 6. Deterministic Risk-Tier Gating Policy

Risk is derived from side-effects and action class, then mapped to required evidence.

## 6.1 Risk Tier Derivation

Suggested deterministic derivation rules:

- low risk
  - read-only actions
  - no external writes
  - no irreversible side effects

- medium risk
  - reversible writes
  - bounded external effects
  - no direct spend/deploy/privilege escalation

- high risk
  - irreversible actions
  - deployment, credential changes, spend, broad data mutation
  - safety-critical behavior

## 6.2 Minimum Evidence Matrix

1. low risk requires
- signed provenance
- compiler and baseline static checks
- test_pass = true
- evaluator_differs_from_generator = true

2. medium risk requires
- low risk requirements
- mutation_score_pct >= 80
- metamorphic_tests_pass = true
- coderabbit_severity_max = 0
- canary_result = pass or not-run with approved exception

3. high risk requires
- medium risk requirements
- mutation_score_pct >= 90
- lean_proof_status = pass for proof-required postconditions
- canary_result = pass
- human SME sign-off recorded
- trust_level must be attested before EXECUTE

---

## 7. Disagreement Handling Policy

Disagreement between evidence sources is a first-class escalation signal.

Examples:

- High confidence_score with low mutation_score_pct
- Positive LLM review with failing metamorphic tests
- Passed tests with failed proof obligation

Deterministic action:

- Route to TRIAGE.
- Block promotion of trust_level.
- Require explicit resolution artifact before re-evaluation.

---

## 8. Orchestrator Gate Behavior

Orchestrator performs lookup on trust and risk policy outputs, not narrative inference.

Required behavior:

1. if trust_level = untrusted
- constitutional deny

2. if trust_level = basic
- allow only low-risk read-only execution
- medium/high risk requires HITL

3. if trust_level = verified
- allow low/medium risk execution per policy
- high risk still requires attested + HITL if configured

4. if trust_level = attested
- allow per action policy
- maintain telemetry and rollback guarantees

---

## 9. Trust Ladder Gate Criteria Updates

This spec explicitly adds these criteria to gate logic:

1. mutation_score_pct
- Required threshold by risk tier.

2. evaluator_model
- Must be present.
- Must differ from generator_model.

Recommended additional checks:

- evaluator_model_family differs from generator_model_family for medium/high risk where available.

---

## 10. Proposed Updates to unified-auth-spec-v0.2.md

Target file:
- analysis/unified-auth/ClaudeCode/unified-auth-spec-v0.2.md

## 10.1 Section 3.7 Update (Code as Trusted or Untrusted Principal)

Add the following bullets:

- Trust level is computed from attestation evidence, not set by artifact author.
- Verification independence is mandatory: evaluator_model must differ from generator_model.
- Correctness evidence includes mutation score and metamorphic test outcomes.
- For proof-required postconditions, proof status must be pass to reach verified for high-risk classes.
- Evidence disagreements trigger deterministic triage and block trust promotion.

## 10.2 Section 4.4 Update (Code-Specific Attributes)

Extend metadata schema with these fields:

```yaml
metadata:
  postconditions_ref: "contract:fragment:{id}"
  attestation_policy_version: "attest-policy-v1"

  generator_model: "claude-sonnet-4-6"
  generator_model_version: "20250514"
  prompt_hash: "sha256:{prompt-hash}"
  toolchain_hash: "sha256:{toolchain-hash}"

  evaluator_model: "claude-haiku-4-5"
  evaluator_model_family: "anthropic"
  evaluator_differs_from_generator: true

  mutation_score_pct: 91
  metamorphic_tests_pass: true
  lean_proof_status: "pass"

  canary_result: "pass"
  rollback_artifact_id: "rb-2026-03-18-001"

  confidence_score: 0.94
  risk_tier: "medium"
  trust_level: "verified"
```

---

## 11. Selling Statement

Every code node in the assembly graph carries a cryptographically bound attestation bundle. The orchestrator selects nodes by risk-tier policy, not model confidence. No model grades its own homework.

---

## 12. Implementation Planning Notes (No Code Yet)

Planned next steps:

1. schema drafting
- Formalize front matter schema for postconditions and attestation.

2. policy drafting
- Encode deterministic risk-tier matrix and trust promotion rules.

3. auth spec alignment
- Update unified-auth-spec-v0.2.md Section 3.7 and 4.4.

4. workflow integration plan
- Define pipeline stages that emit each attestation evidence field.

5. validation playbook
- Define sample artifacts at untrusted/basic/verified/attested levels.

This document is planning-only and intentionally contains no implementation code.
