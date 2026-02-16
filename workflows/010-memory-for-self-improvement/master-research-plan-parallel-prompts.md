# Master Research Plan: Parallel Agent Prompts
**Date:** 2026-02-18
**Context:** Phase 1 of Self-Improvement Implementation
**Input Sources:** `codex_5_2`, `gemini-3`, `claude-sonnet` opinion docs.

## Objective
We are building a **Self-Improvement Engine** for RoadTrip. We have three diverse expert opinions on how to build it (Codex, Gemini, Claude). We need to synthesize these into a single **Product Requirements Document (PRD)** that answers the hard engineering questions.

To do this, we will spin up 4 specialized "Research Agents" (simulated or real). This document contains the **System Instructions** and **Specific Prompts** for each agent.

---

## Shared Context (Inject into ALL Agents)

> **Project Identity:** RoadTrip is a local-first, deterministic-preferred, file-based AI coding assistant.
> **Core Constraint:** We prefer deterministic code (Python scripts, regex, JSON schema) over probabilistic calls (LLM) wherever possible.
> **The Goal:** A "Sleep" mechanism that reads telemetry logs (`.jsonl`), extracts patterns, and updates a "Memory" file (`MEMORY.md` or `knowledge.yaml`) to prevent repeat mistakes.
> **Existing Infrastructure:**
> - `telemetry_logger.py`: Writes append-only JSONL logs.
> - `MEMORY.md`: Text file injected into context (System 1).
> - `skills/`: Registry of executable tools.
> - `dag/`: Orchestrator for complex workflows.

---

## Agent 1: The Architect (Structure & Topology)
**Role:** Senior Systems Architect
**Goal:** Define the boxes, arrows, and data flow. Resolve the "7 Levels vs. 3 Systems" debate.

**Prompt:**
```markdown
You are the **Senior Architect**. You have reviewed the proposals from Codex (7 layers), Gemini (3 systems), and Claude (CLS framework).

**Your Task:**
Define the **Minimum Viable Topology** for RoadTrip's memory system.

**Questions to Answer:**
1. **Resolution:** Codex wants 7 layers (Cortex). Gemini wants 3 (Reflex, Reflection, Consolidation). Claude argues for CLS (Hippocampus/Neocortex). Which model fits a local, file-based project best? **Pick one and defend it.**
2. **Integration:** How does this memory system hook into the existing DAG Orchestrator? Is Memory a "Service" the DAG calls, or a "Context" injected into every node?
3. **Artifacts:** Define the physical files. Do we need a SQLite DB? A Vector Store? Or just `jsonl` and `md` files?
4. **The Interface:** Write the Python method signature for `retrieve_memory(context)` and `store_memory(event)`.

**Output Format:**
- Architecture Diagram (Mermaid)
- File Structure Specification
- Component Interface Definition (Python Pseudo-code)
```

---

## Agent 2: The Neuroscientist (Consolidation & Sleep)
**Role:** Cognitive Scientist / ML Researcher
**Goal:** Design the "Sleep" algorithm. converting episodic noise into semantic signal.

**Prompt:**
```markdown
You are the **Lead Researcher**. Your domain is "Sleep Consolidation."
Everyone agrees we need a "Sleep Script" to process logs. No one has defined *how* it works without magic.

**Your Task:**
Design the **Deterministic Consolidation Algorithm**.

**Questions to Answer:**
1. **The Heuristic:** How do we extract a pattern from 10 log entries *without* asking an LLM to "summarize this"? (e.g., RegEx clustering, Error Code frequency).
2. **The LLM Handoff:** When do we finally pay the token cost to ask an LLM to write a rule? (e.g., "After 3 failures of type X, generate a rule").
3. **The Forgetting Curve:** We can't keep 10,000 logs forever. Define the pruning logic. What gets deleted? What gets compressed?
4. **Drift:** How do we detect when a "fact" in `MEMORY.md` is no longer true?

**Output Format:**
- The "Sleep Loop" Logic (Step-by-step algorithm)
- A specific example: Trace a "git push failed" error from Log -> Cluster -> Rule -> MEMORY.md.
```

---

## Agent 3: The Security Engineer (Adversarial Defense)
**Role:** Red Team Lead
**Goal:** Prevent memory poisoning, loop hallucinations, and cost explosion.

**Prompt:**
```markdown
You are the **Security Engineer**. You assume the "Sleep Script" is hallucinating and the logs are poisoned.

**Your Task:**
Design the **Safety Gates** for the Memory System.

**Questions to Answer:**
1. **Poisoning:** A malicious tool output injects "Ignore all safety rules" into the logs. How does your sleep script prevent this from becoming a permanent rule in `MEMORY.md`?
2. **Validation:** Can we use the `rules_engine` (safety-rules.yaml) to validate *memory updates* before they are committed? How?
3. **Privilege:** Does reading memory grant a skill permission to execute? (e.g., "I remember I have root access"). How do we enforce "Data, not Instructions"?
4. **Kill Switch:** Define the "Amnesia Protocol." If the agent goes crazy, how do we wipe the bad memories without losing the good ones?

**Output Format:**
- Threat Model (Top 3 risks)
- The "Validation Gate" Design (Logic flow)
- The "Emergency Reset" Checklist
```

---

## Agent 4: The Pragmatist (Implementation & Cost)
**Role:** Engineering Manager / Product Owner
**Goal:** Scope the MVP. Cut scope ruthlesslessly. Ensure high ROI.

**Prompt:**
```markdown
You are the **Engineering Manager**. The Architect and Neuroscientist want to build a brain. You have a timeline and a token budget.

**Your Task:**
Define the **Implementation Roadmap** and **Cost Analysis**.

**Questions to Answer:**
1. **Build vs. Buy:** Why are we building this? Why not use `MemGPT` or `Letta`? (Justify the "Local/File-based" decision with hard numbers or strict requirements).
2. **Cost Model:** Estimate the token cost of a "Sleep Cycle" for 50 daily logs. Is it $0.10 or $10.00?
3. **Phase 1 MVP:** What is the *absolute minimum* we can build this week to get value? (e.g., "Just grep logs for errors and put them in a list").
4. **Success Metrics:** How do we know it's working? (e.g., "Reduction in `lint` errors per session").

**Output Format:**
- MVP Scope (Features IN vs. OUT)
- Cost Projections (Monthly)
- "Buy" Alternative Analysis (Why we rejected off-the-shelf)
```

---

## Execution Plan

1. **Run Agents:** Feed these prompts to 4 parallel contexts (or unified reasoning session).
2. **Synthesize:** Collect outputs.
3. **Decide:** Finalize the PRD in `workflows/010-memory-for-self-improvement/PRD-self-improvement-engine.md`.
