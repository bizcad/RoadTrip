# Memory Retrieval Research Notes

Date: 2026-03-08
Author context: RoadTrip assistant architecture notes translated into research terminology

## Purpose
This note translates practical RoadTrip goals into literature-aligned language for memory retrieval systems in assistant workflows.

Source context includes:
- User requirements from RoadTrip sessions
- Example discussion video: https://www.youtube.com/watch?v=JYcidOS9ozU

## Problem Framing (Literature Language)
RoadTrip is not attempting to build a frontier foundation model with native long-context memory. The target is an auxiliary memory and retrieval layer that improves downstream LLM behavior on:

1. Context persistence failures (short-term memory loss / context-window truncation)
2. Factuality and provenance failures (hallucinations without evidence)

In current terminology, this is a retrieval-augmented assistant architecture with tiered memory, domain-specific retrievers, and evidence-grounded response policies.

## Translation: User Intent -> Standard Terms
- "short term memory loss (amnesia)": context window limitations, conversational state loss, long-horizon context decay
- "hallucinations": unsupported generation, factual inconsistency, attribution failure
- "background strategy for assistants": external non-parametric memory layer, retrieval subsystem, memory co-processor
- "modular memories as plugins/connectors": domain-specific retrieval adapters, connectorized memory backends, pluggable retriever stack
- "Fast > slow > slower": hierarchical/tiered retrieval pipeline with progressive cost and precision

## Architectural Position
The recommended system class is:

- Not: parametric-memory scaling (competing with OpenAI/Anthropic model internals)
- Yes: modular Retrieval-Augmented Generation (RAG) with quality controls and explicit evidence contracts

This aligns with:
- Retrieval-augmented memory over model-only memory
- Adaptive retrieval policies instead of fixed-k retrieval
- Hybrid retrieval (lexical + semantic) for robustness
- Citation-aware output constraints for high-stakes tasks

## Proposed Retrieval Policy Model
### Tier 1: Fast Retrieval
Goal: low-latency candidate discovery

- Inputs: frontmatter metadata, filename heuristics, lightweight index
- Methods: lexical match, metadata filters, sparse features
- Output: preliminary candidates + status signal

### Tier 2: Slow Retrieval
Goal: precision and semantic relevance

- Inputs: summary and analysis fields, dense embeddings, reranking
- Methods: hybrid retrieval + reranker
- Output: ranked evidence bundle with confidence

### Tier 3: Slower Retrieval
Goal: deep synthesis and correction

- Inputs: full documents, cross-document links, citation graph
- Methods: corrective retrieval, decomposition/recomposition, critique loop
- Output: high-confidence synthesis with explicit citations and uncertainty annotations

## Response Contract (Required)
Every answer should carry retrieval state metadata:

- `answer_status`: `preview | constrained | complete`
- `semantic_status`: `not_started | queued | running | complete | failed`
- `evidence_count`: integer
- `citations`: list of source anchors (doc + timestamp or line ref)
- `confidence`: calibrated score or discrete band

Interpretation:
- If deep semantic retrieval has not run, the assistant must say so explicitly.
- Questions requiring compositional synthesis (e.g., "what are the 4 things...") should be blocked or marked constrained until Tier 2/3 is complete.

## Domain-Specific Retriever Profiles
The retriever should be tailored to task function, not globalized as one generic ranker.

Examples:
- AP assistant: entity-first retrieval (invoice number, vendor, amount, OCR confidence)
- Marketing/video assistant: claim/timestamp retrieval and comparative evidence
- Coding assistant: symbol-aware retrieval (APIs, diagnostics, source line references)
- Production triage agent: temporal-causal retrieval (incidents, runbooks, code diffs, logs)

## Non-Goals
- Training or fine-tuning a frontier foundation model to own long-term memory
- Replacing enterprise SaaS memory systems broadly
- Eliminating all hallucinations by model behavior alone

The goal is practical reliability improvement through retrieval governance and evidence-grounded output.

## Evaluation Metrics (Suggested)
- Retrieval quality: Recall@k, nDCG@k, MRR
- Evidence quality: citation coverage, citation correctness, unsupported-claim rate
- Operational quality: latency by tier, cost per query, cache hit rate
- Safety/UX: constrained-answer rate when semantic not complete, false confidence rate

## Minimal Roadmap
1. Stabilize Tier 1 index schema (frontmatter + catalog)
2. Add Tier 2 hybrid retrieval and reranker
3. Add explicit response contract in all retrieval tools
4. Add Tier 3 corrective retrieval for hard queries
5. Add domain-specific retriever profiles and benchmarks

## Key References
- Lewis et al. (2020), Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks: https://arxiv.org/abs/2005.11401
- Gao et al. (2024), Retrieval-Augmented Generation for LLMs: A Survey: https://arxiv.org/abs/2312.10997
- Packer et al. (2024), MemGPT: Towards LLMs as Operating Systems: https://arxiv.org/abs/2310.08560
- Asai et al. (2023), Self-RAG: Learning to Retrieve, Generate, and Critique: https://arxiv.org/abs/2310.11511
- Yan et al. (2024), Corrective Retrieval Augmented Generation (CRAG): https://arxiv.org/abs/2401.15884
- Santhanam et al. (2022), ColBERTv2: Lightweight Late Interaction Retrieval: https://arxiv.org/abs/2112.01488
- Hybrid retrieval engineering references:
  - Elastic: https://www.elastic.co/what-is/hybrid-search
  - Pinecone: https://www.pinecone.io/learn/hybrid-search/
