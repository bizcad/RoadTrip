# Controls and Metrics (Refined)

## Minimum control set
- Control 1: Mandatory policy pre-check before every execution attempt.
- Control 2: Mandatory policy attestation after execution attempt.
- Control 3: Policy coverage parity check between primary and fallback paths.
- Control 4: Escalation contract when policy state is unknown.

## Detection queries to implement
- `success AND missing(policy_decision_event)`
- `fallback_used AND missing(pre_execution_attestation)`
- `registry_update AND missing(policy_class OR reviewer)`
- `policy_check_failed AND execution_started=true`

## Scoring rubric (0-5)
- Coverage score: % executions with both pre-check and post-attestation.
- Integrity score: % successful runs with complete policy event fields.
- Drift score: fallback paths with weaker policy coverage than primary.
- Recovery score: mean time from bypass detection to containment.

## Promotion threshold (prospective -> semantic)
- Coverage score >= 4.5 for 14 days.
- Integrity score >= 4.5 for 14 days.
- Drift score <= 0.5 for 14 days.
- No unresolved P0 bypass incidents in the window.

## Quarantine triggers
- Any confirmed silent bypass with no event trail.
- Repeated missing policy fields in successful executions.
- Bypass path discovered in fallback chain not blocked by policy parity check.
