# Master Research Questions List
**Date:** 2026-02-16  
**Purpose:** Comprehensive extraction of all research questions from three adversarial research plans  
**Sources:** 
- adversarial-research-plan-codex_5_2.md
- adversarial-research-plan-gemini-3.md  
- research-plan-claude-sonnet.md

---

## CODEX 5.2 QUESTIONS

### Section 2: Problem Statement
**Q-C1:** How do we store and retrieve just enough, safely, to measurably improve outcomes over time while keeping costs bounded?

### Section 3: Memory Definitions & Mapping
**Q-C2:** Which memory types (working, episodic, semantic, prospective, procedural) require separate storage systems vs. retrieval policies?

**Q-C3:** What retrieval + consolidation policy transforms raw telemetry into learned experience?

### Section 5: Investigation Targets
**Q-C4:** What is our "sleep" process that safely promotes episodes into durable semantic memory? (CLS consolidation)

**Q-C5:** What triggers slow-path retrieval (uncertainty, failure, novelty, or explicit operator request)? (Cognitive load gating)

**Q-C6:** Which LLM-agent memory patterns remain robust under strict safety/audit constraints?

**Q-C7:** What's the policy for retention vs forgetting of episodic records, and what gets promoted? (Cost-reduction via consolidation)

**Q-C8:** Do we need a real graph, or is "structured semantic memory + good indexing" enough? (Knowledge graphs vs documents)

**Q-C9:** How do we make memory updates lineage-aware and reversible, not "magical edits"? (Self-improvement safety)

### Section 6: Research Questions + Adversarial Angles
**Q-C10:** What is the smallest subset of memory capabilities that yields measurable self-improvement? (Minimum viable memory)

**Q-C11:** What retrieval steps *must* be deterministic? What steps can be probabilistic? (Deterministic vs probabilistic boundary)

**Q-C12:** What rules decide whether an episode becomes semantic memory? (Promotion policy)

**Q-C13:** What do we delete or demote, and why? (Forgetting policy)

**Q-C14:** How do we keep "slow-path memory" from becoming the new cost center? (Cost policy)

**Q-C15:** How do we prevent secrets and instructions from entering memory? (Security policy)

**Q-C16:** How does memory integrate with the DAG skill framework? (Interaction with orchestration)

**Q-C17:** What does the operator approve vs the system doing automatically? (Operator control)

---

## GEMINI 3 QUESTIONS

### Section 1: Core Tension
**Q-G1:** Can we build a memory system that makes RoadTrip smarter *without* making it unpredictable or unsafe?

### Section 2: Theoretical Frameworks
**Q-G2:** How do we recognize *when* to switch from System 1 (fast) to System 2 (slow)? (Cognitive dissonance as trigger?)

**Q-G3:** Can we use "execution surprise" (deviation from expected latency/output) as the write-signal for episodic memory? (Predictive Processing)

**Q-G4:** Can we build a deterministic "Sleep Script" that extracts heuristic rules from today's JSONL logs? (CLS consolidation)

**Q-G5:** When `rules_engine` (Deterministic) says "Block" but LLM says "Safe", how do we resolve system dissonance? (Conflict Monitoring)

### Section 3: 7 Levels Critique
**Q-G6:** Which of the 7 Cortex layers are justified for RoadTrip vs. overkill?

**Q-G7:** Is Hybrid Search (Layer 5) overkill? Can we just use `grep` + simple embeddings?

**Q-G8:** Is Knowledge Graph (Layer 6) too high maintenance? What query patterns justify building it?

**Q-G9:** Should we kill RLM-Graph (Layer 7) as too complex for single-user assistant?

### Section 4: Adversarial Attack Vectors
**Q-G10:** Can we inject a poison memory and have the system reject it during consolidation? (Game of Life trap defense)

**Q-G11:** Compare token cost of "Always Search" vs. "Search on Error" retrieval strategies (Cost explosion defense)

**Q-G12:** Should memory store text (RAG) or executable skills (Procedural)? (Medieval data trap defense)

---

## CLAUDE SONNET QUESTIONS

### Section 3: Current State Gap Analysis
**Q-CS1:** We have hippocampal inputs (telemetry logs) with no hippocampus. How do we bridge the gap?

### Section 4: Framework-Specific Questions
**Q-CS2:** How do we route memory retrieval to the right system (S1 vs S2) without always paying System 2 costs? (Kahneman)

**Q-CS3:** Should session bootstrap be *reactive* (load yesterday's context) or *predictive* (load what's likely needed today)? (Friston Active Inference)

**Q-CS4:** What is the selection mechanism that decides what gets broadcast into active context? (Global Workspace Theory)

**Q-CS5:** What is the right "chunk size" for MEMORY.md entries? Bullet points or structured YAML? (Cognitive Load Theory)

**Q-CS6:** Can a nightly Python script read telemetry, extract patterns deterministically, and update MEMORY.md at $0 cost? (Sleep consolidation)

### Section 6: Thirteen Architecture Questions

**Q-CS7:** Should RoadTrip adopt all 7 Cortex layers, a subset, or different topology? What's the minimum viable subset (80/20 value)?

**Q-CS8:** Where is the right split between deterministic and probabilistic retrieval? At what scale does deterministic break down?

**Q-CS9:** What is the token cost of each Cortex layer per session? What's RoadTrip's consolidation ROI baseline?

**Q-CS10:** Should Knowledge Graph be formal (NetworkX, SQLite) or structured YAML/JSON? What are failure modes?

**Q-CS11:** What triggers consolidation? Time (nightly), event (session end), threshold (N entries), or combination?

**Q-CS12:** What should be promoted from episodic to semantic? (Skill patterns, user behavior, error patterns, trip context, tool fitness)

**Q-CS13:** What should be *forgotten*? How do we implement Ebbinghaus forgetting curves?

**Q-CS14:** How does consolidation interact with `safety-rules.yaml`? Can memory updates be validated before commit?

**Q-CS15:** How does memory feed into the self-improvement reward function (α₁-α₄)?

**Q-CS16:** What's the interface between memory and DAG executor? (Skill, service, or context injection?)

**Q-CS17:** Should each skill have memory footprint in its `SKILL.md`? (Distributed vs central memory)

**Q-CS18:** Can episodic memory help evaluate new skill candidates? (Skill Acquisition funnel integration)

**Q-CS19:** What's the storage budget and pruning policy for episodic index? When do vector embeddings need pruning?

### Section 7: Five Design Hypotheses (Kill Criteria)

**Q-CS20 (H1):** Is layered architecture correct? Can layers be implemented incrementally without dependencies?

**Q-CS21 (H2):** Is consolidation (sleep script) the highest-leverage addition? Does telemetry have sufficient signal?

**Q-CS22 (H3):** Can deterministic memory be implemented before probabilistic? What use cases require semantic similarity?

**Q-CS23 (H4):** Should skills have distributed memory footprints? What's the overlap/duplication level?

**Q-CS24 (H5):** Is sleep the right metaphor? Can consolidation output be readable without LLM synthesis?

### Section 8: Attack Vectors
**Q-CS25:** How does consolidation degrade/improve at scale (1K/5K/10K/50K entries)?

**Q-CS26:** What happens when MEMORY.md reaches 500/1000 lines? Who prunes it?

**Q-CS27:** What guardrails prevent cost spikes from aggressive consolidation runs?

**Q-CS28:** How do we detect and reverse wrong consolidation output?

**Q-CS29:** What's the blast radius of bad memory promotion?

**Q-CS30:** Is Cortex 7-layer overkill? What's simplest memory for 6-month trip timeline?

**Q-CS31:** Why build custom vs. use existing frameworks (MemGPT, Zep, Letta, OpenMem)?

---

## CROSS-CUTTING THEMES (Synthesis)

### Architecture & Topology
- Minimum viable memory subset
- Layer dependencies vs independence  
- 7 layers vs 3 systems vs other topology
- Distributed (per-skill) vs centralized memory

### Deterministic vs Probabilistic
- Boundary definition and split criteria
- Cost comparison (token usage)
- Scale threshold where deterministic breaks down
- Safety implications

### Consolidation & Sleep
- Trigger mechanisms (time/event/threshold)
- Promotion criteria (episode → semantic)  
- Forgetting policy and retention scheduling
- LLM involvement (when is it required vs optional?)
- Validation gates (safety-rules.yaml integration)

### Retrieval & Gating
- S1 (fast) vs S2 (slow) routing logic
- Dissonance/uncertainty/novelty as triggers
- Context window management (cognitive load)
- Cost control (prevent "always search")

### Safety & Security
- Prompt injection via memory
- Memory poisoning attacks
- Secret leakage prevention
- Instruction vs data firewall
- Provenance and lineage tracking
- Rollback mechanisms

### Integration Points
- DAG orchestrator integration
- Skill registry coordination
- Self-improvement reward function
- Skill acquisition funnel
- Rules engine validation

### Cost & ROI
- Token cost per layer/operation
- Storage budget and growth rate
- Consolidation ROI quantification
- Build vs buy economics

---

## QUESTION COUNT SUMMARY
- Codex 5.2: 17 questions
- Gemini 3: 12 questions  
- Claude Sonnet: 31 questions
- **Total Unique Questions: 60**

---

## NEXT STEPS
For each question:
1. Research actual answers (papers, implementations, measurements)
2. Document findings with confidence levels
3. Identify pro/con tradeoffs
4. Recommend solution with scoring
5. Synthesize into coherent PRD
