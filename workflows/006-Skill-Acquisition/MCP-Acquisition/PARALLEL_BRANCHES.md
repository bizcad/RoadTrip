# Parallel Development Branches - Strategy

**Date Created**: February 14, 2026  
**Base Commit**: `00db3e8` (MCP acquisition infrastructure complete)  
**Status**: Ready for parallel implementation  

---

## Three Parallel Tracks

### 1️⃣ `feature/mcp-acquisition`
**Purpose**: MCP discovery, processing, and integration  
**Timeline**: Feb 14 - Mar 31 (6 phases, 5 weeks)  
**Owner**: MCP Acquisition (Phase 1-6)  
**What**: 
- Week 1: Registry discovery (RegistryClient)
- Week 2-3: MCP introspection (Inspector, SchemaExtractor)
- Week 3: Schema design (SQLite)
- Week 4: Catalog builder & conversion (CatalogBuilder, MCPToSkillConverter, Validator)
- Week 5: Runtime integration (ClientAdapter, TransportHandler, etc.)

**Code Created**:
- `src/mcp/discovery/*.py` (Phase 1-3)
- `src/mcp/processing/*.py` (Phase 4-5)
- `src/mcp/interactions/*.py` (Phase 6)
- `workflows/006-Skill-Acquisition/MCP-Acquisition/` (planning + outputs)

**Merges Back**: Mar 31 → main

---

### 2️⃣ `feature/batch-1-utilities`
**Purpose**: First batch of utility skills (CSV, YAML, JSON, File operations)  
**Timeline**: Feb 21 - Mar 10 (utility skill implementations)  
**Owner**: Skill Acquisition Batch 1  
**What**:
- CSV reader/writer skills
- YAML reader/writer skills
- JSON reader/writer skills
- File reader/writer skills
- 8 skills total, homogeneous patterns

**Code Created**:
- `src/skills/utilities/` (8 skill implementations)
- `tests/skills/utilities/` (comprehensive test suite)
- Templates for batch 2-4 skills

**Merges Back**: Mar 10 → main

---

### 3️⃣ `feature/phase-1b-metrics`
**Purpose**: ExecutionMetrics collection foundation  
**Timeline**: Feb 14 - Mar 10 (Phase 1b infrastructure)  
**Owner**: Self-Improvement Infrastructure (Phase 1b)  
**What**:
- ExecutionMetrics dataclass
- Telemetry logger
- Metrics collection (success, latency, cost)
- Orchestrator integration
- Metrics storage backend

**Code Created**:
- `src/orchestrator/metrics/` (metrics classes)
- `src/orchestrator/telemetry/` (logging & storage)
- `tests/orchestrator/` (integration tests)

**Merges Back**: Mar 10 → main

---

## Schedule

### Week 1 (Feb 14-20)
```
main (NO CHANGES)
  ├─ feature/mcp-acquisition → Week 1 implementation
  │  └─ RegistryClient, models.py
  ├─ feature/batch-1-utilities → Preparation
  │  └─ Design & scaffold
  └─ feature/phase-1b-metrics → Week 1 implementation
     └─ ExecutionMetrics dataclass
```

### Week 2 (Feb 21-27)
```
main (NO CHANGES)
  ├─ feature/mcp-acquisition → Phase 2 (Introspection)
  │  └─ MCPInspector, SchemaExtractor
  ├─ feature/batch-1-utilities → Week 2 implementation
  │  └─ CSV, YAML skills coding
  └─ feature/phase-1b-metrics → Week 2 implementation
     └─ Telemetry logger, metrics storage
```

### Week 3 (Feb 28-Mar 6)
```
main (NO CHANGES)
  ├─ feature/mcp-acquisition → Phase 3 (Schema Design)
  │  └─ SQLite schema
  ├─ feature/batch-1-utilities → Testing
  │  └─ Unit & integration tests
  └─ feature/phase-1b-metrics → Testing
     └─ End-to-end metrics collection
```

### Week 4 (Mar 7-13)
```
main (push 1)
  ├─ feature/batch-1-utilities → READY
  │  └─ MERGE to main (Mar 10) ✅
  ├─ feature/phase-1b-metrics → READY
  │  └─ MERGE to main (Mar 10) ✅
  └─ feature/mcp-acquisition → Phase 4 (Implementation)
     └─ CatalogBuilder, conversion
```

### Week 5 (Mar 14-20)
```
main (push 2)
  └─ feature/mcp-acquisition → Phase 5-6
     ├─ Runtime integration
     ├─ Documentation
     └─ READY to merge (Mar 31)
```

### Final (Mar 31)
```
main (push 3)
  ├─ feature/batch-1-utilities → MERGED ✅
  ├─ feature/phase-1b-metrics → MERGED ✅
  └─ feature/mcp-acquisition → MERGE complete (Mar 31) ✅
```

---

## Merge Strategy

### Branch Merge Order
1. **Mar 10**: `feature/batch-1-utilities` → main
   - 8 skills complete, tested, independent
   
2. **Mar 10**: `feature/phase-1b-metrics` → main
   - ExecutionMetrics foundation ready, independent

3. **Mar 31**: `feature/mcp-acquisition` → main
   - Full MCP system complete, integrates with above

### Merge Process
Each merge will:
1. Create pull request
2. Run tests
3. Verify no conflicts
4. Squash commits (if desired)
5. Merge to main
6. Push to GitHub
7. Archive branch (optional)

---

## Dependency Matrix

```
feature/mcp-acquisition
  └─ Independent
     (creates catalog for Phase 2a use)

feature/batch-1-utilities
  └─ Independent
     (8 skills, no MCP dependency)

feature/phase-1b-metrics
  └─ Independent
     (collection foundation, no MCP dependency)

Phase 2a Integration (Mar 11+)
  ├─ Depends on: main branch
  │  └─ batch-1-utilities ✓
  │  └─ phase-1b-metrics ✓
  └─ Ready for: mcp-acquisition (or waits until merged)
```

---

## Rollback Plan

If any branch needs to rollback:

```bash
# Revert to base commit (00db3e8)
git reset --hard 00db3e8

# Create new branch from main
git checkout main
git pull origin main
git checkout -b feature/xyz-v2

# Implement differently, then try again
```

---

## Current Status

✅ **ALL BRANCHES CREATED**
- feature/mcp-acquisition: Ready
- feature/batch-1-utilities: Ready
- feature/phase-1b-metrics: Ready
- main: Clean, backed up to GitHub

✅ **CHECKPOINT CREATED**
- Base commit: `00db3e8`
- All planning complete
- Infrastructure in place
- Ready to code

---

## Next Steps

### To Start MCP Acquisition Work
```bash
git checkout feature/mcp-acquisition
# Begin Week 1 implementation (RegistryClient)
```

### To Start Batch 1 Skills Work
```bash
git checkout feature/batch-1-utilities
# Begin week 2 implementation (utility skills)
```

### To Start Phase 1b Metrics Work
```bash
git checkout feature/phase-1b-metrics
# Begin week 1 implementation (ExecutionMetrics)
```

### To Check Status
```bash
git branch -v               # See all branches
git diff main branch-name   # See changes in branch
git log --oneline main..branch-name  # See commits in branch only
```

---

## Benefits of This Approach

✅ **Parallel Development**
- 3 teams can work simultaneously
- No blocking on each other
- Each has clear scope

✅ **Risk Isolation**
- If one branch has issues, others unaffected
- Can rollback one without affecting others
- Easy to pause/resume work

✅ **Easy Integration**
- Merge at logical checkpoints (Mar 10, Mar 31)
- Tested before merge
- Clear integration order

✅ **Rollback Safety**
- Base commit (00db3e8) is clean checkpoint
- Any branch can reset independently
- Main stays stable

---

**Recommended**: Start with MCP acquisition (feature/mcp-acquisition) since it has clearest Phase 1 tasks.

Then parallel tracks can start Week 2 as planned.
