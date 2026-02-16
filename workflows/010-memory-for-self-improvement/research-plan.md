# Memory for Self-Improvement: Research & Adversarial Debate Plan

**Workflow:** `workflows/010-memory-for-self-improvement/`
**Document type:** Research plan — not an implementation plan
**Purpose:** Structured input for an adversarial planning exercise before any architecture is committed
**Status:** Draft v1.0 — 2026-02-15
**Author:** RoadTrip / bizcad

---

## 1. Why This Document Exists

RoadTrip is building a self-learning skill ecosystem (see `workflows/007-self-improvement/`). The 10,000-foot architecture identifies three layers: Strategic (self-improvement engine), Tactical (skill orchestration), and Operational (skill execution). The Strategic layer requires **memory** — specifically, the ability to observe what happened, remember what worked, and act differently in the future.

Today RoadTrip has exactly one memory artifact: `MEMORY.md`, a ~200-line file injected into every Claude Code session. It's Layer 1 of a much deeper stack we have not yet built.

Before building anything, we want to answer a harder question: **what should we build, and in what order, and why?**

The Claude Cortex 7-layer model (`docs/Self-Improvement/7 levels of memory.md`) gives us a reference implementation. But its theoretical citations feel dated (Atkinson-Shiffrin 1968, Tulving 1972). The neuroscience of memory has moved forward dramatically. So has the AI memory systems literature. This document structures an investigation into whether there are better, more modern foundations to build on.

**The goal is not to produce code. The goal is to produce a defensible architectural thesis that survives an adversarial red-team review.**

---

## 2. Scope Boundaries

**In scope:**
- Runtime memory: what the agent knows *within* a session
- Session memory: what the agent carries *across* sessions without retraining
- Skill-level experience: what each skill "knows" from its invocation history
- Personal assistant memory: user preferences, trip context, recurring decisions

**Out of scope:**
- LLM fine-tuning or weight updates
- Training data management
- Real-time model parameter adjustment
- Anything requiring GPU infrastructure

**The one question that defines scope:** *Can a Python script running on a laptop with access to telemetry logs and a Claude API key make the system measurably smarter over time?* If yes, we are in scope. If it requires more, we defer.

---

## 3. Current State: What We Have Today

| Component | Status | Location |
|---|---|---|
| Auto-injected permanent memory | ✅ Running | `MEMORY.md` (Layer 1 analog) |
| Session logging | ✅ Running | `logs/*.jsonl` via `telemetry_logger.py` |
| Skill invocation metrics | ✅ Running | `ExecutionMetrics` in `models.py` |
| Session bootstrap (auto-load on start) | ❌ Missing | Would require `SessionStart` hook |
| Working memory (mid-session goal tracking) | ❌ Missing | No disk-backed scratchpad |
| Episodic search (query past sessions) | ❌ Missing | Logs exist but aren't indexed |
| Knowledge graph (entity relationships) | ❌ Missing | Nothing |
| Sleep/consolidation (promote episodic → semantic) | ❌ Missing | The most critical gap |

**The key insight from inventory:** We are already collecting the raw material for episodic memory. Every skill invocation writes a structured JSONL entry. Nobody reads those files programmatically. That is the gap. We have hippocampal inputs with no hippocampus.

---

## 4. Theoretical Frameworks Under Investigation

For each framework: what it is, what specific question it answers for RoadTrip, why it matters now (not just historically), and key citations.

---

### Framework A — System 1 / System 2 (Kahneman, 2011)

**What it is:** Dual-process theory of human cognition. System 1 is fast, automatic, pattern-matching, always-on, low cost. System 2 is slow, deliberate, effortful, invoked for novel or complex problems.

**What it answers for RoadTrip:** Memory retrieval has a cost. Not every decision should pay the same retrieval cost. MEMORY.md (always injected, zero additional cost) is a System 1 memory — fast lookup with no search. Episodic search (query the telemetry database, rank results, inject top-N) is a System 2 memory — invoked when needed, costs tokens and latency.

**RoadTrip design question:** *How do we route memory retrieval to the right system without always paying System 2 costs?*

**Why modern:** Standard LLMs are System 1 machines — fast, fluent, pattern-matching. The 2025 research on "test-time compute" (o1, o3, DeepSeek-R1) is the first practical System 2 implementation at scale. The architectural insight is that System 2 should be *optional and triggered by uncertainty*, not always on.

**Key citations:**
- Kahneman (2011) — *Thinking Fast and Slow* (foundational)
- arXiv: "Test-time Computing: from System-1 Thinking to System-2 Thinking" (2025)
- https://github.com/open-thought/system-2-research — curated paper list

---

### Framework B — Complementary Learning Systems (Kumaran, Hassabis, McClelland, 2016)

**What it is:** Two-system biological memory architecture. The *hippocampus* is a fast, high-fidelity, pattern-separated store for specific episodes. The *neocortex* is a slow, generalizing store for statistical regularities. The hippocampus replays memories to the neocortex during sleep, allowing gradual knowledge consolidation without catastrophic interference.

**What it answers for RoadTrip:** Should we have one memory store or two? CLS says two, and they must serve different functions. The fast store captures individual events (this push failed because of a .db file). The slow store captures generalizations (pushing .db files always fails — add this to MEMORY.md). The two must be bridged by a consolidation process.

**The 2016 update matters:** Kumaran and Hassabis (both at DeepMind) extended the theory to include rapid neocortical learning when new information is *schema-consistent* — meaning the slow store can update quickly if the information fits a pattern it already knows. This has direct implications: if our existing rules-engine knowledge is well-structured, new examples should update it cheaply.

**RoadTrip mapping:**
- Hippocampus → `logs/*.jsonl` telemetry files (raw episodic store)
- Neocortex → `MEMORY.md` + skill `SKILL.md` experience sections (generalized knowledge)
- Sleep replay → offline consolidation script that reads recent logs and updates the slow store

**Key citations:**
- Kumaran, Hassabis, McClelland (2016) — *What Learning Systems do Intelligent Agents Need?* Cell/TICS — https://www.cnbc.cmu.edu/~tai/nc19journalclubs/KumaranHassabisMcC16CLSUpdate.pdf
- McClelland, McNaughton, O'Reilly (1995) — original CLS paper — https://stanford.edu/~jlmcc/papers/McCMcNaughtonOReilly95.pdf
- 2024 bioRxiv: "RAG as hippocampal-neocortical interaction" (preprint, search bioRxiv 2024)

---

### Framework C — Active Inference / Predictive Processing (Friston)

**What it is:** The brain is a prediction machine. It continuously generates models of the world, makes predictions, and updates the model based on prediction error (free energy minimization). Memory is not a passive store — it is an active generative model that anticipates what will be needed next. *Active inference* means agents also act to make the world conform to their predictions.

**What it answers for RoadTrip:** Should the session bootstrap be reactive (load what happened yesterday) or *predictive* (load what will likely be needed today based on patterns)? Friston's framework suggests that a session that starts by asking "what am I likely to need?" rather than "what did I do last?" will perform better on familiar tasks and flag uncertainty on novel ones.

**Why important:** Friston's direct critique of LLMs is pointed: passive AI systems predict text but don't have the action-perception loop needed for genuine agency. The session bootstrap is where RoadTrip can introduce a weak form of active inference — a prior over what context will be relevant.

**RoadTrip design question:** *Can the Session Bootstrap become a predictive loader, not just a history loader?*

**Key citations:**
- Friston, Pezzulo, Parr, Cisek, Clark (2024) — *Generating meaning: active inference and passive AI* — https://pubmed.ncbi.nlm.nih.gov/37973519/
- Schema-based Hierarchical Active Inference (S-HAI) — two-level agent architecture paper (search arXiv)
- Friston vs. LeCun at Davos 2024 — https://deniseholt.us/deep-learning-is-rubbish-friston-lecun-face-off-at-davos-2024/

---

### Framework D — Global Workspace Theory (Baars, 1988; Dehaene, 2003)

**What it is:** Consciousness arises when information is selected from among competing parallel specialist processors and broadcast globally — made available to all modules simultaneously via a capacity-limited central workspace. The bottleneck is the selection mechanism, not the store.

**What it answers for RoadTrip:** The context window is the global workspace. The question is not "what memories do we have?" but "what is the selection mechanism that decides what gets broadcast into the active context?" This is a design question about the retrieval gateway, not the storage layer.

**AI implementation:** A multi-agent LLM system maps cleanly: specialized agents (rules-engine, auth-validator, telemetry-logger) are the parallel specialist processors. The orchestrator is the bottleneck gateway that selects which agent output gets promoted into the shared context. Memory retrieval is the process of selecting past experience for broadcast.

**2025 relevance:** A 2025 "Cognitive Workspace" paper (arXiv 2508.13171) directly applies GWT to LLM context management, arguing that passive RAG retrieval is insufficient — active, metacognitive context management (deciding *what* to load, not just *how* to retrieve it) is required.

**Key citations:**
- Baars (1988) — *A Cognitive Theory of Consciousness* (foundational)
- Dehaene, Changeux (2011) — *Experimental and Theoretical Approaches to Conscious Processing* — https://pmc.ncbi.nlm.nih.gov/articles/PMC8770991/
- Frontiers 2024: *Global Workspace Agent in a multimodal environment* — https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1352685/full
- arXiv 2508.13171: *Cognitive Workspace: Active Memory Management for LLMs* — https://arxiv.org/html/2508.13171v1

---

### Framework E — Cognitive Load Theory / Working Memory Limits (Sweller, 1988; Cowan, 2001)

**What it is:** Working memory can actively process only 3–4 chunks of information simultaneously (Cowan's "magical number 4"). Cognitive load has three types: intrinsic (inherent complexity), extraneous (unnecessary presentation overhead), and germane (productive learning effort). Good instructional design minimizes extraneous load and maximizes germane load.

**What it answers for RoadTrip:** How much memory should be injected into context, in what format, and with what structure? The Claude Cortex MEMORY.md ~200-line limit is an engineering response to cognitive load. The RLM-Graph (Layer 7) is a chunking mechanism. But neither is principled — they are ad hoc limits.

**2025 relevance:** A 2025 paper "Cognitive Load Limits in Large Language Models" (arXiv 2509.19517) formally demonstrates that LLM performance degrades under "Context Saturation" (too much irrelevant information) — an exact analog of extraneous cognitive load. The implication: injecting everything into context degrades performance. Precision matters more than recall in memory injection.

**RoadTrip design question:** *What is the right "chunk size" for MEMORY.md entries? Should memory be injected as bullet points (low-overhead) or as structured YAML (higher-overhead but more queryable)?*

**Key citations:**
- Sweller (1988) — original CLT paper
- Cowan (2001) — *The magical number 4 in short-term memory* — Behavioral and Brain Sciences
- arXiv 2509.19517: *Cognitive Load Limits in Large Language Models* — https://arxiv.org/pdf/2509.19517
- arXiv 2508.13171: *Cognitive Workspace* — https://arxiv.org/html/2508.13171v1

---

### Framework F — Sleep / Offline Consolidation (2022–2026)

**What it is:** During biological sleep, the hippocampus replays recently encoded memories, transmitting activation patterns to the neocortex. The neocortex slowly integrates statistical regularities across many replays. New memories are generalized, not copied verbatim. Old memories are protected from interference. Forgetting is adaptive (Ebbinghaus forgetting curve — importance × recency determines what is retained).

**Why this is the most important framework for RoadTrip:** It is the direct answer to the gap identified in Section 3. We have a hippocampal store (telemetry JSONL logs) and a neocortical store (MEMORY.md). We have no consolidation bridge. Sleep consolidation is the bridge.

**What has been built in AI (2022–2026):**

| Paper | Key Result | Relevance |
|---|---|---|
| Nature Comms 2022 — *Sleep-like unsupervised replay reduces catastrophic forgetting* | Offline Hebbian replay prevents interference during continual learning | Validates the biological mechanism applies to ANNs |
| LightMem arXiv 2510.18866 | 10.9% accuracy gain, **117x token reduction**, **159x API call reduction** via sleep-time consolidation | Quantifies the ROI of consolidation for LLM agents |
| Language Models Need Sleep (OpenReview iiZy6xyVVE) | Two-phase sleep: memory consolidation (RL distillation) + dreaming (synthetic data) | Full LLM sleep paradigm |
| FOREVER arXiv 2601.03938 | Ebbinghaus forgetting curve applied to memory replay scheduling | Importance-weighted forgetting: not all memories equal |
| NeuroDream SSRN 5377250 | Dedicated sleep-inspired consolidation framework for ANNs | Architecture patterns for the consolidation step |

**RoadTrip design question:** *Can a nightly Python script read the last N telemetry JSONL entries, extract recurring patterns deterministically, and update MEMORY.md — implementing sleep consolidation at $0 cost with no embeddings required?*

**Key citations:**
- Nature Communications 2022 — https://www.nature.com/articles/s41467-022-34938-7
- LightMem — arXiv 2510.18866 — https://arxiv.org/html/2510.18866v1
- Language Models Need Sleep — https://openreview.net/forum?id=iiZy6xyVVE
- FOREVER — arXiv 2601.03938 — https://arxiv.org/html/2601.03938v1
- ICLR 2026 MemAgents Workshop — https://openreview.net/pdf?id=U51WxL382H (signals active community)

---

## 5. The Full Source Map

### Already Acquired (in `docs/`)
- `docs/Self-Improvement/7 levels of memory.md` — Claude Cortex reference implementation
- `docs/Self-Improvement/Part_3_-_Self-Optimization.md` — reality testing as deterministic validation
- `docs/Self-Improvement/Part_7_-_The_Real_Thing.md` — DSE working Ollama implementation
- `docs/Self-Improvement/Part_8_-_Tools_All_The_Way_Down.md` — tool-level fitness, usage stats, RAG

### Existing RoadTrip Architecture Documents
- `workflows/007-self-improvement/10K_FOOT_ARCHITECTURE.md` — 3-layer system, reward function α
- `workflows/007-self-improvement/PHASED_ROADMAP.md` — Phase 1b→3 with ExecutionMetrics dataclass
- `workflows/007-self-improvement/METRICS_CATALOG.md` — measurable dimensions (reliability, cost, speed, vigilance)
- `src/skills/telemetry_logger.py` — current episodic raw data source
- `src/skills/telemetry_logger_models.py` — telemetry data model
- `config/telemetry-config.yaml` — persistence config
- `src/skills/dag/` — execution engine memory must integrate with

### Survey Papers (read next)
- arXiv 2404.13501 — *A Survey on the Memory Mechanism of LLM-based Agents* (ACM TOIS 2025)
- arXiv 2504.15965 — *From Human Memory to AI Memory: A Survey* (April 2025, eight-quadrant classification)
- TechRxiv 2025 — *Memory in LLM-based Multi-Agent Systems: Mechanisms, Challenges, and Collective*
- GitHub: https://github.com/Shichun-Liu/Agent-Memory-Paper-List (Agent Memory Paper List)
- GitHub: https://github.com/nuster1128/LLM_Agent_Memory_Survey (LLM Agent Memory Survey)

### Architecture Papers (implement later)
- arXiv 2502.12110 — *A-Mem: Agentic Memory for LLM Agents* (dynamic self-evolving memory)
- arXiv 2508.15294 — *Multiple Memory Systems for Long-term Agent Memory* (CLS-grounded)
- arXiv 2508.13171 — *Cognitive Workspace: Active Memory Management for LLMs* (GWT + CLT)

---

## 6. Thirteen Research Questions for Adversarial Review

These questions are the agenda for the red-team / adversarial planning exercise. A good answer to each should either confirm or kill the design hypotheses in Section 7.

### Architecture Questions

**Q1.** Should RoadTrip adopt all 7 Cortex layers, a subset, or a different topology?
What is the minimum viable subset that provides 80% of the value at 20% of the implementation cost?

**Q2.** Where is the right split between deterministic (keyword search, structured YAML) and
probabilistic (vector embeddings, semantic similarity) retrieval?
At what scale or complexity does the deterministic approach break down and require vectors?

**Q3.** What is the token cost of each Cortex layer per session?
LightMem claims 117x token reduction from consolidation. What is RoadTrip's equivalent baseline?

**Q4.** Should the Knowledge Graph be a formal graph database (NetworkX, SQLite-backed)
or a structured YAML/JSON file that Claude can read and write directly without code?
What are the failure modes of each?

### Consolidation Questions

**Q5.** What is the right trigger for consolidation:
time-based (nightly), event-based (session end), threshold-based (every N new telemetry entries),
or a combination? What are the failure modes if the trigger fires during an active session?

**Q6.** What should be promoted from episodic to semantic? Candidates:
- Skill performance patterns (rules-engine blocks X% of pushes containing `*.db` files)
- User behavioral patterns (user always pushes at 9am, rarely uses blog-publisher on weekends)
- Error patterns (auth failures cluster before GitHub token expiry)
- Trip context facts (route decisions, fuel stops, hotel preferences from `data/` CSVs)
- Tool fitness scores (which skill versions have the best success rate)

**Q7.** What should be *forgotten*? The FOREVER paper implements Ebbinghaus forgetting curves
for importance-weighted replay scheduling. Not all telemetry entries are worth keeping forever.
What is the forgetting curve for RoadTrip skill invocation history?

**Q8.** How does the consolidation step interact with the rules-engine's `safety-rules.yaml`?
Can consolidation itself be validated by the rules-engine before writing to MEMORY.md?
(i.e., treat memory updates as files to be validated before commit — consistent with existing architecture)

### Integration Questions

**Q9.** How does memory feed back into the existing self-improvement reward function?
`α₁=0.50 reliability + α₂=0.30 cost + α₃=0.15 speed + α₄=0.05 vigilance`
Can historical memory make this function context-aware (e.g., "good latency" means different things
at 9am vs 11pm, or for a small file vs a large one)?

**Q10.** What is the interface between the memory layer and the existing DAG skill executor
(`src/skills/dag/`)? Does memory become:
- (a) a skill invokable in the DAG (clean interface but adds latency),
- (b) a service called by the orchestrator before DAG construction (smarter routing), or
- (c) a cross-cutting concern injected into every skill's context (simplest but highest overhead)?

**Q11.** Should each skill have a memory footprint — a short "what I know from experience"
section in its `SKILL.md` — updated by the consolidation step?
This would keep memory distributed and co-located with each skill, consistent with the
existing `SKILL.md` / `CLAUDE.md` pattern. Downside: duplication and drift across skills.

**Q12.** How does memory interact with the Skill Acquisition funnel (workflow 006)?
Can episodic memory help evaluate whether a new skill candidate will be useful?
(e.g., "we see 23 telemetry entries where the orchestrator had no skill for image compression —
this is a gap that a new skill would fill")

### Cost & Vigilance Questions

**Q13.** What is the storage budget for the episodic index?
At 180 sessions/year × 30 invocations/session × ~2KB per JSONL entry = ~10.8 MB/year.
SQLite handles this trivially. But embedding vectors add ~1,536 floats × 4 bytes = ~6KB per entry.
At what point does the vector store require pruning, and what is the pruning policy?

---

## 7. Five Design Hypotheses (Write Them to Kill Them)

Each hypothesis is stated in a form that can be falsified by the adversarial review.

---

**H1 — Layered is Right**

*Claim:* The 7-layer Cortex structure (or a direct subset) is the correct architecture for
RoadTrip. Each layer is independent and can be implemented incrementally without requiring the others.

*Kill condition:* If the inter-layer dependencies (e.g., Hybrid Search requires both Episodic Memory
and Knowledge Graph to provide value) make incremental adoption impractical, the layered model
should be abandoned in favor of a single unified memory service.

*Test:* Map each layer's dependencies. If any layer requires two others to be fully implemented
before providing measurable value, flag it as a bundled dependency, not a standalone layer.

---

**H2 — Consolidation is the Missing Piece**

*Claim:* The single highest-leverage addition to current RoadTrip memory is an offline
consolidation step (sleep script) that processes telemetry logs and promotes patterns into
MEMORY.md. This requires no new infrastructure — just Python and a scheduler.

*Kill condition:* If telemetry data is too sparse, too noisy, or too low-signal to yield useful
patterns at current invocation rates, consolidation will produce garbage output and corrupt MEMORY.md.

*Test:* Manually read 30 days of telemetry JSONL files. Can a human identify 3+ recurring patterns
that would be useful in MEMORY.md? If not, H2 fails — the episodic store lacks sufficient signal.

---

**H3 — Deterministic Before Probabilistic**

*Claim:* Implement deterministic memory (structured YAML knowledge, keyword search over JSONL)
before probabilistic memory (vector embeddings, semantic similarity). Cost of deterministic: $0.
Cost of probabilistic: ~$0.001/query + embedding infrastructure.

*Kill condition:* If the first real use case for memory retrieval is inherently semantic
(e.g., "find past sessions similar to this one" where keyword matching is insufficient),
then deterministic memory provides no value and the embedding step cannot be deferred.

*Test:* Define the first three memory retrieval use cases for RoadTrip. Can all three be answered
by keyword search over structured JSONL? If yes, H3 holds. If even one requires semantic similarity,
estimate the minimum embedding infrastructure required and cost.

---

**H4 — Skills as Memory Citizens**

*Claim:* Each skill should have a memory footprint — a structured "experience" section in its
`SKILL.md` updated by the consolidation step. Memory is distributed, co-located with each skill,
consistent with the `SKILL.md` / `CLAUDE.md` pattern.

*Kill condition:* If skills have overlapping memory (e.g., git-push-autonomous and rules-engine
both need to know about `.db` file patterns), distributed memory creates duplication and drift.
A central knowledge store is simpler and more consistent.

*Test:* For each of the 6 active skills, write a 3-bullet "what I know from experience" section.
Do the bullets overlap? If more than 30% of content would appear in two or more skills, H4 fails
and a central knowledge.yaml is the better architecture.

---

**H5 — Sleep is the Right Implementation Metaphor**

*Claim:* The consolidation process should be framed as "sleep" — a deliberate offline process
that (a) extracts patterns from recent episodic telemetry, (b) updates skill experience sections
or MEMORY.md, (c) prunes stale entries, (d) writes a handoff note for the next session bootstrap.
Implementable as a standalone Python script. No LLM calls required for the deterministic phase.

*Kill condition:* If the consolidation process requires LLM summarization to produce readable
output (because raw telemetry patterns are not human/agent readable without natural language
synthesis), then the script has an unavoidable API cost — potentially violating the vigilance
constraint (α₄) at high invocation rates.

*Test:* Write a prototype consolidation script that reads 30 days of JSONL and outputs structured
Markdown without any LLM calls. Is the output useful without LLM synthesis? If a human can read
it and identify actionable patterns, H5 holds for the deterministic phase.

---

## 8. Adversarial Attack Vectors

Instructions for the adversarial reviewer (human or Claude in a separate session):

**Scale attacks:**
- 6 months of daily use: 180 sessions × 30 invocations = 5,400 telemetry entries.
  Does the consolidation script degrade (slower, less accurate) or improve (more signal)?
  Estimate at 1,000 / 5,000 / 10,000 / 50,000 entries.

- Context window pressure: what happens when MEMORY.md reaches 500 lines? 1,000 lines?
  Who prunes it? What is the pruning algorithm? Can Claude be trusted to prune safely, or
  does pruning require deterministic rules?

**Cost spike attacks:**
- An overly aggressive consolidation job calls the LLM 50 times in one night for summarization.
  What guardrails prevent this? What is the maximum LLM call budget for a single consolidation run?
  Map to the vigilance α₄ term in the reward function.

- Vector embedding cost: if semantic search is added in Phase 2, and consolidation re-embeds
  all new telemetry entries nightly, estimate the monthly API cost at 30 sessions/month.
  At what session volume does this exceed the free tier?

**Failure mode attacks:**
- Consolidation runs and silently produces wrong output (e.g., misidentifies a one-off error as
  a persistent pattern and updates MEMORY.md with bad information). How is this detected?
  How is it reversed? What is the blast radius?

- The session bootstrap fails (hook doesn't fire, Python not found, file locked).
  Does the session degrade gracefully (starts cold) or fail hard? Is there a fallback?

- The knowledge graph diverges from reality (a skill is updated, but the graph still has the old
  entity relationships). How is staleness detected and corrected?

**Architectural attacks:**
- Is the Cortex 7-layer model overkill for a solo developer with a trip in 6 months?
  What is the simplest possible memory system that provides measurable value by the trip date?

- The S1/S2 split (H3 deterministic → probabilistic) delays the most valuable feature
  (semantic search) until after the deterministic phase is proven. If the trip is June 2026,
  is there time for two phases? What is the minimum viable semantic search implementation?

- Why not just use an existing memory framework (MemGPT, Zep, Letta, OpenMem)?
  What does building custom add that off-the-shelf does not provide?
  Document the build-vs-buy analysis as part of the adversarial review.

---

## 9. Recommended First Experiment (If H2 Survives Review)

This is not an implementation plan. It is a single experiment to validate H2 before committing
to any architecture. If H2 is killed by adversarial review, this experiment is not run.

**Experiment: Manual Consolidation Audit**

1. Read the last 30 days of telemetry JSONL files by hand (or with a simple Python counter)
2. For each skill, list: (a) invocation count, (b) success rate, (c) most common error category
3. Write 3 bullets per skill in plain English: "what I know about this skill from experience"
4. Add these 6 × 3 = 18 bullets to MEMORY.md under a new `## Skill Experience` section
5. Run 5 sessions with the updated MEMORY.md
6. Measure: does Claude make fewer questions about skill behavior? Does routing improve?

**Success criterion:** At least 2 out of 5 sessions show observable use of the experience bullets
(either cited explicitly in reasoning, or avoided a question that would have been asked without them).

**Cost:** 2 hours of human time. $0 in API costs. Reversible (revert MEMORY.md if it degrades performance).

**If it works:** This is the proof of concept for H2 and H5. Automate the Python step. That is the sleep script.

**If it fails:** H2 is killed. Pivot to a different hypothesis.

---

## 10. Next Document (After Adversarial Review)

The output of the adversarial review exercise is a separate document:
`workflows/010-memory-for-self-improvement/architecture-recommendation.md`

That document should contain:
- Which hypotheses survived (H1–H5)
- The recommended layer subset (from Q1)
- The deterministic/probabilistic split decision (from Q2–Q3)
- The consolidation trigger and target (from Q5–Q6)
- The skill memory footprint decision (from Q11)
- A phased implementation plan consistent with the Phase 1b/2a/2b timeline in `007-self-improvement/PHASED_ROADMAP.md`

That document does not exist yet. It will be created after this research plan survives its own adversarial review.

---

*"If you have any questions or need clarifications, please ask me."* — The researcher
