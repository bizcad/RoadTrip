# Research Report: Prospective Memory Research Bridge

**Date**: 2026-03-05
**Topic**: Implementing the 'Retrieve' (Research) Phase in CIRC-gee
**Source**: NotebookLM (0b27fa4a) - 16 Sources Ingested

## 🔍 Executive Summary
Based on the **7 Levels of Memory** and the **Self-Improvement Series (Parts 1-8)**, the "Retrieve" phase is the critical firewall between a "Sensation" (raw idea) and "Execution" (deterministic action). It transforms "probabilistic insights" into "deterministic behavior" by anchoring new ideas against established policies and historical precedence.

## 🛠️ Implementation Rules (Validated)

### 1. The Gated Supply Chain
- **The Rule**: No sensation can move to "Compose" without a "Provenance Fingerprint."
- **Retrieval Action**: The system must query the **Episodic Memory (Layer 4)** to check if this sensation has occurred before. If it has a high failure rate in history, it is flagged as "High Risk."

### 2. Policy Anchoring
- **The Rule**: Validating sensations against the **"Deterministic Core"**.
- **Retrieval Action**: Cross-reference the sensation with **Layer 1 (Auto Memory / MEMORY.md)**. If the sensation violates a "Must Not Do" constraint (e.g., security protocols or trust gates), it is discarded immediately.

### 3. Bayesian Promotion (Salience)
- **The Rule**: Sensations require independence of evidence.
- **Retrieval Action**: Search for "independent replications." An idea captured in a Session Log (Fast Memory) is a 1-point evidence. An idea found in a NotebookLM source (Slow Memory) adds a 2-point weight. Total weight must exceed a threshold (Salience Score > 0.8) for promotion.

### 4. Fast-Fail YouTube Retrieval Policy (Caption-Only)
- **The Rule**: For YouTube research, retrieve only when captions/transcript already exist.
- **Retrieval Action**: Run a lightweight `ResearchSkill` precheck against the URL using MCP transcript metadata/timed transcript endpoints.
- **Decision**:
	- If transcript/CC exists: continue to Compose.
	- If transcript/CC does not exist: return `no transcript available`, log minimal evidence, and stop.
- **Explicit Non-Goal**: No ASR fallback (Whisper or other transcription) in this phase.
- **Rationale**: This keeps Retrieve deterministic and token-thrifty, avoids compute-heavy branches, and prevents unnecessary memory churn.

### 5. Fast-Thinking Shortcut Contract
- **Intent**: Reject low-yield work early.
- **Input**: YouTube URL.
- **Output**:
	- `status: transcript_available` with transcript handle metadata, or
	- `status: no_transcript_available` with reason.
- **Memory Behavior**:
	- `transcript_available`: allow promotion into Compose/Gate pipeline.
	- `no_transcript_available`: do not create long-lived memory artifacts beyond a minimal decision record.

## 🚦 Next Action Point (Execute)
- **Hypothesis**: Automating this "Retrieve" step with a dedicated `ResearchSkill` will reduce "counterfeit money" (bad code) by filtering out ideas that conflict with the established **Agentic Security Policy**.
- **Action**: Implement a caption-check-first `ResearchSkill` that automatically triggers when a new entry is added to `stores/prospective` and exits early on `no transcript available`.

## ✅ Immediate Implementation Decision
1. Remove ASR fallback from the current spec and implementation scope.
2. Add a fast precheck step: `check_youtube_transcript_availability(url)`.
3. Short-circuit pipeline on failure with user-facing message: `No transcript available for this video.`
4. Spend tokens only when transcript retrieval succeeds.

---
*Verified against CIRC-gee standards: Sense → Retrieve (This Report) → Compose → Gate → Execute → Evaluate → Evolve.*
