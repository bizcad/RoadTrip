# Workflow 006 Process Governance

**Version**: 1.0  
**Status**: Operational Framework  
**Created**: Feb 10, 2026  
**Purpose**: Define how RoadTrip operates the Skill Acquisition process

---

## Overview

Skill acquisition is a **human process** first; systems second. This document defines:
- **Weekly cadence** (when things happen)
- **Roles & responsibilities** (who does what)
- **Decision-making framework** (how to decide)
- **Communication norms** (how we talk)
- **Async-first operations** (minimize meetings)

---

## Weekly Cadence

### Monday: Weekly Standup (30 min, async first)

**Format**: Slack thread + optional 15-min video call

**Participants**: Full team (discovery lead, vetting committee, onboarding, product)

**Agenda**:
1. **Discovery**: What did we find this week?
   - New candidates discovered (count)
   - Top 3 candidates for vetting queue
   - Any blockers?

2. **Vetting**: What's moving?
   - Skills completed this week
   - Current queue status
   - Anything stuck?

3. **Onboarding**: What's in production?
   - Skills ready (count)
   - Skills deployed (count)
   - Any issues in production?

4. **Learning**: Anything we learned?
   - Rejected skills with key takeaways
   - Production feedback
   - Discovery improvements

5. **Asks**: Anything blocked?
   - Unblock requests
   - Dependencies
   - Resource constraints

**Output**: Monday standup thread with team input

**Async Protocol**:
- Discovery lead posts summary by 9am Monday
- Each team lead adds their update by 12pm
- Leaders thread-reply if needed
- Optional 2pm video call for discussion (15 min max; optional attendance)
- Everything documented in thread

---

### Wednesday: Vetting Decision Sync (60 min, synchronous)

**Format**: Video meeting (required attendance: vetting committee + product lead)

**Participants**: 
- Security expert (required)
- Infrastructure engineer (required)
- Domain expert (required)
- Product lead (required)
- Optional: Observer from onboarding team

**Agenda**:
1. **Review completed vetting** (30 min)
   - Present each vetting decision
   - Discussion (any flags?)
   - Committee sign-off (unanimous ideal)

2. **Discuss conditional approvals** (15 min)
   - Which conditions are met?
   - Who's fixing outstanding conditions?
   - Timeline confirmation

3. **Next week's prioritization** (15 min)
   - Which candidate should vetting start next?
   - Urgency ranking confirmed
   - Reviewer assignment

**Output**: 
- Vetting decisions recorded & published
- Conditional approval assignments
- Next week's priority list

**Meeting Protocol**:
- Come prepared (read vetting reports beforehand)
- Decisions ideally unanimous; if not, 2/3 majority rules
- Dissenters document their concern (added to decision record)
- All decisions recorded same day; published to team

**Decision Recording** (same day):
- Vetting committee posts decisions to #skill-acquisition Slack
- Each decision: [APPROVED] / [CONDITIONAL] / [REJECTED] + brief rationale
- Full decision record written by reviewer + reviewed by committee

---

### Thursday: Onboarding Check-In (30 min, async-first)

**Format**: Slack thread + optional video call

**Participants**: Onboarding engineer, product lead, optionally vetting committee

**Agenda**:
1. **Onboarding status**: What's in progress?
   - Fingerprints assigned (count)
   - Tests created (count)
   - Blocks discovered?

2. **Production integrations**: How are they doing?
   - New deployments this week?
   - Any production issues?
   - Performance metrics review

3. **Blockers**: Anything stuck?
   - Unblock requests
   - Escalations

**Output**: Asynchronous updates; escalations raised

**Async Protocol**:
- Onboarding lead posts status by 9am Thursday
- Team replies in thread
- Optional video call 3pm for escalations (15 min max)

---

### Friday: Retrospective & Learning (60 min, synchronous)

**Format**: Video meeting (full team; optional attendance but encouraged)

**Participants**: Everyone (discovery, vetting, onboarding, product, observers)

**Agenda**:
1. **This week's wins** (15 min)
   - Skills approved?
   - Skills deployed?
   - Learning captured?
   - Team shout-outs?

2. **What went well?** (10 min)
   - Discovery sprint went smooth?
   - Vetting decisions aligned?
   - Onboarding efficient?
   - From individual reflections

3. **What didn't go well?** (10 min)
   - Blockers we hit?
   - Process friction?
   - Communication gaps?

4. **What will we improve?** (15 min)
   - One process change for next week?
   - One learning to apply?
   - One skill to highlight?

5. **Next week preview** (10 min)
   - Major candidates coming in
   - Expected decisions
   - Any special asks

**Output**: 
- Weekly learning document (published to team)
- One process improvement identified
- Team momentum and morale check

**Publication**:
- Scribe writes up learnings + improvements
- Posted to #skill-acquisition by EOD Friday
- Includes: wins, blockers, process improvements, next week preview

---

## Roles & Responsibilities

### Discovery Lead (1 FTE)

**Responsibilities**:
- Actively scan 5 primary sources for candidates
- Filter by relevance & urgency
- Create candidate profiles (URL, description, initial assessment)
- Prioritize queues (what goes to vetting next)
- Maintain discovery backlog

**Weekly Commitment**:
- Monday: Standup (5 min)
- Wednesday: Vetting sync (optional)
- Thursday: Onboarding check-in (optional)
- Friday: Retrospective (30 min)
- **Total**: 8 hours/week discovery work + 1 hour meetings

**Key Metric**: Candidates/week (target: 5–10)

**Tools**: 
- GitHub, PyPI, HuggingFace API
- Google Docs (candidate backlog)
- Slack for coordination

---

### Security Expert (0.5 FTE)

**Responsibilities**:
- Lead security assessment section of vetting
- Check for CVEs
- Identify suspicious code patterns
- License compatibility review
- Escalate high-risk findings

**Weekly Commitment**:
- Monday: Standup (5 min)
- Wednesday: Vetting sync (1 hour)
- Thursday: Optional onboarding check-in
- Friday: Retrospective (30 min)
- **Total**: 4 hours/week vetting + 2 hours meetings

**Key Metric**: Security issues caught (target: 3/month)

**Tools**: CVE databases, pip-audit, code review tools

---

### Infrastructure Engineer (0.5 FTE)

**Responsibilities**:
- Lead integration feasibility assessment
- Determine infrastructure requirements
- Estimate integration effort
- Identify conflicts with existing skills
- Support onboarding with integration challenges

**Weekly Commitment**:
- Monday: Standup (5 min)
- Wednesday: Vetting sync (1 hour)
- Thursday: Onboarding check-in (15 min)
- Friday: Retrospective (30 min)
- **Total**: 4 hours/week vetting + 2 hours meetings

**Key Metric**: Integration complexity assessments (target: 8/month)

**Tools**: RoadTrip codebase, architecture docs, test harnesses

---

### Domain Expert (0.5 FTE)

**Responsibilities**:
- Lead capability analysis
- Assess RoadTrip fit
- Determine urgency
- Evaluate against roadmap
- Domain-specific code quality review

**Weekly Commitment**:
- Monday: Standup (5 min)
- Wednesday: Vetting sync (1 hour)
- Thursday: Optional onboarding check-in
- Friday: Retrospective (30 min)
- **Total**: 4 hours/week vetting + 2 hours meetings

**Key Metric**: Capability assessments (target: 8/month)

**Tools**: RoadTrip roadmap, domain knowledge, codebase understanding

---

### Onboarding Engineer (1 FTE)

**Responsibilities**:
- Fingerprint skills
- Create capability metadata
- Write integration tests
- Index skills in BERT
- Coordinate production integration
- Monitor production health
- Escalate production issues

**Weekly Commitment**:
- Monday: Standup (5 min)
- Wednesday: Vetting sync (optional)
- Thursday: Onboarding check-in (30 min)
- Friday: Retrospective (30 min)
- **Total**: 8 hours/week onboarding + 1 hour meetings

**Key Metric**: Skills to production-ready/month (target: 3–5)

**Tools**: Python, test frameworks, BERT, monitoring/logging

---

### Product Lead / Decision Maker (0.25 FTE)

**Responsibilities**:
- Strategic alignment (roadmap fit)
- Tiebreaker if vetting committee disagrees
- Escalation point for complex decisions
- Stakeholder communication
- Quarterly reviews of acquisition velocity

**Weekly Commitment**:
- Monday: Standup (5 min, async)
- Wednesday: Vetting sync (1 hour)
- Friday: Retrospective (30 min)
- **Total**: 2 hours/week + 1.5 hours meetings

**Key Metric**: Strategic alignment (100% of approved skills align with roadmap)

**Tools**: RoadTrip roadmap, stakeholder comms

---

## Decision-Making Framework

### Decision Types

**Type 1: Vetting Decision** (Is skill approved? Y/N/Conditional)
- **Authority**: Vetting committee (unanimous ideal; 2/3 majority if needed)
- **Timeline**: Within 14 days of vetting start
- **Escalation**: Product lead if committee deadlocks
- **Documentation**: Decision record published by Friday

**Type 2: Prioritization Decision** (Which skills to evaluate first?)
- **Authority**: Discovery lead + product lead
- **Timeline**: Weekly (Monday standup)
- **Input**: Urgency ranking, roadmap alignment
- **Documentation**: Slack thread

**Type 3: Conditional Approval Decision** (What conditions must be met?)
- **Authority**: Vetting committee
- **Timeline**: When vetting complete
- **Condition Owner**: Assigned during vetting decision
- **Documentation**: Part of decision record

**Type 4: Production Integration Decision** (Ready for production?)
- **Authority**: Onboarding engineer + infrastructure engineer
- **Timeline**: When tests pass
- **Validation**: All integration tests pass (no manual override)
- **Documentation**: CI/CD logs + metadata completed

**Type 5: Deprecation Decision** (Should we retire a skill?)
- **Authority**: Product lead + operations team
- **Timeline**: Quarterly review
- **Cause**: Low usage, poor performance, or replaced
- **Timeline**: 4-week deprecation notice
- **Documentation**: Deprecation record + migration guide

### Disagreement Resolution

**Scenario: Vetting committee can't agree**

Example: Security expert says REJECT (risky); Domain expert says APPROVE (high value)

**Process**:
1. **Document the disagreement** (in decision record)
   - Section A: Security expert's concerns
   - Section B: Domain expert's reasoning
   - Both perspectives clearly stated

2. **Attempt consensus** (Wednesday vetting sync)
   - Discuss rationale
   - Seek additional data
   - Look for compromise (conditional approval?)

3. **If still disagreed**: Use vote
   - **Unanimous**: All 3 agree (ideal)
   - **2/3 Majority**: 2 of 3 agree (acceptable)
   - **Deadlock (1.5/3)**: Escalate to product lead

4. **If escalated to product lead**:
   - Product lead reviews data
   - Makes final call (casting vote)
   - Must document reasoning
   - Disagreeing expert records dissent

**Example Resolution** (Deadlock):
```
Skill: "async-task-queue"
Committee: Split 1.5 / 2.5

Position A (Pro): Domain + Infrastructure say APPROVE
- Urgency: 5/5
- Integration: Feasible (40 hours)
- Risk: Manageable

Position B (Con): Security says REJECT (or CONDITIONAL)
- CVEs: None in core code, but 2 in dependencies (patched)
- License: GPL (potential conflict if we commercialize)
- Suspicious patterns: None

Product Lead Decision (Tiebreaker):
CONDITIONAL APPROVAL
Conditions:
1. Update dependencies to patched versions (Security owns)
2. Clarify GPL implications legally (Legal owns)
3. Resubmit on [date]

Rationale: High-value skill; risks are manageable with conditions.
Dissent Record: Security expert notes concern; conditional path acceptable.
```

---

## Communication Norms

### Slack Guidelines

**Channels**:
- `#skill-acquisition`: Main channel (announcements, decisions, status)
  - Monday standup thread
  - Wednesday vetting decisions
  - Thursday onboarding update
  - Friday retrospective
  
- `#skill-acquisition-dev`: Technical discussions (code review, testing)
  - Technical questions
  - Integration challenges
  - Debug threads

- `#skill-acquisition-process`: Process improvement (meta-discussion)
  - Process friction discussion
  - Suggestions for better ways
  - Lessons learned

**Response Times**:
- Standup posts: Reply by end of day (EOD) with your update
- Vetting decisions: Published same day (by 5pm Friday)
- Questions: Response within 24 hours
- Blockers: Escalate immediately (don't wait for meeting)

### Documentation Standards

**Every Skill Gets Documented**:

1. **Candidate Profile** (Discovery → Vetting)
   - Source URL
   - Description (what does it do?)
   - Urgency ranking (1–5)
   - Approver for vetting
   - Date entered

2. **Vetting Decision Record** (Vetting → Onboarding/Archive)
   - Weighted scores (A, B, C, D)
   - Overall decision (APPROVE / CONDITIONAL / REJECT)
   - Rationale (1–2 sentences)
   - Committee sign-offs
   - If conditional: conditions + owners
   - If rejected: learnings captured

3. **Onboarding Metadata** (Onboarding → Production)
   - Fingerprint (SHA256)
   - Capabilities (named list)
   - Integration notes
   - Test results
   - Deployment date

4. **Production Record** (Production → Learning)
   - Monthly metrics (invocations, success rate, latency)
   - User feedback
   - Issues encountered
   - Quarterly reviews + recommendation

**Storage**:
- Candidate profiles: Google Sheets (discovery backlog)
- Vetting decision records: GitHub gist (linked in Slack)
- Onboarding metadata: In skill header YAML
- Production records: Wiki page (aggregate view)

---

## Async-First Operations

### Principle

Maximize asynchronous work; minimize meetings. 

**Meeting Time Budget**: Max 3.5 hours/week for full team

### How It Works

**Mondays (Standup)**:
- Async-first: Slack thread (30 min for leads to read & update)
- Optional video call (15 min) only if needed for discussion
- Total: 5–15 min per person

**Wednesdays (Vetting Sync)**:
- Synchronous: Video meeting required (1 hour)
- Reason: Decisions require discussion & consensus
- Cannot be fully async (nuanced judgment)
- Come prepared: Read vetting reports beforehand (30 min async prep)

**Thursdays (Onboarding Check-in)**:
- Async-first: Slack thread (30 min for leads)
- Optional video call (15 min) for blockers
- Total: 5–20 min per person

**Fridays (Retrospective)**:
- Synchronous: Video meeting (1 hour)
- Reason: Team building & learning together
- Optional but encouraged (culture-building)
- After-call write-up published asynchronously

### Daily Work

Everything else is async:
- Code reviews: Async (GH PR comments)
- Technical discussions: Slack threads
- Escalations: Asynchronous (document + link in Slack)
- Learning capture: Async (document + share)

---

## Quality Gates

### Skills Must Pass These Gates to Progress

**Discovery → Vetting**:
- [ ] Candidate profile complete
- [ ] Urgency ranking assigned
- [ ] Vetting reviewer assigned

**Vetting → Onboarding**:
- [ ] All 5 vetting sections scored
- [ ] Weighted score calculated
- [ ] Decision record signed by committee
- [ ] If conditional: conditions documented + owners assigned

**Onboarding → Production**:
- [ ] Fingerprint computed
- [ ] Capabilities documented
- [ ] Tests created & passing (100% of capabilities tested)
- [ ] Metadata YAML complete
- [ ] BERT indexed
- [ ] Orchestrator integration verified

**Production → Learning**:
- [ ] 4+ weeks in production
- [ ] Metrics collected & stable
- [ ] Quarterly review completed
- [ ] Learning insights documented for discovery

---

## Escalation Path

### Problem: Blocker in Discovery
**Who**: Anyone
**Action**: @discovery-lead in Slack (immediate)
**Timeline**: Response within 4 hours
**If unresolved**: Escalate to product lead (24 hours)

### Problem: Vetting Disagreement (Committee deadlock)
**Who**: Vetting committee
**Action**: Document both sides; escalate in Wednesday sync
**Timeline**: Decision by Friday
**If unresolved**: Product lead casts tiebreaker vote (same day)

### Problem: Onboarding Blocker (Integration issue)
**Who**: Onboarding engineer
**Action**: @infrastructure-engineer in Slack
**Timeline**: Pair troubleshooting within 24 hours
**If critical**: Escalate to product lead (immediate)

### Problem: Production Issue (Skill failing)
**Who**: Operations / orchestrator
**Action**: Create incident in #skill-acquisition-dev
**Timeline**: Immediate investigation (same day)
**Decision**: Fix, deprecate, or investigate (within 48 hours)

### Problem: Process Friction
**Who**: Any team member
**Action**: Document in #skill-acquisition-process
**Timeline**: Discuss Friday retrospective
**Improvement**: Try new process next week

---

## Learning Capture

### Every Week: Learning Document

**Friday retrospective produces**:
- What went well (winners)
- What didn't work (blockers)
- What we learned (insights)
- What we'll change (improvements)

**Example (Week of Mar 10)**:
```
SKILL ACQUISITION LEARNING REPORT
Week of Mar 10, 2026

WINS:
- Discovered 8 new candidates (above target of 5)
- Approved "async-task-queue" with conditional (Redis setup)
- Deployed "pydantic" to production; 0 issues

BLOCKERS:
- Redis infrastructure delayed; impacts conditional approval path
- Vetting framework took longer than expected (inexperience)
- One skill rejected due to GPL conflict (new learning)

LEARNINGS:
- Discovery tip: PyPI "top packages" trending section is goldmine
- Vetting insight: License check should happen earlier (saves vetting time)
- Production insight: Skills need 2 weeks warm-up before full confidence

IMPROVEMENTS (Next Week):
- Add "license check" as first step of vetting (before capability review)
- Test Redis setup in staging to unblock conditional approvals
- Publish vetting framework guide (new reviewers can learn faster)

NEXT WEEK PRIORITIES:
- Continue vetting async-task-queue conditional (Redis setup)
- Start vetting 3 new candidates (SQLAlchemy, FastAPI extensions, logging)
- Deploy pydantic v2 patch (production performance improvement)
```

### Every Month: Acquisition Report

**Metrics published**:
- New candidates discovered (target: 20)
- Skills evaluated (target: 8)
- Approval rate (target: 40%)
- Skills onboarded (target: 3–4)
- Skills deployed (target: 2–3)
- Production incidents (target: 0)

### Every Quarter: Strategic Review

**Review performed**:
- Top performers (gold-star skills)
- Low performers (candidates for deprecation)
- Discovery patterns (what to look for more)
- Vetting insights (improve framework)
- Process improvements (what's working; what needs change)

---

## Appendix: Meeting Templates

### Monday Standup Template

```
SKILL ACQUISITION STANDUP - Week of [DATE]

🔍 DISCOVERY (Lead: _____)
- New candidates: [#] found
- Top 3 for vetting: [Skill A], [Skill B], [Skill C]
- Blockers: [None / List here]

✓ VETTING (Committee)
- Completed: [Skill X] → Approved / Conditional / Rejected
- In progress: [Skill Y] (X% done)
- Current queue: [Count] skills waiting
- Blockers: [None / List here]

🚀 ONBOARDING (Lead: _____)
- Ready for prod: [Skill A], [Skill B]
- Deployed: [Skill C] (2 days in prod; no issues)
- In progress: [Skill D] (tests 80% done)
- Blockers: [None / List here]

📚 LEARNING
- Key insight: [One learning from rejected skill / production feedback]
- Process improvement idea: [If any]

❓ ASKING FOR HELP
- [Item 1]: Who can help with [specific blocker]?
- [Item 2]: Need approval for [decision]?
```

### Vetting Decision Record Template

```
SKILL VETTING DECISION RECORD
==============================

Skill Name: _________________
Reviewed by: _________________
Date: _________________

A. CAPABILITY ANALYSIS
   - What does it do: [One sentence]
   - RoadTrip relevance: [High/Medium/Low]
   - Urgency: [1–5]
   ✓ Assessment: [Brief summary]

B. CODE QUALITY
   - Type hints: [%]
   - Test coverage: [%]
   - Maintenance: [Active/Stable/Declining]
   ✓ Score: [1–5]

C. SECURITY
   - Known CVEs: [None / List]
   - Suspicious patterns: [None / List]
   - License: [Type and compatibility]
   ✓ Score: [1–5]

D. INTEGRATION
   - Effort estimate: [Hours]
   - Infrastructure required: [Y/N]
   - Feasibility score: [1–5]

E. DECISION
   Weighted Score: [___/5]
   
   ✅ APPROVED
   or
   ⚠️  CONDITIONAL - Conditions:
       1. [Condition], owner: [Person], due: [Date]
       2. [Condition], owner: [Person], due: [Date]
   or
   ❌ REJECTED - Reason: [Brief summary]
       Learning captured: [What we learned]

Committee Sign-Off:
- Security expert: [Name] ✓ / ❌
- Infrastructure: [Name] ✓ / ❌
- Domain expert: [Name] ✓ / ❌

Approved by: _________________ (Unanimous / 2-3 vote)
Date: _________________
```

---

*Workflow 006 Process Governance v1.0 | Feb 10, 2026*
