# Workflow 012 — Operational Agentic Memory

**Status**: Active  
**Date Started**: 2026-03-16  
**Supersedes**: `workflows/010-memory-for-self-improvement` (abandoned)  
**Primary Spec**: `analysis/ppa/memory-substrate-spec-v0.1.md`  
**Auth Dependency**: `analysis/unified-auth/ClaudeCode/unified-auth-spec-v0.2.md`  

---

## Why This Workflow Exists

Workflow 010 (`memory-for-self-improvement`) was abandoned in favor of this approach.

**010's approach**: Constrain agents through rules to achieve self-improvement.  
**012's approach**: Give agents a proper substrate — structured capture, retrieval, governance, and policy gates — through which self-improvement emerges naturally via operational completions rather than prescribed constraints.

Key insight: agents improve when they have reliable memory of what worked and what didn't, combined with deterministic gates (not rules) controlling what gets persisted and acted on. The constraint-based model was a ceiling; the substrate model is a foundation.

---

## Goal

Define and document the **operational memory substrate** for PPA agents:

1. What gets stored and where (SQL Server Express vs SeaweedFS)
2. How artifacts are referenced and retrieved
3. How governance and assurance policies are enforced
4. How this foundation enables the agentic workflow from `unified-auth-spec-v0.2.md`

This is the **infrastructure layer** that everything else (agentic workflows, skill execution, HITL gates, evaluation loops) depends on.

---

## Technology Choices

### SQL Server Express (Durable / Governance tier)

- **Why**: Already owned, EF-familiar from QuestionManager/Aspire project, free, transactional, relational joins for governance sweeps
- **Role**: Records, ledger, state machines, policy evidence, scores, rollback anchors
- **Does NOT store**: Blob content, large docs, code files

### SeaweedFS (Artifact / Blob tier)

- **Why**: O(1) key-blob access, multi-tier (hot/warm/cold), S3-compatible, replication, CockroachDB parser for future migration
- **Role**: All content — code, docs, transcripts, plans, telemetry, embeddings, snapshots
- **Does NOT store**: Metadata, governance state, scores

### Future / Optional

- **CockroachDB**: Replaces SQL Server Express for cloud-scale or team-scale deployment (Option B)
- **AWS managed stack**: Future adapter option (Option C) if Azure-first local stack needs cloud burst

---

## Documents in This Workflow

| Document | Purpose | Status |
|----------|---------|--------|
| [sql-server-table-list.md](sql-server-table-list.md) | All 11 SQL Server tables with column definitions, indexes, ER map | Draft v0.1 |
| [seaweedfs-artifact-map.md](seaweedfs-artifact-map.md) | Bucket structure, artifact taxonomy, key naming, tier migration, drive assignment, SRCGEEE phase mapping | Draft v0.1 |
| [reference-contract.md](reference-contract.md) | Join and reference contract between SQL Server and SeaweedFS, including integrity guarantee, lifecycle contract, hydration protocol | Draft v0.1 |
| [impl-plan-v0.1.md](impl-plan-v0.1.md) | 8-phase implementation plan: schema → capture → blobs → retrieval → embeddings → governance → auth → BitNet | Draft v0.1 |

---

## Architecture in One Picture

```
                        ┌───────────────────────────────────────────────────┐
                        │                  PPA ORCHESTRATOR                 │
                        │  (BitNet local LLM: prediction + memory search)   │
                        └───────────────────────────┬───────────────────────┘
                                                    │ SRCGEEE lifecycle
                                         ┌──────────▼──────────┐
                                         │    MEMORY SUBSTRATE  │
                                         └────────┬─────────────┘
                                                  │
                  ┌───────────────────────────────┼────────────────────────────────┐
                  │                               │                                │
         ┌────────▼────────┐           ┌──────────▼──────────┐        ┌───────────▼────────┐
         │  SQL Server      │           │     SeaweedFS        │        │  Embedding Index   │
         │  Express         │           │     (S3-compatible)  │        │  (FAISS / local)   │
         │                  │           │                      │        │                    │
         │ MemoryRecords     │◄──────────┤ ContentRef pointer   │        │ EmbeddingRef vec   │
         │ EventLedger       │           │ Blob hash verify     │        │ (retrieveSlow)     │
         │ GovernanceState   │           │ Tier migration       │        └────────────────────┘
         │ PolicyEvidence    │           │ Snapshot blobs       │
         │ RollbackAnchors   │           │ Session logs         │
         │ AccessMetrics     │           │ Code artifacts       │
         │ Principals        │           │ Plans & outputs      │
         │ Delegations       │           │ Telemetry exports    │
         └──────────────────┘           └──────────────────────┘
                  │
                  └── Auth layer: unified-auth-spec-v0.2.md (L0-L6)
                      - Principal registry (Principals table)
                      - Delegation grants (Delegations table)
                      - Policy evidence (PolicyEvidence table)
                      - Decision receipts (EventLedger + ReceiptHash)
```

---

## SRCGEEE Alignment

| Phase | SQL Server writes | SeaweedFS writes |
|-------|------------------|-----------------|
| **Sense** | EventLedger (phase = Sense) | `sessions/ppa-events/` raw payload |
| **Retrieve** | AccessMetrics updated | `sessions/snapshots/` (optional) |
| **Compose** | EventLedger (phase = Compose) | `artifacts/proposals/` draft plan |
| **Gate** | PolicyEvidence, EventLedger (phase = Gate) | `artifacts/plans/` approved plan |
| **Execute** | EventLedger (phase = Execute) | `artifacts/outputs/`, `code/patches/` |
| **Evaluate** | GovernanceTransitions, AccessMetrics | `artifacts/evaluations/` |
| **Evolve** | MemoryRecords updated/promoted | `code/skills/`, `docs/specs/` |

---

## Governance State Machine

```
    ┌──────────────┐
    │  candidate   │◄── New capture
    └──────┬───────┘
           │ passes classification checks
           ▼
    ┌──────────────┐
    │  validated   │
    └──────┬───────┘
           │ scores exceed promote threshold
           ▼
    ┌──────────────┐
    │   promoted   │◄──────────────┐
    └──────┬───────┘               │
           │ access drops          │ re-validate
           ▼                       │
    ┌──────────────┐               │
    │    stale     │───────────────┘ (if scores recover)
    └──────┬───────┘
           │ retention sweep
           ▼
    ┌──────────────┐
    │   archived   │
    └──────┬───────┘
           │ legal hold expired
           ▼
    ┌──────────────┐
    │    purged    │  (blob deleted, tombstone retained)
    └──────────────┘
```

---

## Phased Implementation Plan (Sketch)

| Phase | Deliverable | Dependencies |
|-------|------------|-------------|
| **1 — Schema** | EF Core models for all 11 tables, migrations, seed data | SQL Server Express local instance |
| **2 — Capture API** | `captureEvent()`, `captureArtifact()`, classifier stub | Phase 1 |
| **3 — SeaweedFS integration** | Blob write, ContentRef assembly, BlobHash verification | SeaweedFS running locally |
| **4 — Retrieval API** | `retrieveFast()`, `retrieveSlow()`, `retrieveDeep()` with hash verify | Phases 2-3 |
| **5 — Embedding lane** | Local FAISS integration, EmbeddingRefs table, `retrieveSlow` rerank | Phase 3 |
| **6 — Daily governance job** | Score recompute, GovernanceTransitions, tier migration | Phases 2-5 |
| **7 — Auth integration** | Principals, Delegations, PolicyEvidence wired to unified-auth-spec-v0.2.md L0-L6 | Phase 4 |
| **8 — BitNet integration** | Orchestrator memory search wired to retrieval API | Phase 4 |

---

## Decision Log (Confirmed)

The following decisions are now baseline for Workflow 012:

1. **Retention defaults approved**: `7/30/90/365` seeds are accepted for v0.1.
2. **EventLedger granularity**: track **all SRCGEEE phases** (`Sense`, `Retrieve`, `Compose`, `Gate`, `Execute`, `Evaluate`, `Evolve`) so self-improvement, triage, and reward/cost accounting have complete evidence.
3. **SeaweedFS hosting**: local machine only (no LAN NAS target currently).
4. **ContentRef URI**: use `seaweedfs://ppa/...` as canonical v0.1 scheme.
5. **Embedding timing**: async embedding generation; `EmbeddingRef` may be NULL until job completion.
6. **Write consistency**: intent-first outbox pattern preferred over ad hoc eventual consistency.
7. **Schema prefix**: use flat `[dbo]` for v0.1 simplicity.
8. **Project isolation**: the executable PPA app lives outside RoadTrip at `G:\repos\AI\PPA`. `PPA.Memory.Data` and sibling libraries are standalone .NET class libraries within that app. They are NOT added to the Aspire/QuestionManager solution, which is a live production app. RoadTrip remains the developer workspace and planning surface for now; the PPA runtime is a separate application.
9. **Duplicate capture identity key**: `(BlobHash, SourceFile, SourceLineStart, SourceLineEnd)`. If all four match an existing `MemoryRecord`, the capture is a duplicate — add an `EventLedger` row with `Phase = 'Capture', PhaseOutcome = 'duplicate-detected'` pointing at the existing record, emit an alert, return the existing `MemoryId`, and create no new record. If the hash matches but the citation (file or line range) differs, create a new `MemoryRecord` — different citation = different identity. Formatting variants (plain text vs Markdown) produce different hashes and are handled as distinct records; preventing those from arriving is the caller's responsibility.
10. **Separation of duties**: orchestrator, executor, triage, evaluator, tester, and agent-factory responsibilities are split into separate projects/services. Agent creation is not part of the orchestrator or task runner. Any future agent creation by PPA must remain behind explicit authorization and RBAC/HITL controls.

## Remaining Clarifications

1. **Rollback granularity**: workflow-step, run-level (current), or deployment-level anchors?
2. **Snapshot scope**: full context snapshot vs delta summary for `sessions/snapshots/`.
3. **Embedding storage location**: keep vectors in local FAISS outside SeaweedFS or store embedding files inside `seaweedfs://ppa/embeddings/` for durability.
4. **Session purge behavior**: hard-delete session blobs at TTL or move to cold tier for audit/legal hold.
5. **EventLedger correction pattern**: append correction event only, or append + explicit `CorrectedBy` link.

---

## Related Files

| File | Relationship |
|------|-------------|
| `analysis/ppa/memory-substrate-spec-v0.1.md` | Parent spec — this workflow implements it |
| `analysis/ppa/ppa_approach_summary.json` | Index of all PPA architectural directions |
| `analysis/unified-auth/ClaudeCode/unified-auth-spec-v0.2.md` | Auth layer this substrate serves |
| `G:\repos\AI\PPA\PPA.App.slnx` | Standalone executable PPA application root |
| `workflows/010-memory-for-self-improvement/` | Abandoned predecessor — reference for what was tried |
| `skills/telemetry-logger/CLAUDE.md` | Phase 2 placeholder for QuestionManager/Aspire integration |
| `config/telemetry-config.yaml` | Telemetry config with Aspire integration hook |
