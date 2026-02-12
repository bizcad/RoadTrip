# Phase 2a: Skill Fingerprinting & Registry — Narrowed Scope

**Status**: Ready to Start (Next Monday, Feb 17, 2026)  
**Duration**: 6 weeks (Feb 17 – Mar 30, 2026)  
**Workstream**: A only (defer B & C to Phase 2b)  
**Team**: Solo developer + Claude agents  

---

## Why This Scope

The full Phase 2 plan (005-Skill-Trust-Capabilities/plan.md) is **too ambitious for 8 weeks solo**. Instead:

1. **Focus Workstream A** (Skill Fingerprinting) — the foundation
2. **Defer Workstream B** (IBAC Verification) — 4 weeks later in Phase 2b
3. **Defer Workstream C** (Constitutional AI) — make it optional for Phase 2c

This gives you a **shippable, testable milestone** by end of March while building the infrastructure that Phase 2b will extend.

---

## Phase 2a Goals

### Primary Goal
**Generate deterministic, cryptographically signed fingerprints for all Phase 1b skills.**

These fingerprints become the trust anchor for Phase 2b (IBAC) and Phase 2c (Constitutional AI).

### Secondary Goals
1. Build a **Skill Registry Agent** that maintains a catalog of skills with their fingerprints
2. Enable **semantic search** over skill descriptions (optional: vector embeddings in v2)
3. Create **event-driven trust scoring** infrastructure (write-only, for Phase 2b to read)

### What You Ship
- ✅ Fingerprint Agent (generates and signs fingerprints)
- ✅ Registry Agent (maintains catalog)
- ✅ Fingerprints for all Phase 1b skills (auth_validator, telemetry_logger, commit_message, blog_publisher, git_push_autonomous)
- ✅ Local registry backend (file-based YAML/JSON, no DB setup needed)
- ✅ Test suite for both agents
- ✅ Simple CLI tool to query registry

### What You DON'T Build (Phase 2b)
- IBAC verification (Intent-Based Access Control)
- Constitutional AI agent
- Event-driven trust scoring backend
- Vector embeddings / Pinecone integration

---

## Architecture (Simplified for Phase 2a)

```
Phase 1b Skills                 Phase 2a New
└─ auth_validator              ├─ Fingerprint Agent
   commit_message              │  ├─ Generate cryptographic fingerprints
   telemetry_logger            │  ├─ Sign with authority key
   blog_publisher              │  └─ Return SkillFingerprint dataclass
   git_push_autonomous         │
                               ├─ Registry Agent
                               │  ├─ Maintain skill catalog (YAML/JSON)
                               │  ├─ Store fingerprints, metadata, tests
                               │  └─ Enable semantic search (grep + regex, later: embeddings)
                               │
                               └─ TrustScore Event Emitter (write-only)
                                  └─ Append events to JSONL (same pattern as telemetry_logger)
```

**Phase 2a does NOT include**:
- Verifier Agent (needs IBAC logic — Phase 2b)
- Constitutional Agent (needs LLM evaluator — Phase 2b/2c)
- Permission enforcement (phase 2b)
- Event subscription/consumption (Phase 2b)

---

## Workstream A Breakdown

### A0: Setup (1 day)
- ✅ Create src/agents/fingerprint_agent.py
- ✅ Create src/agents/registry_agent.py
- ✅ Create data models (fingerprint_models.py, registry_models.py)
- ✅ Create test stubs (tests/test_fingerprint_agent.py, tests/test_registry_agent.py)

### A1: Fingerprint Agent (3 weeks)

#### A1a: Crypto Attestation (Week 1)
**Goal**: Generate deterministic fingerprints  
**Inputs**: Skill source code + test metadata

**Deliverables**:
- [x] SkillFingerprint dataclass (code_hash, capabilities_hash, test_metadata, created_at, signed=true)
- [x] SHA256 hashing over:
  - Skill Python source code
  - capabilities.json (what the skill can do)
  - test_coverage.json (how many tests, coverage %)
  - version info
- [x] Determinism test: same inputs → same hash (idempotent)
- [x] No external calls (pure crypto, file I/O only)

**Code Estimate**: 40-60 lines  
**Tests**: 10+ test cases verifying determinism, hash stability

#### A1b: Self-Signed Authority (Week 1-2)
**Goal**: Sign fingerprints with a self-generated vetting authority key

**Deliverables**:
- [x] Generate vetting authority key (RSA-2048, stored in config/fingerprint-authority/)
- [x] Sign fingerprint hash with authority private key
- [x] PublicKey export for verification (Phase 2b will verify signatures)
- [x] Signature validation (self-test)

**Code Estimate**: 50-80 lines  
**Tests**: 5+ test cases for signature generation, validation, key rotation

**Note**: No external HSM in Phase 2a — file-based key is fine for dev/test. Upgradeable in Phase 2c.

#### A1c: Integration Tests (Week 2-3)
**Goal**: Test Fingerprint Agent end-to-end

**Deliverables**:
- [x] Test all Phase 1b skills:
  - auth_validator.py → generate fingerprint
  - telemetry_logger.py → generate fingerprint
  - commit_message.py → generate fingerprint
  - blog_publisher.py → generate fingerprint
  - git_push_autonomous.py → generate fingerprint (after creating it)
- [x] Verify all fingerprints are signed
- [x] Verify fingerprints don't change on re-run

**Test Cases**:
- 5 skills × 3 test cases = 15+ integration tests

---

### A2: Registry Agent (2 weeks)

#### A2a: Skill Catalog (Week 3-4)
**Goal**: Maintain a centralized catalog of skills with their fingerprints

**Deliverables**:
- [x] SkillRegistryEntry dataclass:
  ```python
  @dataclass
  class SkillRegistryEntry:
      name: str
      version: str
      description: str
      fingerprint: SkillFingerprint
      capabilities: List[str]  # ["validate_auth", "check_permissions"]
      test_count: int
      test_pass_rate: float
      last_fingerprinted: datetime
      trusted: bool = False  # Set by Phase 2b
  ```
- [x] Storage backend (file-based YAML/JSON):
  ```
  data/skill-registry/
  ├── auth_validator.yaml
  ├── commit_message.yaml
  ├── telemetry_logger.yaml
  ├── blog_publisher.yaml
  └── index.yaml  # master index with all skills
  ```
- [x] CRUD operations: add, update, read, list, delete

**Code Estimate**: 80-120 lines  
**Tests**: 8+ test cases (CRUD, error handling, concurrent access)

#### A2b: Semantic Search (Week 4) — OPTIONAL, can defer
**Goal**: Find skills by description, capability, type

**Deliverables** (pick one):
- **Option 1 (Simple)**: grep + filename matching
  - Search for "auth" → returns auth_validator.yaml
  - Search for "git" → returns commit_message.yaml, blog_publisher.yaml
  - No code changes needed; Python os.scandir() + regex
  - Estimate: 20 lines

- **Option 2 (Better)**: BM25 ranking (no ML, pure algorithm)
  - Rank skills by relevance
  - Example: search "validate authentication" → auth_validator (0.95), rules_engine (0.42)
  - Estimate: 60-80 lines (use rank_bm25 Python library)

- **Option 3 (Advanced)**: BERT embeddings + Pinecone
  - **NOT RECOMMENDED for Phase 2a** — scope creep, requires Pinecone account
  - Defer this to Phase 2b/2c

**Code Estimate**: 20-80 lines (depending on option)  
**Tests**: 5+ test cases

**Decision**: Do Option 1 (grep) for Phase 2a, upgrade to Option 2 in Phase 2b if time permits.

---

### A3: Event Infrastructure (1 week)

#### A3a: Trust Score Events (Week 5-6)
**Goal**: Emit events when fingerprints are generated or skills are tested

**Deliverables**:
- [x] SkillFingerprintedEvent (skill_name, fingerprint_hash, signed=true, timestamp)
- [x] SkillTestPassedEvent (skill_name, test_count, pass_rate, timestamp)
- [x] Event emitter (append to data/skill-events.jsonl)
- [x] Event reader (filter by skill, date range)

**Note**: This is **write-only** in Phase 2a. Phase 2b will subscribe to these events for trust scoring.

**Code Estimate**: 40-60 lines  
**Tests**: 5+ test cases (emit, read, filter)

---

### A4: CLI & Integration (Week 5-6)

#### A4a: Simple CLI
**Deliverables**:
```bash
# Fingerprint all skills
python -m src.agents.fingerprint_agent --all

# Fingerprint one skill
python -m src.agents.fingerprint_agent --skill auth_validator

# List all skills in registry
python -m src.agents.registry_agent --list

# Search registry
python -m src.agents.registry_agent --search "auth"

# Show details of one skill
python -m src.agents.registry_agent --detail auth_validator
```

**Code Estimate**: 40-50 lines (argparse wrapper)

#### A4b: Integration Test
**Goal**: Verify entire pipeline works

**Test**:
- Fingerprint all Phase 1b skills → Registry → Search → Display results
- Verify event log has entries for each fingerprint

---

## Timeline (6 weeks)

| Week | Task | Owner | Hours |
|------|------|-------|-------|
| 1 | A0 + A1a (setup, crypto, hashing) | You | 12 |
| 2 | A1b + A1c (signing, integration tests) | You | 16 |
| 3 | A2a (registry CRUD) | You | 12 |
| 4 | A2b (semantic search) | You | 8 |
| 5 | A3a + A4a (events, CLI) | You | 12 |
| 6 | A4b + docs + deployment | You | 8 |
| **Total** | | | **68 hours** |

**Realistic estimate**: 60-80 hours solo (8-10 hours/week if starting Feb 17)

---

## Success Criteria

- ✅ All Phase 1b skills have signed fingerprints
- ✅ Registry stores fingerprints + metadata
- ✅ Semantic search works (finds auth_validator when you search "authenticate")
- ✅ Event log has entries for each fingerprinted skill
- ✅ All new code has tests (>80% coverage)
- ✅ CLI tools work (python -m src.agents.fingerprint_agent --skill auth_validator)
- ✅ Phase 2b can read fingerprints + events for IBAC verification

---

## What Phase 2b Will Do (Not Phase 2a)

- Build Verifier Agent (evaluates intent, issues trust decisions)
- Subscribe to trust score events
- Implement IBAC policy enforcement
- Add user credibility scoring
- Integrate with External tool vulnerability analysis (bandit, pip-audit)

**Phase 2b will START with the Phase 2a foundation and add 2-3 new agents + verification logic.**

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Crypto/signing complexity | Medium | Use cryptography library (standard), write isolated tests first |
| File-based registry performance | Low | 50 skills = no problem, scale to DB in Phase 2c if needed |
| Semantic search overhead | Low | Start with grep, add BM25 if time permits |
| Time overrun | Medium | Drop A2b (semantic search) first, drop A3a (events) second |

---

## Definition of Done

Phase 2a is complete when:

1. ✅ All Phase 1b skills have signed fingerprints
2. ✅ Registry Agent can CRUD skills + fingerprints
3. ✅ Semantic search works (basic grep-based)
4. ✅ Event log initialized and CLI works
5. ✅ All code tested (pytest)
6. ✅ Documentation updated
7. ✅ Code reviewed and merged to main
8. ✅ Tag release: v2a.0

---

## Next Steps

### Before Phase 2a Starts
1. Run full Phase 1b test suite:
   ```powershell
   pytest tests/ -v
   ```
2. Create git_push_autonomous.py (if not already done)
3. Review this plan with stakeholders (team/Claude)

### Day 1 of Phase 2a
1. Create directory structure:
   ```
   src/agents/
   ├── fingerprint_agent.py
   ├── registry_agent.py
   ├── fingerprint_models.py
   ├── registry_models.py
   └── __init__.py
   ```
2. Create test stubs
3. Implement A1a (crypto)

---

## Comparison to Original Phase 2 Plan (005)

| Aspect | Original 005 | Phase 2a |
|--------|-------------|---------|
| Duration | 8 weeks | 6 weeks |
| Workstreams | A, B, C | A only |
| Agents | 5+ (Fingerprint, Registry, Verifier, Constitutional, Orchestrator) | 2 (Fingerprint, Registry) |
| Sub-agents | 4 (1a/1b/1c, plus 3a/3b/3c/3d) | 0 (event infrastructure only) |
| IBAC implementation | Yes | No (Phase 2b) |
| Constitutional AI | Yes (exploratory) | No (Phase 2c) |
| Scope risk | High | Low |
| Solo dev realistic | Questionable | Achievable ✅ |

---

## Dependency: git_push_autonomous.py

**Blocker**: Phase 2a fingerprinting needs all Phase 1b skills ready, including git_push_autonomous.py.

**If git_push_autonomous doesn't exist by Feb 17**:
1. Create it first (2-3 hours)
2. Then start Phase 2a fingerprinting

**If it does exist**:
- Start Phase 2a immediately

---

## Conclusion

**Phase 2a is a focused, achievable 6-week sprint** that delivers:
- ✅ Fingerprinting infrastructure (the foundation for trust)
- ✅ Registry capability (manage skills at scale)
- ✅ Event logging (enable future verification)
- ✅ Shippable, testable code

**Phase 2b will extend this with IBAC verification**, and **Phase 2c with Constitutional AI**.

**Ready to start?** Begin with A0 setup on Monday, Feb 17, 2026.
