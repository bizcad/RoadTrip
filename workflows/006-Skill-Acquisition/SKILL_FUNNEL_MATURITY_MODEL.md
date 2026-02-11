# Skill Funnel Maturity Model

**Version**: 1.0  
**Status**: Framework Definition  
**Created**: Feb 10, 2026  
**Purpose**: Define detailed criteria and gates for skill progression through the acquisition funnel

---

## Overview

The Skill Acquisition Funnel has four stages. Each stage has:
- **Entry Criteria** (what must be true to enter?)
- **Process** (what happens in this stage?)
- **Maturity Model** (levels 0–5; where is this skill?)
- **Exit Criteria** (what must be true to move forward?)
- **Hold/Loop** (what if it doesn't meet criteria?)

This document defines the **maturity model** for each stage, allowing skills to be ranked, prioritized, and tracked consistently.

---

## Universal Maturity Scale (0–5)

Every skill can be assessed along these dimensions:

| Level | Status | Definition |
|-------|--------|-----------|
| 0 | Unknown | No information gathered yet |
| 1 | Initial | Minimal assessment; high uncertainty |
| 2 | Repeatable | Process started; some structure |
| 3 | Defined | Clear understanding; documented |
| 4 | Managed | Metrics tracked; under control |
| 5 | Optimized | Continuous improvement; proven |

**Purpose**: Transparently communicate where each skill is in the funnel.

---

## Stage 1: Research & Discovery

### Goal
Find candidates meeting basic criteria (relevance, viability). Create ranked list.

### Entry Criteria
- Skill exists somewhere (GitHub, PyPI, HuggingFace, ArXiv, internal idea)
- Discoverable (public repository, published paper, documented code)

### Process
1. Identify potential sources
2. Scan for candidates
3. Apply initial filters
4. Rank by urgency
5. Create candidate profile

### Maturity Progression

**Level 0: Unknown**
- Skill not yet in discovery pipeline
- No candidate profile created
- Unknown relevance

**Level 1: Initial Discovery**
- Skill found in source (GitHub trending, PyPI, etc.)
- Basic info gathered (name, description, creator)
- Quick relevance check (appears relevant? Y/N)
- Not yet ranked

**Level 2: Identified as Candidate**
- Candidate profile created (source URL, brief description)
- Initial filter applied (is this worth deeper look?)
- Rough urgency ranking (low/med/high)
- Status: "In Discovery Backlog"

**Level 3: Prioritized for Vetting**
- Detailed relevance assessment (roadmap alignment)
- Urgency ranking confirmed
- Assigned to vetting reviewer
- Status: "Ready for Vetting Queue"

**Level 4: Vetting Scheduled**
- Vetting reviewer assigned
- Interview scheduled
- Skill moved to "In Vetting" queue
- Status: "In Vetting"

**Level 5: Vetting Started**
- Vetting actively in progress
- Initial capability review underway
- Status: "Active Vetting"

### Maturity Checklist

| Maturity | Entry Criteria | Process | Tracking |
|----------|---|---|---|
| 1 | Found, basic info | Quick scan | URL, title, desc |
| 2 | Relevant?✓, filters✓ | Raw candidacy | Profile created |
| 3 | Detailed relevance✓, urgency✓ | Prioritized | Roadmap alignment |
| 4 | Vetting reviewer assigned✓ | Scheduled | Reviewer name, date |
| 5 | Reviewer started✓ | In-progress | Time invested (hrs) |

### Exit Criteria (Move to Vetting)
- [x] Candidate profile complete
- [x] Urgency ranking assigned (1–5 scale)
- [x] Vetting reviewer assigned
- [x] Skill moved to "Active Vetting" status

### Metrics
- **Discovery Velocity**: New candidates/week (target: 5–10)
- **Filter Rate**: % candidates that pass initial filter (target: 40–60%)
- **Ranking Agreement**: % candidates where reviewers agree on urgency (target: 80%+)

### Hold Conditions
- Candidate profile incomplete → Return to "Level 1" for more research
- Relevance unclear → Defer to next quarter
- Urgency very low → Archive until roadmap changes

---

## Stage 2: Vetting & Evaluation

### Goal
Deep analysis of capability, code quality, security, and integration feasibility. Produce go/no-go decision.

### Entry Criteria
- Candidate profile complete (from Stage 1)
- Vetting reviewer assigned
- Time allocated for review (8–16 hours typical)

### Process
**2a: Capability Analysis** (2–4 hours)
- Read documentation
- Understand intended use
- Run code examples
- Verify reality matches claims

**2b: Code Quality Review** (2–4 hours)
- Type hints? (Python)
- Tests? (target: 80%+ coverage)
- Documentation? (README, docstrings, examples)
- Structure? (SOLID principles)
- Maintenance? (last update, activity level)

**2c: Security & Risk Assessment** (2–4 hours)
- Known CVEs?
- Suspicious patterns? (shell execution, network calls)
- Dependency health?
- License compatibility?
- Could this be malicious?

**2d: Integration Feasibility** (1–2 hours)
- Effort estimate to integrate into orchestrator
- Conflicts with existing skills?
- Need for modifications?
- Infrastructure requirements?

**2e: Learning Documentation** (1–2 hours)
- Capture key learnings
- Decision rationale
- Pattern identification
- Recommendations for discovery

### Maturity Progression

**Level 0: Not Started**
- Skill in vetting queue
- No analysis begun
- Status: "Waiting for Review"

**Level 1: Initial Assessment**
- Reviewer started; reviewing docs
- First impressions gathered
- No formal evaluation yet
- Quick "gut check" underway

**Level 2: Capability Analysis Complete**
- What does it do? Documented
- Claims vs. reality assessed
- Fit for RoadTrip? Preliminary yes/no
- Status: "Capability Review Done"

**Level 3: Technical Review Complete**
- Code quality assessed
- Test coverage documented
- Dependencies analyzed
- Maintenance status clear
- Status: "Technical Review Done"

**Level 4: Security Assessment Complete**
- CVEs checked
- Suspicious patterns identified
- License confirmed compatible
- Risk level assigned (low/med/high)
- Status: "Security Review Done"

**Level 5: All Reviews Complete + Decision Made**
- Integration feasibility assessed
- Learning documentation written
- Go/No-Go decision made
- Status: "Vetting Complete" → Decision determined

### Maturity Checklist

| Maturity | Reviewed | Documented | Decided |
|----------|----------|-----------|---------|
| 1 | Docs scanned | Initial notes | Preliminary vibes |
| 2 | Capability ✓ | What it does | Fit? Yes/No/Maybe |
| 3 | Code quality ✓ | Code score (1–5) | Quality? Y/N |
| 4 | Security ✓ | Risks identified | Risk level (L/M/H) |
| 5 | Integration ✓ | Effort estimate | GO / NO-GO / CONDITIONAL |

### Exit Criteria (Move to Onboarding or Rejection)

**For APPROVAL**:
- [x] All five reviews complete
- [x] Capability: Fit for RoadTrip (Y/N)
- [x] Code Quality: 3+ on 5-point scale
- [x] Security: No critical issues; risk < HIGH
- [x] Integration: Feasible (effort estimated)
- [x] Committee consensus (unanimous or 2/3?)

**For REJECTION**:
- [x] Clear rationale documented
- [x] Learning captured
- [x] Deferred or archived?

**For CONDITIONAL APPROVAL**:
- [x] Condition clearly stated (e.g., "if we add Redis")
- [x] Path forward defined

### Vetting Framework (Applied in This Stage)
See VETTING_FRAMEWORK.md for detailed checklist & rating scales.

### Metrics
- **Vetting Cycle Time**: Days from start to decision (target: < 14 days)
- **Approval Rate**: % of evaluated skills approved (target: 40–50%)
- **Reviewer Agreement**: % decisions with consensus (target: 90%+)
- **Learning Capture**: % decisions have decision records (target: 100%)

### Hold Conditions
- Insufficient information → Request more data; extend review
- Reviewer unavailable → Reassign to backup reviewer
- External dependency blocks review → Document blocker; update ETA

---

## Stage 3: Onboarding & Codification

### Goal
Formalize skill metadata, fingerprints, capabilities, and integration tests. Make it production-ready.

### Entry Criteria
- Skill approved from Stage 2
- "Ready for Onboarding" status
- Onboarding engineer assigned
- Infrastructure in place (BERT, registry, etc.)

### Process

**3a: Skill Fingerprinting** (1 hour)
- Compute SHA256 of interface + tests + version
- Store in skill header
- Create provenance record (source, commit, vetting date)

**3b: Capability Definition** (2–3 hours)
- List named capabilities
- Input/output type specs
- Cost estimates (latency, memory, CPU)
- Confidence levels (0.0–1.0)
- Constraints & limitations

**3c: Metadata Assignment** (1–2 hours)
- Skill header YAML
- Integration notes
- Maintenance contact
- Sunset date
- Support matrix

**3d: BERT Indexing** (1 hour)
- Embed in knowledge base
- By capability name
- By category tags
- Link to vetting decision record

**3e: Test Harness Creation** (2–4 hours)
- Unit tests
- Integration tests
- Error scenarios
- Performance baseline

### Maturity Progression

**Level 0: Not Started**
- Skill approved; awaiting onboarding
- No metadata assigned
- Status: "Waiting for Onboarding"

**Level 1: Metadata Started**
- Fingerprint computed (not yet stored)
- Draft capabilities list started
- Status: "Onboarding In Progress"

**Level 2: Metadata Assigned**
- Fingerprint in header ✓
- Capabilities documented ✓
- YAML skeleton created ✓
- Status: "Metadata Ready for Review"

**Level 3: Metadata Finalized**
- All metadata reviewed
- Capabilities validated
- Test harness created ✓
- Status: "Tests Created"

**Level 4: Tests Passing**
- All integration tests pass ✓
- Performance baseline established ✓
- Error scenarios handled ✓
- Status: "Tests Pass"

**Level 5: Production Ready**
- Everything verified ✓
- Developer documentation written ✓
- Ready for orchestrator integration ✓
- Status: "Ready for Production"

### Maturity Checklist

| Maturity | Metadata | Tests | Ready |
|----------|----------|-------|-------|
| 1 | Partial | None | No |
| 2 | Assigned | Created | Testing |
| 3 | Complete | Draft | Review |
| 4 | Complete | Passing | Verification |
| 5 | Complete | Passing | YES ✓ |

### Exit Criteria (Move to Production)
- [x] Fingerprint computed & stored
- [x] All capabilities documented
- [x] Header YAML complete
- [x] BERT indexed
- [x] All tests passing
- [x] Performance baseline established
- [x] Developer documentation complete
- [x] Ready for orchestrator integration

### Metrics
- **Onboarding Cycle Time**: Days to production-ready (target: < 7 days)
- **Test Coverage**: % of capabilities tested (target: 100%)
- **Metadata Completeness**: % of required fields filled (target: 100%)
- **Integration Success**: % of skills that pass orchestrator tests (target: 95%+)

### Hold Conditions
- Tests failing → Debug & fix; hold in "Testing" state
- Metadata incomplete → Return to onboarding for completion
- Performance unacceptable → Optimize or reject

---

## Stage 4: Production & Continuous Feedback Loop

### Goal
Monitor real-world usage. Collect feedback. Measure value. Continuously improve. Learn for next skills.

### Entry Criteria
- Skill passed all onboarding tests
- Orchestrator integrated
- Monitoring configured
- Status: "In Production"

### Process

**4a: Production Monitoring** (Continuous)
- Invocation count (is it being used?)
- Success rate (% of calls succeed)
- Error patterns (what breaks?)
- Latency distribution (P50, P95, P99)
- Resource usage (CPU, memory)
- Operator feedback (surveys, comments from logs)

**4b: Feedback Collection** (Ongoing)
- Weekly: Auto-generated metrics digest
- Monthly: Operator survey (manual feedback)
- Quarterly: Skill review meeting
- Continuous: Exception alerts (errors, performance degradation)

**4c: Skill Improvements** (Quarterly decision)
- Is it working well? → Confidence up
- Errors increasing? → Investigate
- Too slow? → Optimize or replace
- Opportunities to extend? → Plan Phase 3 upgrade
- Should we sunset this? → Plan deprecation

**4d: Quality Score Updates** (Quarterly)
- Adjust confidence score based on metrics
- Public score (reliability, value)
- Recommendation: "Use in X scenarios"

**4e: Continuous Learning Loop** (Quarterly)
- Review patterns in top performers
- Review patterns in poor performers
- Update discovery priorities
- Feed learnings back to Stage 1

### Maturity Progression

**Level 0: Pre-Production**
- Skill ready; not yet deployed
- Status: "Not Yet Deployed"

**Level 1: Initial Deployment**
- Deployed to production
- Minimal usage (< 10 invocations/week)
- No metrics baseline yet
- Status: "Deployed, Pre-Metrics"

**Level 2: Early Production**
- Active usage (10–100 invocations/week)
- Initial metrics collected
- Issues identified & resolved
- Status: "Early Production"

**Level 3: Steady Production**
- Regular usage (100+ invocations/week)
- Metrics stable
- Success rate 90%+
- Confidence score 0.80–0.90
- Status: "Steady Production"

**Level 4: Production Grade**
- High usage (1000+ invocations/month)
- Metrics consistently good
- Success rate 95%+
- Confidence score 0.90–0.97
- Trusted for important tasks
- Status: "Production Grade"

**Level 5: Optimized**
- Mature use (well-understood patterns)
- Continuous improvement applied
- Multiple extensions deployed
- Confidence score 0.97–1.0
- Subject matter expert on staff
- Status: "Gold Star / Best in Class"

### Maturity Checklist

| Maturity | Deployed | Metrics | Stability | Confidence | Comment |
|----------|----------|---------|-----------|-----------|---------|
| 1 | Yes | Partial | Uncertain | 0.70–0.80 | Early |
| 2 | Yes | Collected | Improving | 0.80–0.85 | Learning |
| 3 | Yes | Stable | Good | 0.85–0.90 | Trusted |
| 4 | Yes | Strong | Very Good | 0.90–0.95 | Grade A |
| 5 | Yes | Excellent | Optimized | 0.95–1.0 | Gold Star |

### Exit / Progression Criteria

**Level 1 → 2**: (4 weeks)
- 10+ invocations collected
- No critical errors
- Initial feedback positive

**Level 2 → 3**: (8 weeks)
- 100+ invocations (confidence building)
- Success rate 90%+
- Feedback: "Work is good"

**Level 3 → 4**: (12+ weeks)
- 1000+ invocations (proven)
- Success rate 95%+
- Operators request more use cases
- Feedback: "Production ready"

**Level 4 → 5**: (26+ weeks, ongoing)
- Multiple extensions deployed
- Team specialized on skill
- Continuous improvements
- Feedback: "Essential tool"

### Maintenance & Sunset Criteria

**Maintenance Mode** (Level 3–4)
- Skill still performs well
- No new features requested
- Updates only for critical issues
- Plan: "Indefinite production use"

**Deprecation** (Level 2–1)
- Success rate drops below 85%
- Replaced by better alternative
- No longer fits roadmap
- Plan: "Sunset by Q3 2027"

### Metrics (Comprehensive)

**Usage Metrics**:
- Invocations/week
- % of workflows using this skill
- User satisfaction (1–5 scale)

**Quality Metrics**:
- Success rate (%)
- Error rate (%)
- Latency (P50, P99)
- Resource usage (CPU, memory)

**Business Metrics**:
- Value created (qualitative + quantitative)
- Cost (server resources)
- Time saved (estimated operator hours)
- Risk incidents (0 ideal)

**Learning Metrics**:
- Improvements contributed to discovery
- Best practices documented
- Community engagement

### Continuous Improvement Actions

**If Good Performers:**
- Promote in discovery (look for similar)
- Document best practices
- Plan extensions

**If Poor Performers:**
- Root cause analysis
- Fix or replace?
- Sunset timeline

**If Operators Request Extensions:**
- Evaluate feasibility
- Plan Phase 3 upgrade
- Extend capabilities

---

## Cross-Stage Progression Example

**Timeline: A Single Skill (celery task queue)**

```
Feb 10 (Week 1) - STAGE 1: DISCOVERY
  Maturity: 2
  Event: Found on GitHub trending
  Status: "Candidate Identified"
  
Feb 17 (Week 2) - STAGE 1: DISCOVERY
  Maturity: 3
  Event: Prioritized for vetting (urgency: HIGH)
  Status: "Ready for Vetting Queue"
  
Feb 24 (Week 3) - STAGE 2: VETTING START
  Maturity: 1
  Event: Vetting started
  Status: "Capability Review Started"
  
Mar 10 (Week 4–5) - STAGE 2: VETTING COMPLETION
  Maturity: 5
  Decision: "APPROVED with Redis requirement"
  Status: "Vetting Complete"
  
Mar 15 (Week 6) - STAGE 3: ONBOARDING START
  Maturity: 1
  Event: Metadata assignment begun
  Status: "Onboarding In Progress"
  
Mar 22 (Week 7) - STAGE 3: TESTS PASSING
  Maturity: 4
  Event: All integration tests pass
  Status: "Tests Pass"
  
Mar 29 (Week 8) - STAGE 3: PRODUCTION READY
  Maturity: 5
  Event: Fingerprint, metadata, tests all complete
  Status: "Ready for Production"
  
Apr 5 (Week 9) - STAGE 4: DEPLOYED
  Maturity: 1
  Event: Deployed to production
  Status: "Deployed, Pre-Metrics"
  Confidence: 0.75
  
Apr 26 (Week 13) - STAGE 4: EARLY PRODUCTION
  Maturity: 2
  Event: 50 invocations, 96% success
  Status: "Early Production"
  Confidence: 0.82
  
May 24 (Week 17) - STAGE 4: STEADY PRODUCTION
  Maturity: 3
  Event: 500 invocations, 97% success
  Status: "Steady Production"
  Confidence: 0.90
  
Jun 30 (Week 22) - STAGE 4: PRODUCTION GRADE
  Maturity: 4
  Event: 2000 invocations, 98% success, Gold Star review
  Status: "Production Grade"
  Confidence: 0.95
```

**Total Time to Production Grade**: 22 weeks (5+ months)

---

## Using This Model

### For Tracking
- Every skill gets a maturity level (0–5) in every stage
- Update weekly (Friday status report)
- Public dashboard showing all skills + current stage + maturity

### For Decision Making
- Maturity 0–1 in vetting? → Likely stuck; reassign reviewer
- Maturity 4–5 in production for 16+ weeks? → Consider promotion to "Gold Star"
- Maturity 1–2 in production after 12 weeks? → Investigate issues

### For Learning
- Compare maturity curves across skills
- "Why did celery reach Grade 4 in 22 weeks, but RabbitMQ only got to Grade 3?"
- Learnings feed back into vetting framework

---

## Appendix: Maturity Dashboard View

```
SKILL ACQUISITION FUNNEL STATUS (Week of Feb 10, 2026)

STAGE 1: DISCOVERY (50 candidates)
├── Maturity 1: 10 skills (just found)
├── Maturity 2: 20 skills (candidate profiles created)
├── Maturity 3: 15 skills (prioritized for vetting)
├── Maturity 4: 5 skills (assigned, scheduled)
└── Maturity 5: 0 skills (vetting started) → Move to Stage 2

STAGE 2: VETTING (20 skills)
├── Maturity 1: 5 skills (initial review)
├── Maturity 2: 7 skills (capability done)
├── Maturity 3: 5 skills (technical done)
├── Maturity 4: 2 skills (security done)
├── Maturity 5: 1 skill (decision made)
│   └── APPROVED: celery (to Stage 3)
│   └── APPROVED: fastapi (to Stage 3)
│   └── REJECTED: bad_package (archive)
│   └── DEFERRED: maybe_later (revisit Q2)
└── Maturity 4 blocked: 3 skills (waiting for decision)

STAGE 3: ONBOARDING (3 skills)
├── Maturity 1: 1 skill (metadata start)
├── Maturity 2: 1 skill (metadata assigned)
├── Maturity 3: 0 skills
├── Maturity 4: 1 skill (tests passing)
└── Maturity 5: 0 skills → Move to Stage 4

STAGE 4: PRODUCTION (5 skills)
├── Maturity 1: 1 skill (fastapi, just deployed)
├── Maturity 2: 2 skills (pydantic, httpx, early production)
├── Maturity 3: 1 skill (docker, steady production)
├── Maturity 4: 1 skill (celery, production grade) ⭐
└── Maturity 5: 0 skills (not yet optimized)

TOTAL SKILLS IN PIPELINE: 78
APPROVED FOR PRODUCTION: 5 (3 in progress, 2 deployed)
GOLD STAR (0.95+): 1 (celery)
THROUGHPUT: 2–3 skills/month (on track for 30 by Q2 end)
```

---

*Skill Funnel Maturity Model v1.0 | Feb 10, 2026*
