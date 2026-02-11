# Skill Vetting Framework

**Version**: 1.0  
**Status**: Operational Framework  
**Created**: Feb 10, 2026  
**Purpose**: Provide practical evaluation checklist and decision matrix for vetting skills

---

## Overview

This framework is applied in **Stage 2 (Vetting & Evaluation)** of the Skill Acquisition Funnel. It provides:
- Detailed questions for each vetting dimension
- Scoring rubrics (1–5 point scales)
- Checklists for reviewers
- Decision matrix (approve/reject/conditional)

---

## Section A: Capability Analysis

**Goal**: Understand EXACTLY what this skill does and whether it fits RoadTrip.

### A1: Capability Verification

**Question Set**:
1. What does the documentation claim this skill does?
   - [ ] Read README
   - [ ] Read examples
   - [ ] Read API docs
   - *Summary*: _______________

2. What does it actually do? (Run it, test it)
   - [ ] Executed at least one example
   - [ ] Tested basic functionality
   - [ ] Tested edge cases
   - *Findings*: Reality matches claims? Yes / Partially / No

3. Can you articulate the skill in one sentence?
   - *One-liner*: _______________

### A2: RoadTrip Relevance

**Question Set**:
1. How does this align with RoadTrip roadmap?
   - [ ] Directly addresses planned feature
   - [ ] Solves known problem
   - [ ] Nice-to-have / opportunistic
   - [ ] Not aligned (but interesting)
   - *Relevance*: High / Medium / Low / None

2. What problems does it solve for us?
   - Problem 1: _______________
   - Problem 2: _______________
   - Problem 3: _______________

3. Are there alternative solutions?
   - [ ] Yes, here: _______________
   - [ ] No, this is unique
   - [ ] Yes, but this is better because: _______________

### A3: Urgency Assessment

**Question Set**:
1. When do we need this capability?
   - [ ] Right now (Phase 1, by Mar 2026)
   - [ ] Soon (Phase 2, by May 2026)
   - [ ] Later (Phase 3+, after May 2026)
   - [ ] Opportunistic (nice-to-have)
   - [ ] Not currently needed

2. Impact if we don't adopt this?
   - [ ] Blocks critical feature
   - [ ] Delays feature by 4+ weeks
   - [ ] Minor delay or workaround exists
   - [ ] No impact

3. Does this enable other capabilities?
   - [ ] Yes, enables: _______________
   - [ ] No

**Urgency Scoring** (1–5):
- 5 = Critical path; blocks Phase 1 feature; needed by Mar 2026
- 4 = Important; Phase 2 feature; needed by May 2026
- 3 = Valuable; Phase 3+; opportunistic but solid
- 2 = Nice-to-have; solves minor problem; lower priority
- 1 = Interesting but not needed now

---

## Section B: Code Quality Review

**Goal**: Assess maintainability, structure, and production readiness.

### B1: Type Safety & Documentation

**Python Scoring Rubric**:

| Score | Type Hints | Docstrings | Comments | Structure |
|-------|-----------|-----------|----------|-----------|
| 5 ⭐ | 90%+ of functions | Complete (all functions) | Clear & helpful | SOLID principles; well-organized |
| 4 ✓ | 70%+ | Most functions | Ad-hoc | Good organization |
| 3 ⚠️ | 50%+ | Some functions | Minimal | Reasonable structure |
| 2 ❌ | 30%+ | Few functions | None | Confusing structure |
| 1 💥 | <30% | None or minimal | None | Ad-hoc / unmaintainable |

**Questions**:
1. Type hint coverage: What %?
   - [ ] 90%+ (5pts)
   - [ ] 70%+ (4pts)
   - [ ] 50%+ (3pts)
   - [ ] 30%+ (2pts)
   - [ ] <30% (1pt)

2. Docstrings present for:
   - [ ] All public functions/classes (5pts)
   - [ ] Most public interfaces (4pts)
   - [ ] Some modules (3pts)
   - [ ] Few/sporadic (2pts)
   - [ ] None/minimal (1pt)

3. Code comments: Helpful? Outdated?
   - [ ] Clear & current (5pts)
   - [ ] Mostly clear (4pts)
   - [ ] Adequate (3pts)
   - [ ] Confusing/sparse (2pts)
   - [ ] None/misleading (1pt)

4. Code organization (modules, classes, functions):
   - [ ] SOLID principles; clear structure (5pts)
   - [ ] Good organization (4pts)
   - [ ] Reasonable (3pts)
   - [ ] Confusing (2pts)
   - [ ] Monolithic/unclear (1pt)

### B2: Testing

**Questions**:
1. Test coverage?
   - [ ] 90%+ coverage (5pts)
   - [ ] 80%+ coverage (4pts)
   - [ ] 70%+ coverage (3pts)
   - [ ] 50%+ coverage (2pts)
   - [ ] <50% coverage, hard to assess (1pt)
   - *Coverage %*: ____%

2. Test types present?
   - [ ] Unit tests (functions/methods)
   - [ ] Integration tests (components working together)
   - [ ] End-to-end tests (whole workflow)
   - [ ] Error scenario tests
   - [ ] Performance tests
   - *Check all that apply*

3. Test quality: Do they test the right things?
   - [ ] Tests are meaningful; catch regressions (5pts)
   - [ ] Tests are mostly good (4pts)
   - [ ] Tests exist but could be better (3pts)
   - [ ] Tests are minimal/weak (2pts)
   - [ ] Tests missing or inadequate (1pt)

4. How to run tests?
   - [ ] Simple, documented (5pts)
   - [ ] Clear instructions (4pts)
   - [ ] Requires some setup (3pts)
   - [ ] Undocumented / unclear (2pts)
   - [ ] Broken / not runnable (1pt)

**Testing Score** (average of above):
- 5 = Excellent testing discipline
- 4 = Good coverage and test quality
- 3 = Adequate testing; could improve
- 2 = Weak testing
- 1 = Minimal or broken testing

### B3: Maintenance & Activity

**Questions**:
1. When was last update?
   - [ ] This week (5pts)
   - [ ] This month (4pts)
   - [ ] Within 3 months (3pts)
   - [ ] Within 6 months (2pts)
   - [ ] >6 months (1pt)
   - *Last update*: _______________

2. How many commits/month (trend)?
   - [ ] 5+ (very active) (5pts)
   - [ ] 2–4 (active) (4pts)
   - [ ] 1–2 (maintained) (3pts)
   - [ ] <1 (low activity) (2pts)
   - [ ] Abandoned (1pt)

3. Issue response time (if you post an issue)?
   - [ ] Same-day response (5pts)
   - [ ] 1–3 day response (4pts)
   - [ ] 1 week response (3pts)
   - [ ] Slow response (2pts)
   - [ ] No response (1pt)

4. How many maintainers?
   - [ ] 3+ active (5pts)
   - [ ] 2 active (4pts)
   - [ ] 1 active (3pts)
   - [ ] 1 inactive (2pts)
   - [ ] 0 or unknown (1pt)

**Maintenance Score**: Average of above
- 5 = Actively maintained
- 4 = Well maintained
- 3 = Stable; maintenance as-needed
- 2 = Declining activity
- 1 = Abandoned/unmaintained

### B4: Code Quality Summary

**Overall Code Quality Score** (average of B1, B2, B3):
- 5 = Excellent: Production-ready; well-tested; maintained
- 4 = Good: Solid codebase; some room for improvement
- 3 = Acceptable: Usable; may need improvements
- 2 = Concerning: Has issues; need to fix before production
- 1 = Poor: Not production-ready

---

## Section C: Security & Risk Assessment

**Goal**: Identify security risks, license issues, and potential for misuse.

### C1: Known Vulnerabilities

**Questions**:
1. Are there known CVEs?
   - [ ] Check: https://cve.mitre.org/
   - [ ] Check: https://nvd.nist.gov/
   - [ ] Check: Dependency vulnerability scanner (e.g., pip-audit, safety)
   - *CVEs found*: None / [list here]

2. If vulnerabilities found:
   - [ ] Vulnerability details reviewed
   - [ ] Patch available? Y/N
   - [ ] Maintainer's response?
   - [ ] Acceptable risk? Y/N

3. Dependencies checked for vulns?
   - [ ] All dependencies scanned
   - [ ] No vulnerabilities found
   - [ ] Some vulnerabilities; paths patched
   - [ ] Significant vulnerabilities; risky

**Vulnerability Score**:
- 5 = No CVEs; dependencies clean
- 4 = No CVEs; one old/low-risk vuln in dependency
- 3 = No CVEs; some out-of-date dependencies
- 2 = Has CVE with patch available
- 1 = Has unpatched CVE or severe risk

### C2: Suspicious Code Patterns

**Check for these red flags**:
- [ ] Executes shell commands directly (suspicious)
- [ ] Makes network calls to unknown hosts
- [ ] Writes to system directories without warning
- [ ] Loads code dynamically from internet
- [ ] Uses pickle or other unsafe serialization
- [ ] Modifies global state unexpectedly
- [ ] Hides functionality (obfuscated code)
- [ ] Requires unusual permissions

**Code Behavior Assessment**:
1. Read the code. Does it do what it says?
   - [ ] Yes, straightforward (5pts)
   - [ ] Mostly, with some surprises (3pts)
   - [ ] Multiple discrepancies (1pt)

2. Are dangerous operations documented?
   - [ ] YES, all documented with warnings (5pts)
   - [ ] SOME documented (3pts)
   - [ ] NO, hidden or surprising (1pt)

**Risk Pattern Score**:
- 5 = Clean; no suspicious patterns
- 4 = Safe; some risky code clearly marked
- 3 = Acceptable; risky features isolated
- 2 = Concerning; risky code unmarked
- 1 = Dangerous; Red flags everywhere

### C3: License Compatibility

**Questions**:
1. What license does this skill use?
   - *License*: _______________

2. Is it compatible with RoadTrip?
   - [ ] MIT / Apache 2.0 / BSD (✅ Compatible)
   - [ ] GPL v3 (⚠️ Check compatibility; may require open-sourcing)
   - [ ] AGPL (❌ Likely incompatible; requires open-sourcing)
   - [ ] Proprietary (❌ Incompatible)
   - [ ] Custom (⚠️ Requires legal review)

3. If GPL:
   - [ ] RoadTrip also GPL? → ✅ OK
   - [ ] RoadTrip is proprietary? → ❌ Requires decision
   - [ ] Unsure? → 🔍 Get legal review

**License Score**:
- 5 = MIT/Apache/BSD (fully compatible)
- 4 = Compatible with minimal restrictions
- 3 = Compatible but requires care
- 2 = Requires legal review
- 1 = Incompatible

### C4: Overall Security Score

**Average of C1, C2, C3**:
- 5 = Excellent: No vulns; clean code; compatible license
- 4 = Good: No major issues; some minor concerns
- 3 = Acceptable: Manageable risks; documented
- 2 = Risky: Has issues; requires mitigation plan
- 1 = Too Risky: Should not use

---

## Section D: Integration Feasibility

**Goal**: Assess effort and complexity to integrate into RoadTrip orchestrator.

### D1: Integration Effort

**Estimation Rubric**:

| Effort | Characteristics | Estimate | Example |
|--------|-----------------|----------|---------|
| **Trivial** (1–2 hrs) | Pure Python function; no dependencies; typical I/O | 2 hours | String utility function |
| **Easy** (4–8 hrs) | Single import; clear interface; one-time setup | 6 hours | JSON parser integration |
| **Moderate** (16–24 hrs) | Requires some wrapper code; simple setup | 20 hours | API client integration |
| **Complex** (40–64 hrs) | Needs significant wrapper; some infrastructure setup | 50 hours | Async task queue (needs config) |
| **Very Complex** (80+ hrs) | Major architectural change; multiple components | 100+ hours | Full ML pipeline integration |

**Questions**:
1. How hard to call this from orchestrator?
   - [ ] Trivial: Just import and call (1–2 hrs)
   - [ ] Easy: Simple wrapper needed (4–8 hrs)
   - [ ] Moderate: Some integration code (16–24 hrs)
   - [ ] Complex: Significant setup needed (40–64 hrs)
   - [ ] Very Complex: Major work (80+ hrs)
   - *Estimate*: ___ hours

2. Does it require new infrastructure?
   - [ ] No (0 hrs)
   - [ ] Yes, simple (4 hrs)
   - [ ] Yes, moderate (16 hrs)
   - [ ] Yes, complex (40+ hrs)

3. Does it conflict with existing skills?
   - [ ] No conflicts
   - [ ] Minor conflicts (easy to resolve)
   - [ ] Major conflicts (need refactoring)

4. Can we mock/fallback if it fails?
   - [ ] Yes, easy fallback (5pts: low risk)
   - [ ] Yes, feasible fallback (3pts: moderate risk)
   - [ ] No fallback; critical path (1pt: high risk)

### D2: Dependencies & Infrastructure

**Questions**:
1. External dependencies (databases, services, config)?
   - [ ] None (5pts)
   - [ ] Minor (env var config) (4pts)
   - [ ] Moderate (needs setup) (3pts)
   - [ ] Major (infrastructure required) (2pts)
   - [ ] Critical (can't run without) (1pt)
   - *List dependencies*: _______________

2. Can we run this in test environment?
   - [ ] Yes, locally (5pts)
   - [ ] Yes, but needs mock service (3pts)
   - [ ] No, needs live service (1pt)

3. Deployment complexity?
   - [ ] Single Python module (5pts)
   - [ ] Package + config (4pts)
   - [ ] Package + setup script (3pts)
   - [ ] Multi-component; needs orchestration (1pt)

### D3: Integration Feasibility Score

**Average of D1 & D2**:
- 5 = Trivial: < 8 hours; ready to integrate
- 4 = Easy: 8–20 hours; straightforward
- 3 = Moderate: 20–50 hours; doable
- 2 = Complex: 50–100 hours; significant work
- 1 = Very Complex: 100+ hours; major effort

---

## Section E: Decision Matrix

### E1: Scoring Summary

**Fill in scores from sections A–D**:

| Category | Score (1–5) | Weighting | Weighted Score |
|----------|-----------|-----------|---|
| A: Capability (Relevance + Urgency) | ___ | 30% | ___ |
| B: Code Quality | ___ | 25% | ___ |
| C: Security | ___ | 35% | ___ |
| D: Integration Feasibility | ___ | 10% | ___ |
| **TOTAL WEIGHTED SCORE** | | | **___/5.0** |

### E2: Decision Rules

**Use the weighted score to recommend:

| Score | Recommendation | Rationale | Action |
|-------|---|---|---|
| **4.5–5.0** ⭐ | **APPROVE** | Excellent across all dimensions | **Proceed to Onboarding** |
| **3.5–4.4** ✓ | **APPROVE** | Strong capability; acceptable risk | **Proceed to Onboarding** |
| **2.5–3.4** ⚠️ | **CONDITIONAL APPROVE** | Good but has conditions; see below | **Conditional path** |
| **1.5–2.4** ❌ | **REJECT** | Concerns outweigh benefits | **Archive; revisit Q3** |
| **<1.5** 💥 | **STRONG REJECT** | Significant issues; not viable | **Reject permanently** |

### E3: Conditional Approval Framework

**If score is 2.5–3.4, specify conditions**:

```
Skill: ___________
Weighted Score: ___________

CONDITIONAL APPROVAL - Fix before integration:

1. Condition: [Describe what must be fixed/added]
   Owner: [Who fixes]
   Timeline: [When]
   Verification: [How to confirm it's fixed]

2. Condition: [Next condition]
   ...

Approval Path: Resubmit when conditions met
No.: RoadTrip will [action] on [date]
```

**Example**:
```
Skill: celery (async task queue)
Weighted Score: 3.2

CONDITIONAL APPROVAL - Fix before integration:

1. Condition: Infrastructure - Add Redis to RoadTrip deployment
   Owner: Infra team
   Timeline: By Mar 31, 2026
   Verification: Redis running in staging; RoadTrip tests pass

2. Condition: Documentation - Add RoadTrip-specific examples
   Owner: Skills team
   Timeline: By Apr 7, 2026
   Verification: Examples run successfully

Approval Path: Resubmit on Apr 7 when conditions met.
Next: RoadTrip will integrate celery week of Apr 12.
```

### E4: Reviewer Sign-Off

**Vetting Decision Record**:

```
SKILL VETTING REPORT
====================

Skill: _____________
Reviewer(s): _______
Date: _____________

A. CAPABILITY ANALYSIS
   Relevance: [High/Medium/Low]
   Urgency: [1–5]
   Summary: [One-liner]
   ✓ Approved / ❌ Concerns

B. CODE QUALITY
   Type hints: __%
   Test coverage: __%
   Maintenance: [Active/Stable/Declining/Abandoned]
   Overall Score: [1–5]
   ✓ Approved / ⚠️ Acceptable / ❌ Poor

C. SECURITY
   CVEs: [None/[list]]
   Suspicious patterns: [None/[list]]
   License: [Type and compatibility]
   Overall Score: [1–5]
   ✓ Approved / ⚠️ Mitigated / ❌ Unacceptable

D. INTEGRATION
   Effort estimate: ___ hours
   Infrastructure: [None/Minor/Moderate/Major]
   Feasibility Score: [1–5]
   ✓ Approved / ⚠️ Doable / ❌ Too complex

E. DECISION
   Weighted Score: ___ / 5.0
   
   ⭐ APPROVED - Proceed to Onboarding
   or
   ⚠️  CONDITIONAL - Fix: [list conditions]
   or
   ❌ REJECTED - Reason: [brief summary]
   
   Reviewer Signature: ________________
   Date: ________________
```

---

## Appendix: Vetting Reviewer Checklist

**Before Starting Review**:
- [ ] Skill profile received
- [ ] Access to source code
- [ ] 6–8 hours allocated for review
- [ ] Interdisciplinary review team identified (if needed)

**During Review** (Sections A–D):
- [ ] Section A: Capability analysis complete
- [ ] Section B: Code quality review complete
- [ ] Section C: Security assessment complete
- [ ] Section D: Integration feasibility assessed
- [ ] Scores recorded

**Before Signing Off**:
- [ ] All four sections scored
- [ ] Weighted total calculated
- [ ] Decision rule applied
- [ ] If conditional: conditions clearly specified
- [ ] Decision record written & dated
- [ ] Committee review scheduled (if needed)

**Post-Decision**:
- [ ] If APPROVED: Schedule onboarding
- [ ] If CONDITIONAL: Assign condition follow-up owner
- [ ] If REJECTED: Document learnings for discovery
- [ ] Archive decision record in skill file

---

*Skill Vetting Framework v1.0 | Feb 10, 2026*
