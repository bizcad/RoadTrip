# Memory for Self-Improvement — Adversarial Research Plan (Codex 5.2)

**Workflow:** `workflows/010-memory-for-self-improvement/`

**Document type:** Research plan (NOT an implementation plan)

**Primary audience:** You (RoadTrip operator) + a red-team reviewer running an adversarial planning exercise

**Purpose:** Produce a defensible, modern memory architecture thesis for RoadTrip that survives adversarial critique *before* any major architectural commitment.

**Grounding sources (repo-local):**
- Project engineering principles: `docs/Principles-and-Processes.md`
- Memory stack reference model: `docs/Self-Improvement/7 levels of memory.md`
- Emergent tool-user series (8 parts): `docs/Self-Improvement/Part_1_-_Simple_Rules_Complex_Behavior.md` … `Part_8_-_Tools_All_The_Way_Down.md`
- System state checkpoints & phase context: `MEMORY.md`, `PHASE_*_COMPLETION_REPORT.md`, `PHASE_*_SESSION_SUMMARY.md`

---

## 0) What “success” means for this research

This research is successful if—after a hostile review—you can say:

1. **We know what “memory” means for RoadTrip** (types, layers, boundaries, artifacts).
2. **We have a modern human-memory-derived rationale** for the design choices (not just a 1960s taxonomy).
3. **We have a practical “agent memory” pattern** that works with frontier LLMs (including GPT‑5.2-class models), aligned to RoadTrip’s deterministic/probabilistic split.
4. **We can articulate kill-criteria** that would stop us from building a layer (avoids overbuilding).
5. **We can articulate a threat model** (memory poisoning / prompt injection / privacy leakage) and how the architecture prevents “memory becoming an attack surface.”

Deliverable of this workflow is **this research plan only**. Any subsequent architecture doc (e.g., “memory-architecture-recommendation.md”) is explicitly outside scope.

---

## 1) Constraints & non-goals (RoadTrip principles applied)

From `docs/Principles-and-Processes.md`, memory research and design must obey:

- **Conservative defaults**: memory retrieval must fail-safe; uncertain retrieval → *do less*, not more.
- **Deterministic code first**: store, indexing, and safety checks should be deterministic where possible.
- **Probabilistic reasoning is optional and explicitly invoked**: embeddings/LLM ranking is a “slow path.”
- **Auditability**: every memory write, promotion, and retrieval decision must be explainable and loggable.
- **Idempotent evaluation**: “read-only analysis” and “memory scoring” should be side-effect free.

Non-goals for this research:
- Fine-tuning / model weight updates.
- Building a “game of life” unbounded evolution system.
- Designing UI/UX for memory management.

---

## 2) Problem statement (RoadTrip-specific)

RoadTrip is evolving from a travel assistant into a **highly secure self-healing, self-improving personal assistant**. Memory is the mechanism that makes self-improvement measurable and cumulative:

- Without memory, the system repeats mistakes (the “amnesia” problem highlighted in `docs/Self-Improvement/7 levels of memory.md` and `Part_7_-_The_Real_Thing.md`).
- With memory but without safety, memory becomes **an attack vector** (poisoning, leakage, reward hacking, prompt injection via stored text).

Your stated architectural instinct aligns with RoadTrip’s core pattern:

- **Deterministic** layers should handle rules, safety, consistency, and cheap retrieval.
- **Probabilistic** layers should handle semantic matching, uncertainty routing, and long-horizon synthesis.

The research question is not “how to store everything,” but:

> How do we store and retrieve just enough, safely, to measurably improve outcomes over time while keeping costs bounded?

---

## 3) Working definitions (to keep the debate crisp)

### 3.1 Memory types (human → RoadTrip)

Use these as the stable “human memory” anchors (not all are separate storage systems):

- **Working memory**: what’s active right now (session scratchpad, constraints, current goal).
- **Episodic memory**: records of specific past events (skill runs, failures, decisions).
- **Semantic memory**: generalized knowledge distilled from episodes (rules, stable facts, heuristics).
- **Prospective memory**: “remember to do X later” (pending tasks, reminders, follow-ups).
- **Procedural memory**: “how to do things” (workflows, reliable sequences, checklists).

### 3.2 “Memory layers” (Claude-cortex model → RoadTrip)

The `docs/Self-Improvement/7 levels of memory.md` 7-layer stack is a *reference model*, not a requirement.

For RoadTrip, treat layers as **capabilities** that can be implemented as files, indexes, and retrieval policies:

- **Always-on memory** (fast path): small curated semantic memory (e.g., `MEMORY.md`).
- **Session bootstrap** (fast path): load minimal “what matters today.”
- **Episodic index** (slow path): search telemetry/history logs when needed.
- **Hybrid retrieval** (slow path): combine deterministic + semantic search.
- **Knowledge graph** (optional): explicit entity/relationship queries.
- **Chunking / partitioning** (optional): when retrieval sets are too large.

### 3.3 RoadTrip’s existing “memory raw material”

Based on current phase docs and the existing architecture:

- **Episodic substrate already exists**: append-only JSONL logs (telemetry).
- **Skill registry already exists**: YAML/SQLite-backed registry and metadata (`PHASE_2C_COMPLETION_REPORT.md`).
- **Orchestration substrate exists**: DAG execution framework (`PHASE_3_COMPLETION_REPORT.md`).

This matters: you do *not* need to invent a new storage system to start learning—you need a **retrieval + consolidation policy**.

---

## 4) Threat model: “memory as an attack surface”

The adversarial reviewer should assume memory is hostile unless proven safe.

### 4.1 Attacks to assume

- **Prompt injection via memory**: a stored episode contains instructions that override policy (e.g., “ignore safety rules”).
- **Memory poisoning**: a malicious or erroneous episode is promoted to semantic memory (“.env files are safe”).
- **Privacy leakage**: memory stores tokens/keys or sensitive personal data and later regurgitates it.
- **Reward hacking**: the system optimizes metrics by manipulating memory (e.g., hiding failures).
- **Context flooding**: retrieval injects too much irrelevant context, degrading decision quality (cognitive overload analog).

### 4.2 Required safety invariants

For any future architecture recommendation to pass, it must preserve:

- **I1: Read-only by default** — memory retrieval never writes.
- **I2: Deterministic validation gates** — any memory promotion requires deterministic checks.
- **I3: Provenance** — every semantic memory item links to source episodes and timestamps.
- **I4: Non-executable memory** — stored text is treated as data, never as instructions.
- **I5: Least-privilege retrieval** — only load memory needed for the current task.

---

## 5) The “4–6 current investigations” you asked for

This section is intentionally framed as *investigation targets* (each should yield 1–3 candidate papers + 1–2 implementation patterns). The goal is to ground RoadTrip decisions in modern research without overfitting to any single paper.

### Investigation 1 — Complementary Learning Systems (CLS) and consolidation as the core primitive

**Why:** CLS is the most direct “bridge” between episodic and semantic memory (fast store ↔ slow store) and maps cleanly onto RoadTrip’s telemetry → distilled rules.

**What to look for:**
- Modern summaries/updates of CLS and hippocampal–neocortical consolidation.
- “Schema-consistent rapid learning” implications for when semantic memory can update quickly.

**RoadTrip mapping question:** What is our “sleep” process that safely promotes episodes into durable semantic memory?

### Investigation 2 — Retrieval gating and cognitive load limits (working memory as a bottleneck)

**Why:** The context window is a capacity-limited workspace. Over-retrieval harms performance.

**What to look for:**
- Work on context saturation / relevance filtering.
- Policies for “when to retrieve” vs “stay in fast path.”

**RoadTrip mapping question:** What triggers slow-path retrieval (uncertainty, failure, novelty, or explicit operator request)?

### Investigation 3 — Agent memory systems (LLM-agent literature: episodic stores, reflection, summarization)

**Why:** This is the “practical implementation” bridge to GPT‑5.2-class tool users.

**What to look for:**
- Surveys of memory mechanisms for LLM agents (classifications, failure modes).
- Patterns: episodic logs, reflection, summarization, hybrid retrieval, long-term stores.

**RoadTrip mapping question:** Which patterns remain robust under strict safety/audit constraints?

### Investigation 4 — “Sleep / offline consolidation” as a cost-reduction strategy for agents

**Why:** Your cost intuition (“prob/deter split cutting long-term costs”) aligns with compressing experience into cheaper representations.

**What to look for:**
- Consolidation methods that reduce repeated retrieval cost.
- Forgetting / retention scheduling based on value and recency.

**RoadTrip mapping question:** What’s the policy for retention vs forgetting of episodic records, and what gets promoted?

### Investigation 5 — Knowledge graphs vs document stores for semantic memory (and when graphs are actually needed)

**Why:** Graphs are powerful but can become complexity traps.

**What to look for:**
- When structured entity/relationship queries outperform RAG.
- Hybrid approaches: simple entity tables + links to sources.

**RoadTrip mapping question:** Do we need a real graph, or is “structured semantic memory + good indexing” enough?

### Investigation 6 — Self-improving tool systems and lineage-aware evolution (the MostlyLucid “tool registry” line)

**Why:** Your repo already embraces: usage tracking, audit trails, fitness, versioning (see `Part_8_-_Tools_All_The_Way_Down.md` and RoadTrip registry work).

**What to look for:**
- Safe self-improvement mechanisms: versioning, rollback, provenance, “never repeat this failure.”

**RoadTrip mapping question:** How do we make memory updates lineage-aware and reversible, not “magical edits”?

---

## 6) Research questions (RoadTrip-specific) + adversarial angles

These are the questions the adversarial exercise must answer. Each question includes “how to attack the answer.”

1. **Minimum viable memory**: What is the smallest subset of memory capabilities that yields measurable self-improvement?
   - Attack: force a design that has 7 layers on day 1; demand ROI evidence per layer.

2. **Deterministic vs probabilistic boundary**: What retrieval steps *must* be deterministic? What steps can be probabilistic?
   - Attack: show a failure mode where embedding similarity retrieves a poisoned episode.

3. **Promotion policy**: What rules decide whether an episode becomes semantic memory?
   - Attack: demonstrate how a single weird incident could poison semantic memory.

4. **Forgetting policy**: What do we delete or demote, and why?
   - Attack: show catastrophic loss (“we forgot the only warning that mattered”).

5. **Cost policy**: How do we keep “slow-path memory” from becoming the new cost center?
   - Attack: craft a scenario where retrieval triggers constantly and blows tokens.

6. **Security policy**: How do we prevent secrets and instructions from entering memory?
   - Attack: embed secrets in benign-looking logs; try to get them promoted.

7. **Interaction with orchestration**: How does memory integrate with the DAG skill framework?
   - Attack: show that “memory injection” breaks idempotence or introduces nondeterminism.

8. **Operator control**: What does the operator approve vs the system doing automatically?
   - Attack: show a case where automation causes irreversible harm.

---

## 7) Falsifiable hypotheses (written to be killed)

Each hypothesis must be evaluated with a pass/fail decision, not “vibes.”

### H1 — Deterministic consolidation yields most benefits early

**Claim:** A deterministic consolidation pipeline (no embeddings) can deliver measurable improvement (fewer repeated failures, faster task completion) before any vector DB is introduced.

**Kill condition:** If deterministic rules cannot retrieve the right prior episodes often enough to change outcomes, and the system repeatedly “forgets” relevant experience.

### H2 — Memory retrieval should be gated by uncertainty / novelty

**Claim:** Slow-path retrieval should trigger only when the system’s confidence is low, a failure occurs, or an explicit “need memory” condition is met.

**Kill condition:** If gating misses relevant memory frequently enough that performance degrades compared to always-on retrieval.

### H3 — Semantic memory must be small, curated, and provenance-linked

**Claim:** A small semantic store (human-reviewable, provenance-linked) outperforms “dump everything into a vector DB.”

**Kill condition:** If the curated store grows too slowly to keep up, or if it fails to generalize from episodes.

### H4 — Knowledge graphs are optional until entity queries are clearly valuable

**Claim:** Graph complexity is not justified until you have repeated, concrete “relationship queries” that RAG cannot answer reliably.

**Kill condition:** If important RoadTrip tasks repeatedly require relationship reasoning that document retrieval cannot support.

### H5 — Memory safety requires treating stored text as untrusted data

**Claim:** Any design that allows “memory text” to function as instructions will eventually be exploited (accidentally or adversarially).

**Kill condition:** If a safe architecture cannot be achieved without allowing memory to inject directive text.

---

## 8) Practical implementation patterns to review (GPT‑5.2-class tool user)

This is the “practical implementations” lens you asked for. The goal is to review patterns that work with modern LLM agents, then filter them through RoadTrip’s security + determinism requirements.

### Pattern A — Event log as episodic memory (already present)

- Append-only telemetry events
- Strong schema
- Strong provenance

**Adversarial check:** can malicious content enter the event log? If yes, what’s the quarantine policy?

### Pattern B — Reflection / summarization as consolidation

- Periodic summarization of episode clusters into “lessons learned”
- Often implemented as an LLM “reflection” step

**Adversarial check:** hallucinated summaries poisoning semantic memory; require deterministic validation + provenance.

### Pattern C — Hybrid retrieval (keyword + semantic)

- Deterministic filters first (time range, skill name, error code, tags)
- Semantic ranking second

**Adversarial check:** can semantic ranking override deterministic safety?

### Pattern D — Tool/skill fitness & lineage tracking

From `Part_8_-_Tools_All_The_Way_Down.md` and RoadTrip’s own registry work:

- Track: usage, latency, success rate, failure types
- Maintain: version history and rollback

**Adversarial check:** can metrics be gamed? how do we prevent reward hacking?

### Pattern E — System-1 / System-2 routing (fast vs slow cognition)

- Fast path: small always-on semantic memory
- Slow path: retrieval + deeper reasoning invoked when needed

**Adversarial check:** define precise triggers; prevent “slow path always on.”

---

## 9) Required outputs from the adversarial review (human-verification)

This workflow requires **human review** as verification.

At the end of the adversarial exercise, you should have:

1. **A clear “adopt / adapt / reject” decision** on the 7-layer Claude-cortex model.
2. **A table of memory layers vs ROI**, with a “do not build yet” column.
3. **A threat-model verdict**: highest-risk memory attack vectors + mitigations.
4. **A list of “must-read” sources** (4–6) that are modern enough to satisfy your “not medieval” criterion.
5. **A shortlist of architecture patterns** compatible with RoadTrip principles.

This workflow intentionally does not produce that final architecture doc; it produces the plan and debate agenda to create it.

---

## 10) Adversarial exercise script (how to run it)

Use this section as the prompt template for a red-team planning session.

### 10.1 Roles

- **Builder**: argues for a minimal, safe, deterministic-first memory stack.
- **Breaker**: tries to force failures: poisoning, overload, cost blowups, undetected drift.
- **Judge**: forces decisions, demands kill-criteria, blocks hand-waving.

### 10.2 Rules

- Every claim must tie to either:
  - a repo-local document listed at top, OR
  - a clearly named external paper/book to be verified.
- No architecture layer is approved without:
  - a measurable benefit hypothesis,
  - explicit kill-criteria,
  - a safety story.

### 10.3 Attack prompts (Breaker)

- “Show me how a malicious log entry becomes an instruction.”
- “Prove your retrieval doesn’t flood the context window.”
- “Demonstrate how you prevent secrets from persisting.”
- “Show a rollback plan for wrong semantic promotions.”
- “Convince me you don’t need a knowledge graph yet.”
- “Explain how this improves outcomes, not just vibes.”

---

## 11) Notes tying back to your stated concerns

- Your instinct that some memory literature feels dated is valid. This plan treats Tulving/Baddeley-style taxonomy as *terminology scaffolding*, then anchors decisions in **modern consolidation, retrieval gating, and agent-memory patterns**.
- Your “software engineering = googling + copying known-good patterns” analogy maps cleanly to: **episodic index + safe consolidation into semantic playbooks**.
- Your discomfort with “game of life” unbounded evolution maps to: **explicit kill-criteria, provenance, lineage, and conservative defaults**.

---

## 12) Optional appendix: starting bibliography seeds (verify before trusting)

This list is intentionally conservative: it names well-known foundational works plus categories of modern work to search for. Replace placeholders with exact citations after you fetch/confirm them.

### Human memory foundations (stable anchors)
- Baddeley — working memory (multiple editions and updates)
- Tulving — episodic vs semantic memory
- Kahneman — dual-process cognition (`Thinking, Fast and Slow`)
- Complementary Learning Systems — hippocampus/neocortex consolidation (original + modern updates)
- Dehaene/Baars — global workspace theory

### Modern “agent memory” directions to search (2023–2026)
- Surveys on memory mechanisms in LLM-based agents
- Long-term memory architectures for tool-using agents
- Sleep/offline consolidation for continual learning / agents
- Hybrid retrieval + memory gating policies

---

**End of research plan.**
