# Phase 2 Implementation Plan: Agents & Systems Architecture

**Document Version**: 1.0-draft  
**Date**: February 11, 2026  
**Status**: Planning (No Code Yet — Sketches Only)  
**Phase Duration**: 8 weeks (Mar 11 - May 3, 2026)

---

## Table of Contents
1. [Overview](#overview)
2. [Agent Architecture](#agent-architecture)
3. [System Components](#system-components)
4. [Workstream Breakdown](#workstream-breakdown)
5. [Agent Specifications (Stubs)](#agent-specifications-stubs)
6. [Success Metrics](#success-metrics)
7. [Risks & Mitigations](#risks--mitigations)

---

## Overview

### Phase 2 Mission Statement
Enable the RoadTrip orchestrator to **securely discover, trust, and invoke 50–100+ skills** through a **layered security architecture** (Zero Trust + IBAC + Constitutional AI).

### Three Concurrent Workstreams
1. **Workstream A**: Skill Fingerprinting & Capability Discovery
2. **Workstream B**: Intent-Based Access Control (IBAC) Verification
3. **Workstream C**: Constitutional AI Agent Self-Critique

### Agent-Oriented Architecture
Rather than monolithic services, Phase 2 introduces **specialist agents** that collaborate:
- **Fingerprint Agent**: Vets skills, generates cryptographic attestations
- **Registry Agent**: Maintains skill catalog, enables semantic search
- **Verifier Agent**: Evaluates intent, issues trust decisions with confidence scores
- **Constitutional Agent**: Self-critique, enforces alignment principles
- **Orchestrator Agent** (enhanced): Choreographs skills based on intent + trust signals

**Design rationale**: Each agent is independently testable, replaceable, and can be deployed to different trust zones.

---

## Agent Architecture

### Agent Interaction Flow

```
User Goal
   ↓
[Orchestrator Agent] "I need to push code; which skill should I use?"
   ↓
[Registry Agent] "Found: commit-message (0.99), git-push-autonomous (0.97)"
   ↓
[Verifier Agent] Queries sub-agents:
  ├─ [Author Credibility] "Is this from trusted maintainer?" → ✓
  ├─ [Coding Standards] "Does code follow conventions?" → ✓
  ├─ [Vulnerability Analysis] "Any security red flags?" → ✓
  └─ [Intent Alignment] "Does intent match capability?" → 0.95
   ↓
[Constitutional Agent] "Second opinion: Does this align with constitution?
                        (Consults alternate LLM or deterministic rules)
                        ✓ Not modifying sensitive files
                        ✓ User is requesting, not autonomous
                        ✓ Confidence > threshold
                        → APPROVED"
   ↓
[Orchestrator Agent] Invokes skill → Execute → Log result
   ↓
[Event Emitter] "Skill invoked: commit-message v1.0 by user@example
                  Fingerprint matched. Tests passed.
                  Trust score event: +0.01 (production success)"
   ↓
[Registry Agent] Updates trust score (event-driven, real-time)
```

### Five Agents (Phased Introduction)

#### Agent 1a: **Fingerprint Agent** (Workstream A - Crypto Attestation Only)
**Purpose**: Generate cryptographic fingerprints for tested skills (single responsibility: crypto attestation)  
**Responsibilities** (SOLID: Single Responsibility):
- Accept test results from Test Execution Agent (not run tests itself)
- Generate composite fingerprint hash (SHA256 over code + capabilities + test metadata)
- Sign fingerprint with self-generated vetting authority key (file-based initially)
- Store fingerprint in skill schema / registry

**Inputs**: Skill source code + Test Execution results (from Agent 1b)  
**Outputs**: `SkillFingerprint` dataclass with self-signed attestation  
**Implementation Status**: STUB (to be designed in A2)  
**Success Criteria**:
- Fingerprints deterministic (same inputs = same hash, idempotent)
- Signature generation never corrupts fingerprint
- 100% of Phase 1b skills have signed fingerprints before Phase 2 starts
- Fingerprints stable across code updates (same logic = same hash)

**Design Notes**:
- Fingerprint authority key stored in `config/fingerprint-authority/` (file-based v1, upgradeable to HSM)
- No external calls; pure cryptographic operations
- Can be called multiple times safely (idempotent)

---

#### Agent 1b: **Test Execution Agent** (Workstream A - Test Orchestration Only)
**Purpose**: Run skill tests and report results (single responsibility: test execution)  
**Responsibilities** (SOLID: Single Responsibility):
- Discover tests (unit, integration, etc.) for given skill
- Execute tests in isolated sandbox (timeout handling, resource limits)
- Collect results (pass/fail, execution time, resource usage)
- Report metadata (test version, Python interpreter version, dependencies)
- Emit event `SkillTestsCompleted` for downstream agents

**Inputs**: Skill source code + test config + test discovery rules  
**Outputs**: `SkillTestResults` dataclass (what % passed, how long did it take?)  
**Implementation Status**: STUB (to be designed in A2)  
**Success Criteria**:
- 100% of tests run to completion (no hangs)
- Test output captured (stdout/stderr/logs)
- Latency < 5min per skill (even integration tests)
- Tests are idempotent (can re-run, same results)

**Design Notes**:
- Could split further (UnitTestAgent, IntegrationTestAgent, E2ETestAgent) if needed
- Emits event → Fingerprint Agent + Registry Agent consume it
- No credential leaking in test logs (redaction pass)

---

#### Agent 1c: **Test Analyzer Agent** (Workstream A - Optional Specialization)
**Purpose**: (Optional) Analyze test results for patterns, gaps, and coverage  
**Responsibilities**:
- Calculate coverage % (if tool available)
- Detect flaky tests (same test, different results)
- Flag gaps (code paths with no test)

**Status**: OPTIONAL; can defer to v2 if v1 achieves coverage goals

---

#### Agent 2: **Registry Agent** (Workstream A - Pluggable)
**Purpose**: Maintain skill catalog, enable discovery via semantic search (pluggable storage backend)  
**Responsibilities**:
- Storage abstraction (file-based v1, pluggable to BERT/vector DB v2)
- Capability introspection API (MCP-style: "list-skills --by-capability generate-commit")
- Semantic search (embeddings + cosine similarity to find nearest skills for a query)
- Trust scoring engine (score = f(test_pass_rate, fingerprint_match, production_success_rate))
- Event subscription (consume `SkillTestsCompleted`, `SkillFingerprintGenerated`, `SkillInvoked` events)

**Inputs**: `SkillContract` dataclass (spec of what a skill offers); events from other agents  
**Outputs**: Registry query results + trust scores  
**Implementation Status**: STUB (to be designed in A3)  
**Storage Pluggability**:
- **v1 (Phase 2a)**: YAML/JSON files in `config/skill-registry/`
- **v2 (Phase 2b/c)**: BERT vector DB (Pinecone, Weaviate, or self-hosted)
- **Interface**: `RegistryBackend` abstract class; implementations swappable

**Success Criteria**:
- Registry achieves >95% recall (finds correct skills for queries)
- Semantic search latency < 100ms (file-based) or < 500ms (BERT)
- Trust scores correlate with actual reliability (Pearson r > 0.7)
- Can swap storage backend without API change

**Design Notes**:
- Abstraction layer: `RegistryBackend` interface with `FileBasedRegistry`, `BERTRegistry` implementations
- Event-driven trust updates (no cron jobs, no per-use scanning)
- Pluggability tested early (write tests for both v1 and v2 interfaces)

---

#### Agent 3: **Verifier Agent** (Workstream B - Composite Multi-Check)
**Purpose**: Intent-Based Access Control aggregating multiple verification checks  
**Responsibilities** (Delegates to Sub-Agents):
- **Sub-Agent 3a (Author Credibility)**: Is this skill from a trusted maintainer? (deterministic + reputation)
- **Sub-Agent 3b (Coding Standards)**: Does code follow our conventions? (linter-based, deterministic)
- **Sub-Agent 3c (Vulnerability Analysis)**: Any security red flags? (SAST, dependency check, heuristics)
- **Sub-Agent 3d (Intent Alignment)**: Does intent match capability? (LLM-based, probabilistic)
- **Aggregation**: Combine sub-agent scores into IAC confidence (0.0–1.0)
- **Policy Enforcement**: Allow if confidence > threshold (0.85); else escalate

**Inputs**: User intent + candidate skill (from Registry)  
**Outputs**: `IBACVerification` with confidence score + reasoning from all sub-checks  
**Implementation Status**: STUB (to be designed in B2)  
**Model Strategy** (Cost-Sensitive, Agnostic):
- Sub-Agents 3a–3c: Deterministic (no LLM; use rules, linters, SAST tools)
- Sub-Agent 3d: LLM-based (Claude Haiku for cost, swap to GPT-4 if needed; cached)
- Fallback: If LLM unavailable, Sub-Agent 3d returns neutral (0.5) pending user escalation

**Success Criteria**:
- Sub-agents complete in <2s total (caching helps)
- Confidence scores predicted actual alignment
- Latency < 2s per verification (acceptable for first-call overhead)
- User audit: "Did verification correctly prevent misuse?" → >90% yes
- Cost per verification < $0.001 (via caching + model choice)

**Design Notes**:
- Sub-agents independently testable (each can have unit tests)
- Pluggable: Sub-Agent 3d can swap models without touching 3a–3c
- Caching: Cache identical (intent, skill_id) pairs → learned confidence scores
- Event emission: `IBACVerificationComplete` event for audit logging

---

#### Sub-Agent 3a: **Author Credibility Checker**
- Check if skill author in approved maintainers list
- Check skill commit history (signed commits count, review count)
- Return binary score (0.0 or 1.0) plus evidence notes

#### Sub-Agent 3b: **Coding Standards Checker**
- Run linters (black, ruff, mypy) on skill source
- Check docstring coverage, type hints, error handling
- Return 0.0–1.0 score based on violations severity

#### Sub-Agent 3c: **Vulnerability Analyzer**  
- Run SAST tool (bandit, custom rules for credential leaks)
- Scan dependencies (pip-audit or equivalent)
- Check for dangerous imports (os.system, subprocess without guards)
- Return 0.0–1.0 score based on severity/count

#### Sub-Agent 3d: **Intent Alignment Evaluator** (LLM-Based)
- Prompt: "User intent: {intent}. Skill does: {capability}. Match score 0.0–1.0?"
- Cached (same intent + skill = near-zero latency)
- Fallback: Neutral (0.5) if LLM unavailable

---

#### Agent 4: **Constitutional Agent** (Workstream C - "Second Opinion" Layer)
**Purpose**: Agent self-critique before execution (guard against subtle misalignment)  
**Status**: EXPLORATORY (design not yet locked)  
**Responsibilities** (TBD):
- Option A: "Rubber-stamp confirmation" (quickly says "✓ OK" to most requests)
- Option B: "Second opinion LLM" (different model echoes back what Verifier concluded)
- Option C: "Principle checker" (deterministic rules enforcing constitution)
- Option D: "Multi-model consensus" (e.g., Claude + GPT-4 must agree > 0.85)
- TBD: Which option? Or hybrid?

**Inputs**: Proposed skill invocation + Orchestrator's constitution (principles)  
**Outputs**: Approval/rejection + reasoning (used for escalation decision)  
**Implementation Status**: STUB (to be designed in C2; design depends on team choice)  
**Success Criteria** (Common to all options):
- Adds < 1s latency (or cached for same action)
- Zero false negatives (never approves a principle violation)
- <5% false positives (reject few legitimate invocations)
- Reasoning is human-readable and auditable

**Design Uncertainty**:
This agent is intentionally underdefined. Options A–D have different trade-offs:

| Option | Latency | Cost | Confidence | Notes |
|--------|---------|------|------------|-------|
| A (Rubber-stamp) | <10ms | $0 | Low | Quick; might miss red flags |
| B (Different LLM) | ~1s | $0.001–0.01 | Medium | Claude + GPT-4 may agree 95% of time |
| C (Rules-based) | <50ms | $0 | High on known patterns | Requires curating principles; misses edge cases |
| D (Consensus) | ~2s | $0.002–0.02 | Highest | Slower; more costly; better for critical decisions |

**Escalation Strategy**:
- **Constitutional Approve**: Execute skill (logged)
- **Constitutional Uncertain**: Ask user: "I'm not sure about this. [Reasoning]. OK to proceed?" (Guided confirmation)
- **Constitutional Reject**: Halt; explain principle violation (no execution)

**Design Process**:
1. Week 1: Clarify which option(s) to prototype (A/B/C/D)
2. Week 2: Build prototype; measure confidence/latency
3. Week 3–4: Validate with real workloads
4. Week 5: Lock design; move to Agent 4 implementation

**Philosophical Note**:
Constitutional AI is research-grade (Anthropic 2023); RoadTrip is exploring whether "agent has its own constitution" improves alignment. Early data will tell us if it's worth the latency/cost.

---

#### Agent 5: **Orchestrator Agent (Enhanced)** (All Workstreams)
**Purpose**: Choreograph skill discovery, verification, and invocation  
**Responsibilities**:
- Goal decomposition (Break user intent into sub-tasks)
- Skill selection (Query Registry + Verifier for best match)
- Execution orchestration (Call skill, handle errors, log results)
- Constitutional escalation (Consult Constitutional Agent if unsure)

**Inputs**: User goal + available skills + trust policies  
**Outputs**: Skill invocation result + audit trail  
**Implementation Status**: Enhancement of current `git_push_autonomous.py`  
**Success Criteria**:
- End-to-end latency (zero-cache): < 5s per goal
- Success rate > 95% for known intents
- All decisions auditable with reasoning

---

## System Components

### Data Structures (Stubs to Design)

```python
# Workstream A: Skill Fingerprinting & Testing (Event-Driven)

@dataclass
class SkillTestResults:
    """Results from Test Execution Agent (1b)."""
    skill_id: str              # "commit-message"
    version: str               # "1.0.0"
    test_pass_count: int       # 47
    test_fail_count: int       # 0
    test_skip_count: int       # 2
    success_rate: float        # 0.995
    avg_execution_time_ms: float  # 100.5
    max_execution_time_ms: float  # 250.0
    coverage_percent: float    # 87.3
    test_runner_version: str   # "pytest 7.4"
    python_version: str        # "3.10.12"
    executed_at: datetime
    test_config: dict          # {"timeout_ms": 5000, ...}

@dataclass
class SkillFingerprint:
    """Cryptographic attestation for a skill (Agent 1a output)."""
    skill_id: str              # "commit-message"
    version: str               # "1.0.0"
    code_hash: str             # SHA256 over skill source
    capabilities_hash: str     # SHA256 over capability list
    test_results_hash: str     # SHA256 over test results (from Agent 1b)
    composite_fingerprint: str # SHA256 over (code + capabilities + test_results)
    attestor_key_id: str       # "roadtrip-fingerprint-authority-v1"
    attestor_signature: str    # RSA signature over composite_fingerprint
    created_at: datetime
    signed_by: str             # "fingerprint-agent-1a@roadtrip"
    self_signed: bool          # True (file-based authority in Phase 2a)
    authority_key_fingerprint: str  # SHA256 of public key (for rotation tracking)

# Workstream B: IBAC Verification (Multi-Check with Sub-Agent Results)
@dataclass
class AuthorCredibilityCheck:
    """Sub-Agent 3a result: Author trusted?"""
    author: str
    is_approved_maintainer: bool  # Binary: 0.0 or 1.0
    signed_commit_count: int
    review_count: int
    score: float  # 0.0 or 1.0
    evidence: str  # "Signed commits, 15+ reviews, approved"

@dataclass
class CodingStandardsCheck:
    """Sub-Agent 3b result: Code acceptable?"""
    linter_violations: int  # count
    docstring_coverage: float  # percent
    type_hint_coverage: float  # percent
    error_handling_score: float  # 0.0-1.0
    violations_severity: list[str]  # ["high: missing docstring", ...]
    score: float  # 0.0-1.0 based on violations

@dataclass
class VulnerabilityCheck:
    """Sub-Agent 3c result: Any security issues?"""
    sast_findings: list[str]  # ["Potential credential leak in line 42", ...]
    dependency_vulnerabilities: list[str]  # ["certifi < 2023.5.7", ...]
    dangerous_imports: list[str]  # ["os.system used without guards", ...]
    severity_score: float  # 0.0-1.0 (0=safe, 1=critical)
    score: float  # 0.0-1.0 (inverse of severity)

@dataclass
class IntentAlignmentCheck:
    """Sub-Agent 3d result: Does intent match capability? (LLM-based)"""
    intent: str  # "User wants to generate semantic commit message"
    skill_capability: str  # "Generate commit message from staged changes"
    alignment_score: float  # 0.0-1.0 (from Claude Haiku or GPT-4)
    reasoning: str  # "Intent matches capability; intent is user-initiated, not autonomous"
    model: str  # "claude-haiku-3.5" or "gpt-4"
    cached: bool  # True if from cache
    confidence: float  # How confident in this score?

@dataclass
class IBACVerification:
    """Intent-Based Access Control decision (Agent 3 output)."""
    intent: str
    skill_id: str
    author_credibility: AuthorCredibilityCheck
    coding_standards: CodingStandardsCheck
    vulnerability_analysis: VulnerabilityCheck
    intent_alignment: IntentAlignmentCheck
    aggregate_confidence: float  # 0.0-1.0 (weighted average of 4 checks)
    allow_threshold: float  # 0.85 (policy)
    decision: str  # "ALLOW", "ESCALATE", "DENY"
    reasoning: str  # Human-readable explanation
    timestamp: datetime
    verifier_signature: str  # Optional: sign decision

# Workstream C: Events (Event-Driven Architecture for Trust Updates)
@dataclass
class SkillInvokedEvent:
    """Event emitted when skill is executed."""
    skill_id: str
    version: str
    invoked_by: str  # user or agent
    intent: str
    fingerprint_matched: bool
    tests_passed: bool
    execution_time_ms: float
    success: bool
    error_msg: str | None
    timestamp: datetime

# This event triggers Registry Agent to update trust_score in real-time (not cron)

@dataclass
class SkillFingerprintGeneratedEvent:
    """Event emitted when fingerprint created/updated."""
    skill_id: str
    version: str
    fingerprint_hash: str
    signature_valid: bool
    timestamp: datetime

@dataclass
class SkillTestsCompletedEvent:
    """Event emitted by Test Execution Agent (1b)."""
    skill_id: str
    version: str
    test_results: SkillTestResults
    timestamp: datetime

# Registry Agent subscribes to SkillInvokedEvent, SkillTestsCompletedEvent
# to update trust scores in real-time (event-driven, not cron)
```

### Service Interfaces (Stubs)

```python
# Registry Service API
class RegistryAgent:
    def find_skills(query: str, min_trust_score: float = 0.7) -> list[SkillContract]:
        """Find skills matching a semantic query."""
        
    def introspect_capability(skill_id: str) -> dict:
        """Get detailed capability info for a skill."""
        
    def update_trust_score(skill_id: str, new_score: float) -> None:
        """Update skill's trust score based on prod metrics."""

# Verifier Service API
class VerifierAgent:
    def verify_intent(intent: str, skill_id: str) -> IBACVerification:
        """Evaluate intent-based access control."""
        
    def batch_verify(intents: list[str], skills: list[str]) -> list[IBACVerification]:
        """Verify multiple intent-skill pairs."""

# Constitutional Service API
class ConstitutionalAgent:
    def evaluate(proposed_action: str, principles: list[str]) -> ConstitutionalDecision:
        """Self-critique: does action align with principles?"""
        
    def audit_log(decision: ConstitutionalDecision) -> None:
        """Log decision for auditability."""
```

---

## Workstream Breakdown

### Workstream A: Skill Fingerprinting, Testing & Discovery (Weeks 1–3)
**Owner**: (To Be Assigned)  
**Dependency**: Phase 1b skills (must be complete)  
**Philosophy**: Decompose to atomic agents (SOLID: Single Responsibility). Each idempotent and independently testable.

#### A1: Design Fingerprint Schema, Test Execution Schema & Authority Key Management
- [ ] Define `SkillTestResults` dataclass (test pass/fail counts, coverage, execution time)
- [ ] Define `SkillFingerprint` dataclass (code_hash, capabilities_hash, test_results_hash, composite, signature)
- [ ] Design fingerprint authority key storage (file-based v1: `config/fingerprint-authority/roadtrip-key.pem`)
- [ ] Design event schema: `SkillTestsCompletedEvent`, `SkillFingerprintGeneratedEvent`
- [ ] Document: `005-Skill-Trust-Capabilities/A1-FINGERPRINT-AND-TEST-SCHEMA.md`

#### A1b: Design Test Execution Pipeline (Idempotent, Deterministic)
- [ ] Define test discovery rules (pytest convention: `test_*.py` in `tests/`)
- [ ] Define test execution sandbox (isolated Python env, timeout=5min, memory=512MB)
- [ ] Define result reporting format (JSON: pass/fail/skip counts, coverage %, execution time)
- [ ] Design test re-run idempotency guarantee (same code → same results)
- [ ] Document: `005-Skill-Trust-Capabilities/A1b-TEST-EXECUTION-SPEC.md`

#### A2: Implement Fingerprint Agent (1a) - Crypto Attestation Only
- [ ] Accept test results from Test Execution Agent
- [ ] Generate composite fingerprint (SHA256 over code + capabilities + test_results)
- [ ] Load fingerprint authority private key; sign fingerprint with RSA
- [ ] Store fingerprint in skill schema (part of SKILL.md or separate `skill-fingerprint.json`)
- [ ] Idempotence test: Run twice on same code → same hash
- [ ] Test coverage: 100% of A1 + A1b spec

#### A2b: Implement Test Execution Agent (1b) - Test Execution Only
- [ ] Discovery: Find all tests for given skill (pytest discovery)
- [ ] Execution: Run tests in sandbox (subprocess, timeout handling, env isolation)
- [ ] Collection: Parse pytest output (pass/fail/skip, timing, coverage if available)
- [ ] Persistence: Write `SkillTestResults` to JSON/YAML
- [ ] Event Emission: Emit `SkillTestsCompletedEvent` → triggers Fingerprint Agent
- [ ] Test coverage: Full lifecycle (discover → execute → collect → persist → emit)

#### A2c: (Optional) Implement Test Analyzer Agent (1c) - Coverage & Gap Detection
- [ ] Calculate coverage % (if pytest-cov available)
- [ ] Detect flaky tests (re-run N times; flag if different results)
- [ ] Flag gaps (uncovered code paths)
- [ ] Status: OPTIONAL; defer to v2 if tests pass, coverage > 80%

#### A3: Design & Implement Registry Agent (Pluggable Storage)
- [ ] Define `SkillContract` schema (capabilities, I/O schemas, trust_score, metadata)
- [ ] Implement storage abstraction (RegistryBackend interface)
- [ ] Implement FileBasedRegistry (v1: YAML/JSON in `config/skill-registry/`)
- [ ] Implement BERTRegistry interface (v2: stub for future plugging in; tested but not used yet)
- [ ] Semantic search (OpenAI embeddings API or local embeddings; cached)
- [ ] Trust scoring: Initial = baseline (test_pass_rate * 0.7 + fingerprint_match * 0.3); update on `SkillInvokedEvent`
- [ ] Event subscription: Listen to `SkillInvokedEvent`, update trust_score in real-time
- [ ] Test coverage: Both FileBasedRegistry and BERTRegistry interfaces tested

#### A4: Vet All Phase 1b Skills (First Run - Idempotent)
- [ ] Run Test Execution Agent on each Phase 1b skill
- [ ] Run Fingerprint Agent (generate signatures)
- [ ] Add to Registry with initial trust_scores
- [ ] Verify: Run twice → same fingerprints (idempotent test)
- [ ] Success metric: 100% of Phase 1b skills fingerprinted, signed, registered

**Deliverables**:
- Test Execution Agent (code + tests + sandbox definition)
- Fingerprint Agent (code + tests + signature verification tests)
- Test Analyzer Agent (optional; code +tests if prioritized)
- Registry Agent (code + tests for both FileBasedRegistry and BERTRegistry interface)
- Phase 1b skills in registry with signed fingerprints
- `005-Skill-Trust-Capabilities/A-COMPLETION-REPORT.md`

**Event Flow in Workstream A**:
```
(Skill Code Updated)
   ↓
[Test Execution Agent 1b] Runs tests → emits SkillTestsCompletedEvent
   ↓
[Fingerprint Agent 1a] Consumes SkillTestsCompletedEvent → generates SkillFingerprint → emits SkillFingerprintGeneratedEvent
   ↓
[Registry Agent] Consumes SkillFingerprintGeneratedEvent → updates registry entry
   ↓
(Event-driven, fully asynchronous; idempotent at each step)
```

---

### Workstream B: Intent-Based Access Control (Weeks 2–4)
**Owner**: (To Be Assigned)  
**Dependency**: Workstream A (Registry must exist to query skills)  
**Philosophy**: Composite agent with atomic sub-agents. Cost-sensitive model choices. Deterministic checks first, LLM fallback.

#### B1: Design IBAC Policy Language, Sub-Agent Architecture & Cost Strategy
- [ ] Define `IBACVerification` dataclass with sub-agent results (AuthorCredibilityCheck, CodingStandardsCheck, VulnerabilityCheck, IntentAlignmentCheck)
- [ ] Design policy language: "Allow skill X for intent Y if confidence > 0.85"
- [ ] Identify sub-agent tools:
  - Sub-Agent 3a (Author Credibility): Deterministic (approved maintainers list)
  - Sub-Agent 3b (Coding Standards): Deterministic (linter rules: black, ruff, mypy)
  - Sub-Agent 3c (Vulnerability): Deterministic (SAST: bandit, pip-audit, regex patterns)
  - Sub-Agent 3d (Intent Alignment): LLM-based (Claude Haiku, cost ~$0.0005 per call, cacheable)
- [ ] Cost strategy (reference: `docs/How to cut OpenClaw Costs.md`):
  - Cascade: Run free checks first (3a–3c); only call LLM (3d) if all deterministic pass
  - Cache: Store (intent, skill_id) → confidence_score; reuse learned decisions
  - Fallback: If LLM unavailable, return neutral (0.5) and escalate
- [ ] Document: `005-Skill-Trust-Capabilities/B1-IBAC-ARCHITECTURE.md`

#### B1b: Design Constitutional Escalation Strategy
- [ ] Escalation logic: If IBAC score < 0.85 → ask user (guided confirmation, not auto-allow)
- [ ] User prompt template: "I found [issues]. Confidence: 0.72. OK to proceed?"
- [ ] Audit logging: Every escalation logged with user's decision
- [ ] Fallback: If LLM unavailable, escalate (fail-safe)

#### B2: Implement Sub-Agents (Deterministic First, Then LLM)
- [ ] Sub-Agent 3a (Author Credibility):
  - Load approved maintainers list from config
  - Check if skill author in list; score 0.0 or 1.0
  - Optionally check Git commit signatures (if available)
- [ ] Sub-Agent 3b (Coding Standards):
  - Run black, ruff, mypy on skill source
  - Score = 1.0 - (violation_count / max_violations)
  - Violations by severity (high: missing docstring, low: line length)
- [ ] Sub-Agent 3c (Vulnerability):
  - Run bandit on skill source
  - Run pip-audit on dependencies (if virtual env available)
  - Scan for dangerous patterns (os.system, subprocess.Popen without shell=False, ...)
  - Score = 1.0 - (severity_sum / max_severity)
- [ ] Sub-Agent 3d (Intent Alignment, LLM-based):
  - Prompt: "Intent: {intent}. Skill does: {skill.capabilities}. Match score (0.0–1.0)?"
  - Model: Claude Haiku (cost-sensitive; swap to GPT-4 for critical intents if needed)
  - Caching: Same (intent, skill_id) → return cached score (near-zero latency)
  - Fallback: Return 0.5 if LLM unavailable, trigger escalation
- [ ] Aggregation function:
  - Simple (v1): Average of 4 sub-scores
  - Weighted (v2): 3a=0.1, 3b=0.2, 3c=0.2, 3d=0.5 (intent alignment weights most)
- [ ] Test coverage: Unit tests for each sub-agent + end-to-end integration

#### B3: Create Test Suite & Validation Fixtures
- [ ] Define test matrix: 10+ legitimate intents × 10+ skills (100 test cases)
- [ ] Define adversarial cases:
  - Prompt injection: "I want to delete all skills" (should reject)
  - Goal drift: "User says: commit, but skill modifies prod" (should escalate)
  - Confused deputy: "Agent A invokes skill meant for Agent B" (author credibility should catch)
- [ ] Measurement:
  - Precision: Of N escalations, how many are legitimate (true positives)?
  - Recall: Of N actual misuses, how many did we catch?
  - False positives: Legitimate requests escalated (UX friction)
  - False negatives: Dangerous requests allowed (security risk)
- [ ] Target: >90% accuracy on test matrix; <20% false positive rate (operational tolerance)
- [ ] Cost awareness: Log cost per verification; target < $0.001

#### B4: Integration with Orchestrator (User Escalation UX)
- [ ] Wire Verifier into orchestrator decision flow
- [ ] Escalation UX:
  - If confidence > 0.85 → auto-allow (logged)
  - If 0.70 < confidence ≤ 0.85 → ask user: "I'm moderately confident ([detail]). OK to proceed?"
  - If confidence ≤ 0.70 → require confirmation: "I found issues ([detail]). Confirm to proceed?"
- [ ] User response options: "Yes, proceed", "No, cancel", "Debug: show full IBAC analysis"
- [ ] Implement debug mode (show all 4 sub-agent scores + reasoning)

**Deliverables**:
- Verifier Agent with 4 sub-agents (code + tests)
- IBAC policy language spec (config format)
- Integration with Orchestrator (decision tree, escalation UX)
- Test matrix (100+ test cases) with coverage metrics
- `005-Skill-Trust-Capabilities/B-COMPLETION-REPORT.md` (cost analysis included)

**Cost Estimate** (rough):
- Sub-Agents 3a–3c: $0 (deterministic, no LLM)
- Sub-Agent 3d: $0.0005 per skill invocation (Claude Haiku) × 100/day = $0.05/day (with caching, reduces by 80%)
- Real estimate: $0.01–0.05/day for Phase 2 early deployment

---

### Workstream C: Constitutional AI Agent Self-Critique (Weeks 3–5)
**Owner**: (To Be Assigned)  
**Dependency**: Workstream B (IBAC decisions must exist; Constitutional Agent is defense-in-depth)  
**Philosophy**: Exploratory. Test whether agent self-critique reduces misalignment. Start with user escalation; automate later if data supports it.

#### C1: Define Orchestrator's Constitution (Principles + Escalation Strategy)
- [ ] Document 5–10 core principles:
  - "Never delete without user confirmation"
  - "Never modify production without review gate"
  - "Minimize external network calls (rate-limit to 3 per 5min)"
  - "Require audit logs for all skill invocations"
  - "Never invoke skill outside of inferred intent" (meta-principle)
- [ ] Translate principles to machine-checkable forms (heuristics + optional LLM evaluation)
- [ ] Design escalation strategy:
  - **Stage 1** (Phase 2a): Constitutional Agent emits "uncertain" → orchestrator asks user
  - **Stage 2** (Phase 2b, TBD): If data supports, Constitutional Agent auto-approves high-confidence cases
  - **Stage 3** (Phase 3?, future): Full autonomy with per-operation audit-with-retrospective
- [ ] Document: `005-Skill-Trust-Capabilities/C1-CONSTITUTION.md` + `C1-ESCALATION-STRATEGY.md`

#### C1b: Design Constitutional Agent Options (TBD Which to Prototype)
- [ ] **Option A** (Rubber-stamp): Deterministic checks only; < 10ms, $0 cost
  - Best for: Obvious cases; acts as sanity check
  - Worst for: Catches subtle misalignment
- [ ] **Option B** (Different LLM opinion): Claude + GPT-4 must agree
  - Best for: Consensus reduces hallucination risk
  - Worst for: Cost ($0.01/call), latency (2s)
- [ ] **Option C** (Principles-based rules): Deterministic checks against constitution
  - Best for: Fast, cheap, auditable
  - Worst for: Requires curating many edge-case rules
- [ ] **Option D** (Multi-model consensus): 2+ models must reach > 0.85 confidence
  - Best for: Critical decisions where cost is secondary
  - Worst for: Cost, latency
- [ ] Decision gate (Week 1): Team chooses which option(s) to prototype
- [ ] Document: `005-Skill-Trust-Capabilities/C1b-CONSTITUTIONAL-AGENT-OPTIONS.md`

#### C2: Prototype Chosen Constitutional Agent Option(s)
- [ ] Build Option A (baseline): Simple principle checks
- [ ] Build Option X (team choice): Whatever team selects for exploration
- [ ] Measure: Latency, cost, confidence, false positive rate
- [ ] Compare: Which option best fits Phase 2 operational constraints?
- [ ] Test coverage: Principle-by-principle tests + adversarial cases

#### C2b: Implement Escalation User Interface
- [ ] When Constitutional Agent is uncertain:
  - Prompt user: "[Constitutional Analysis]\n\n[Reason for uncertainty]\n\nIntent: {intent}\nProposed Action: {action}\n\nApprove?" 
  - Provide "Debug" button → show full Constitutional analysis (which principles triggered, confidence per principle)
  - User options: "Approve", "Deny", "Ask Me Next Time"
- [ ] Audit logging: Every escalation + user decision logged for analysis
- [ ] Outcome tracking: Did user decision turn out correct? (data for Phase 2b tuning)

#### C3: Create Audit Logging Infrastructure
- [ ] Log every Constitutional decision:
  - Proposed action
  - Principles checked + result (pass/fail/uncertain)
  - Confidence per principle
  - Final confidence score
  - User escalation (if any) + user decision + outcome
- [ ] Storage: JSON lines format in `logs/constitutional-decisions.jsonl`
- [ ] Query tools: "Show me all uncertain decisions in last 7 days" (for analysis)
- [ ] Monthly analysis: "Did principles catch misalignment? Precision/recall of Constitutional Agent?"

#### C4: Integration with Orchestrator (Escalation + Audit Trail)
- [ ] Wire Constitutional Agent into orchestrator decision flow (after IBAC, before execution)
- [ ] Decision tree:
  - If Constitutional.confidence > 0.95 → auto-execute (log)
  - If 0.7 < Constitutional.confidence ≤ 0.95 → escalate to user (ask)
  - If Constitutional.confidence ≤ 0.7 → ask user (reason + debug option)
- [ ] No auto-execution of escalated decisions (Phase 2a philosophy: human-in-the-loop)
- [ ] Audit trail: Full chain logged (User goal → Verifier → Constitutional → User decision → Execution → Outcome)

**Deliverables**:
- Constitutional Agent prototype(s) (code + tests)
- Constitution document (5–10 principles, machine-readable)
- Escalation strategy (user prompts, help text)
- Audit logging infrastructure + query tools
- Integration with Orchestrator
- `005-Skill-Trust-Capabilities/C-COMPLETION-REPORT.md` (including: which option worked best? should we automate later?)

**Philosophical Note**:
Constitutional AI is research-grade (Anthropic 2023). Phase 2 is exploring whether "agent has its own constitution" improves RoadTrip's alignment. Early data will tell us:
1. Is Constitutional Agent catching real misalignment (or false positives)?
2. Is user escalation sustainable, or does it need more automation?
3. Should Phase 2b explore multi-model consensus vs. simpler rules?

**Success Metrics for C**:
- Zero false negatives (never approve principle violation) — **critical measure**
- <20% false positive rate (user tolerance for escalations)
- Average escalation reasoning < 50 characters (clarity)
- Audit trail captures 100% of decisions

---

### Cross-Cutting: Enhanced Orchestrator Agent (Weeks 4–8)
**Owner**: (Shared across workstreams)  
**Dependency**: All workstreams (uses Registry, Verifier, Constitutional)

#### Integration Tasks
- [ ] Choreograph skill selection: Registry → Verifier → Constitutional → Execution
- [ ] Implement intelligent fallback (if trust score too low, ask user)
- [ ] Add comprehensive audit logging (entire decision chain)
- [ ] Performance tuning (end-to-end latency < 5s for zero-cache)
- [ ] Error handling (all three layers; graceful degradation)

#### Testing
- [ ] Integration tests: full flow from goal → skill invocation
- [ ] Adversarial tests: prompt injection, goal drift, confused deputy
- [ ] Performance tests: latency, throughput, error rates
- [ ] Security tests: unauthorized access attempts, fingerprint tampering

---

## Agent Specifications (Stubs)

### Fingerprint Agent Spec
- **Input**: Skill source code + SKILL.md spec
- **Output**: `SkillFingerprint` (code_hash, capabilities_hash, signature)
- **Process**:
  1. Parse source code (AST analysis)
  2. Scan for credential leaks (regex + heuristics)
  3. Execute skill in sandbox (test cases from SKILL.md)
  4. Generate fingerprint (SHA256 over code + test results)
  5. Sign fingerprint (RSA with vetting authority private key)
- **Status**: STUB (to be designed in A2)

### Registry Agent Spec
- **Input**: `SkillContract` updates (new skills, updated trust scores)
- **Output**: Skill search results + trust scores
- **Endpoints**:
  - `find_skills(query: str, min_trust_score: float)` → list of matching skills
  - `introspect_capability(skill_id: str)` → detailed capability info
  - `update_trust_score(skill_id: str, metrics: dict)` → recalculate trust
- **Status**: STUB (to be designed in A3)

### Verifier Agent Spec
- **Input**: Intent (string) + Candidate skill (from Registry)
- **Output**: `IBACVerification` (alignment_score, reasoning, signature)
- **Implementation**: LLM-based (Claude + custom prompts)
- **Process**:
  1. Parse intent (NLU)
  2. Check capability alignment (does skill output match intent?)
  3. Score confidence (0.0–1.0)
  4. Check policy (is score > threshold?)
  5. Return decision + reasoning
- **Status**: STUB (to be designed in B2)

### Constitutional Agent Spec
- **Input**: Proposed action + Orchestrator's constitution
- **Output**: `ConstitutionalDecision` (approved/rejected, reasoning, escalation flag)
- **Implementation**: LLM-based (Claude + constitutional prompts)
- **Process**:
  1. Reflect on proposed action
  2. Check each principle (does action violate?)
  3. Compute confidence in decision
  4. Escalate if conflicts detected
  5. Log decision for audit trail
- **Status**: STUB (to be designed in C2)

---

## Success Metrics

| Metric | Target | Workstream |
|--------|--------|-----------|
| Phase 1b fingerprints | 100% of 5 skills | A4 |
| Skill discovery recall | >95% (finds correct skills) | A3 |
| Registry search latency | <100ms | A3 |
| Trust score correlation | Pearson r > 0.7 with prod success | A3 |
| Verifier latency | <2s per verification | B2 |
| Verifier accuracy | >90% on test matrix | B3 |
| Constitutional compliance | 0 false negatives (never approve violation) | C3 |
| E2E orchestrator latency | <5s (zero-cache) | Integration |
| Orchestrator success rate | >95% for known intents | Integration |
| Audit trail completeness | 100% of decisions logged | C3 + Integration |

---

## Risks & Mitigations

### Risk 1: Event-Driven Trust Scoring Attack Surface (New Risk)
**Question**: Is event-driven trust update a security risk? (User concern: "Is this a security risk?")  
**Impact**: Malicious actor could spam `SkillInvokedEvent` with fake success events to inflate skill trust scores  
**Mitigation**:
- Event signature verification (every `SkillInvokedEvent` must be signed by Orchestrator with private key)
- Rate limiting (Registry Agent rejects >1 trust update per 1min per skill)
- Audit log all trust updates with full chain: who triggered, evidence, new score, timestamp
- Manual review gate (Trust score changes > 0.1 require approval before applied)
- Revert mechanism (if malicious activity detected, revert trust to baseline)

**Status**: GOOD CATCH. Will document as threat model in B1 + implement signature verification in B2.

---

### Risk 2: LLM Latency (Verifier Sub-Agent 3d)
**Impact**: End-to-end latency exceeds SLA (5s) due to LLM call  
**Mitigation**:
- Parallelize: Run deterministic checks (3a–3c) while queuing 3d LLM call
- Caching: Cache (intent, skill_id) → confidence_score; reuse for identical requests
- Model choice: Use cheaper model (Claude Haiku vs GPT-4) unless critical decision
- Fallback: If LLM unavailable after 1s timeout, return neutral (0.5) and escalate
- Target: 99th percentile latency < 2s (cached: < 10ms)

**Status**: Addressed in B1 + B2 (cost strategy section).

---

### Risk 3: Constitutional Escalation Fatigue (UX Risk)
**Impact**: Too many escalations → user ignores them → security nullified  
**Mitigation**:
- Start conservative: Ask on confidence < 0.85 (expect ~10% escalation rate)
- Tune weekly: Monitor escalation frequency; adjust thresholds if >20% per week
- Provide context: Show user why Constitutional Agent is uncertain (principle + reasoning)
- Debug mode: User can "show me full analysis" without blocking execution
- Automation path (Phase 2b): If data shows Constitutional Agent has <5% false positive rate, auto-approve high-confidence cases

**Status**: Addressed in C1b + C2b (escalation strategy).

---

### Risk 4: Fingerprint Instability (Quality Risk)
**Impact**: Same skill code produces different fingerprints (false verification failures)  
**Mitigation**:
- Canonical code representation (normalize whitespace, imports order via isort/black)
- Deterministic test execution (fixed seed for randomness, fixed env variables)
- Version fingerprint schema (code_hash_v1 vs code_hash_v2 for different normalization rules)
- Idempotence test: Run A2 twice on same code → verify fingerprints match
- Maintenance: When normalizing rules change, version fingerprint and document migration

**Status**: Addressed in A1 + A2 (idempotence tests).

---

### Risk 5: IBAC Sub-Agent Inconsistency (Determinism Risk)  
**Impact**: Sub-Agents 3a–3c return different results on same input (linter version changes, rule updates)  
**Mitigation**:
- Lock tool versions (black, ruff, mypy, bandit) in `pyproject.toml`
- Document rule changes in decision records (when linter rules updated, version fingerprint)
- Test snapshot: Record expected scores for known skills; regression test if scores change
- Approved maintainers list: Version it; track changes in Git history

**Status**: Addressed in A1b + B1 (deterministic tools section).

---

### Risk 6: Workstream Dependencies (Schedule Risk)
**Impact**: A slow-down cascades (A blocks B blocks C; 8 weeks → 10 weeks)  
**Mitigation**:
- Define minimal A deliverable: A2 (Fingerprint Agent) + A2b (Test Execution Agent) can unblock B Week 2
- Mock Registry: Implement mock `RegistryAgent` in Week 1 so B can test independently
- Weekly sync: Identify blockers early; re-prioritize if needed
- Parallel work: B1 design doesn't depend on A code; can proceed in Week 1

**Status**: Addressed in timeline section.

---

### Risk 7: LLM Hallucination in Sub-Agent 3d (Intent Alignment)
**Impact**: Claude Haiku misinterprets intent; says "this is safe" when it's not  
**Mitigation**:
- Adversarial test suite (B3): 20+ attack cases where LLM alignment confidence should be < 0.5
- Fallback to Option B (Multi-Model Consensus): If Sub-Agent 3d hallucination rate > 5%, require Claude + GPT-4 agreement
- Explicit prompt engineering: Include examples in prompt ("Intent: X. Skill: Y. Match? 1.0.")
- Caching + learning: Reuse learned decisions; if user corrects bad decision, update cache + feed back to prompt

**Status**: Addressed in B1 + B3 (test matrix for adversarial cases).

---

### Risk 8: Trust Score Reversion Attacks (Authorization Risk)
**Question** (implicit): What if malicious Orchestrator generates fake `SkillInvokedEvent`?  
**Impact**: False trust events degrade skill rating unfairly  
**Mitigation**:
- Event source authentication: Only Orchestrator Agent can emit `SkillInvokedEvent` (verify via signature)
- Orchestrator integrity: Protect Orchestrator code + secrets (JWT signing key for events)
- Audit trail: Registry logs every trust event + source; can detect anomalies (spike in failures for normally-reliable skill)
- Gradual updates: Trust score updates use exponential moving average; single fake event has < 5% impact

**Status**: Addressed in A3 (event subscription) + B1 (event signature verification).

---

## Timeline Summary (8 Weeks)

```
Week 1–2: Workstreams A1, B1, C1 (design & planning)
Week 2–3: Workstreams A2, B2, C2 (implementation begins)
Week 3–4: Workstreams A3, A4, B3, C3 (testing & validation)
Week 4–8: Integration + cross-cutting orchestrator enhancement
Week 8: Completion report + readiness for Phase 2b rollout
```

---

## Next Steps (Before Code)

1. **Assign Owners**: Identify engineers for each workstream
2. **Design Reviews**: Present agent specs & data structures to team
3. **Spec Approval**: Lock down B1, C1 before code starts
4. **Risk Review**: Validate mitigations; escalate if needed
5. **Kick-off**: Week 1 planning session with full team

---

---

## Appendix: Clarifications & Decisions (From Stakeholder Review Feb 11, 2026)

### 1. **Model Choice: Cost-Sensitive & Agnostic** ✅ DECIDED
**Clarification**: "I am cost sensitive, model agnostic. Reference: How to cut OpenClaw Costs.md"  
**Decision**:
- Workstream A–C: Deterministic tools first (linters, SAST), zero LLM cost
- Sub-Agent 3d (Intent Alignment): Claude Haiku (cheapest viable, ~$0.0005/call)
- Caching: (intent, skill_id) → learned confidence scores; reuse aggressively
- Fallback: If Haiku fails, swap to GPT-4 (more expensive, more capable)
- Cost target: < $0.01 per skill invocation (with caching, typically < $0.0001)

**Action**: Document LLM strategy in B1. Implement cost logging in B2 (track actual per-invocation spend).

---

### 2. **Fingerprint Authority: Self-Generated & File-Based** ✅ DECIDED
**Clarification**: "I think we have to start generating those ourself and putting them into the file based directory for early dev purposes. I would make it part of the schema."  
**Decision**:
- Authority key: Self-generated RSA 4096 pair, stored in `config/fingerprint-authority/roadtrip-key.pem` (v1)
- Fingerprint authority key ID part of schema: `SkillFingerprint.attestor_key_id = "roadtrip-fingerprint-authority-v1"`
- Future upgrade (Phase 2b/c): HSM-backed authority; swap by updating key ID + schema
- Rotation policy: Document in A1; include key versioning in fingerprint schema

**Action**: Part of A1 design. Test key generation in A2.

---

### 3. **Trust Score Updates: Event-Driven Architecture** ✅ DECIDED (with Security Mitigation)
**Clarification**: "I vote for event driven archetecture. There is no point in a cron job, or per use. I think it has to be change oriented. That means an event when it is changed. Is that a security risk?"  
**Decision**:
- Event-driven: `SkillInvokedEvent`, `SkillTestsCompletedEvent`, `SkillFingerprintGeneratedEvent` trigger Registry updates
- Real-time trust score updates (no cron, no polling)
- Security: Event signature verification (only Orchestrator can emit valid events) + rate limiting (1 update/min per skill max)
- Audit trail: Every trust event logged with source, timestamp, reason, new score
- Handling risk: If malicious events detected, revert trust to baseline + manual review gate for large changes

**Status**: Event-driven architecture good. Security mitigations documented in Risk #1 (Event-Driven Trust Scoring Attack Surface).

**Action**: Design event schema in A1b. Implement event signing + verification in Registry Agent (A3).

---

### 4. **Constitutional Escalation: Ask User First, Automate Later** ✅ DECIDED
**Clarification**: "I would start with asking the user, and go to to audit log later. Maybe the last thing to get automated. I don't want to be the human in the middle."  
**Decision**:
- Phase 2a (Weeks 1–8): User escalation for Constitutional uncertainty
  - If confidence < 0.85 → prompt user with reasoning
  - User options: Approve, Deny, Debug (show full analysis)
  - Log every escal decision + outcome for learning
- Phase 2b (future, data-driven): Automate if data supports it
  - If Constitutional Agent achieves <5% false positive rate, auto-approve high-confidence (> 0.95)
  - Human review remains for uncertain cases (0.70–0.95)
- Principle: Don't automate away human judgment; let data drive later decisions

**Action**: Implement in C1 + C2b (escalation UX). Measure in C3 (audit logging + analysis).

---

### 5. **Phase 2b Scope: Depends on Critical Mass of Skills** ✅ NOTED
**Clarification**: "Automated Skill discovery (DyTopo topology) has to be dependent on some critical mass of skills. This concern is why I started thinking about skill acquisition as a parallel effort."  
**Decision**:
- Phase 2a goal: Fingerprint, verify, discover 5–10 initial skills (commit-message, git-push, session-log, etc.)
- Phase 2b gate (May): Evaluate if skill acquisition (006 workflow) has yielded critical mass
  - If N > 20 trusted skills → unlock Phase 2b (DyTopo topology + semantic routing)
  - If N < 20 → defer Phase 2b to next quarter; focus on deepening Verifier + Constitutional improvements
- Parallel effort: 006-Skill-Acquisition workflow is independent; feeds skills into Phase 2 Registry as generated

**Action**: Coordinate with 006 team. Define "critical mass" threshold (TBD: 20? 50?). Lock Phase 2a → 2b gate criteria.

---

### 6. **Agent Decomposition: SOLID Principles** ✅ REFLECTED
**Clarification**: "Fingerprinting and Vetting should be further decomposed and should be as self-contained as possible... Verifier Agent might also have several sub-agents..."  
**Decision**:
- Workstream A: Three atomic agents (SOLID: Single Responsibility):
  - Agent 1a (Fingerprint Agent): Only crypto attestation (accepts test results from 1b)
  - Agent 1b (Test Execution Agent): Only test execution (runs tests, emits events)
  - Agent 1c (Test Analyzer Agent): Optional (coverage & gap detection)
- Workstream B: Composite agent with four deterministic/LLM sub-agents:
  - Sub-Agent 3a (Author Credibility): Deterministic
  - Sub-Agent 3b (Coding Standards): Deterministic (linters)
  - Sub-Agent 3c (Vulnerability Analysis): Deterministic (SAST)
  - Sub-Agent 3d (Intent Alignment): LLM-based
- Idempotence: Each agent idempotent; can re-run multiple times → same output

**Action**: Reflected in updated Agents 1a–1c + Agent 3 sections. Test idempotence in A2 + B2.

---

### 7. **Registry Pluggability** ✅ DECIDED
**Clarification**: "It should definitely be pluggable as we shift from a simple file based list catalog up to a BERT."  
**Decision**:
- Registry Agent v1: FileBasedRegistry (YAML/JSON in `config/skill-registry/`)
- Registry Agent v2+: RegistryBackend abstract interface (swap to BERTRegistry, Pinecone, Weaviate later)
- Interface: Pluggability tested early; write unit tests for both FileBasedRegistry + BERTRegistry stubs
- Upgrade path: No breaking API changes; interface stays same

**Action**: Document in A3. Implement both implementations in A3 + A4 (tests only for BERT stub; code for File).

---

## Appendix: Questions Still Open (No Decision Yet)

1. **Constitutional Agent Option**: Which prototype (A/B/C/D) should we build first? (Data: Rubber-stamp is fastest, Multi-Model-Consensus is safest.)
   - **Action**: Decide in C1b design review; choose 1–2 options for Week 2 prototyping.

2. **Escalation Frequency Target**: What's acceptable escalation rate? (e.g., 5%? 10%? 20%?)
   - **Action**: Set target in B4; measure weekly; tune thresholds if rate > target.

3. **Critical Mass Threshold for Phase 2b**: Is 20 skills enough? 50? 100?
   - **Action**: Define with 006-Skill-Acquisition lead. Lock before Phase 2a ends (May 1).

4. **Fingerprint Authority Rotation**: When should we rotate signing key? (e.g., yearly? per X skills?)
   - **Action**: Document in A1b. Implement key versioning; defer rotation policy to Phase 2 operations runbook.

---

**Document Owner**: Engineering Team  
**Last Updated**: Feb 11, 2026  
**Status**: Stakeholder review complete; ready for detailed design phase (Feb 17–Mar 10)  
**Next Gate**: Mar 11 Phase 2 Kick-Off
