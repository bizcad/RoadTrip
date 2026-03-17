# Phased Implementation Plan — Operational Agentic Memory

**Workflow**: 012-operational-agentic-memory  
**Status**: Draft v0.1  
**Date**: 2026-03-16  
**Feeds**: memory-substrate-spec-v0.1.md, sql-server-table-list.md, seaweedfs-artifact-map.md, reference-contract.md  
**Auth dependency**: unified-auth-spec-v0.2.md  

---

## Overview

This plan breaks the memory substrate into eight sequential phases.  
Each phase is independently shippable and testable.  
Phases 1–3 are the critical foundation. Nothing else can start until they are solid.

**Primary stack**:
- SQL Server Express (local, EF Core, dbo schema)
- SeaweedFS (local, C: hot / E: warm / D: cold)
- .NET 10 standalone solution rooted at `G:\repos\AI\PPA\PPA.App.slnx` — **independent from the Aspire/QuestionManager production solution**
- Local FAISS for embedding-based retrieval

**Execution boundary**:
- RoadTrip is the developer workspace and planning surface.
- PPA is the executable target application.
- Runtime responsibilities are split across dedicated projects rather than collapsed into one process by default.

---

## Phase 1 — SQL Server Schema and EF Core Models

**Goal**: All 11 tables running locally, seeded, and exercised by basic integration tests.

### Deliverables

1. New .NET class library project: `PPA.Memory.Data` in the standalone PPA app at `G:\repos\AI\PPA\src\PPA.Memory.Data`
2. EF Core `DbContext`: `MemoryDbContext`
3. Entity models for all 11 tables (see `sql-server-table-list.md`)
4. Initial EF migration
5. Seed data: `RetentionPolicies` (7 default rows) + `DomainProfiles` (5 default rows) + `Principals` (3 seed rows)
6. Basic integration test: round-trip write → read on each table

### Initial PPA project split

- `PPA.Memory.Data` — EF Core models, DbContext, migrations, SQL Server access
- `PPA.Memory.Capture` — capture boundary, dedup logic, hash chain write path
- `PPA.Memory.Blobs` — SeaweedFS adapter and integrity verification
- `PPA.Memory.Retrieval` — fast/slow/deep retrieval APIs
- `PPA.Orchestrator` — SRCGEEE flow coordination only
- `PPA.Executor` — deterministic execution boundary
- `PPA.Triage` — issue routing, retry strategy, escalation decisions
- `PPA.Evaluator` — outcome scoring and promotion/demotion signals
- `PPA.TestRunner` — isolated testing/verification boundary
- `PPA.AgentFactory` — authorized agent creation only; not part of default orchestration loop

### Table checklist

| # | Entity class | Table name |
|---|-------------|-----------|
| 1 | `MemoryRecord` | `dbo.MemoryRecords` |
| 2 | `EventLedgerEntry` | `dbo.EventLedger` |
| 3 | `GovernanceTransition` | `dbo.GovernanceTransitions` |
| 4 | `RetentionPolicy` | `dbo.RetentionPolicies` |
| 5 | `PolicyEvidenceEntry` | `dbo.PolicyEvidence` |
| 6 | `RollbackAnchor` | `dbo.RollbackAnchors` |
| 7 | `AccessMetric` | `dbo.AccessMetrics` |
| 8 | `Principal` | `dbo.Principals` |
| 9 | `Delegation` | `dbo.Delegations` |
| 10 | `DomainProfile` | `dbo.DomainProfiles` |
| 11 | `EmbeddingRef` | `dbo.EmbeddingRefs` |

### Key EF rules

- `EventLedger` is insert-only. No `Update` or `Remove` calls in EF. Enforced via repository pattern.
- `GovernanceState` on `MemoryRecord` is backed by an `enum`. Only updated through the Governance API, never directly.
- JSON columns (`Tags`, `ArtifactRefs`, `MemoryIds`) use `HasConversion` + `ValueComparer`.
- `HasData` seeds go in `OnModelCreating`.

### Done when

- Migration applies cleanly to local SQL Server Express.
- Integration test writes one row per table and reads it back.
- Seed data is populated and queryable.

---

## Phase 2 — Capture API (SQL Server only, no blobs yet)

**Goal**: Record events and memory records into SQL Server correctly. No SeaweedFS dependency yet — `ContentRef` is NULL at this phase.

### Deliverables

1. New class library: `PPA.Memory.Capture`
2. `ICaptureService` interface with:
   - `CaptureEventAsync(event)` — writes `EventLedger` row with hash chain
   - `CaptureRecordAsync(record)` — writes `MemoryRecord` with `GovernanceState = candidate`; performs dedup check first
   - `ClassifyAsync(memoryId)` — assigns `MemoryClass`, `Domain`, `RetentionPolicy`, and `TtlAt`
3. **Duplicate-capture logic** (inside `CaptureRecordAsync`):
   - Compute `BlobHash` (SHA-256) before attempting insert
   - Query `IX_MemoryRecords_DedupKey` on `(BlobHash, SourceFile, SourceLineStart, SourceLineEnd)`
   - **If match found**: write `EventLedger` row with `Phase = 'Capture', PhaseOutcome = 'duplicate-detected'`, `MemoryId = existing record`; emit diagnostic alert; return existing `MemoryId` — do NOT insert new `MemoryRecord`
   - **If hash matches but citation differs** (different `SourceFile` or line range): this is a different citation — proceed with new `MemoryRecord` insert as normal
   - **If no match**: proceed with new `MemoryRecord` insert as normal
   - Callers are expected to hash-check before calling (prevent, don't just detect); this is the last line of defense
4. Hash chain logic: each `EventLedger` row computes `EventHash` from its canonical fields and chains `PrincipalId.PrevEventHash` from the previous row.
5. Outbox table or staging pattern: write intent row first, then confirm.
6. Integration tests: verify hash chain continuity across 5+ events; verify duplicate-capture path emits event and returns existing ID without inserting.

### SRCGEEE phase events

Capture emits one `EventLedger` row per SRCGEEE phase transition:

| Phase | `PhaseOutcome` values | Notes |
|-------|----------------------|-------|
| **Capture** | `completed`, `duplicate-detected` | Synthetic phase — used only for dedup events outside SRCGEEE lifecycle |
| Sense | `completed`, `failed` | First event in a workflow run |
| Retrieve | `completed`, `skipped`, `failed` | |
| Compose | `completed`, `failed` | |
| Gate | `completed`, `hitl-held`, `failed` | HITL hold suspends the run |
| Execute | `completed`, `failed` | |
| Evaluate | `completed`, `failed` | |
| Evolve | `completed`, `skipped`, `failed` | |

**Cost/resource tracking**: `Payload` on the `EventLedger` row carries cost/resource metadata per phase. Structure:
```json
{
  "tokens_in": 1200,
  "tokens_out": 800,
  "model": "bitnet-local",
  "latency_ms": 340,
  "cost_usd": 0.0,
  "resource_notes": "..."
}
```
This feeds the reward system and triage agent analysis.

### Done when

- A simulated 7-phase workflow run produces 7 correct ledger rows with unbroken hash chain.
- `MemoryRecord` is written with `GovernanceState = candidate` and correct `TtlAt` from seed retention policy.

---

## Phase 3 — SeaweedFS Integration

**Goal**: Blob write, `ContentRef` assembly, SHA-256 hash verification, and tier placement working end-to-end.

### Deliverables

1. New class library: `PPA.Memory.Blobs`
2. `IBlobStore` interface with:
   - `WriteAsync(stream, metadata)` → returns `ContentRef` URI
   - `ReadAsync(contentRef)` → returns `Stream`
   - `DeleteAsync(contentRef)` → idempotent delete
   - `MigrateAsync(contentRef, targetTier)` → changes volume group
3. `SeaweedFsBlobStore` implementation using SeaweedFS S3-compatible HTTP API
4. Local drive configuration (loaded from `appsettings.json` or `dotnet user-secrets`):
   ```json
   {
     "SeaweedFS": {
       "HotPath": "C:\\SeaweedFS\\hot",
       "WarmPath": "E:\\SeaweedFS\\warm",
       "ColdPath": "D:\\SeaweedFS\\cold",
       "BaseUri": "http://localhost:8333"
     }
   }
   ```
5. Hash verification at write: compute SHA-256 before upload, confirm after.
6. `ContentRef` format: `seaweedfs://ppa/{bucket}/{subfolder}/{date}/{hash-prefix}-{memory-id}.{ext}`
7. Phase 2 capture updated: after blob write succeeds, update `MemoryRecord.ContentRef` and `BlobHash`.
8. Integrity check on read: verify hash before returning stream.

### Failure modes to handle

| Failure | Behavior |
|---------|----------|
| Blob write fails | Keep `ContentRef = NULL`; mark record `candidate`; retry via background job |
| Hash mismatch on read | Flag record `stale`; do not serve to LLM; log integrity event to `EventLedger` |
| Blob missing (404) | Same as hash mismatch |

### Done when

- Capture of a code artifact writes blob to `C:\SeaweedFS\hot`, records `ContentRef` and `BlobHash` in SQL Server.
- Reading the same record fetches blob, verifies hash, returns stream.
- Manually corrupting the blob triggers the integrity violation path.

---

## Phase 4 — Retrieval API

**Goal**: Fast, Slow, and Deep retrieval working. Confidence decomposition returned. Suitable for orchestrator consumption.

### Deliverables

1. New class library: `PPA.Memory.Retrieval`
2. `IRetrievalService` interface:
   - `RetrieveFastAsync(query, k)` → top-k candidates by metadata/tags + domain filter
   - `RetrieveSlowAsync(query, candidates)` → rerank by trust/policy + optional embedding score
   - `RetrieveDeepAsync(query, shortlist)` → hydrate blobs, run integrity check, return evidence bundle
   - `RetrieveGraphAsync(query, seeds)` → optional relationship expansion (defer to Phase 4b)
3. `RetrievalResult` response contract:
   ```json
   {
     "memory_id": "mem_...",
     "summary": "...",
     "content": "(blob bytes or null)",
     "confidence": {
       "retrieval_confidence": 0.85,
       "coherence_confidence": 0.72,
       "execution_confidence": 0.68
     },
     "policy_ok": true,
     "provenance": { ... }
   }
   ```
4. Policy gate in `RetrieveSlow`: records with `GovernanceState ∈ {archived, purged}` return 403 unless caller has elevated delegation.
5. Access metric update on every retrieval hit: increment `AccessCount`, `AccessCountD7`, `AccessCountD30`, update `LastAccessedAt`.

### Retrieval speed tiers

| Method | Latency budget | Data sources |
|--------|---------------|-------------|
| `RetrieveFast` | < 50 ms | SQL Server metadata query only |
| `RetrieveSlow` | < 500 ms | SQL Server + embedding vector score |
| `RetrieveDeep` | < 2 s | SQL Server + SeaweedFS blob fetch + hash verify |

### Done when

- `RetrieveFast` on a domain filter returns correct candidates.
- `RetrieveDeep` fetches, verifies, and returns blob content.
- Archived/purged records are gated correctly.
- `AccessMetrics` row is updated after each retrieval.

---

## Phase 5 — Async Embedding Lane

**Goal**: Embeddings generated in the background; `EmbeddingRef` populated asynchronously; `RetrieveSlow` uses vectors when available.

### Deliverables

1. Background worker: `EmbeddingWorker` (hosted service)
   - Polls for `MemoryRecords` where `EmbeddingRef IS NULL AND GovernanceState IN ('candidate','validated','promoted')`
   - Generates embeddings via local FAISS-compatible model
   - Writes embedding to local FAISS index
   - Inserts row into `dbo.EmbeddingRefs`
   - Updates `MemoryRecords.EmbeddingRef`
2. `IEmbeddingProvider` interface (pluggable):
   - v0.1 default: local sentence-transformer / small model via ONNX
   - v0.2 option: swap to Azure AI Search or OpenAI embedding endpoint
3. FAISS index location: `C:\SeaweedFS\hot\embeddings\` (hot tier, fast access)
4. `RetrieveSlow` updated: if `EmbeddingRef IS NOT NULL`, incorporate vector cosine score into rerank; otherwise fall back to metadata-only score.
5. Graceful degradation: retrieval must still work when `EmbeddingRef IS NULL`.

### Done when

- A newly captured record has `EmbeddingRef = NULL` immediately after capture.
- Background worker populates `EmbeddingRef` within 5 seconds (local dev).
- `RetrieveSlow` returns higher-ranked results when embedding is present vs absent.

---

## Phase 6 — Daily Governance Job

**Goal**: Automated score recomputation, state transitions, and tier migration running on a schedule.

### Deliverables

1. Background job: `GovernanceJob` (hosted service, runs on timer — daily at 02:00 UTC local)
2. Job steps in order:
   ```
   Step 1: Score recompute
     - For each MemoryRecord (not purged):
       - RecencyScore    = decay_fn(LastAccessedAt)
       - UsefulnessScore = weighted(AccessCountD7, AccessCountD30, FeedbackPositive, FeedbackNegative)
       - TrustScore      = from Principal.TrustLevel + PolicyEvidence.RiskScore
   
   Step 2: Promotion sweep
     - If (RecencyScore + UsefulnessScore + TrustScore) / 3 >= PromoteThreshold:
       - candidate → validated → promoted
       - Insert GovernanceTransition row
   
   Step 3: Demotion sweep
     - If (RecencyScore + UsefulnessScore) / 2 < DemoteThreshold OR TtlAt < NOW:
       - promoted → stale (or validated → stale)
       - Insert GovernanceTransition row
   
   Step 4: Archive sweep
     - If stale AND TtlAt < NOW - 7 days buffer:
       - stale → archived
       - Insert GovernanceTransition row
   
   Step 5: Tier migration
     - promoted records: ensure blob in vg-hot (C:); move from vg-warm if needed
     - stale records: ensure blob in vg-warm (E:); move from vg-hot if needed
     - archived records: ensure blob in vg-cold (D:); move from vg-warm if needed
   
   Step 6: Purge pass
     - Records where archived AND TtlAt < NOW (legal-hold class excluded):
       - Delete blob from SeaweedFS
       - NULL ContentRef, BlobHash on MemoryRecord
       - archived → purged transition
       - Append EventLedger row: Phase=Evolve, Outcome=completed, ArtifactRefs=[deleted key]
   ```
3. Each step writes audit rows to `GovernanceTransitions`.
4. Job run summary written to `EventLedger` as a synthetic `Evolve` phase event.

### Done when

- A test run with seeded records exercises all state transitions.
- Tier migration moves test blobs between hot/warm/cold paths on the correct drive.
- Purge correctly tombstones the SQL Server row and deletes the blob.

---

## Phase 7 — Auth Integration

**Goal**: Principals, Delegations, and PolicyEvidence wired to the L0–L6 model from `unified-auth-spec-v0.2.md`.

### Deliverables

1. All capture and retrieval operations require a `PrincipalId` in their request context.
2. `Delegations` table is consulted on every write: caller must have an active, non-revoked delegation for `domain:X action:memory.capture`.
3. `PolicyEvidence` is written for every Gate-phase event (risk score, HITL flag, decision receipt hash).
4. `Decision Receipt` hash chained through `EventLedger.ReceiptHash` — matches §3.8 of unified-auth-spec-v0.2.md.
5. HITL gate: if `RiskScore > threshold` on a capture or retrieval, mark `HitlRequired = 1` and suspend until `HitlCompletedAt` is populated.
6. Row-level security approach: enforced in the application layer (no SQL Server RLS for v0.1 per user preference), but every query includes `PrincipalId` filter or delegation check.

### Why RLS in app layer is acceptable for v0.1

- Agents operate as distinct `Principal` records in the `Principals` table.
- Every capture and retrieval caller supplies a `PrincipalId` from their delegation context.
- The app enforces it — no untrusted caller reaches the DB directly.
- SQL Server RLS can be added in v0.2 without schema changes if the team scales.

### Done when

- A call with an unknown or revoked `PrincipalId` is rejected before any DB write.
- A high-risk capture sets `HitlRequired = 1` and does not complete until approved.
- `PolicyEvidence` is populated for every Gate event with a valid `ReceiptHash`.

---

## Phase 8 — BitNet Orchestrator Integration

**Goal**: Local BitNet LLM wired to the retrieval API for memory-augmented orchestration and probabilistic next-step selection.

### Deliverables

1. New library: `PPA.Memory.Orchestration`
2. `IMemoryAugmentedOrchestrator` with:
   - `GroundedQueryAsync(prompt, domain, k)` → calls `RetrieveFast` → `RetrieveSlow` → assembles bounded evidence bundle → calls BitNet with bundle
   - `PredictNextPhaseAsync(workflowState)` → uses `EventLedger` history to predict next SRCGEEE phase
3. BitNet adapter: thin HTTP client to local BitNet inference endpoint.
4. Evidence bundle cap: max `k` records in the context, chosen by retrieval confidence ranking.
5. Confidence decomposition is passed back with every orchestrator response.

### Done when

- Orchestrator answers a grounded query using only memory evidence (no raw internet).
- `PredictNextPhase` returns a probability distribution over phases from recent `EventLedger` data.
- A workflow run with BitNet in the loop produces a complete 7-phase `EventLedger` trace with cost metadata in each `Payload`.

---

## Dependency Graph

```
Phase 1 (Schema)
    └── Phase 2 (Capture API)
            └── Phase 3 (SeaweedFS)
                    ├── Phase 4 (Retrieval API)
                    │       ├── Phase 5 (Embedding lane)
                    │       ├── Phase 6 (Gov job)
                    │       └── Phase 7 (Auth)
                    │               └── Phase 8 (BitNet orchestrator)
                    └── Phase 6 (Gov job) [also depends on Phase 2]
```

Phases 5, 6, and 7 can be developed in parallel once Phase 4 is solid.

---

## Recommended Start Point

**Start with Phase 1.** The schema is the skeleton everything else hangs on.

Order of first week:
1. Create `PPA.Memory.Data` project.
2. Write entity models for `MemoryRecords`, `EventLedger`, `Principals` first (the core triad).
3. Run first migration against local SQL Server Express.
4. Add remaining 8 tables.
5. Seed and validate.

Use the existing QuestionManager/Aspire project as the EF Core model reference — the patterns are already familiar.

---

## Open Items (not blocking Phase 1, but decide before Phase 2)

1. **Duplicate-capture policy**: new record per episode, or dedupe + new ledger event?
2. **Rollback anchor granularity**: workflow-step vs run-level.
3. **Snapshot scope**: full context window vs delta summary.
4. **Session purge behavior**: hard-delete at TTL or cold-tier move.
5. **EventLedger correction**: append correction event only vs append + `CorrectedBy` column.
