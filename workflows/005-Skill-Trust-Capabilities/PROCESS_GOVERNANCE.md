# Phase 2: Process & Governance Framework

**Status**: DRAFT  
**Purpose**: Define *how* Phase 2 will operate (process > product)  
**Inspired by**: Principles-and-Processes.md + RoadTrip Living Document approach  

---

## Table of Contents
1. [Core Process Principles](#core-process-principles)
2. [Weekly Cadence](#weekly-cadence)
3. [Decision-Making Framework](#decision-making-framework)
4. [Quality Gates](#quality-gates)
5. [Escalation & Unblocking](#escalation--unblocking)
6. [Documentation & Knowledge Capture](#documentation--knowledge-capture)
7. [Post-Mortems & Learning](#post-mortems--learning)

---

## Core Process Principles

### Principle 1: Capture Decisions, Not Just Outcomes

**The Practice**:
- Every architectural decision gets a decision record (DR)
- DRs go in `workflows/005-Skill-Trust-Capabilities/` with timestamp
- Format: Question → Options → Decision → Rationale → Confidence → Next Review Date

**Why It Matters**:
- Future teams understand *why* we chose X over Y
- Decisions are reversible (we can revisit with new data)
- Confidence scores show what we're uncertain about

**Example DR Structure**:
```markdown
# DR-2026-03-15: IBAC Confidence Threshold (0.85 vs 0.75 vs 0.95)

Question: What confidence threshold should IBAC use to auto-allow requests?

Options Evaluated:
1. 0.95 (very conservative): ~20% escalation rate
2. 0.85 (balanced): ~10% escalation rate  
3. 0.75 (permissive): ~5% escalation rate

Decision: 0.85 (balanced)
Rationale: 10% escalation rate is operationally sustainable
Confidence: 0.8 (may adjust as we see real data)
Next Review: May 1, 2026 (after 4 weeks of production data)
```

---

### Principle 2: Iterate on Feedback, Not Speculation

**The Practice**:
- Design Phase 2 carefully (done: Phase 2 PRD)
- Implement Phase 2 with best understanding
- **Collect data** (logs, feedback, incidents)
- **Review data** monthly (not weekly; let patterns emerge)
- **Adjust course** only if data contradicts design

**Why It Matters**:
- Prevents analysis paralysis ("what if X happens?")
- Grounds decisions in evidence, not fear
- Reduces scope creep (stick to PRD unless data forces change)

**Data Collection Points**:
- IBAC decisions: How many escalations? What patterns?
- Constitutional violations: Are principles too strict?
- Performance: Is latency acceptable?
- Operator feedback: What's frustrating operationally?

---

### Principle 3: Each Workstream Owns Its Quality

**The Practice**:
- Workstream owner = single point of accountability for quality
- Owner responsible for: code review, test coverage, documentation
- Weekly report: "On track? Blockers? Need help?"

**Why It Matters**:
- Clear accountability (no "I thought someone else checked")
- Empowerment (owner has authority to make decisions)
- Visibility (status is always clear)

**Workstream Owners (Proposed)**:
- Skill Fingerprinting: Infrastructure Lead
- IBAC Policy Engine: Security Lead
- Constitutional AI: Alignment Lead
- Zero Trust Tokens: Infrastructure Lead
- DyTopo Integration: Orchestration Lead
- End-to-End Testing: QA Lead

---

### Principle 4: Tests Are the First Deliverable, Not an Afterthought

**The Practice**:
- For each feature: Write tests *before* code
- Tests define "done" (not subjective interpretation)
- Code passes tests → feature is done

**Test Types**:
- **Unit Tests**: Component works in isolation
- **Integration Tests**: Components work together
- **End-to-End Tests**: Entire workflow works (orchestrator → skill → result)
- **Performance Tests**: Meets latency targets
- **Security Tests**: No credential leakage, proper audit logs

**Why It Matters**:
- Prevents "done" ambiguity (tests are objective)
- Catches regressions (test suite is always running)
- Reduces debugging time (tests fail before production)

---

### Principle 5: Process Improvement Happens Asynchronously

**The Practice**:
- Friday 3pm: Team uploads learnings & process feedback to `workflows/005-Skill-Trust-Capabilities/weekly-retrospectives/`
- Monday 9am: Lead reviews retrospectives; logs improvements (if any) for next week
- Improvements are *emergent*, not imposed by leadership

**Example Retrospective Entry**:
```markdown
# Weekly Retrospective: Week of Mar 18–22, 2026

## What Went Well
- IBAC rule testing was faster than expected (2 days vs 3)
- Constitutional AI framework was clearer than designed (operators understood immediately)

## What Could Be Better
- IBAC LLM calls slower than expected (2.5s avg vs 1.5s target)
- Need to add caching earlier

## Improvement for Next Week
- Implement IBAC decision cache (Redis) → estimate 0.5s
- Profile LLM calls to find latency bottleneck
```

---

## Weekly Cadence

### Monday 9:00 AM – Standup & Blocking Issues
**Attendees**: Workstream owners + Lead  
**Duration**: 30 min  
**Agenda**:
1. (5 min) Last week's status: On track? Blockers?
2. (10 min) Critical issues: Do we need to unblock anyone?
3. (5 min) This week's priorities: What's each workstream starting?
4. (10 min) Dependency check: Any inter-team conflicts?

**Output**: Standup notes in `workflows/005-Skill-Trust-Capabilities/standups/standup-2026-03-17.md`

---

### Wednesday 2:00 PM – Mid-Week Sync (Infrastructure & Integration)
**Attendees**: Infrastructure + Security + Orchestration leads + Architect  
**Duration**: 30 min  
**Agenda**:
1. (10 min) Integration point check: Are pieces fitting together?
2. (10 min) Performance update: Any latency surprises?
3. (10 min) Risk review: Any new blockers?

**Output**: Integration notes in `workflows/005-Skill-Trust-Capabilities/mid-week-syncs/`

---

### Friday 3:00 PM – Retrospective + Decision Records
**Attendees**: Entire team  
**Duration**: 45 min  
**Agenda**:
1. (15 min) Retrospective: What worked? What didn't? (see Principle 5)
2. (15 min) New decision records: Any architectural choices this week?
3. (10 min) Next week prep: Priorities? Challenges anticipated?
4. (5 min) Commitment: What will each workstream finish?

**Output**: 
- Retrospective in `workflows/005-Skill-Trust-Capabilities/weekly-retrospectives/retro-2026-03-22.md`
- Decision records in `workflows/005-Skill-Trust-Capabilities/decision-records/`
- Next-week priorities pinned in README

---

## Decision-Making Framework

### Decision Types & Who Decides

**Type 1: Architectural Decisions** (e.g., "Should IBAC use 0.85 or 0.95 confidence?")
- **Owner**: Lead + 2 workstream leads most affected
- **Process**: 
  1. Present options (including rationale & trade-offs)
  2. Vote (not unanimous required; 2/3 is OK)
  3. Dissenting opinions captured in decision record
  4. Decision is binding (proceed; we'll learn from results)
- **Timeline**: Max 1 week from question → decision

**Type 2: Implementation Decisions** (e.g., "Should IBAC cache use Redis or in-memory?")
- **Owner**: Implementation workstream lead
- **Process**:
  1. Lead proposes approach (why this, not others?)
  2. Lead implements & tests
  3. Code review gates it (architect signs off)
  4. Can be reversed if performance doesn't match expectations
- **Timeline**: Lead decides; architect reviews within 3 days

**Type 3: Process Decisions** (e.g., "Should we add a Thursday sync?")
- **Owner**: Entire team (consensus)
- **Process**:
  1. Anyone can propose in retrospective
  2. Two-week trial period
  3. If team finds it valuable, keep; otherwise revert
- **Timeline**: Propose Friday, trial starts Monday, assess in 2 weeks

**Type 4: Escalation Decisions** (e.g., "Do we delay Phase 2 to fix auth issue?")
- **Owner**: Executive sponsor + Lead + Architect (emergency decision)
- **Process**:
  1. Blocker surfaces (cannot proceed without decision)
  2. 24-hr assessment window
  3. Executive vote (break ties if team is split)
  4. Decision communicated to full team immediately
- **Timeline**: Urgent (< 24 hr)

---

## Quality Gates

### Before Merging Any Code

**Gate 1: Tests Pass**
- [ ] Unit tests: 100% for new code
- [ ] Integration tests: Cover interaction points
- [ ] No regressions: Existing tests still pass
- **Owner**: Workstream lead

**Gate 2: Code Review**
- [ ] Two reviewers sign off (one architect, one peer)
- [ ] Type hints present & correct (mypy passes)
- [ ] Docstrings on public functions
- [ ] No credentials in logs/comments (grep: PAT, token, password)
- **Owner**: Code reviewers

**Gate 3: Documentation Complete**
- [ ] Function docstrings updated
- [ ] Configuration examples provided
- [ ] Decision record updated (if arch change)
- [ ] Tests are self-documenting (not cryptic)
- **Owner**: Workstream lead

**Gate 4: Performance Targets Met** (for latency-sensitive features)
- [ ] IBAC deterministic rules: < 100ms
- [ ] IBAC LLM fallback: < 2s (with cache)
- [ ] Skill invocation: < 1s
- Measured via automated perf tests (CI/CD gate)
- **Owner**: Performance testing workstream

---

## Escalation & Unblocking

### If a Workstream Is Blocked

**Same-Day** (< 4 hours):
- Workstream owner flags in Slack + standup
- Lead investigates severity
- If blocker is external (another workstream): immediate sync to unblock
- If blocker is technical: code review priority or design session scheduled

**Next-Day** (< 24 hours):
- If unresolved: escalate to architect + executive sponsor
- Options: 
  1. Parallel workaround path
  2. Descope feature (cut from Phase 2, push to Phase 2b)
  3. Delay start date (push workstream by N days, extend Phase 2)

**Weekly Check**:
- Retrospective identifies systemic blockers (e.g., "We keep waiting for X")
- Lead proposes process fix (e.g., "Let's assign X person as on-call for cross-team questions")

---

## Documentation & Knowledge Capture

### Where Documentation Lives

| Document Type | Location | Frequency | Owner |
|---|---|---|---|
| Decision Records | `workflows/005-Skill-Trust-Capabilities/decision-records/` | On decision | Decider |
| Weekly Standups | `workflows/005-Skill-Trust-Capabilities/standups/` | Every Monday | Lead |
| Retrospectives | `workflows/005-Skill-Trust-Capabilities/weekly-retrospectives/` | Every Friday | Team |
| Mid-Week Syncs | `workflows/005-Skill-Trust-Capabilities/mid-week-syncs/` | Every Wednesday | Lead |
| Technical Details | `docs/Phase_2_*.md` | On completion of workstream | Workstream owner |
| Operator Guide | `docs/Phase_2_Operator_Guide.md` | Continuously updated | Operator team |
| Audit Log Spec | `docs/Phase_2_Audit_Log_Reference.md` | On feature completion | Security team |

### Knowledge Capture Checklist (End of Each Workstream)

Before marking a workstream complete:
- [ ] Code is merged & reviewed
- [ ] Tests pass (80%+ coverage minimum)
- [ ] Technical doc written (for operators & future engineers)
- [ ] Operator guide updated (how to configure / troubleshoot)
- [ ] Decision records finalized (explaining trade-offs)
- [ ] Retrospective lessons captured
- [ ] Known issues documented (if any)

---

## Post-Mortems & Learning

### Monthly Review: Data-Driven Course Correction

**First Friday of Each Month**:
1. **IBAC Performance Review**:
   - How many escalations? (Target: 10–20%)
   - How many false positives? (Target: < 5%)
   - Average latency? (Target: < 500ms)
   - Any patterns in escalations? (e.g., "NLP always escalates X type of request")

2. **Constitutional AI Adoption Review**:
   - How many constitutional violations detected? (Target: > 0, < 10/day)
   - How many operator overrides? (Target: < 5%)
   - Are principles clear to operators?

3. **Agent Stability Review** (DyTopo):
   - How many agents active? Growth trajectory?
   - How many fail-overs? (Target: < 1 per week)
   - MTTR (mean time to recovery): < 1 sec?

4. **Operational Burden Review**:
   - Operator feedback: Is Phase 2 making their job easier or harder?
   - Policy maintenance: How often do IBAC policies change?
   - False alarms: Any constitutional violations that are actually OK?

**Action**: If data contradicts design (e.g., "Escalation rate is 40%, target was 10%"):
- Root cause analysis (why is it higher?)
- Decision: Adjust threshold? Change rules? Improve LLM prompt?
- Implement & re-measure in 2 weeks

---

## Team Rituals for Health

### The "Brag Board" (Friday Retrospective)
**Purpose**: Celebrate wins; build morale

**Practice**: 
- Each workstream lead shares one thing they're proud of this week
- "Brag board" is screenshotted and shared with exec sponsor

**Example**:
```
Infrastructure: "IBAC cache reduced latency from 2.5s to 0.8s! 🎉"
Security: "Constitutional violation detection @ 100% accuracy ✅"
QA: "Caught a race condition in DyTopo! Would have been P1 incident in prod 🛡️"
```

---

### The "Gut Check" (Monthly Retrospective)
**Purpose**: Honest assessment of whether we're on track

**Questions**:
- Are we hitting our latency targets?
- Is operational burden acceptable?
- Do we still believe in our architectural decisions?
- Would we make the same choices again?

**Possible Outcomes**:
- ✅ Green: On track; continue as planned
- 🟡 Yellow: Some concerns; minor adjustments next sprint
- 🔴 Red: Major issue; needs architect review + possible delay

---

## Escalation Paths for Common Issues

### Issue: Test Coverage Is Low (< 80% on a workstream)

**What to do**:
1. Workstream lead talks to QA lead (same day)
2. Options:
   - Add more tests (extends timeline by ~5 days)
   - Reduce scope (descope low-risk feature, maintain 80%)
   - Risk acceptance (document why this workstream is exception)
3. Decision documented in decision record
4. Code review requires explicit sign-off on coverage decision

---

### Issue: Latency Target Not Met (IBAC is 2.5s instead of 1.5s)

**What to do**:
1. Perf team profiles (where is time spent?)
2. Root cause identified (e.g., "LLM model inference is 2s")
3. Options:
   - Optimize (parallelization, caching, model swap)
   - Accept & adjust target (1.5s → 2.5s)
   - Defer (move to Phase 2b; keep Phase 2a simpler)
4. Data presented at decision meeting
5. Team decides (architect breaks ties)

---

### Issue: Operator Feedback Is Negative (Constitution is too strict)

**What to do**:
1. Collect feedback (monthly operator survey)
2. If consistent pattern (e.g., "Constitution blocks 30% of our normal work"):
   - Host operator workshop (design constitutional amendments)
   - Propose new principles
   - Test with operators (trial run)
3. If adopted: Decision record explains change + rationale
4. If not adopted: Document why (helps future teams)

---

## Success Criteria for Phase 2 Process

- ✅ Weekly standups happen (100%)
- ✅ Decision records capture all architectural decisions (100%)
- ✅ Code review turnaround < 3 days (95%)
- ✅ Test coverage >= 80% on all workstreams (100%)
- ✅ No surprises at end of workstream (all blockers surfaced early)
- ✅ Team morale remains high (subjective, but celebrated in retros)
- ✅ Scope creep < 10% (track in decision records)

---

## How This Differs from Typical "Agile"

| Aspect | Typical Agile | Phase 2 Process |
|--------|---------------|-----------------|
| Iteration | 2-week sprints w/ burn-down | 8-week workstreams w/ monthly data reviews |
| Decision Making | Story points + velocity | Data-driven; confidence scores |
| Documentation | "User stories" | Decision records + retrospectives |
| Feedback Loop | Sprint retro every 2 weeks | Monthly data deep-dives |
| Scope Adjustment | Every sprint | Monthly; track all changes in DRs |
| Quality Gate | "Definition of done" (subjective) | Tests pass (objective) + No credential leaks |
| Knowledge Capture | Wiki/Confluence (often stale) | Timestamped DRs + retrospectives (searchable, time-bound) |

**Why This Approach?**
- Phase 2 is strategic (8 weeks); short sprints waste effort on sprint planning
- Architectural stability matters (don't change design every 2 weeks)
- Learning matters (retrospectives analyze patterns, not just "What happened last sprint?")

---

## Next Steps

1. **This Week**: Team reviews & approves process framework
2. **Week of Mar 11**: Kick-off; workstreams officially start
3. **Every Monday**: Standup (notes in `workflows/005-Skill-Trust-Capabilities/`)
4. **Every Friday**: Retrospective + decision record review
5. **First Friday of Each Month**: Data review + course correction

---

*Process & Governance v1.0 | Feb 10, 2026*
