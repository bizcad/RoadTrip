# Fast Thinking Ideas -> Slow Thinking Research (Secret Leakage)

## Purpose
Generate low-cost, high-signal hypotheses now, then promote only evidence-backed findings into policy.

## Framing
- Fast thinking asks: "What might fail?"
- Slow thinking asks: "What does evidence say and what policy should change?"

## Hypothesis Set A: Exposure Surfaces

### H1: Session logs are the highest accidental leakage surface
- Why: free-form narrative + copy/paste from terminals
- Fast test:
  - run secret-pattern scan on new session logs daily
  - count alerts by source (prompt, response, command output)
- Slow research question:
  - Which redaction strategy yields lowest false negatives with acceptable false positives?

### H2: Docs and memory artifacts leak placeholders that normalize bad habits
- Why: examples like `password=...` become copy targets
- Fast test:
  - classify findings into "live-secret", "sensitive placeholder", "safe reference"
- Slow research question:
  - Should placeholder styles be standardized to non-copyable safe templates?

### H3: Tool output streams are riskier than source code for raw secret exposure
- Why: runtime values appear in command output/logs
- Fast test:
  - compare leak-alert density between `src/**` and `PromptTracking/**`
- Slow research question:
  - Which pre-write output filters should be mandatory at runtime?

## Hypothesis Set B: Controls

### H4: "Authority store + delivery env var" is safer than env-var-only
- Why: env vars are transport, not governance
- Fast test:
  - map incidents where env var existed without audited authority source
- Slow research question:
  - What minimum authority-store metadata is required (owner, rotation SLA, scope)?

### H5: Paired review closes severe leaks faster than solo review
- Why: second reader catches context misses
- Fast test:
  - track mean-time-to-contain for paired vs solo incidents
- Slow research question:
  - Is paired review required only for P0/P1 leaks or all leak classes?

### H6: Auto-redaction before persistence outperforms post-hoc cleanup
- Why: prevention beats remediation
- Fast test:
  - simulate leak strings in test logs; compare pre-write redaction vs post-write scrub
- Slow research question:
  - What is the acceptable redaction miss rate for promotion to default-on?

## Hypothesis Set C: Lifecycle / TTL

### H7: Most raw telemetry should TTL quickly; anomalies should persist longer
- Why: reduce exposure window and noise
- Fast test:
  - route anomaly-tagged events to investigative lane, TTL baseline logs aggressively
- Slow research question:
  - What TTL split minimizes risk while preserving forensic usefulness?

### H8: Secret incidents need an immutable minimal trail, not full payload retention
- Why: auditability without re-exposure
- Fast test:
  - record incident metadata only (hash, source, timestamp, owner, action)
- Slow research question:
  - What minimum incident schema satisfies governance and root-cause analysis?

## Candidate Experiments (1-week sprint)
1. Daily secret-pattern scan + triage labels (`live`, `placeholder`, `reference`).
2. Add pre-persistence redaction check for logs/memory writes in one path.
3. Run a tabletop incident drill using the exposure checklist and measure time-to-contain.
4. Compare two local secret workflows:
   - encrypted local vault + env delivery
   - env-var-only
5. Define anomaly-lane TTL policy draft and test on one telemetry stream.

## Evidence to Capture
- leak alerts/day by source
- false positive / false negative estimates
- mean-time-to-contain and mean-time-to-rotate
- percentage of artifacts with safe placeholder style
- number of incidents requiring history rewrite/scrub

## Promotion Criteria to Slow-Thinking Output
Promote an idea only if:
- measured on real repo artifacts,
- repeated signal over >= 3 observations,
- clear policy recommendation,
- rollback/exception path is defined.

## Expected Slow-Thinking Deliverables
- ADR: secret authority boundary and enforcement model
- PDR: redaction + TTL + incident handling implementation plan
- Policy Appendix: required fields, retention classes, escalation thresholds
