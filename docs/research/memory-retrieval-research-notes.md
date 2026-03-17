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

## Addendum (2026-03-16): AWS Multi-Tier Memory Pattern + SeaweedFS for PPA

### New Source Inputs
- YouTube transcript brief: `docs/research/aws-events-20260305-build-agents-remember-agentic.md`
- AWS blog: https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/
- SeaweedFS wiki scrape: `docs/research/Welcome to the SeaweedFS wiki!.md`

### Key Signals From the AWS Pattern
1. Memory should be explicitly classified at write time (session vs user profile scope).
2. Retrieval should return a small top-k memory bundle (example shown: top 5) to control token cost.
3. Vector index tuning and filtering are as important as embeddings for relevance.
4. Relationship traversal (graph) complements vector similarity for multi-hop context.
5. Orchestration benefits from a memory layer that abstracts storage and retrieval mechanics.

### Proposed PPA Memory Fabric (Integrated)
Use a hybrid memory fabric with specialized stores and one policy router:

1. Classifier/Policy Router
- Input: event from orchestrator (goal, task, plan step, user/session metadata)
- Output: memory class, retention class, retrieval profile, safety level
- Classes:
  - Session memory (short-term)
  - User/project preference memory (long-term)
  - Workflow memory (plan and execution outcomes)
  - Code intelligence memory (symbols, blobs, diagnostics, run/test outcomes)

2. Fast Metadata Plane (Thinking Fast)
- Store one-line summaries and compact JSON descriptors per blob.
- Index fields: repo, path, language, symbol list, tags, recency, usage count, dependency edges, risk score.
- Retrieval objective: very low latency candidate generation and routing.

3. Semantic Plane (Thinking Slow)
- Store embeddings for summaries and code/document chunks.
- Query mode: hybrid lexical + vector with re-ranking.
- Retrieval objective: semantic matching when metadata is insufficient.

4. Relationship Plane (Thinking Slow+)
- Store graph edges: imports, calls, co-change, test coverage links, plan-step-to-artifact links, MCP-to-skill links.
- Query mode: constrained graph expansion from seed candidates.
- Retrieval objective: coherence across multi-step plans and dependency-aware retrieval.

5. Blob/Object Plane (Source of Truth)
- SeaweedFS as primary blob/object backend for code blobs, docs, artifacts, and snapshots.
- Keep canonical files in SeaweedFS-backed object/file storage; keep pointers/hashes in fast planes.
- Retrieval objective: fetch exact artifacts only after candidate narrowing.

### How SeaweedFS Fits the Multi-Tier Memory
SeaweedFS is well suited as the blob/object/file persistence layer behind PPA memory:

1. O(1) style key->blob access supports fast materialization after metadata selection.
2. Tiering support maps naturally to hot/warm/cold memory retention.
3. Object + file interfaces help unify code files, docs, and generated artifacts.
4. Horizontal scaling allows memory growth without changing retrieval contract.

Practical mapping:
- Hot: frequently accessed code/doc blobs for active plans.
- Warm: recently used project artifacts and reusable skill outputs.
- Cold: archived snapshots, historical completions, rollback points.

### End-to-End Retrieval Flow for Plan Completion
1. Plan step arrives (from plan.md or orchestrator intent).
2. Classifier selects profile (coding, docs, MCP wiring, diagnostics, etc.).
3. Fast retrieve: metadata index returns top N seed blobs.
4. Expand: nearest-neighbor + graph neighbors (next 5-20 candidates).
5. Rerank: hybrid semantic + policy filters (safety, scope, ownership).
6. Materialize: fetch exact blobs from SeaweedFS for shortlisted set.
7. Decide: LLM chooses candidate route and proposes completion.
8. Validate: compile/test/lint/policy checks for coherence.
9. Commit or rollback: if checks fail, revert to last known-good snapshot and choose alternate candidate route.

### Minimal Descriptor JSON (for Fast Plane)
```json
{
  "blob_id": "sha256:...",
  "repo": "RoadTrip",
  "path": "src/...",
  "kind": "code|doc|mcp|skill|config|artifact",
  "one_line": "purpose in one line",
  "symbols": ["..."],
  "tags": ["memory", "retrieval", "planner"],
  "depends_on": ["blob_id"],
  "used_by": ["blob_id"],
  "plan_roles": ["discover", "decide", "validate"],
  "safety_level": "low|medium|high",
  "last_green": "git-sha",
  "embedding_ref": "vec:...",
  "blob_ref": "seaweedfs://volume/key",
  "updated_at": "2026-03-16T00:00:00Z"
}
```

### Why This Helps PPA Specifically
1. Better route prediction: metadata + graph context approximates "next likely blob" selection.
2. Lower latency: only fetch full blobs late in the pipeline.
3. Better safety: validation and rollback are built into orchestration, not afterthoughts.
4. Better completion rate: candidate branching allows fallback paths instead of single-shot failure.

### Recommended Next Prototype Slice
1. Implement write-time classifier with 4 memory classes.
2. Build descriptor index for code/docs/skills/MCP manifests.
3. Add top-k + neighbor expansion API for orchestrator.
4. Store canonical artifact blobs in SeaweedFS with hash-addressed keys.
5. Add validation gate and rollback pointer per completion attempt.
