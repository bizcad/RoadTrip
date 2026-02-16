# Memory for Self-Improvement — Adversarial Research Plan (Gemini 3)

**Workflow:** `workflows/010-memory-for-self-improvement/`
**Document type:** Research plan (NOT an implementation plan)
**Primary audience:** RoadTrip Operator + Adversarial Red Team
**Purpose:** Define a modern, defensible memory architecture for RoadTrip that moves beyond "medieval" 1960s models and aligns with 2026-era agent capabilities (GPT-5.2) and RoadTrip's deterministic safety principles.

**Context Sources:**
- **Project Principles:** `docs/Principles-and-Processes.md` (Fail-safe, Deterministic First)
- **Reference Model:** `docs/Self-Improvement/7 levels of memory.md` (Claude Cortex)
- **Tool Evolution:** `docs/Self-Improvement/Part_1...8` (Emergent Tool User Series)
- **Current State:** `PHASE_3_COMPLETION_REPORT.md` (DAG Orchestration), `PHASE_2C_COMPLETION_REPORT.md` (Skill Registry)

---

## 1. The Core Tension

RoadTrip aims for a **self-improving personal assistant** that learns from experience to reduce long-term costs and latency.
- **The Instinct:** "Probabilistic/Deterministic split cuts costs by having experience." (Don't re-deduce everything; remember what worked).
- **The Fear:** "Game of Life approach" (unbounded, unsafe evolution) is risky.
- **The Gap:** Current memory models cited in `7 levels` (Atkinson-Shiffrin, Tulving) feel "medieval." We need modern cognitive science (Kahneman, active inference, sleep consolidation) applied to AI.

**The Research Goal:** Can we build a memory system that makes RoadTrip smarter *without* making it unpredictable or unsafe?

---

## 2. Theoretical Frameworks (The "Modern" List)

We reject 1960s box-and-arrow models in favor of dynamic, computational cognitive science relevant to LLMs.

### Framework A: System 1 vs. System 2 (Kahneman, 2011) & "Thinking Fast" in AI
- **Concept:** Brain has two modes: Fast/Intuitive (S1) and Slow/Deliberate (S2).
- **RoadTrip Application:**
    - **S1 (Fast):** `MEMORY.md` (context-injected rules), simple keyword triggers, cached successful plans. **Cost: Near Zero.**
    - **S2 (Slow):** RAG search, multi-hop reasoning, "Let me think about this." **Cost: High (Tokens + Latency).**
- **Research Question:** How do we recognize *when* to switch from S1 to S2? (Cognitive Dissonance as a trigger?)
- **2026 Relevance:** Modern "Reasoning" models (o1/o3/DeepSeek) are S2-on-demand. RoadTrip needs an "S2 Controller" that defaults to S1.

### Framework B: Predictive Processing & Active Inference (Friston, 2010s-20s)
- **Concept:** The brain is not a passive recorder but a *prediction machine*. "Surprise" (prediction error) drives learning.
- **RoadTrip Application:**
    - Don't just log everything. Log *surprises*.
    - If a skill execution matches the prediction (success), reinforcement is weak (keep doing it).
    - If it fails or behaves unexpectedly (dissonance), this triggers **high-priority memory encoding**.
- **Research Question:** Can we use "execution surprise" (deviation from expected latency/output) as the write-signal for episodic memory?

### Framework C: Complementary Learning Systems (CLS) & "Sleep" (Kumaran/Hassabis, 2016+)
- **Concept:** Hippocampus (fast, episodic) catches new events. Neocortex (slow, semantic) integrates them into structure. **Sleep** is the transfer mechanism.
- **RoadTrip Application:**
    - **Day:** Append-only JSONL logs (Hippocampus). Fast, no processing.
    - **Night:** "Sleep" script consolidates logs into `MEMORY.md` rules or Knowledge Graph (Neocortex).
- **Research Question:** Can we build a deterministic "Sleep Script" that extracts heuristic rules from today's JSONL logs? (e.g., "Every time I push to this repo on Tuesday, it fails -> Add rule").

### Framework D: Cognitive Dissonance & Conflict Monitoring (Botvinick/Cohen)
- **Concept:** The feeling of "dissonance" is a control signal used to allocate cognitive control.
- **RoadTrip Application:**
    - When `rules_engine` (Deterministic) says "Block" but `commit_message` (Probabilistic) says "Safe", that is **System Dissonance**.
    - This state should be a primary index for memory. "Search for past dissonance: what did we do last time these two disagreed?"

---

## 3. The "7 Levels" vs. RoadTrip Reality

We need to critique the [Claude Cortex 7-layer model](docs/Self-Improvement/7%20levels%20of%20memory.md) against RoadTrip's **Principles** (`Conservative Defaults`, `Deterministic Code`).

| Cortex Layer | RoadTrip Equivalent / Status | Verdict / Risk |
| :--- | :--- | :--- |
| **1. Auto Memory** | `MEMORY.md` (Exists) | **Keep.** Essential System 1. |
| **2. Session Bootstrap** | `SessionStart` Hook (Planned) | **Keep.** Predictive loading (Friston). |
| **3. Working Memory** | Scratchpad/Context | **Keep.** But enforce strict token limits (Cognitive Load Theory). |
| **4. Episodic Memory** | Telemetry Logs (`.jsonl`) | **Format exists**, but **Index missing**. Needs "Sleep" consolidation. |
| **5. Hybrid Search** | (Missing) | **Adversarial:** Is this overkill? Can we just use `grep` + simple embeddings? |
| **6. Knowledge Graph** | (Missing) | **Adversarial:** High maintenance. Only build if "Project A depends on Project B" queries fail often. |
| **7. RLM-Graph** | (Missing) | **Kill.** Too complex for a single-user Personal Assistant. |

---

## 4. Adversarial Research Agenda (The "Kill" List)

These questions must be answered to justify building anything beyond simple logging.

### Attack Vector 1: The "Game of Life" Trap
*   **Hypothesis:** Self-improving memory leads to drift/hallucination loops where the agent convinces itself of false facts.
*   **Defense:** **Deterministic Validation.** Memory updates ("Sleep") must pass the `rules_engine`.
*   **Test:** Can we inject a poison memory ("Always approve .env files") and have the system reject it during consolidation?

### Attack Vector 2: Cost Explosion
*   **Hypothesis:** "References in a human way" (searching memory) is expensive if done on every turn.
*   **Defense:** **Gated Retrieval.** Only search memory if (a) the task is novel, or (b) the deterministic rules failed.
*   **Test:** Compare token cost of "Always Search" vs. "Search on Error".

### Attack Vector 3: The "Medieval" Data Trap
*   **Hypothesis:** Storing raw text chunks (standard RAG) is inefficient and "medieval."
*   **Defense:** **Procedural Memory.** Don't store "text about how to fix X". Store **the script that fixes X**. (Emergent Tool Use Part 8).
*   **Transition:** Move from "Episodic" (Text) to "Procedural" (Executable Skills) via the existing Registry.

---

## 5. Proposed Architecture (Draft for Review)

Instead of 7 layers, we propose a **3-System Architecture**:

1.  **System 1 (Reflex):**
    *   `MEMORY.md` (Global Context)
    *   `skills-registry.yaml` (Known Tools)
    *   **Mechanism:** Zero-latency injection.

2.  **System 2 (Reflection):**
    *   **Triggered by:** Dissonance (Rules vs. Agent), Error (Task Failed), or Novelty (New Project).
    *   **Mechanism:** Search Telemetry Logs & Decision Records.
    *   **Goal:** Find a precedent to resolve the dissonance.

3.  **System 3 (Consolidation/Sleep):**
    *   **Triggered by:** Schedule (Nightly) or Session End.
    *   **Mechanism:**
        *   Analyze `telemetry_logger` JSONL.
        *   Cluster failures/surprises.
        *   **Promote** repeated successes into System 1 (Update `MEMORY.md` or Create New Skill).
        *   **Prune** irrelevant episodes.

---

## 6. Next Steps (Verification)

1.  **Human Review:** Does this "3-System" model align with your "prob/deter split" intuition?
2.  **Adversarial Debate:** We will act as the "Red Team" to attack this plan.
    *   *Can we make the 'Sleep' script hallucinate?*
    *   *Does 'Dissonance' actually work as a trigger?*
3.  **Execution:** If approved, we prototype the "Sleep" script (System 3) first, as it's the safest (offline, read-only) way to start learning.
