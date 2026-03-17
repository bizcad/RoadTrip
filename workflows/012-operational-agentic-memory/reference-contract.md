# Reference Contract: SQL Server ↔ SeaweedFS

**Workflow**: 012-operational-agentic-memory  
**Status**: Draft v0.1  
**Date**: 2026-03-16  
**Feeds**: sql-server-table-list.md, seaweedfs-artifact-map.md, memory-substrate-spec-v0.1.md  

---

## Purpose

This document defines the **join and reference contract** between the two storage tiers of the PPA memory substrate:

| Tier | Technology | Role |
|------|-----------|------|
| Durable / Governance | SQL Server Express | Metadata, ledger, state, policy, scores |
| Artifact / Blob | SeaweedFS | Content, code, docs, snapshots, telemetry |

The contract defines:
1. How SQL Server rows **point to** SeaweedFS objects (outbound references)
2. How SeaweedFS objects **identify themselves back to** SQL Server (inbound headers)
3. The **integrity guarantee** (hash-verified, not just pointer-referenced)
4. The **lifecycle contract** (who is authoritative for each transition)
5. The **resolution protocol** (how to hydrate a full record in retrieval)

---

## 1. Primary Reference Columns

The following SQL Server columns carry SeaweedFS references.

### 1.1 `MemoryRecords.ContentRef`

The canonical pointer from a memory record to its blob content.

**Format**:
```
seaweedfs://ppa/{bucket}/{subfolder}/{date}/{hash-prefix}-{memory-id}.{ext}
```

**Examples**:
```
seaweedfs://ppa/code/skills/2026-03/sha256-a3f7b2-mem_01HXYZ.py
seaweedfs://ppa/docs/specs/2026-03/sha256-b9c1d4-mem_01HABC.md
seaweedfs://ppa/artifacts/plans/2026-03/sha256-c2e1f8-mem_01HDEF.json
```

**Nullability**: Nullable. Not all memory records have a content blob. Examples of records without a `ContentRef`:
- Pure metadata summaries (semantic memory, distilled knowledge stored in the Summary field)
- Event records that carry their full payload in `EventLedger.Payload`

**Integrity**: `MemoryRecords.BlobHash` (SHA-256) MUST be verified on every deep retrieval. If the hash of the fetched blob does not match `BlobHash`, the record is flagged corrupt and escalated to the Governance API.

---

### 1.2 `MemoryRecords.BlobHash`

SHA-256 of the raw blob content at time of capture.  
Computed before writing to SeaweedFS. Stored in SQL Server.  
Verified before serving the blob to the LLM.

**Format**: Lowercase hex, no prefix: `a3f7b2c4d5e6f7...` (64 characters)

---

### 1.3 `MemoryRecords.EmbeddingRef`

Points to the embedding vector for this record.

**Format**: Depends on provider configuration.

| Provider | Format | Example |
|---------|--------|---------|
| Local FAISS (file) | `faiss://{index-path}/{vector-id}` | `faiss://data/embeddings/engineering/index.bin/000123` |
| SeaweedFS flat file | `seaweedfs://ppa/embeddings/flat/2026-03/{memory-id}.npy` | see below |
| Azure AI Search | `azureaisearch://{service}/{index}/{doc-id}` | `azureaisearch://ppa-search/memory-idx/mem_01HXYZ` |

The EmbeddingRef is also mirrored in `EmbeddingRefs.VectorRef` for cross-provider queries.

---

### 1.4 `EventLedger.ArtifactRefs`

JSON array of SeaweedFS keys produced or consumed during the logged SRCGEEE phase.

**Format**: JSON array of `ContentRef` strings.
```json
[
  "seaweedfs://ppa/artifacts/outputs/2026-03/sha256-c2e1f8-evt_01HPPP.json",
  "seaweedfs://ppa/code/patches/2026-03/sha256-d3f2a9-evt_01HPPP.patch"
]
```

**Purpose**: Allows an event to reference multiple artifacts without a separate join table.  
For auditors: the `ArtifactRefs` array is the definitive list of "what was touched" during a phase.

---

### 1.5 `RollbackAnchors.SnapshotRef` + `SnapshotHash`

Points to the compressed snapshot blob in SeaweedFS.

**Format**: `seaweedfs://ppa/snapshots/rollback/{date}/{hash-prefix}-{workflow-run-id}.tar.gz`

**Example**:
```
seaweedfs://ppa/snapshots/rollback/2026-03/sha256-e2f5a1-wfrun_01HQQ7.tar.gz
```

`SnapshotHash` is the SHA-256 of the `.tar.gz` blob — verified before rollback is applied.

---

## 2. Inbound Headers (SeaweedFS → SQL Server)

Every blob stored in SeaweedFS MUST carry these custom headers.  
These allow SeaweedFS-side discovery and tier migration without a SQL Server roundtrip.

| Header | SQL Server Column Mirrored | Purpose |
|--------|--------------------------|---------|
| `x-ppa-memory-id` | `MemoryRecords.MemoryId` | Reverse lookup from blob to record |
| `x-ppa-domain` | `MemoryRecords.Domain` | Tier migration filtering by domain |
| `x-ppa-artifact-kind` | `MemoryRecords.ArtifactKind` | Bucket validation and routing |
| `x-ppa-governance-state` | `MemoryRecords.GovernanceState` | Tier migration trigger |
| `x-ppa-principal` | `MemoryRecords.PrincipalId` | Ownership for purge authorization |
| `x-ppa-blob-hash` | `MemoryRecords.BlobHash` | Integrity self-check on read |

**Rule**: Headers are **written at upload time** (the same transaction that writes the SQL Server record). They are **never updated** after that — governance state changes are reflected by tier migration, not header mutation.

---

## 3. Integrity Guarantee

### 3.1 Capture-time guarantee

```
1. Compute SHA-256 of blob bytes → BlobHash
2. Write blob to SeaweedFS with x-ppa-blob-hash header
3. Write MemoryRecord to SQL Server with BlobHash = computed hash
   (within the same logical unit of work — use outbox pattern if needed)
4. If either write fails, mark record as candidate/failed and retry
```

### 3.2 Retrieval-time verification

```
1. Read MemoryRecord from SQL Server → extract ContentRef, BlobHash
2. Fetch blob from SeaweedFS by ContentRef
3. Compute SHA-256 of fetched bytes
4. If computed hash ≠ BlobHash → INTEGRITY VIOLATION
   - Do NOT serve blob to LLM
   - Log violation event to EventLedger (Phase: Evaluate, Outcome: failed)
   - Update GovernanceState to 'stale' (triggers re-validation or re-capture)
5. If hashes match → serve blob
```

### 3.3 Governance purge guarantee

```
1. GovernanceTransitions row created: ToState = 'purged'
2. EventLedger row created: Phase = Evolve, Outcome = completed, ArtifactRefs = [ContentRef]
3. DELETE blob from SeaweedFS
4. Update MemoryRecords.ContentRef = NULL, BlobHash = NULL
5. MemoryRecord row is retained (tombstone) with GovernanceState = 'purged'
6. EventLedger row is retained indefinitely
```

The tombstone pattern maintains audit continuity: we can always prove the record existed and was purged, even after the blob is gone.

---

## 4. Lifecycle Contract

**Authority table** — who is authoritative for each state change:

| Transition | Authoritative System | Triggered By |
|-----------|---------------------|-------------|
| Blob write | SeaweedFS | Capture API |
| `MemoryRecord` row create | SQL Server | Capture API |
| `ContentRef` set | SQL Server | Capture API (after blob write) |
| Tier migration (hot → warm) | SeaweedFS | Daily governance job |
| `GovernanceState` update | SQL Server | GovernanceTransitions insert |
| Blob tier change (warm → cold) | SeaweedFS | Weekly governance job |
| Blob delete | SeaweedFS | Purge job (after SQL Server purge record) |
| `ContentRef` NULL | SQL Server | Purge job (after blob delete confirmed) |
| Hash re-verification | Retrieval API | On every deep retrieval |

**Invariant**: SQL Server is always the source of truth for governance state. SeaweedFS is always the source of truth for blob content. Neither should be queried for the other's responsibility.

---

## 5. Resolution Protocol (Hydration)

When an agent requests deep retrieval, the full record is hydrated in this order:

```
Step 1 — Metadata      Read MemoryRecord from SQL Server
Step 2 — Policy        Read PolicyEvidence for this MemoryId
Step 3 — Scores        Read AccessMetrics for this MemoryId
Step 4 — ContentRef    Extract ContentRef from MemoryRecord
Step 5 — Blob Fetch    Fetch blob from SeaweedFS using ContentRef
Step 6 — Hash Verify   Verify fetched blob SHA-256 = MemoryRecord.BlobHash
Step 7 — Embedding     Optionally load embedding vector via EmbeddingRef
Step 8 — Assemble      Return: {metadata, policy_evidence, scores, blob, embedding}
```

**Short-circuit rules**:
- If `ContentRef` is NULL → skip Steps 4-6 (metadata-only record)
- If `GovernanceState` ∈ {archived, purged} → return 403 from retrieval unless caller has elevated auth
- If Step 6 fails (hash mismatch) → return error blob, do not serve stale content

---

## 6. ContentRef URI Resolution Table

Maps `ContentRef` URI scheme to storage backend:

| URI Scheme | Backend | Resolution |
|-----------|---------|-----------|
| `seaweedfs://ppa/...` | Local SeaweedFS | HTTP GET to SeaweedFS S3-compatible API |
| `s3://ppa-bucket/...` | S3-compatible (future) | AWS/Azure Blob S3 adapter |
| `faiss://...` | Local FAISS index | Read from local embedding index file |
| `azureaisearch://...` | Azure AI Search | REST API call to Azure AI Search |
| `vec://local/...` | Local vector file | Read `.npy` or `.bin` from disk |

The Retrieval API resolves the URI scheme to the correct backend adapter.  
Adding a new backend = adding a new URI scheme + adapter, not changing existing records.

---

## 7. Dependency Graph

```
[Capture Event]
       │
       ├─► Write blob → SeaweedFS (gets FID/path)
       │       │
       │       └─► ContentRef URI assembled from path
       │
       ├─► Compute BlobHash (SHA-256 of blob bytes)
       │
       ├─► Write MemoryRecord → SQL Server
       │       ├── ContentRef = seaweedfs://...
       │       ├── BlobHash = sha256:...
       │       └── EmbeddingRef = (set after embedding job)
       │
       └─► Write EventLedger row → SQL Server
               ├── ArtifactRefs = [ContentRef]
               └── PrevEventHash = hash of last ledger row

[Retrieval Event]
       │
       ├─► Read MemoryRecord → SQL Server (ContentRef, BlobHash)
       ├─► Fetch blob → SeaweedFS (ContentRef)
       ├─► Verify hash (BlobHash)
       └─► Log access → AccessMetrics (SQL Server)

[Governance Sweep]
       │
       ├─► Read MemoryRecords + AccessMetrics → SQL Server
       ├─► Compute new scores
       ├─► Insert GovernanceTransitions rows
       ├─► Update MemoryRecords.GovernanceState
       └─► If state = stale/archived → tier migrate blob → SeaweedFS
```

---

## 8. Anti-Patterns (Do Not Do)

| ❌ Anti-Pattern | ✅ Correct Pattern |
|-----------------|------------------|
| Store blob content in SQL Server VARBINARY | Store in SeaweedFS, store ContentRef in SQL Server |
| Update EventLedger rows | EventLedger is append-only. Create correction events instead. |
| Trust SeaweedFS headers as authoritative governance state | SQL Server GovernanceState is authoritative. Headers are cache/hint only. |
| Delete MemoryRecord on purge | Retain tombstone row. Only delete blob and NULL ContentRef. |
| Generate ContentRef before blob write succeeds | Always write blob first, then assemble ContentRef from the confirmed path. |
| Skip hash verify on deep retrieval | Always verify BlobHash. Corrupted blobs must never reach the LLM. |

---

## Open Questions (for clarification)

1. **EventLedger correction pattern**: If a ledger row is recorded with wrong metadata, what's the canonical correction pattern? Options: (a) append a correction event with the same WorkflowRunId, (b) add a `CorrectedBy` column pointing to the correction event.

## Decisions Applied

1. Transactional consistency baseline is intent-first outbox pattern (SQL intent row first, async blob write + confirm).
2. Canonical `ContentRef` URI scheme is `seaweedfs://ppa/...`.
3. Embedding generation is asynchronous; `EmbeddingRef` may be NULL until embedding worker completion.
