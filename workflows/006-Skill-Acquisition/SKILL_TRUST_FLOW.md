# Skill Trust Flow (Operator Guide)

**Purpose**: Make the end-to-end trust flow explicit for skill acquisition and release decisions.

---

## 1) What This Flow Produces

For each skill, this flow produces:
- A **trust manifest** (`*.trust-manifest.json`) with gate outcomes and decision.
- Evidence pointers (tests/security/provenance/fingerprint) used during review.
- A clear decision state: `ALLOW_AUTO`, `MANUAL_REVIEW`, or `BLOCK`.

---

## 2) End-to-End Flow

1. **Discover skill candidates**
   - Source: `scripts/discover_skills.py`
   - Output: list of candidate skills and entry points.

2. **Vetting review (Workflow 006)**
   - Apply: capability, quality, security, and integration checks.
   - Source docs:
     - `VETTING_FRAMEWORK.md`
     - `SKILL_FUNNEL_MATURITY_MODEL.md`

3. **Populate evidence manifest map**
   - Start from template:
     - `TRUST_MANIFEST_EVIDENCE_MAP_TEMPLATE.json`
   - Fill `"*"` defaults and per-skill overrides.

4. **Generate trust scorecard + per-skill trust manifests**
   - Command:
     - `py scripts/generate_trust_scorecard.py --manifest-dir workflows/006-Skill-Acquisition/trust-manifests --release-id <release-id> --manifest-evidence-map workflows/006-Skill-Acquisition/TRUST_MANIFEST_EVIDENCE_MAP_TEMPLATE.json`
   - Outputs:
     - `logs/trust_scorecard.json`
     - `workflows/006-Skill-Acquisition/trust-manifests/<skill>.trust-manifest.json`

5. **Decision and action**
   - `ALLOW_AUTO`: eligible for autonomous execution path.
   - `MANUAL_REVIEW`: requires human approval before use.
   - `BLOCK`: not allowed for autonomous use; remediate and re-evaluate.

---

## 3) Gate Model (Current Scaffolding)

Current scorecard includes these gates:
- `fingerprint_verified` (blocking)
- `version_provenance_verified` (blocking)
- `security_review_passed` (blocking)
- `test_coverage_minimum` (blocking)
- `capability_fit` (advisory)
- `author_reputation` (advisory)

**Important**: Gate provider is currently mock/scaffold-friendly by design. This enables deterministic testing while real gate integrations are added incrementally.

---

## 4) Files You Actually Touch

- Policy/process:
  - `workflows/006-Skill-Acquisition/VETTING_FRAMEWORK.md`
  - `workflows/006-Skill-Acquisition/SKILL_FUNNEL_MATURITY_MODEL.md`
- Manifest input template:
  - `workflows/006-Skill-Acquisition/TRUST_MANIFEST_EVIDENCE_MAP_TEMPLATE.json`
- Engine/CLI:
  - `src/skills/trust_scorecard.py`
  - `scripts/generate_trust_scorecard.py`

---

## 5) Practical Review Rhythm

Per skill:
1. Update evidence links in the manifest map.
2. Run scorecard generation.
3. Inspect `<skill>.trust-manifest.json`.
4. Approve, hold for manual review, or block.
5. Record remediation work for blocked skills, then re-run.

---

## 6) Current Maturity and Next Step

Current maturity:
- ✅ Repeatable trust manifest generation.
- ✅ Deterministic mocked gate outputs for tests.
- ✅ Portable per-skill trust artifact.

Next step:
- Replace mocked gate inputs with progressively real providers (security scanners, provenance verifier, runtime telemetry checks), while preserving the same trust manifest schema.
