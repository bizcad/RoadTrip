# Skill Acquisition Strategy: "HR for Machine Resources"

**Version**: 1.0  
**Status**: Framework Planning  
**Created**: Feb 10, 2026  
**Purpose**: Define systematic approach to discovering, vetting, and integrating skills and MCPs  

---

## Vision Statement

**Goal**: Build a continuous, systematic process to expand RoadTrip's skill library by discovering high-quality skills, rigorously vetting them for safety and fit, and safely integrating them into production.

**Metaphor**: This is organizational Human Resources, but for machine capabilities.

**Outcome**: By end of Q2 2026, RoadTrip has a mature skill acquisition pipeline processing 5+ skills/month with 80%+ approval rate and zero production incidents.

---

## The HR Metaphor (Why It Works)

### Organizational HR Process
```
Gap Analysis (what roles do we need?)
    ↓
Recruiting (find candidates)
    ↓
Screening (are they worth interviewing?)
    ↓
Technical Interview (can they do the job?)
    ↓
Background Check (are they trustworthy?)
    ↓
Offer & Negotiation (integration feasibility)
    ↓
Onboarding (formalize role, expectations, responsibilities)
    ↓
Productivity (work in role; deliver value)
    ↓
Performance Review (is this working? Feedback loop)
    ↓
(Repeat: Loop back to Gap Analysis)
```

### Machine Skill Acquisition Process
```
Skill Gap Analysis (RoadTrip roadmap → what skills missing?)
    ↓
Discovery (find skills on GitHub, HuggingFace, PyPI, etc.)
    ↓
Initial Filtering (quick assessment: relevant? Viable?)
    ↓
Technical Vetting (code quality, capability analysis, feasibility)
    ↓
Security Audit (is it safe? Malicious? Dependencies risky?)
    ↓
Integration Assessment (how much effort? What modifications needed?)
    ↓
Onboarding (fingerprint, capabilities, metadata, BERT indexing)
    ↓
Production Integration (orchestrator knows about the skill; in use)
    ↓
Production Evaluation (metrics: is this skill adding value? Errors? Feedback)
    ↓
(Repeat: Loop back to Gap Analysis with learnings)
```

### Why This Metaphor Resonates

| HR Reality | Skill Acquisition Reality |
|---|---|
| Not all candidates are good fits (even if they have the skills) | Not all published code is production-ready (even if it works) |
| Hiring team has specific needs (domain expertise, culture fit) | RoadTrip has specific needs (safety, alignment, integration ease) |
| Reference checks reveal hidden issues | Code review + usage metrics reveal hidden issues |
| Onboarding formalizes expectations | Fingerprinting + capabilities formalize what the skill is supposed to do |
| Performance reviews feedback into future hiring | Production metrics feedback into discovery (what to look for next) |
| You learn from every candidate (even rejected ones) | You learn from every skill (even rejected ones) |
| Turnover is expected (sometimes you need to let people go) | Skill deprecation is expected (sometimes packages become outdated) |

---

## Four Phases of Skill Acquisition

### Phase 1: RESEARCH & DISCOVERY

**Goal**: Cast a wide net. Find skill candidates. Index them.

**Activities**:
- Scan multiple sources (GitHub trending, HuggingFace, PyPI, ArXiv, internal ideas)
- Filter by relevance to RoadTrip mission (roughly: "Does this look potentially useful?")
- Rank by urgency (what does our roadmap need most?)
- Create candidate list

**Input**: Gap analysis from Phase 2 work + team intuition  
**Output**: Candidate skill list (50–100 possibilities)  
**Quality Gate**: Candidate list reviewed; priorities confirmed  

**Example Candidates**:
- "Automated code review framework" (GitHub trending in ML)
- "Document summarization via Claude" (HuggingFace model)
- "Async task queue" (PyPI popular package)
- "Zero-trust identity service" (ArXiv paper with code)

**Success Metric**: Discovery cadence (5 new candidates/week)

---

### Phase 2: VETTING & EVALUATION

**Goal**: Deep analysis. What does it really do? What's the risk? Should we adopt?

**Activities**:

**2a: Capability Analysis**
- What does the skill claim to do? (README, docs)
- What does it actually do? (Run it, test it)
- Does reality match claims?
- Is it applicable to RoadTrip?

**2b: Code Quality Review**
- Is code typed? (type hints in Python)
- Is it documented? (docstrings, README)
- Does it have tests? (80%+ coverage ideal)
- Is it maintainable? (clear structure, SOLID principles)
- When was it last updated?

**2c: Security & Risk Assessment**
- Any known vulnerabilities? (CVEs, advisory databases)
- Does it do anything sketchy? (shell execution, network calls)
- Are dependencies trustworthy?
- Could this be malicious? (code review for hidden behavior)
- License compatible with RoadTrip? (GPL, MIT, Apache, etc.)

**2d: Integration Feasibility**
- How much effort to integrate into orchestrator?
- Does it fit existing patterns (deterministic? Or needs LLM)?
- Any conflicts with existing skills?
- Would we need to fork/modify it?

**2e: Learning Documentation**
- For rejected skills: Why? What did we learn?
- Capture patterns (good ideas, bad implementations)
- Create decision record (for future teams)
- Even "rejected for now" skills inform discovery

**Input**: 50–100 candidates  
**Output**: 
- 5–10 "Approved for Onboarding"
- 20–30 "Rejected + Learnings"
- 15–25 "Revisit Later"

**Quality Gate**: Vetting committee sign-off (3+ reviews per skill)

**Example Vetting Decision**:
```
Skill: "Async task queue" (Python celery)

2a Capability: Does what it claims ✅
    - Async execution ✅
    - Task scheduling ✅
    - Error handling ✅

2b Code Quality: Good ✅
    - Typed ✅
    - Well-documented ✅
    - 85% test coverage ✅
    - Active maintainer ✅

2c Security: Low risk ✅
    - No known vulns ✅
    - Dependencies ok ✅
    - Does what it says ✅

2d Integration: Medium effort ⚠️
    - Needs Redis; RoadTrip doesn't have Redis
    - Could use in-process queue as fallback
    - Minimal code changes needed

2e Learning: 
    - Learned: External dependencies are ok if we can fallback

Recommendation: CONDITIONAL APPROVAL
  - Approve for onboarding IF we add Redis to infrastructure
  - Or: Use simpler built-in queue; revisit celery in Phase 3
```

**Success Metric**: Vetting cycle time (< 2 weeks per skill)

---

### Phase 3: ONBOARDING & CODIFICATION

**Goal**: Formalize metadata. Create fingerprints. Build capability spec. Make it production-ready.

**Activities**:

**3a: Skill Fingerprinting** (builds on Phase 2)
- Compute SHA256(interface + tests + version)
- Store fingerprint in skill header
- Create provenance record (source URL, commit hash, vetting date)

**3b: Capability Definition**
- Define named capabilities (e.g., `execute_queue_task(queue, payload)`)
- Input/output specs (types, ranges)
- Cost estimate (latency, memory, CPU)
- Confidence range (0.0–1.0; when should this capability be used?)

**3c: Metadata Assignment**
- Skill header YAML (name, version, author, license, capabilities)
- Integration notes (how to call it, prerequisites, error scenarios)
- Maintenance contact (who to reach out to if issues?)
- Sunset date (when should we revisit? Annual? Quarterly?)

**3d: Knowledge Base Indexing** (Add to BERT)
- Index skill in knowledge base by capability
- Tag by category (auth, data processing, network, etc.)
- Add embeddings (semantic search)
- Link to vetting decision record (transparency)

**3e: Test Harness Creation**
- Integration tests (can orchestrator call this skill?)
- Basic smoke tests (does it work?)
- Error scenarios (what happens when it breaks?)
- Performance baseline (latency curve, resource usage)

**Input**: 5–10 approved skills  
**Output**: 
- Production-ready skills in `src/skills/`
- Updated `config/skills-registry.yaml`
- BERT indexed
- Integration tests passing

**Quality Gate**: All tests pass + header reviewed + integration verified

**Example Header** (for celery skill):
```yaml
---
name: async-task-queue
version: 0.1.0
author: celery-project (packaged by: RoadTrip)
license: BSD-3-Clause
fingerprint: "sha256:abc123def456"
provenance:
  source: "https://github.com/celery/celery"
  commit: "abc123def456..."
  vetting_date: "2026-03-15"
  vetting_decision: "APPROVED with Redis requirement"

capabilities:
  - name: execute_task
    inputs:
      - queue: str
      - payload: dict
    outputs: 
      - task_id: str
      - status: "queued" | "failed"
    latency_ms: [50, 500]  # P50, P99
    confidence: 0.92
    ideal_for: "background tasks, async work"

maintenance:
  contact: "roadtrip-team@example.com"
  review_date: "2026-09-15"  # Quarterly review
```

**Success Metric**: Onboarding cycle time (< 1 week)

---

### Phase 4: PRODUCTION & FEEDBACK LOOP

**Goal**: Monitor performance. Learn from real-world usage. Continuously improve.

**Activities**:

**4a: Production Monitoring**
- Is the skill being used? (invocation count)
- Success rate? (% of invocations succeed)
- Error patterns? (what goes wrong?)
- Performance vs. baseline (latency, resource usage)
- User satisfaction (feedback from operators)

**4b: Feedback & Learnings**
- What's working well? (keep, maybe expand)
- What's not working? (debug, or plan deprecation)
- Operator feedback: "This skill is too slow" or "This saved us hours!"
- Feed insights back to discovery (what to look for next)

**4c: Skill Improvement Requests**
- Can we optimize this skill? (faster, cheaper)
- Can we extend capabilities? (do more with it)
- Should we fork & maintain our own version?
- Is it time to deprecate?

**4d: Quality Score Updates**
- Adjust confidence score based on production metrics
- If skill fails consistently → confidence drops → orchestrator uses it less
- If skill excels → confidence rises → orchestrator uses it more
- Decision record updated (why confidence changed)

**4e: Continuous Loop**
- Every quarter: Review which skills are "stars" (high value, high reliability)
- Every quarter: Review which skills are "low performers" (deprecate?)
- Every quarter: Update discovery priorities based on production learnings
- Every quarter: Cycle back to Phase 1 (discovery) with new knowledge

**Input**: Skills in production for 4+ weeks  
**Output**: 
- Production metrics dashboard
- Feedback-informed discovery priorities
- Updated fingerprint confidence scores
- Deprecation notices (if needed)

**Quality Gate**: Monthly review; quarterly decision on each skill

**Example Feedback Loop**:
```
Mar 31: Async-task-queue integrated (Phase 3 complete)

Apr 15: Initial production review
  - 150 tasks executed
  - 94% success rate ✅
  - Avg latency: 120ms (below 500ms baseline) ✅
  - Operator feedback: "Works great! Using for cleanup tasks"
  → Confidence: 0.92 → 0.95 ✅

May 15: Mid-production review
  - 500 tasks executed
  - 98% success rate ✅✅
  - Avg latency: 110ms ✅
  - New feedback: "Can we use it for pushes too?"
  → Add new capability? Yes, plan for Phase 3 extension

Jun 15: Quarterly review
  - 2000 tasks executed
  - 97% success rate (one bad incident, root-caused to misconfiguration)
  - Latency: stable at 110ms
  - Operator feedback: "Production-ready. Invisible to us (runs well)."
  → Confidence: 0.95 → 0.97 (near-production-grade)
  
Next Discovery Question (Phase 1):
  - "Are there other async frameworks we should evaluate?"
  - "What other background-task patterns do we need?"
```

**Success Metric**: Skills reaching "production-grade" (0.95+ confidence) within 2 months

---

## The Continuous Loop (Emphasizing Process)

```
Month 1: Discovery (find 50 candidates) + Initial Vetting (20 approved to Phase 2)
         ↓
Month 2: Deep Vetting (20 → 5 approved) + First Onboarding (3 skills ready)
         ↓
Month 3: Integration (3 skills live) + Second Onboarding (2 more skills)
         ↓
Month 4: Production Evaluation (first feedback loop) + Discovery (find more)
         ↓
Month 5: Second batch integration + Third batch vetted
         ↓
Month 6+: Continuous pipeline; learning loop improves discovery
          (Discovery gets faster; Vetting gets smarter; Integration streamlined)
```

**Key Insight**: This is NOT "finish Phase 1, then Phase 2, then Phase 3."  
**It IS**: "Phases run in parallel; one skill in Phase 1 while another is in Phase 4."

---

## Integration with Phase 2

**Phase 2** (Skill Trust & Orchestration) builds infrastructure to **VERIFY** skills:
- IBAC: Does intent match action?
- Constitutional AI: Does this fit our principles?
- Fingerprints: Can we trace this skill?

**Workflow 006** builds infrastructure to **FIND & VET** skills:
- Discovery: Where do good skills live?
- Vetting: Is this skill worth our time?
- Onboarding: How do we formalize it?

**Together**: Complete skill lifecycle
```
Workflow 006 (Find & Vet)  →  Phase 2 (Trust & Execute)  →  Workflow 006 Feedback (Learn & Improve)
```

---

## Success Metrics

### By End of March 2026 (Month 1)
- [ ] Discovery sources operational (5 prioritized sources)
- [ ] 50+ skill candidates identified
- [ ] Vetting framework operational (checklist; committee formed)
- [ ] First 10 skills evaluated (3 approved, 7 learnings captured)
- [ ] Approval rate: 30% (3 of 10) ✅

### By End of April 2026 (Month 2)
- [ ] 25+ skills evaluated (8–10 approved)
- [ ] First 3 skills onboarded (fingerprints, capabilities, metadata)
- [ ] BERT schema designed & initial skills indexed
- [ ] Integration with Phase 2 infrastructure verified
- [ ] Approval rate: 40% (up from 30%; vetting improves)

### By End of May 2026 (Month 3)
- [ ] 40+ skills evaluated (15–20 approved)
- [ ] 10 skills in production pipeline
- [ ] First production feedback loop complete
- [ ] Discovery velocity: 5+ new candidates/week (stable)
- [ ] Approval rate: 45% (vetting framework proven)

### By End of Q2 2026 (June)
- [ ] 50+ skills acquired
- [ ] 20 skills in production
- [ ] Vetting cycle time: < 2 weeks
- [ ] Continuous loop: discovery → vetting → integration → feedback
- [ ] Team runs async (minimal meetings; max async collaboration)

### Long-Term Success (By EOY 2026)
- [ ] 100+ skills cataloged
- [ ] 40–50 skills in regular production use
- [ ] Acquisition velocity steady (5 new/month)
- [ ] Community contributions (people contribute skills to RoadTrip)
- [ ] Published skill catalog (external visibility)

---

## Learning > Outcomes

**Philosophy**: Every skill—even rejected ones—teaches us something.

**Rejected Skill Learning Examples**:
- "Code quality was bad, but the idea is solid" → Learn what "solid idea" means
- "This required too much integration" → Know integration complexity limits
- "This had GPL license conflict" → Know licensing constraints
- "This was actually malicious" → Know adversarial patterns

**Captured in Decision Records**:
Every skill gets a decision record explaining:
- What we learned
- Why we approved/rejected/deferred
- What to look for next time
- How this informs discovery

**Feedback Loop Closure**:
Discovery team reads quarterly summaries:
- "Here are the patterns in rejected skills"
- "Here are skills we regretted approving"
- "Here are gaps in our evaluation"
- "Here's what production taught us"

---

## Organizational Aspects

### Skills Acquisition Committee (Proposed)

**Composition**:
- **Security Expert** (risk assessment, malicious pattern detection)
- **Infrastructure Engineer** (integration feasibility, system design)
- **Domain Expert** (capability analysis, RoadTrip fit)
- **Product Lead** (strategic alignment, urgency ranking)

**Authority**:
- Approve skills for onboarding (unanimous requirement?)
- Reject skills with documented reasoning
- Defer skills for later re-evaluation
- Request modifications before approval

**Cadence**:
- Weekly 1-hour review meeting (Thursday 3pm)
- Friday decision records published
- Skills approved by end of week integrated next week

### Discovery Team
- 1–2 people dedicated to scanning sources
- Weekly: Find new candidates, filter, rank
- Monthly: Update discovery criteria based on committee feedback

### Onboarding Team
- 1 person dedicated to fingerprinting & metadata
- Works on-demand as skills are approved
- End goal: Skill ready for Phase 2 orchestrator integration

---

## Timeline: When Workflow 006 Starts

**Target Start**: Mar 1, 2026 (2 weeks before Phase 2 kick-off)

**Why Earlier Than Phase 2?**
- Discovery can start immediately (no dependencies)
- Vetting can proceed in parallel
- By time Phase 2 completes (May 3), we have skills ready to integrate
- No waiting: Skills flow into production as soon as Phase 2 is ready

**Overlap**:
```
Mar 1  ----------- Workflow 006 starts (discovery)
       Mar 11 ---- Phase 2 starts (building trust infrastructure)
       
May 1  ----------- Workflow 006: First batch in production
May 3  ----------- Phase 2: Complete
       
May 3+ ----------- Full velocity: Workflow 006 feeding skills into Phase 2 orchestrator
```

---

## Decision Records (To Be Created)

This document establishes the vision. Separate decision records will cover:
1. **Discovery Sources**: Which 5 sources to prioritize?
2. **Vetting Criteria**: Deep dive on evaluation checklist
3. **Committee Composition**: Who's on the committee?
4. **Approval Thresholds**: Unanimous or 2/3?
5. **Skill Rejection Protocol**: What happens to rejected skills?

Each decided in collaboration with stakeholders.

---

## Appendix: Skill Lifecycle States

```
DISCOVERY (Phase 1)
  └─→ CANDIDATE (found on GitHub, etc.)
       ├─→ FILTERED_OUT (not relevant)
       └─→ IN_VETTING (passed initial filter)
  
VETTING (Phase 2)
  ├─→ APPROVED (passes all vetting)
  ├─→ CONDITIONAL_APPROVED (approved if we fix X)
  ├─→ DEFERRED (good, but not now)
  └─→ REJECTED (rejected with documented reasons)

ONBOARDING (Phase 3)
  └─→ METADATA_ASSIGNED (fingerprint, capabilities, headers ready)
       └─→ READY_FOR_INTEGRATION (passed integration tests)

PRODUCTION (Phase 4)
  ├─→ INTEGRATED (orchestrator knows about it)
  ├─→ IN_USE (actively used by systems)
  ├─→ PRODUCTION_GRADE (0.95+ confidence; stable)
  ├─→ MAINTENANCE_MODE (still works, not extended)
  └─→ DEPRECATED (scheduled for removal)

RETIRED
  └─→ ARCHIVED (full history preserved; available if needed)
```

---

*Skill Acquisition Strategy v1.0 | Feb 10, 2026*
