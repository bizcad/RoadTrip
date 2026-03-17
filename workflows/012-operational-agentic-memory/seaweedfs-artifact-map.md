# SeaweedFS Artifact Map

**Workflow**: 012-operational-agentic-memory  
**Status**: Draft v0.1  
**Date**: 2026-03-16  
**Feeds**: memory-substrate-spec-v0.1.md, reference-contract.md  

---

## Overview

SeaweedFS is the **canonical artifact substrate** for the PPA memory system.  
It stores all binary and large content that would be expensive or wrong to put in SQL Server Express:

- Code blobs, skills, scripts
- Documents, specs, transcripts
- Execution outputs, plans
- Workflow snapshots for rollback
- Session logs and telemetry exports
- MCP manifests and configuration artifacts
- Embeddings (if stored on disk rather than in an external vector DB)

SeaweedFS gives us:
- **O(1) key-blob access** via FID (File ID)
- **Multi-tier storage**: hot (SSD) → warm (HDD) → cold (archive)
- **S3-compatible API** for tooling interop
- **Replication** configurable per volume group
- **CockroachDB parser** for future migration path

Every artifact stored in SeaweedFS has a corresponding row in `MemoryRecords` (SQL Server) that holds the metadata, governance state, and reference pointer back to SeaweedFS.

Baseline deployment for v0.1 is local-only storage (no LAN NAS target).

---

## Bucket Structure

SeaweedFS organizes content by **logical bucket** (collection in SeaweedFS terms).  
All paths below are logical — SeaweedFS maps them internally to volume/FID addresses.

```
seaweedfs://ppa/
├── code/
│   ├── skills/         Skills (.py, .json, SKILL.md, CLAUDE.md)
│   ├── scripts/        Utility scripts (.py, .ps1)
│   ├── tools/          MCP server scripts and tools
│   └── patches/        Code diffs and patch artifacts from agent-generated changes
│
├── docs/
│   ├── specs/          Architecture specs, PRDs, ADRs, design docs
│   ├── transcripts/    Conversation transcripts, session exports
│   ├── research/       Research notes, Perplexity exports, literature summaries
│   └── reports/        Completion reports, phase reports, evaluation summaries
│
├── artifacts/
│   ├── plans/          Agent-generated execution plans (JSON/YAML)
│   ├── outputs/        Execution results, command outputs, LLM completions
│   ├── evaluations/    Evaluation runs, score exports, benchmarks
│   └── proposals/      Draft conclusions, recommendations before HITL gate
│
├── sessions/
│   ├── logs/           Session log files (.md, .jsonl)
│   ├── snapshots/      Context window dumps at phase boundaries
│   └── ppa-events/     Raw SRCGEEE event payloads (pre-ledger format)
│
├── telemetry/
│   ├── metrics/        Metric exports (JSON, Prometheus format)
│   ├── traces/         Distributed traces (OTLP format)
│   └── audit/          Audit trail exports (for cross-system archival)
│
├── mcp/
│   ├── manifests/      MCP server manifest files
│   ├── configs/        MCP runtime configuration
│   └── results/        MCP tool call output artifacts
│
├── snapshots/
│   └── rollback/       Workflow rollback blobs (referenced by RollbackAnchors table)
│
└── embeddings/         (optional — if using local file-backed vector store)
    ├── flat/           Flat embedding files (.npy, .bin)
    └── index/          FAISS or similar index files
```

---

## Artifact Taxonomy

Each stored artifact maps to an `ArtifactKind` value from the Canonical Memory Record.

| ArtifactKind | Buckets Used | File Types | Description |
|-------------|-------------|-----------|-------------|
| `code` | `code/skills/`, `code/scripts/`, `code/tools/` | .py, .ps1, .js, .sh | Executable code produced or consumed by agents |
| `doc` | `docs/specs/`, `docs/research/`, `docs/reports/` | .md, .txt, .pdf | Documentation, specs, research notes |
| `mcp` | `mcp/manifests/`, `mcp/configs/`, `mcp/results/` | .json, .yaml | MCP server configs and tool output artifacts |
| `skill` | `code/skills/` | .md, .py, .json | Skill definition packages (SKILL.md + supporting code) |
| `log` | `sessions/logs/`, `telemetry/audit/` | .md, .jsonl | Session logs and audit trail exports |
| `plan` | `artifacts/plans/` | .json, .yaml, .md | Agent-generated execution plans |
| `telemetry` | `telemetry/metrics/`, `telemetry/traces/` | .json, .otlp | Metrics, traces, and telemetry exports |
| `binary` | `artifacts/outputs/`, `embeddings/` | .bin, .npy, .index | Compiled artifacts, embedding blobs, index files |
| `transcript` | `docs/transcripts/`, `sessions/logs/` | .md, .txt | Conversation exports and session transcripts |
| `snapshot` | `snapshots/rollback/`, `sessions/snapshots/` | .json, .tar.gz | Workflow and context window snapshots |

---

## Key Naming Convention

All SeaweedFS keys follow a deterministic, collision-resistant naming scheme.

### Format

```
{bucket}/{subfolder}/{date}/{content-hash-prefix}-{short-id}.{ext}
```

### Examples

```
code/skills/2026-03/sha256-a3f7b2-mem_01HXYZ.py
docs/specs/2026-03/sha256-b9c1d4-mem_01HABC.md
snapshots/rollback/2026-03/sha256-e2f5a1-wfrun_01HQQ7.tar.gz
sessions/logs/2026-03/sha256-c8d3e9-evt_01HPPP.jsonl
```

### Rules

1. Use UTC date prefix (`YYYY-MM`) for partition-friendliness.
2. Hash prefix is the first 6 hex characters of the blob SHA-256.
3. Short ID is the `MemoryId` or `WorkflowRunId` from SQL Server (strip the `mem_`/`wfrun_` prefix in the path for brevity, but document the mapping in `ContentRef`).
4. Extension matches the actual content type.
5. No spaces in paths. Use hyphen as separator.

---

## Volume Groups and Tiering

### Local Drive Assignment (v0.1 — confirmed March 2026)

| Tier | Drive | Label | Type | Free | Path | Notes |
|------|-------|-------|------|------|------|-------|
| **Hot** | `C:` | (system) | SSD (WD Black SN850X) | ~841 GB | `C:\SeaweedFS\hot` | Fastest internal SSD; not a backup target |
| **Warm** | `E:` | BigDrive | HDD 18 TB (WD Purple) | ~3.6 TB | `E:\SeaweedFS\warm` | Primary operational blob store; not a backup target |
| **Cold** | `D:` | Gold | HDD 14 TB (WD Gold) | ~8.3 TB | `D:\SeaweedFS\cold` | Archive tier; co-located with `D:\Backup` (repo backups) |
| **Off-limits** | `H:` | Fast Backup | SSD | — | — | Macrium Reflect nightly system backup — do not allocate |
| **Off-limits** | `I:` | ArmorATD | USB 3.1 SSD | — | — | Detachable backup of H:; unreliable for operational storage |
| **Off-limits** | `G:` | DevDrive | ReFS SSD | ~51 GB | — | Repos and active dev — too small, in constant use |

### Volume Groups

| Tier | Volume Group | Storage Type | GovernanceState trigger | Use |
|------|-------------|-------------|------------------------|-----|
| Hot | `vg-hot` | SSD (C:) | `validated` / `promoted` | Fast retrieval, active sessions, embedding index |
| Warm | `vg-warm` | HDD (E:) | `stale` + sessions > 30 days | Main blob store, background retrieval, governance sweeps |
| Cold | `vg-cold` | HDD (D:) | `archived` | Legal hold, rollback archives, audit blobs |

**Replication**:
- Hot: replication factor 1 for local dev (add a second copy to `vg-warm` if durability matters)
- Warm: replication factor 1
- Cold: replication factor 1

**Tiering triggers** (automated) — align with GovernanceTransitions:
- `promoted` → `vg-hot`
- `stale` → `vg-warm`
- `archived` → `vg-cold`
- `purged` → delete command issued (with DELETE receipt logged in EventLedger)

---

## Blob Lifecycle

```
Capture
  │
  ▼
[write blob to SeaweedFS hot tier]
  │
  ├──► ContentRef URI is written to MemoryRecords.ContentRef
  ├──► BlobHash (SHA-256) is written to MemoryRecords.BlobHash
  └──► ArtifactRefs array in EventLedger entry for Sense/Capture phase
  │
  ▼
[On governance state → stale]
  └──► Move blob from vg-hot to vg-warm (SeaweedFS tier migration API)
  │
  ▼
[On governance state → archived]
  └──► Move blob from vg-warm to vg-cold
  │
  ▼
[On governance state → purged]
  └──► Delete blob from SeaweedFS
  └──► Record DELETE event in EventLedger (retain the ledger row, not the blob)
```

---

## Metadata Stored with Each Blob (SeaweedFS Custom Headers)

SeaweedFS supports custom headers per object. Use these for fast lookup without hitting SQL Server.

| Header Key | Value | Example |
|-----------|-------|---------|
| `x-ppa-memory-id` | MemoryId from SQL Server | `mem_01HXYZ` |
| `x-ppa-domain` | Domain | `engineering` |
| `x-ppa-artifact-kind` | ArtifactKind | `code` |
| `x-ppa-governance-state` | Current GovernanceState | `promoted` |
| `x-ppa-principal` | PrincipalId | `agent:orchestrator` |
| `x-ppa-blob-hash` | SHA-256 of content | `sha256:a3f7b2...` |

These headers allow SeaweedFS-side searches and migrations without round-tripping to SQL Server.

---

## Access Patterns

| Operation | SQL Server role | SeaweedFS role |
|----------|----------------|----------------|
| **Capture** | Write MemoryRecord + EventLedger row | Write blob |
| **Fast retrieval** (metadata) | Query MemoryRecords by domain/class/tags | No access needed |
| **Slow retrieval** (rerank) | Read MemoryRecords candidates | No access needed (use embedding ref) |
| **Deep retrieval** (hydrate) | Read MemoryRecord for ContentRef | Fetch blob by ContentRef |
| **Governance sweep** | Read/update GovernanceState | Move blob between tiers |
| **Rollback** | Read RollbackAnchors.SnapshotRef | Fetch snapshot blob |
| **Purge** | Update GovernanceState → purged | Delete blob |
| **Audit export** | Read EventLedger | Read audit blobs from telemetry/audit/ |

---

## SRCGEEE Phase → Bucket Mapping

Which buckets are written during each SRCGEEE phase:

| Phase | Bucket(s) Written | Notes |
|-------|------------------|-------|
| Sense | `sessions/ppa-events/` | Raw event payload before classification |
| Retrieve | `sessions/snapshots/` (optional) | Context snapshot if latency budget allows |
| Compose | `artifacts/proposals/` | Draft plan before Gate |
| Gate | `artifacts/plans/` | Approved execution plan after HITL |
| Execute | `artifacts/outputs/`, `code/patches/` | Execution results and code changes |
| Evaluate | `artifacts/evaluations/` | Evaluation scores and recommendations |
| Evolve | `code/skills/`, `docs/specs/` | Updated artifacts from learning loop |

---

## Open Questions (for clarification)

1. **Embedding storage**: Should embeddings be stored in SeaweedFS (`embeddings/` bucket) or in a separate local FAISS index directory outside SeaweedFS? SeaweedFS adds durability; local FAISS is faster but not replicated.
2. **Snapshots granularity**: Should `sessions/snapshots/` capture the full context window (can be large) or only a delta summary? Full context = easier rollback; delta = smaller storage footprint.
3. **Sessions bucket retention**: Session logs are short-lived (`session` memory class = 7 days default). Should the blob be deleted from SeaweedFS on purge, or moved to `vg-cold` for legal-hold compliance?

## Decisions Applied

1. SeaweedFS hosting is local-only for v0.1 (dev machine disks).
2. Canonical `ContentRef` URI scheme is `seaweedfs://ppa/...`.
