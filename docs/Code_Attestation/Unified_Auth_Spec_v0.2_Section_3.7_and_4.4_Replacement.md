# Replacement Text for unified-auth-spec-v0.2 Section 3.7 and 4.4

<!--
Replacement note:
This document is a replacement draft for two sections in the original file:
analysis/unified-auth/ClaudeCode/unified-auth-spec-v0.2.md
- Section 3.7: Code as a Trusted (or Untrusted) Principal
- Section 4.4: Code-Specific Attributes
Use this file as the authoritative replacement language for those two sections.
-->

Date: 2026-03-18
Status: Replacement draft for review
Source file: analysis/unified-auth/ClaudeCode/unified-auth-spec-v0.2.md

---

## Replacement for Section 3.7 Code as a Trusted (or Untrusted) Principal

- Code trust is evidence-derived and policy-computed, never self-declared by the producing model or author.
- Provenance evidence is mandatory but insufficient on its own. Signature, fingerprint, and SBOM prove integrity and lineage, not behavioral fitness.
- Correctness evidence must include independent verification. The entity verifying correctness must differ from the entity that generated the artifact.
- For medium and high-risk actions, evaluator_model must differ from generator_model. Different evaluator family/provider is preferred where available.
- Mutation testing is a required correctness signal for verified trust promotion. Passing tests without acceptable mutation score is insufficient.
- Metamorphic and postcondition-derived adversarial tests are first-class evidence to reduce implementation-mirroring bias.
- Where postconditions are declared proof-required, proof status must be pass before promotion to verified for high-risk classes.
- Evidence disagreement is a first-class escalation signal. Contradictory evidence blocks promotion and routes to triage.
- Trust levels are deterministic policy outputs: untrusted, basic, verified, attested.
- High-impact actions require attested trust plus human identity-backed approval according to constitutional policy.

### 3.7 Operational Rule

The orchestrator selects code by deterministic risk-tier policy over attestation evidence, not by model confidence narratives.

---

## Replacement for Section 4.4 Code-Specific Attributes

Use the following schema to extend code principal metadata with attestation and independence evidence.

```yaml
metadata:
  artifact_type: "skill"           # skill | script | tool | library | pipeline
  version: "1.0.3"
  source_repo: "bizcad/RoadTrip"
  source_commit: "5c20400"
  author_principal: "agent:commit-message-v1"
  reviewer_principal: "human:bizcad"
  build_environment: "github-actions-runner-ubuntu-22.04"

  # Provenance and integrity
  signed: true
  signature_method: "cosign"       # cosign | gpg | none
  provenance_level: "slsa-2"       # none | slsa-1 | slsa-2 | slsa-3
  sbom_hash: "sha256:{sbom-hash}"
  fingerprint: "sha256:{artifact-hash}"
  prompt_hash: "sha256:{prompt-hash}"
  toolchain_hash: "sha256:{toolchain-hash}"
  build_reproducible: true

  # Correctness
  test_status: "passing"           # passing | failing | untested | skipped
  test_coverage_pct: 94
  mutation_score_pct: 91
  metamorphic_tests_pass: true
  postcondition_tests_pass: true
  lean_proof_status: "pass"        # pass | fail | not-required | not-run

  # Independence
  generator_model: "claude-sonnet-4-6"
  generator_model_version: "20250514"
  evaluator_model: "claude-haiku-4-5"
  evaluator_model_family: "anthropic"
  evaluator_differs_from_generator: true

  # Security
  sast_clean: true
  dependency_scan_clean: true
  secret_scan_clean: true
  coderabbit_severity_max: 0

  # Operations
  canary_result: "pass"            # pass | fail | not-run
  rollback_artifact_id: "rb-2026-03-18-001"
  error_budget_impact: "low"       # low | medium | high

  # Policy-computed outputs
  confidence_score: 0.94
  risk_tier: "medium"              # low | medium | high
  trust_level: "verified"          # untrusted | basic | verified | attested
  attestation_policy_version: "attest-policy-v1"
  postconditions_ref: "contract:fragment:{id}"
```

### 4.4 Validation Constraints

- trust_level is computed by policy and cannot be manually authored.
- confidence_score is computed from evidence and cannot be model self-reported.
- evaluator_differs_from_generator must be true for verified and attested promotion.
- mutation_score_pct threshold is risk-tier dependent and must pass policy minimums.
- High-risk actions require attested trust and human identity-backed approval.

---

## Replacement Adoption Note

When this replacement is adopted, keep a pointer in the source spec sections so readers can discover this file without ambiguity:

- Section 3.7 points here for enhanced trust computation and independence policy.
- Section 4.4 points here for enhanced metadata schema and validation constraints.
