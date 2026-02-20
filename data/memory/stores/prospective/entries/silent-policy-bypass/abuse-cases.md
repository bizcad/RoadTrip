# Abuse Cases (Fast Thinking)

## Why this risk is realistic
Users may treat controls as optional friction, especially under urgency. A bypass can look like productivity while accumulating hidden safety debt.

## High-probability bypass patterns
- Request asks for an outcome and implicitly asks to skip controls ("just do it fast").
- Agent retries through an alternate path that does not emit policy events.
- Fallback uses a legacy skill with weaker gate coverage.
- Manual terminal command executes outside orchestrator policy checkpoints.
- Local config toggles reduce enforcement without audit note.

## Explicit anti-patterns
- Success without a policy decision record.
- Fallback success with missing pre-check attestation.
- Registry mutation without policy class and reviewer identity.

## Guardrail stance
- If policy check cannot run, stop with `POLICY_UNAVAILABLE`.
- If policy event cannot be written, stop with `POLICY_AUDIT_WRITE_FAILED`.
- If fallback path has lower policy coverage than primary, block fallback.
