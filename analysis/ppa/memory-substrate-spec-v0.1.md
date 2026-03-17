# Memory Substrate Spec v0.1

Project: PPA
Status: Draft
Date: 2026-03-16
Location: analysis/ppa

## 1. Purpose
Define a provider-agnostic memory substrate for PPA focused on capture and retrieval, with explicit governance and evaluation loops.

This spec is designed to plug into existing PPA direction from:
- ppa_approach_summary.json
- Unified Auth Spec v0.2

## 2. Design Goals
1. Fast retrieval for active orchestration decisions.
2. Durable memory for auditability, policy, and replay.
3. Deterministic governance controls on what persists.
4. Pluggable backend providers (AWS stack, Convex/Cockroach, others).
5. SRCGEEE alignment, with explicit Evaluate and Evolve feedback.

## 3. Non-Goals
1. Model-side long-term memory training.
2. Single-vendor lock-in.
3. Unlimited retention without policy.

## 4. Memory Planes
1. Prediction Plane
- Probabilistic next-step selection for workflow routing.
- Inputs: task state, prior outcomes, domain profile.

2. Retrieval Plane
- Think Fast: metadata + vector candidate retrieval.
- Think Slow: semantic rerank + relational checks.
- Think Slow+: full artifact retrieval, deep validation context.

3. Governance Plane
- Classification, retention, promotion, demotion, decay, archival, purge.

4. Assurance Plane
- Provenance, policy evidence, traceability, rollback anchors.

## 5. Canonical Memory Record
Each stored item uses a common contract regardless of backend.

```json
{
  "memory_id": "mem_...",
  "tenant_id": "roadtrip",
  "domain": "engineering|ap|legal|sales|custom",
  "memory_class": "session|working|episodic|semantic|procedural|artifact|policy",
  "artifact_kind": "code|doc|mcp|skill|log|plan|telemetry|binary",
  "summary": "one-line purpose",
  "content_ref": "object://...",
  "embedding_ref": "vec://...",
  "graph_refs": ["node://..."],
  "tags": ["srcgeee:retrieve", "risk:medium"],
  "trust_score": 0.0,
  "usefulness_score": 0.0,
  "recency_score": 0.0,
  "governance_state": "candidate|validated|promoted|stale|archived|purged",
  "retention_policy": "daily|weekly|monthly|legal-hold",
  "ttl_at": "2026-03-31T00:00:00Z",
  "created_at": "2026-03-16T00:00:00Z",
  "updated_at": "2026-03-16T00:00:00Z",
  "provenance": {
    "principal": "agent:orchestrator",
    "source": "session_log_events.jsonl",
    "hash": "sha256:..."
  },
  "policy_evidence": {
    "auth_decision_id": "dec_...",
    "risk_score": 42,
    "hitl": false
  }
}
```

## 6. Provider Interface (Plugin Contract)

### 6.1 Capture API
- captureEvent(event): write raw interaction or execution event.
- captureArtifact(record): write memory record + references.
- classify(record): assign memory_class, domain, retention policy.
- embed(record): create embedding in configured embedding provider.

### 6.2 Retrieval API
- retrieveFast(query, k): metadata/vector candidate pull.
- retrieveSlow(query, candidates): semantic rerank + constraints.
- retrieveDeep(query, shortlist): artifact hydration and supporting evidence.
- retrieveGraph(query, seeds): optional relationship expansion.

### 6.3 Governance API
- evaluate(record_id): recompute scores and state transitions.
- promote(record_id), demote(record_id), archive(record_id), purge(record_id).
- applyRetention(policy_window): daily/weekly/monthly sweeps.

### 6.4 Assurance API
- attest(result_set): attach provenance and policy evidence.
- rollbackAnchor(workflow_id): return known-good recovery point.

## 7. Capture Workflow
1. Orchestrator emits event at SRCGEEE phase boundary.
2. Classifier assigns memory_class and domain.
3. Tagger enriches semantic/risk/process tags.
4. Embedder creates vectors if eligible.
5. Record and refs are written:
- fast index
- durable store
- object store
- optional graph
6. Governance state starts as candidate.
7. Policy evidence is attached from auth/risk gate outputs.

## 8. Retrieval Workflow
1. Query classification (intent, risk, domain, latency budget).
2. retrieveFast returns initial candidates.
3. retrieveSlow reranks and filters by trust/policy.
4. Optional graph expansion for coherence.
5. retrieveDeep hydrates shortlisted artifacts.
6. LLM receives bounded evidence bundle.
7. Response includes confidence decomposition:
- retrieval_confidence
- coherence_confidence
- execution_confidence

## 9. Governance and Evaluate Jobs

### 9.1 Daily
- Recompute recency/usefulness/trust scores.
- Promote high-performing candidates.
- Demote stale low-utility items.

### 9.2 Weekly
- Drift analysis by domain.
- Resolve conflicts and supersession chains.
- Tune retrieval thresholds and k values.

### 9.3 Monthly
- Retention and compliance sweep.
- Archive or purge policy-expired memory.
- Domain profile recalibration.

## 10. Backend Mapping Options

Backend choices are now resolved. See `workflows/012-operational-agentic-memory/impl-plan-v0.1.md` for the phased implementation plan.

### Option A (Active — v0.1): Local-First SQL Server Express + SeaweedFS

- **Durable / Governance tier**: SQL Server Express (local, `[dbo]` schema, EF Core)
- **Artifact / Blob tier**: SeaweedFS (local, S3-compatible HTTP API)
  - Hot: `C:\SeaweedFS\hot` (internal SSD)
  - Warm: `E:\SeaweedFS\warm` (18 TB HDD)
  - Cold: `D:\SeaweedFS\cold` (14 TB HDD)
- **Embedding lane**: Local FAISS index at `C:\SeaweedFS\hot\embeddings\`
- **Orchestrator LLM**: BitNet (local inference endpoint)

Pros:
- Zero cloud cost
- Already owned hardware and tooling
- EF/Aspire familiarity from QuestionManager project
- SeaweedFS multi-tier maps directly to owned drives

Tradeoffs:
- Single-machine; no replication unless cold tier is on separate drive (it is)
- SQL Server Express 10 GB DB cap (more than sufficient for metadata-only records)

### Option B (Future migration path): CockroachDB + SeaweedFS

- **Durable tier**: CockroachDB (distributed, survives node loss)
- **Blob tier**: SeaweedFS (same bucket structure, same ContentRef URIs)

Note:
- SeaweedFS provides a CockroachDB parser integration reference:
  https://github.com/seaweedfs/cockroachdb-parser
- Migration from SQL Server Express to CockroachDB is a schema adapter swap only; the blob tier and ContentRef contract are unchanged.

### Option C (Future cloud adapter): Azure-first managed stack

- **Durable tier**: Azure SQL or Cosmos DB
- **Blob tier**: Azure Blob Storage (S3-compatible ContentRef URIs swap scheme to `az://`)
- Trigger: needed if multi-user, multi-machine, or cloud-burst scenarios arise.

## 11. Multimodal Embedding Readiness
Support pluggable embedding providers with a unified vector contract.

Required capabilities:
1. Shared embedding space for text/images/audio/video/docs when enabled.
2. Interleaved multimodal input support where available.
3. Provider abstraction so retrieval APIs remain unchanged.

## 12. Security and Policy Hooks
1. All capture operations carry principal identity and delegation context.
2. Retrieval enforces policy scope before returning content.
3. High-risk retrieval requests may require HITL or elevated audit.
4. Memory writes and promotion actions are fully audited.

## 13. Implementation Plan

See `workflows/012-operational-agentic-memory/impl-plan-v0.1.md` for the full 8-phase plan.

Summary:
1. SQL Server Express schema + EF Core models (11 tables, `[dbo]`)
2. Capture API (`captureEvent`, `captureArtifact`, hash chain, outbox)
3. SeaweedFS integration (blob write, ContentRef assembly, hash verify, tier placement)
4. Retrieval API (`retrieveFast`, `retrieveSlow`, `retrieveDeep`, confidence decomposition)
5. Async embedding lane (local FAISS, background worker, graceful degradation)
6. Daily governance job (score recompute, state transitions, tier migration, purge)
7. Auth integration (Principals, Delegations, PolicyEvidence, unified-auth-spec v0.2 L0–L6)
8. BitNet orchestrator integration (memory-augmented queries, next-phase prediction)

## 14. Open Questions

1. Duplicate-capture policy: new `MemoryRecord` per episode vs dedupe + new `EventLedger` event?
2. Rollback anchor granularity: workflow-step, run-level (current default), or deployment?
3. Snapshot scope: full context window vs delta summary for `sessions/snapshots/`.
4. Embedding storage: local FAISS outside SeaweedFS vs inside `seaweedfs://ppa/embeddings/`.
5. Session purge behavior: hard-delete at TTL or cold-tier move for audit.
6. EventLedger correction: append correction event only, or add `CorrectedBy` column.
