# SQL Server Express — Operational Agentic Memory Table List

**Workflow**: 012-operational-agentic-memory  
**Status**: Draft v0.1  
**Date**: 2026-03-16  
**Feeds**: memory-substrate-spec-v0.1.md, reference-contract.md  

---

## Overview

SQL Server Express is the **durable / governance / accountability store** for the PPA memory substrate.  
It handles everything that must be:  
- Transactionally safe (no lost events)
- Auditable (every write and state change is traceable)
- Query-able with relational joins (governance sweeps, drift analysis)
- Aligned to EF Core (existing QuestionManager/Aspire familiarity)

It does **not** store the artifact content itself — blobs, code, and docs live in SeaweedFS.  
SQL Server holds the **record, ledger, and policy envelope** that points to SeaweedFS objects.

---

## Table Inventory

| # | Table Name | Plane | Purpose | Volume Estimate |
|---|-----------|-------|---------|-----------------|
| 1 | `MemoryRecords` | All | Canonical record for each captured item | Medium (one row per artifact/event) |
| 2 | `EventLedger` | Governance / Assurance | Immutable SRCGEEE phase-boundary events | High (append-only, never updated) |
| 3 | `GovernanceTransitions` | Governance | State machine transitions for each record | Medium |
| 4 | `RetentionPolicies` | Governance | Domain-specific retention rules | Low (config-like) |
| 5 | `PolicyEvidence` | Assurance | Auth decisions, risk scores, HITL flags per action | Medium |
| 6 | `RollbackAnchors` | Assurance | Known-good workflow recovery points | Low |
| 7 | `AccessMetrics` | Retrieval / Governance | Recency, frequency, utility scores per record | High (updated on each access) |
| 8 | `Principals` | Auth | Human / Agent / Code principal registry | Low |
| 9 | `Delegations` | Auth | Scoped, time-boxed delegation grants | Low-Medium |
| 10 | `DomainProfiles` | Governance | Domain-specific memory configuration | Low (config-like) |
| 11 | `EmbeddingRefs` | Retrieval | Pointer to embedding vectors for each record | Medium |

---

## Table Definitions

### 1. MemoryRecords

The canonical record. One row per captured memory unit.  
Content lives in SeaweedFS; this row holds all metadata + references.

```sql
CREATE TABLE MemoryRecords (
    MemoryId         NVARCHAR(40)   NOT NULL PRIMARY KEY,   -- "mem_" + UUID/hash
    TenantId         NVARCHAR(50)   NOT NULL DEFAULT 'roadtrip',
    Domain           NVARCHAR(50)   NOT NULL,               -- engineering|ap|legal|sales|custom
    MemoryClass      NVARCHAR(30)   NOT NULL,               -- session|working|episodic|semantic|procedural|artifact|policy
    ArtifactKind     NVARCHAR(30)   NOT NULL,               -- code|doc|mcp|skill|log|plan|telemetry|binary
    Summary          NVARCHAR(500)  NOT NULL,               -- one-line human-readable description
    ContentRef       NVARCHAR(500)  NULL,                   -- seaweedfs://{bucket}/{key}
    BlobHash         NCHAR(64)      NULL,                   -- SHA-256 of blob content
    EmbeddingRef     NVARCHAR(500)  NULL,                   -- vec://{provider}/{id}
    Tags             NVARCHAR(MAX)  NULL,                   -- JSON array: ["srcgeee:retrieve","risk:medium"]
    TrustScore       DECIMAL(5,4)   NOT NULL DEFAULT 0.0,
    UsefulnessScore  DECIMAL(5,4)   NOT NULL DEFAULT 0.0,
    RecencyScore     DECIMAL(5,4)   NOT NULL DEFAULT 0.0,
    GovernanceState  NVARCHAR(20)   NOT NULL DEFAULT 'candidate',
                                                            -- candidate|validated|promoted|stale|archived|purged
    RetentionPolicy  NVARCHAR(20)   NOT NULL DEFAULT 'weekly',
    TtlAt            DATETIME2      NULL,
    PrincipalId      NVARCHAR(40)   NOT NULL,               -- FK → Principals.PrincipalId
    SourceFile       NVARCHAR(500)  NULL,
    SourceLineStart  INT            NULL,                   -- first line of cited content (citation-aware dedup)
    SourceLineEnd    INT            NULL,                   -- last line of cited content (inclusive)
    ProvHash         NCHAR(64)      NULL,                   -- SHA-256 of capture-time state for provenance
    CreatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_MemoryRecords_Domain         ON MemoryRecords (Domain);
CREATE INDEX IX_MemoryRecords_MemoryClass    ON MemoryRecords (MemoryClass);
CREATE INDEX IX_MemoryRecords_GovernanceState ON MemoryRecords (GovernanceState);
CREATE INDEX IX_MemoryRecords_TtlAt          ON MemoryRecords (TtlAt) WHERE TtlAt IS NOT NULL;
CREATE INDEX IX_MemoryRecords_PrincipalId    ON MemoryRecords (PrincipalId);
CREATE INDEX IX_MemoryRecords_DedupKey       ON MemoryRecords (BlobHash, SourceFile, SourceLineStart, SourceLineEnd)
    WHERE BlobHash IS NOT NULL;                            -- fast lookup for duplicate-capture check
```

**Notes**:
- `ContentRef` is the join key to SeaweedFS. See reference-contract.md.
- `Tags` is a denormalized JSON column for fast client-side filtering; no separate tag table at v0.1.
- `GovernanceState` is managed exclusively through `GovernanceTransitions` (FSM). Direct updates are not allowed outside the Governance API.
- **Dedup identity key**: `(BlobHash, SourceFile, SourceLineStart, SourceLineEnd)`. The Capture API checks this composite before inserting. A match means duplicate content at the same citation location. See Decision #9 in README.md.
- `SourceLineStart`/`SourceLineEnd` are NULL for artifacts that do not originate from a line-numbered source file (e.g. binary blobs, MCP tool outputs). For those, dedup falls back to hash-only.

---

### 2. EventLedger

Immutable append-only log of every SRCGEEE phase event.  
Rows are never updated or deleted (except by legal-hold purge with full audit).

```sql
CREATE TABLE EventLedger (
    EventId          NVARCHAR(40)   NOT NULL PRIMARY KEY,   -- "evt_" + UUID
    WorkflowRunId    NVARCHAR(40)   NOT NULL,               -- groups events within one SRCGEEE run
    Phase            NVARCHAR(20)   NOT NULL,               -- Sense|Retrieve|Compose|Gate|Execute|Evaluate|Evolve
    PhaseOutcome     NVARCHAR(20)   NOT NULL,               -- completed|skipped|failed|hitl-held
    PrincipalId      NVARCHAR(40)   NOT NULL,               -- FK → Principals.PrincipalId
    MemoryId         NVARCHAR(40)   NULL,                   -- FK → MemoryRecords.MemoryId (nullable: pre-capture)
    ArtifactRefs     NVARCHAR(MAX)  NULL,                   -- JSON array of seaweedfs:// keys
    Payload          NVARCHAR(MAX)  NULL,                   -- phase-specific metadata (JSON)
    PrevEventHash    NCHAR(64)      NULL,                   -- SHA-256 of previous row = hash chain
    EventHash        NCHAR(64)      NOT NULL,               -- SHA-256 of this row's canonical form
    OccurredAt       DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_EventLedger_WorkflowRunId  ON EventLedger (WorkflowRunId);
CREATE INDEX IX_EventLedger_Phase          ON EventLedger (Phase);
CREATE INDEX IX_EventLedger_PrincipalId    ON EventLedger (PrincipalId);
CREATE INDEX IX_EventLedger_OccurredAt     ON EventLedger (OccurredAt);
```

**Notes**:
- `PrevEventHash` + `EventHash` form a hash chain matching the Decision Receipt chain model in Unified Auth Spec v0.2 §3.8.
- `ArtifactRefs` stores SeaweedFS keys produced or consumed during the phase.
- `Payload` carries phase-specific data (query text, risk gate result, execution plan, eval scores).
- Emit events for all phases (`Sense` through `Evolve`) so triage and reward/cost accounting can be reconstructed deterministically.
- **`Phase = 'Capture'`** is a synthetic phase outside the SRCGEEE lifecycle used exclusively for duplicate-detection events. `PhaseOutcome = 'duplicate-detected'` means a record with the same dedup key already exists; `MemoryId` points at the surviving original. This event is logged and triggers an alert — it should not be a silent no-op.

---

### 3. GovernanceTransitions

Every state change for a MemoryRecord is recorded here.  
The current state is a projection of these transitions (last row per MemoryId).

```sql
CREATE TABLE GovernanceTransitions (
    TransitionId     NVARCHAR(40)   NOT NULL PRIMARY KEY,
    MemoryId         NVARCHAR(40)   NOT NULL,               -- FK → MemoryRecords.MemoryId
    FromState        NVARCHAR(20)   NOT NULL,
    ToState          NVARCHAR(20)   NOT NULL,
    Reason           NVARCHAR(200)  NOT NULL,               -- e.g. "daily-score-promote", "ttl-expire"
    TriggeredBy      NVARCHAR(50)   NOT NULL,               -- "daily-job"|"manual"|"api-call"|"policy-sweep"
    PrincipalId      NVARCHAR(40)   NOT NULL,
    OccurredAt       DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_GovTrans_MemoryId    ON GovernanceTransitions (MemoryId, OccurredAt DESC);
CREATE INDEX IX_GovTrans_TriggeredBy ON GovernanceTransitions (TriggeredBy);
```

**Valid state transitions** (FSM):
```
candidate  → validated     (pass classification checks)
candidate  → purged        (failed validation)
validated  → promoted      (scores exceed promotion threshold)
validated  → stale         (TTL or low scores)
promoted   → stale         (access drops below threshold)
stale      → archived      (retention sweep)
archived   → purged        (legal hold expired)
any        → archived      (manual governance action)
```

---

### 4. RetentionPolicies

Per-domain, per-memory-class retention configuration.  
These are looked up at capture time to set `TtlAt` on MemoryRecords.

```sql
CREATE TABLE RetentionPolicies (
    PolicyId         NVARCHAR(40)   NOT NULL PRIMARY KEY,
    Domain           NVARCHAR(50)   NOT NULL,
    MemoryClass      NVARCHAR(30)   NOT NULL,
    RetentionWindow  NVARCHAR(20)   NOT NULL,               -- daily|weekly|monthly|annual|legal-hold
    RetentionDays    INT            NOT NULL,               -- 1, 7, 30, 365, -1 (indefinite)
    PromoteThreshold DECIMAL(5,4)   NOT NULL DEFAULT 0.7,   -- min combined score to promote
    DemoteThreshold  DECIMAL(5,4)   NOT NULL DEFAULT 0.2,   -- max combined score before stale
    Description      NVARCHAR(500)  NULL,
    CreatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    UNIQUE (Domain, MemoryClass)
);
```

**Seed data (v0.1 defaults — approved)**:

| Domain | MemoryClass | Window | Days | Notes |
|--------|------------|--------|------|-------|
| * | session | daily | 7 | Session memory is short-lived |
| * | working | weekly | 30 | Active work context |
| * | episodic | monthly | 90 | Recent experiences |
| * | semantic | annual | 365 | Distilled knowledge |
| * | procedural | annual | 365 | Skills and workflows |
| * | artifact | monthly | 90 | Execution outputs |
| * | policy | legal-hold | -1 | Policy evidence never expires by default |

---

### 5. PolicyEvidence

One row per authorization decision tied to a memory capture or governance action.  
This is the Policy Evidence referenced in the Unified Auth Spec v0.2.

```sql
CREATE TABLE PolicyEvidence (
    EvidenceId       NVARCHAR(40)   NOT NULL PRIMARY KEY,
    MemoryId         NVARCHAR(40)   NOT NULL,               -- FK → MemoryRecords.MemoryId
    AuthDecisionId   NVARCHAR(40)   NOT NULL,               -- from PDP decision receipt
    PrincipalId      NVARCHAR(40)   NOT NULL,
    Action           NVARCHAR(100)  NOT NULL,               -- e.g. "memory.capture", "skill.execute"
    Resource         NVARCHAR(500)  NOT NULL,               -- resource URN or seaweedfs:// key
    Decision         NVARCHAR(10)   NOT NULL,               -- allow|deny|hitl
    RiskScore        INT            NOT NULL DEFAULT 0,     -- 0–100
    HitlRequired     BIT            NOT NULL DEFAULT 0,
    HitlCompletedAt  DATETIME2      NULL,
    HitlApprovedBy   NVARCHAR(40)   NULL,                   -- FK → Principals.PrincipalId
    ReceiptHash      NCHAR(64)      NOT NULL,               -- Decision Receipt SHA-256 (v0.2 §3.8)
    OccurredAt       DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_PolicyEvidence_MemoryId       ON PolicyEvidence (MemoryId);
CREATE INDEX IX_PolicyEvidence_AuthDecisionId ON PolicyEvidence (AuthDecisionId);
CREATE INDEX IX_PolicyEvidence_Decision       ON PolicyEvidence (Decision, RiskScore DESC);
```

---

### 6. RollbackAnchors

Workflow-run level recovery points.  
A rollback anchor records what was the known-good state of a workflow run at a snapshot moment.

```sql
CREATE TABLE RollbackAnchors (
    AnchorId         NVARCHAR(40)   NOT NULL PRIMARY KEY,
    WorkflowRunId    NVARCHAR(40)   NOT NULL,
    AnchorLabel      NVARCHAR(100)  NOT NULL,               -- e.g. "pre-execute", "post-gate"
    SnapshotRef      NVARCHAR(500)  NOT NULL,               -- seaweedfs://snapshots/{key}
    SnapshotHash     NCHAR(64)      NOT NULL,               -- SHA-256 of snapshot blob
    MemoryIds        NVARCHAR(MAX)  NOT NULL,               -- JSON array of MemoryRecord IDs in scope
    PrincipalId      NVARCHAR(40)   NOT NULL,
    CreatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_RollbackAnchors_WorkflowRunId ON RollbackAnchors (WorkflowRunId);
```

---

### 7. AccessMetrics

Access pattern tracking per MemoryRecord.  
Updated on every retrieval hit. Used by daily governance jobs to compute `UsefulnessScore` and `RecencyScore`.

```sql
CREATE TABLE AccessMetrics (
    MetricId         NVARCHAR(40)   NOT NULL PRIMARY KEY,
    MemoryId         NVARCHAR(40)   NOT NULL UNIQUE,        -- FK → MemoryRecords.MemoryId  (1:1)
    AccessCount      INT            NOT NULL DEFAULT 0,
    LastAccessedAt   DATETIME2      NULL,
    AccessCountD7    INT            NOT NULL DEFAULT 0,     -- rolling 7-day window
    AccessCountD30   INT            NOT NULL DEFAULT 0,     -- rolling 30-day window
    AvgRetrievalRank DECIMAL(5,2)   NULL,                   -- mean rank position when retrieved
    FeedbackPositive INT            NOT NULL DEFAULT 0,     -- explicit positive signals
    FeedbackNegative INT            NOT NULL DEFAULT 0,     -- explicit negative signals
    UpdatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_AccessMetrics_MemoryId       ON AccessMetrics (MemoryId);
CREATE INDEX IX_AccessMetrics_LastAccessedAt ON AccessMetrics (LastAccessedAt DESC);
```

---

### 8. Principals

Human / Agent / Code principal registry.  
Maps to the three principal types from Unified Auth Spec v0.2 §2.

```sql
CREATE TABLE Principals (
    PrincipalId      NVARCHAR(40)   NOT NULL PRIMARY KEY,  -- "human:|agent:|code:" + name/id
    PrincipalType    NVARCHAR(10)   NOT NULL,              -- human|agent|code
    Name             NVARCHAR(100)  NOT NULL,
    DisplayName      NVARCHAR(200)  NULL,
    TrustLevel       INT            NOT NULL DEFAULT 0,    -- 0=untrusted, 1=low, 2=medium, 3=high
    IsActive         BIT            NOT NULL DEFAULT 1,
    Metadata         NVARCHAR(MAX)  NULL,                  -- JSON: OIDC claims, version hash, etc.
    CreatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_Principals_PrincipalType ON Principals (PrincipalType);
```

**Example seed rows**:
```sql
INSERT INTO Principals VALUES ('human:bizcad',    'human', 'bizcad',         'Nick Stein',     3, 1, '{}', SYSUTCDATETIME(), SYSUTCDATETIME());
INSERT INTO Principals VALUES ('agent:orchestrator', 'agent', 'orchestrator', 'PPA Orchestrator', 2, 1, '{}', SYSUTCDATETIME(), SYSUTCDATETIME());
INSERT INTO Principals VALUES ('code:gpush-skill',   'code', 'gpush-skill',   'Git Push Skill',  1, 1, '{}', SYSUTCDATETIME(), SYSUTCDATETIME());
```

---

### 9. Delegations

Scoped, time-boxed grants matching the delegation model in Unified Auth Spec v0.2.

```sql
CREATE TABLE Delegations (
    DelegationId     NVARCHAR(40)   NOT NULL PRIMARY KEY,
    GrantorId        NVARCHAR(40)   NOT NULL,               -- FK → Principals.PrincipalId
    GranteeId        NVARCHAR(40)   NOT NULL,               -- FK → Principals.PrincipalId
    Scope            NVARCHAR(500)  NOT NULL,               -- e.g. "domain:engineering skill:gpush"
    MaxTrustLevel    INT            NOT NULL DEFAULT 1,
    ExpiresAt        DATETIME2      NOT NULL,
    IsRevoked        BIT            NOT NULL DEFAULT 0,
    RevokedAt        DATETIME2      NULL,
    RevokedBy        NVARCHAR(40)   NULL,
    Note             NVARCHAR(500)  NULL,
    CreatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_Delegations_GranteeId  ON Delegations (GranteeId, ExpiresAt);
CREATE INDEX IX_Delegations_GrantorId  ON Delegations (GrantorId);
```

---

### 10. DomainProfiles

Per-domain memory configuration controlling classifier behavior, embedding eligibility, and governance thresholds.

```sql
CREATE TABLE DomainProfiles (
    DomainId         NVARCHAR(50)   NOT NULL PRIMARY KEY,   -- engineering|ap|legal|sales|custom
    DisplayName      NVARCHAR(100)  NOT NULL,
    DefaultRetentionClass NVARCHAR(20) NOT NULL DEFAULT 'working',
    EmbeddingEnabled  BIT           NOT NULL DEFAULT 1,
    GraphEnabled      BIT           NOT NULL DEFAULT 0,     -- optional relationship expansion
    ClassifierHints   NVARCHAR(MAX) NULL,                   -- JSON hints to guide auto-classification
    IsActive          BIT           NOT NULL DEFAULT 1,
    CreatedAt         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
```

---

### 11. EmbeddingRefs

Lightweight pointer table that decouples the embedding store from the canonical record.  
Supports swapping embedding providers without touching MemoryRecords.

```sql
CREATE TABLE EmbeddingRefs (
    EmbeddingId      NVARCHAR(40)   NOT NULL PRIMARY KEY,
    MemoryId         NVARCHAR(40)   NOT NULL UNIQUE,        -- FK → MemoryRecords.MemoryId  (1:1)
    Provider         NVARCHAR(50)   NOT NULL,               -- e.g. "local-faiss"|"azure-aisearch"|"weaviate"
    VectorRef        NVARCHAR(500)  NOT NULL,               -- provider-specific ID or path
    ModelVersion     NVARCHAR(100)  NOT NULL,               -- embedding model used
    Dimensions       SMALLINT       NOT NULL,
    CreatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt        DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_EmbeddingRefs_Provider ON EmbeddingRefs (Provider);
```

---

## Entity Relationship Summary

```
Principals ──────────────────────┐
     │                           │
     │(1:N)                      │(1:N)
     ▼                           ▼
Delegations               EventLedger
                               │
                               │(N:1)
                               ▼
DomainProfiles ──(1:N)──► MemoryRecords ◄──(1:1)── AccessMetrics
                               │                └── (1:1)── EmbeddingRefs
                               │
                      ┌────────┴──────────┐
                      │                   │
                      ▼                   ▼
          GovernanceTransitions      PolicyEvidence
                      
RetentionPolicies ──(lookup)──► MemoryRecords.TtlAt

RollbackAnchors ──(N:1)──► EventLedger.WorkflowRunId
                ──(ref)──►  SeaweedFS snapshots bucket
```

---

## EF Core Model Notes

- All tables map to `[dbo]` for v0.1 simplicity.
- Use `ValueComparer` for JSON columns (`Tags`, `ArtifactRefs`, `MemoryIds`).
- `GovernanceState` is an enum-backed column; enforce only via `GovernanceTransitions`, not direct EF updates.
- `EventLedger` rows are insert-only — no `DbSet.Update()` or `DbSet.Remove()` calls allowed.
- Seed data for `RetentionPolicies` and `DomainProfiles` goes in `OnModelCreating` via `HasData`.

---

## Clarifications and Remaining Questions

### Definitions

1. **ContentRef**: the pointer in SQL Server (`MemoryRecords.ContentRef`) to the canonical SeaweedFS blob, for example `seaweedfs://ppa/docs/specs/2026-03/sha256-b9c1d4-mem_01HABC.md`.
2. **Duplicate capture**: when a newly captured blob computes the same `BlobHash` as an existing `MemoryRecord`, meaning the artifact bytes are identical even if captured in a different session.

### Decisions Already Made

1. Retention defaults (`7/30/90/365`) are accepted.
2. EventLedger tracks all SRCGEEE phases.
3. Schema prefix is `[dbo]` for v0.1.

### Remaining Questions

1. **Duplicate-capture policy**: new `MemoryRecord` per episode vs dedupe to existing record + new EventLedger event.
2. **RollbackAnchor granularity**: workflow-step level, run level, or deployment level.
