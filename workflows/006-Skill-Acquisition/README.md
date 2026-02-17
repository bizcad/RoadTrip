# Workflow 006: Skill & MCP Acquisition ("HR for Machine Resources")

**Status**: Planning & Framework Definition  
**Created**: Feb 10, 2026  
**Purpose**: Systematic discovery, vetting, onboarding, and integration of skills and MCPs  
**Metaphor**: Human Resources, but for machine capabilities  

---

## What Is This Workflow?

**Traditional HR Loop** (Human Resources):
```
Job Market → Candidate Search → Application/Resume → Phone Screen → 
Interview → Background Check → Offer → Onboarding → Productivity → 
Employee Performance Feedback → ... (improvement loop)
```

**Machine Resource Loop** (This Workflow):
```
Skill Market → Discovery → Definition/Indexing → Risk Assessment → 
Technical Vetting → Onboarding (Fingerprint/Metadata) → Integration → 
Production Evaluation → Feedback → ... (improvement loop)
```

**Goal**: Systematically expand the RoadTrip skill library by finding high-quality skills, thoroughly vetting them, and safely integrating them into production.

---

## The Skill Acquisition Funnel

```
┌────────────────────────────────────────────────────────────────┐
│ PHASE 1: RESEARCH & DISCOVERY                                   │
│ Cast a wide net. Find skills everywhere. Index what we find.   │
│ Input: Market scan (GitHub, HuggingFace, PyPI, ArXiv, etc.)   │
│ Output: Candidate skill list (100s of possibilities)           │
└────────────────────────────────────────────────────────────────┘
                           ↓
        ┌─────────────────────────────────────────┐
        │ Filtering: Relevance to RoadTrip mission │
        │ Input: 100s candidates                   │
        │ Output: 20–30 promising candidates       │
        └─────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 2: VETTING & EVALUATION                                   │
│ Deep analysis. What does it really do? What's the risk?        │
│ Input: 20–30 candidates                                        │
│ Output: 5–10 "Ready for Onboarding" + learnings for others     │
│                                                                │
│ Sub-phases:                                                   │
│  2a: Capability Analysis (does it do what it claims?)          │
│  2b: Code Quality Review (is it well-written?)                │
│  2c: Security & Risk Assessment (is it safe? Malicious?)       │
│  2d: Integration Feasibility (can we integrate it?)            │
│  2e: Learning & Dismissal (keep learnings even if we reject)   │
└────────────────────────────────────────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────┐
        │ Vetting Committee Review              │
        │ Input: Vetting reports                 │
        │ Output: "Approved for Onboarding" OK  │
        └────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 3: ONBOARDING & CODIFICATION                              │
│ Formalize metadata. Create fingerprints. Build capability spec. │
│ Input: 5–10 approved skills                                    │
│ Output: Skill headers, capabilities, confidence levels         │
│          Provenance records. Ready for integration.             │
└────────────────────────────────────────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────┐
        │ Integration into Orchestrator          │
        │ Input: Onboarded skill                 │
        │ Output: Skill available in production  │
        └────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 4: PRODUCTION & FEEDBACK LOOP                             │
│ Monitor skill performance. Learn from real-world usage.        │
│ Input: Production metrics, operator feedback                   │
│ Output: Skill quality scores, improvement suggestions          │
│         → Update fingerprint confidence? Remove skill?         │
│         → Feed insights back to discovery (Phase 1)            │
└────────────────────────────────────────────────────────────────┘
                           ↓
                    (Continuous Loop)
```

---

## Documents in This Workflow

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| **README.md** (this file) | Overview + navigation | 10 min | Everyone |
| **SKILL_ACQUISITION_STRATEGY.md** | Vision, methodology, phases | 25 min | Leaders, architects |
| **SKILL_FUNNEL_MATURITY_MODEL.md** | Detailed stages + criteria | 20 min | Vetting committee |
| **VETTING_FRAMEWORK.md** | How to evaluate skills (checklist) | 20 min | Vetting team |
| **PROCESS_GOVERNANCE.md** | Weekly loop, cadence, roles | 20 min | Entire team |
| **DECISION_RECORD_Acquisition_Architecture.md** | Why this approach | 15 min | Architects |
| **TRUST_BUNDLE_TEMPLATE.json** | Standard per-skill trust decision artifact schema | 5 min | Vetting + onboarding |
| **TRUST_BUNDLE_EVIDENCE_MAP_TEMPLATE.json** | Default + per-skill evidence link mapping for bundle generation | 5 min | Vetting + onboarding |

---

## Quick Links by Role

### For Skill Acquisition Lead
1. Read **SKILL_ACQUISITION_STRATEGY.md** (entire)
2. Review **SKILL_FUNNEL_MATURITY_MODEL.md** (entire)
3. Study **VETTING_FRAMEWORK.md** (evaluation criteria)
4. Skim **PROCESS_GOVERNANCE.md** (responsibilities section)

### For Vetting Committee Members
1. Read **VETTING_FRAMEWORK.md** (your checklist)
2. Review **SKILL_FUNNEL_MATURITY_MODEL.md** (Phase 2: Vetting details)
3. Familiarize with decision records process

### For Orchestrator/Integration Team
1. Read **SKILL_ACQUISITION_STRATEGY.md** (Phase 3: Onboarding)
2. Review **SKILL_FUNNEL_MATURITY_MODEL.md** (Phase 3 & 4)
3. Check **PROCESS_GOVERNANCE.md** (your timeline)

### For Research & Discovery Team
1. Study **SKILL_ACQUISITION_STRATEGY.md** (Phase 1: Research)
2. Review **SKILL_FUNNEL_MATURITY_MODEL.md** (Phase 1 details)
3. Understand filtering criteria (relevance, urgency)

### For Executives/Sponsors
1. Skim **SKILL_ACQUISITION_STRATEGY.md** (Vision section)
2. Read **DECISION_RECORD_Acquisition_Architecture.md** (rationale)
3. Review success metrics in STRATEGY doc

---

## Key Concepts

## Trust Bundle Artifact (New)

For each skill that reaches vetting decision, produce a per-skill trust bundle JSON using:

`py scripts/generate_trust_scorecard.py --bundle-dir workflows/006-Skill-Acquisition/trust-bundles --release-id <release-id>`

Optional evidence mapping (global defaults + per-skill overrides):

`py scripts/generate_trust_scorecard.py --bundle-dir workflows/006-Skill-Acquisition/trust-bundles --release-id <release-id> --bundle-evidence-map workflows/006-Skill-Acquisition/TRUST_BUNDLE_EVIDENCE_MAP_TEMPLATE.json`

This emits one `*.trust-bundle.json` file per skill in a format aligned with `TRUST_BUNDLE_TEMPLATE.json`.

Use this bundle as the portable handoff record between vetting, onboarding, and release review.

### Skill vs. MCP vs. Capability

**Skill**: A Python module in `src/skills/` that does one thing well
- Example: `commit-message.py` (generates commit messages)
- Owns: Interface, tests, documentation

**MCP** (Model Context Protocol): A standardized interface for AI tools
- Example: OpenAI's function calling, Claude's tools
- Can wrap multiple skills

**Capability**: Named action a skill can perform
- Example: `generate_commit_message(files, diff, threshold)` is a capability
- One skill can have multiple capabilities

### The "HR for Machines" Metaphor

| HR Concept | Machine Equivalent |
|---|---|
| Job posting | Skill gap analysis (what do we need?) |
| Candidate search | GitHub/HuggingFace/PyPI search |
| Resume screening | README + documentation review |
| Technical interview | Capability analysis + code review |
| Background check | Security & license audit |
| Reference check | Community reputation + usage metrics |
| Offer negotiation | Integration complexity assessment |
| Onboarding | Fingerprint + metadata assignment |
| Performance review | Production metrics + feedback loop |
| Severance | Skill deprecation (with notice) |

---

## The Continuous Loop (Emphasizing Process)

**Key Insight**: This is NOT a one-time project. It's a continuous loop.

```
Discover (Month 1)
  → Evaluate (Month 1-2)
  → Integrate (Month 2)
  → Use in Production (Month 2+)
  → Improve (Month 3+)
  → Discover more (Month 4+)
  → ... (cycle repeats)
```

**Why Process > Outcome**:
- We learn from every skill (even rejected ones)
- Vetting improves as we experience real skills
- Production feedback refines discovery priorities
- Loop tightens over time (faster discovery, faster vetting)

**Learning Points Even from Rejected Skills**:
- "This implementation is bad, but the idea is good" → Know what to look for
- "This requires too much integration" → Know integration boundaries
- "This has licensing issues" → Know legal constraints
- "This is malicious" → Know security patterns to watch for

---

## Parallel Timeline (vs. Phase 2)

```
Phase 2 (Skill Trust & Orchestration):   Mar 11 – May 3
├─ Building infrastructure to TRUST skills
├─ IBAC, Constitutional AI, fingerprinting
└─ Enables Phase 2b/3 scaling

Workflow 006 (Skill Acquisition):         Starts Mar 1 (parallel to Phase 2)
├─ Finding GOOD skills to trust
├─ Discovery, vetting, onboarding
└─ Continuously fills skill library
```

**Why Run in Parallel?**
- Phase 2 builds infrastructure; Workflow 006 feeds content into it
- Discovery can start before Phase 2 completes
- By May 3, we'll have both trust framework AND acquisition process
- Together → complete skill lifecycle management

---

## Success Criteria for Workflow 006

### By End of Month 1 (Mar 31, 2026)
- [ ] Discovery process defined & running (scanning 5+ sources)
- [ ] Candidate list generated (50+ skills identified)
- [ ] Vetting framework complete & tested
- [ ] First 5 skills evaluated (3 approved, 2 rejected + learnings)

### By End of Month 2 (Apr 30, 2026)
- [ ] 10–15 skills in production pipeline
- [ ] Onboarding process validated (fingerprints, capabilities, metadata)
- [ ] First batch integrated into orchestrator (5 skills added)
- [ ] Production evaluation metrics established

### By End of Month 3 (May 31, 2026)
- [ ] 20–30 skills acquired
- [ ] Continuous learning loop established (feedback → discovery)
- [ ] Team runs completely async (minimal meetings)
- [ ] Vetting process has tightened (cycle time < 2 weeks per skill)

### Long-Term (Month 6+)
- [ ] Skill library reaches 50+ curated skills
- [ ] Acquisition velocity steady (5 new skills/month)
- [ ] BERT (or equivalent) fully populated
- [ ] Strategy adjusts based on production learnings

---

## Key Decisions to Make (Before Workflow Starts)

1. **Discovery Sources**: Where do we search for skills?
   - GitHub (trending repos in certain categories)?
   - HuggingFace Hub (ML-specific skills)?
   - PyPI (Python packages)?
   - ArXiv (research papers with code)?
   - Internal team ideas?
   - **Decision needed**: Prioritize and schedule sweeps

2. **Vetting Team**: Who evaluates skills?
   - Security expert (risk assessment)?
   - Integration engineer (feasibility)?
   - Domain expert (capability analysis)?
   - **Decision needed**: Roster; decision-making rules

3. **Urgency Ranking**: How do we prioritize?
   - Gap analysis (what does RoadTrip need most)?
   - Community signal (trending on GitHub)?
   - Strategic alignment (Phase 2 roadmap)?
   - **Decision needed**: Ranking algorithm

4. **Rejection Handling**: What happens to rejected skills?
   - Document learnings in decision records?
   - Create "anti-pattern" library?
   - Revisit later if updated?
   - **Decision needed**: Rejection protocol

5. **Integration Friction**: How much friction is acceptable?
   - "Must integrate perfectly" (high bar, slow pipeline)?
   - "Can adapt it if needed" (lower bar, faster pipeline)?
   - "Can make it from scratch if inspired by idea" (very low bar)?
   - **Decision needed**: Integration flexibility

---

## How This Workflow Complements Phase 2

| Aspect | Phase 2 Builds | Workflow 006 Builds |
|---|---|---|
| **Trust Layer** | IBAC, Constitutional AI, fingerprints | Vetting framework to initially assess trustworthiness |
| **Discovery** | Orchestrator queries capabilities | Skill acquisition finds new capabilities to query |
| **Metadata** | Phase 2 standardizes headers | Workflow 006 populates headers during onboarding |
| **Risk Mgmt** | Phase 2: runtime risk (what if skill misbehaves?) | Workflow 006: selection risk (did we pick good skills?) |
| **Feedback Loop** | Phase 2: production metrics | Workflow 006: production insights inform discovery |

**Together**: Complete skill lifecycle (find → trust → use → improve → find more)

---

## Next Steps

### This Week (Feb 10–14)
- [ ] Review Workflow 006 documents (start with **SKILL_ACQUISITION_STRATEGY.md**)
- [ ] Identify skill acquisition lead
- [ ] Form vetting committee (suggest 3–4 people; diverse backgrounds)
- [ ] Add questions/feedback to decision records

### Next Week (Feb 17–21)
- [ ] Finalize discovery sources (5 prioritized)
- [ ] Define vetting criteria (customize VETTING_FRAMEWORK.md)
- [ ] Assign roles & responsibilities
- [ ] Create BERT/knowledge base schema (how will skills be indexed?)

### Week of Mar 1 (Start of Workflow 006)
- [ ] Kick-off: Explain metaphor & loop
- [ ] Discovery team: Begin scanning sources
- [ ] Vetting team: Review framework & prepare templates
- [ ] First candidate batch by Mar 10

### Mar 11+ (Parallel with Phase 2)
- [ ] Continuous discovery pipeline
- [ ] Weekly evaluation meetings (Thursday afternoon, 1 hour)
- [ ] Onboarding skills as Phase 2 infrastructure completes
- [ ] Feedback loop from Phase 2 production

---

## Documents Overview

### 1. SKILL_ACQUISITION_STRATEGY.md
**What**: Full vision for skill acquisition  
**Covers**:
- Metaphor & mental model
- Four phases (Research → Vetting → Onboarding → Production)
- Success metrics
- Continuous improvement loop

### 2. SKILL_FUNNEL_MATURITY_MODEL.md
**What**: Detailed breakdown of each funnel stage  
**Covers**:
- Phase 1: Research (where to find skills, filtering, ranking)
- Phase 2: Vetting (capability analysis, quality review, risk assessment, integration feasibility)
- Phase 3: Onboarding (fingerprinting, metadata, provenance)
- Phase 4: Production (monitoring, feedback, deprecation)

### 3. VETTING_FRAMEWORK.md
**What**: Practical checklist for evaluating skills  
**Covers**:
- Capability analysis (does it do what it claims?)
- Code quality (typing, docs, tests, maintainability)
- Security & risk (malicious? vulnerable? dependencies risky?)
- Integration complexity (how hard to integrate?)
- Licensing (any restrictions?)
- Decision tree (approve, reject, conditional approval)

### 4. PROCESS_GOVERNANCE.md
**What**: How the team will operate (weekly loops, decisions, escalations)  
**Covers**:
- Weekly cadence (discovery sweeps, vetting meetings, integration updates)
- Decision-making framework
- Roles & responsibilities
- Escalation paths (disagreement on skill quality)
- Async learning (retrospectives, decision records)

### 5. DECISION_RECORD_Acquisition_Architecture.md
**What**: Why this approach (integration with Phase 2, metaphor justification)  
**Covers**:
- HR metaphor rationale
- Funnel design (why 4 phases?)
- Why "learning > outcomes"
- Risks & mitigations
- Alternative approaches considered

---

## Get Started

**Start Here**: Read **SKILL_ACQUISITION_STRATEGY.md** (25 min)  
**Then**: Skim **SKILL_FUNNEL_MATURITY_MODEL.md** (phase overview)  
**Questions**: Post in **DECISION_RECORD_Acquisition_Architecture.md**

---

*Workflow 006: Skill & MCP Acquisition | v1.0 | Feb 10, 2026*
