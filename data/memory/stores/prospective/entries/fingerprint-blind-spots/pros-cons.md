# Fingerprint Blind Spots — Pros and Cons (Fast Thinking)

## Candidate controls
- expand fingerprint scope to include critical dependency/config fingerprints
- enforce periodic revalidation scans
- fail closed on mismatch unless explicit preview override
- emit explicit telemetry for every allow/reject decision

## Pros
- Reduces false trust in modified or drifted artifacts.
- Makes verification decisions auditable and measurable.
- Tightens boundary between trusted and preview execution lanes.

## Cons / Risks
- Broader fingerprint scope can increase false positives.
- Revalidation scans add runtime/ops overhead.
- Strict fail-closed policy can interrupt productivity if override paths are unclear.

## Guardrails
- keep stable and preview lanes separate by policy
- cap override duration and require justification
- preserve rollback pointer for any registry fingerprint update

## Evidence to collect
- false-accept rate over time
- mismatch rate by skill and environment
- override frequency and outcome quality
- mean time to recover from reject events
