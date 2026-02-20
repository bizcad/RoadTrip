# Fast Thinking Options — Dark Factory (Interesting Idea, Not Process Change)

## Intent
Capture plausible process implications from the Dark Factory transcript as **prospective memory** for later evidence-based review.

## Current Position
- Classification: **interesting idea**
- Policy state: **no immediate process change**
- Promotion requirement: measured evidence in RoadTrip context

## Clarified Direction (from operator)
- Pilot target: **self-improvement path** (use failures as opportunities for improvements)
- Evidence bar: **two independent replications** before proposing process change
- Primary objective: **quality/safety first**
- Review cadence: **next phase gate**

## Quick Opinion (RoadTrip Fit)
The strongest near-term value is not “full dark factory,” but selective upgrades to our existing docs-first and deterministic-first workflow:
- stronger spec quality checks,
- better eval/holdout design,
- explicit tracking of the AI adoption J-curve,
- role evolution toward system judgment over coordination overhead.

This aligns with `docs/Principles-and-Processes.md` and avoids premature, high-risk re-org.

## Fast-Thinking Possibilities

### 1) Holdout Scenario Lane (Low Risk, High Learning)
Hypothesis:
Agent-hidden behavioral scenarios reduce false confidence vs agent-visible tests.

Cheap test:
- Add a small external scenario set for one high-impact workflow path.
- Compare: scenario-pass rate vs unit/integration pass rate.

Signal to watch:
- Cases where regular tests pass but scenario fails.

### 2) Spec Quality Gate v0 (Low Risk)
Hypothesis:
Better specs reduce rework more than adding another coding tool.

Cheap test:
- Introduce a spec checklist score (clarity, edge cases, acceptance criteria, rollback).
- Correlate checklist score with rework cycles/defects.

Signal to watch:
- Rework drops as spec score rises.

### 3) J-Curve Telemetry Slice (Low Risk)
Hypothesis:
RoadTrip experiences short-term productivity dip unless process is redesigned.

Cheap test:
- Track cycle time and defect escape before/after AI-heavy workflow changes.
- Keep one “control lane” with current process.

Signal to watch:
- Initial dip followed by recovery only when process changes accompany tool changes.

### 4) Failure-to-Improvement Loop Pilot (Medium Risk)
Hypothesis:
Structured post-failure learning improves quality faster than adding more implementation automation.

Cheap test:
- Select one recurring failure class and run a closed loop:
	1. capture incident/failure signal,
	2. classify root cause (spec gap, eval gap, policy gap, implementation gap),
	3. create one candidate control,
	4. validate in sandbox,
	5. track recurrence.

Signal to watch:
- Recurrence rate drops without introducing new safety regressions.

### 5) Brownfield Spec Extraction Sprint (Low Risk)
Hypothesis:
Converting implicit legacy behavior into explicit specs is a prerequisite for deeper autonomy.

Cheap test:
- Pick one older path and produce behavior spec + scenario suite from real behavior.

Signal to watch:
- Faster future changes and fewer regressions on that path.

## Guardrails
- No “no-human-review” policy changes without hard evidence.
- Security and auth controls remain conservative defaults.
- New autonomy patterns must include rollback and containment paths.
- Any gains claim requires quality + safety metrics, not speed alone.

## Candidate Metrics
- Scenario miss rate (tests pass, holdout fails)
- Rework cycles per change
- Defect escape rate
- Time-to-rollback for bad AI-generated changes
- Spec quality score vs outcome quality
- Failure recurrence rate by class (before/after pilot)

## Promotion Trigger (Prospective -> Working)
Promote this item only if:
1. at least two independent pilots show repeatable benefit,
2. no safety regression is observed,
3. a concrete draft process update is written,
4. owner + review date are assigned.

## Open Questions for Clarification
1. Which workflow should be the first pilot target (rules-engine, orchestrator, telemetry, other)?
2. What evidence threshold should be required before process change (1 pilot vs 2+ replications)?
3. Should we prefer quality gains first, speed gains first, or balanced scoring?
4. At the next phase gate, do we review this as a standalone packet or bundled with other self-improvement candidates?
