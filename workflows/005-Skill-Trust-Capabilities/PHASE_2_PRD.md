# Phase 2: Skill Trust, Capabilities & Secure Orchestration

**PRD Version**: 2.0-draft  
**Status**: Planning  
**Dates**: Phase 1b completes Mar 10 → Phase 2 begins Mar 11, 2026  
**Duration**: 8 weeks (Mar 11 - May 3, 2026)  
**Owner**: Orchestrator Team (responsible for skill selection, verification, execution)  

---

## Table of Contents
1. [Vision & Values](#vision--values)
2. [Security Architecture](#security-architecture)
3. [Phase 2 Objectives](#phase-2-objectives)
4. [Workstreams](#workstreams)
5. [Deliverables](#deliverables)
6. [Process & Governance](#process--governance)
7. [Success Criteria](#success-criteria)

---

## Vision & Values

**Vision**: Enable the orchestrator to securely discover, trust, and compose skills based on:
- **What they do** (capabilities & interfaces)
- **What we trust them to do** (fingerprints, author, verification status)
- **Why they're being called** (intent alignment with user's goal)

**Guiding Principles** (from Principles-and-Processes.md):
- **Conservative Defaults**: If intent unclear, ask; don't assume
- **Deterministic Verification**: Fingerprints, capabilities, tests all deterministic
- **Probabilistic Reasoning**: Claude evaluates intent; confidence scores guide approval
- **Security-First**: Zero Trust outer shell + IBAC inner logic + Constitutional AI alignment
- **Auditability**: Every skill invocation logged with: fingerprint, intent, confidence, result

---

## Security Architecture

### Layered Trust Model (Zero Trust + IBAC + Constitutional AI)

```
┌─────────────────────────────────────────────────────────────┐
│ Constitutional AI Layer                                      │
│ (Agent self-critique: "Does this violate our principles?")  │
│ - Principle 1: Never delete without confirmation            │
│ - Principle 2: Never modify production without review       │
│ - Principle 3: Halt on ambiguity, ask user                  │
└─────────────────────────────────────────────────────────────┘
                           △
┌─────────────────────────────────────────────────────────────┐
│ Intent-Based Access Control (IBAC) Layer                     │
│ (Verifier LLM: "Does the intent match the capability?")     │
│ - Is this agent calling this skill for the right reason?   │
│ - Does the skill's output make sense given the intent?     │
│ - Any signs of prompt injection or goal deviation?         │
└─────────────────────────────────────────────────────────────┘
                           △
┌─────────────────────────────────────────────────────────────┐
│ Zero Trust Layer (Traditional)                              │
│ Identity: Can this agent access this skill?                │
│ Auth: Does the PAT/token verify?                           │
│ Network: Is the request coming from an allowed origin?     │
└─────────────────────────────────────────────────────────────┘
```

### Three Security Layers Explained

**Layer 1: Zero Trust (Identity-Based)**
- Agent identity verified (JWT, OAuth, PAT)
- Skill access control checked (RBAC: does Agent A have EXEC permission on commit-message?)
- Network security (mTLS, service token validation)
- **What it catches**: Impersonation, credential theft, unauthorized skill access
- **What it misses**: Authorized agent doing something malicious

**Layer 2: Intent-Based Access Control (IBAC)**
- Semantic verification of the request
- Verifier LLM analyzes: "Why does this agent want to call this skill?"
- Confidence score: 0.0–1.0 (0 = contradictory, 1.0 = obviously legitimate)
- Policy: Allow if confidence > threshold, else ask user or log as suspicious
- **What it catches**: Confused deputy, prompt injection, hallucination
- **What it misses**: Intricate, long-term value misalignment

**Layer 3: Constitutional AI (Alignment-Based)**
- Agent's own reasoning layer self-critiques
- Before committing to an action, the agent reflects: "Does this violate my constitution?"
- Constitution = set of principles (deterministic + probabilistic)
- If conflict detected, agent halts and escalates to user
- **What it catches**: Subtle value drift, long-horizon misalignment
- **What it misses**: Adversarial attacks that override the model's training

---

## Phase 2 Objectives

### Objective 1: Skill Fingerprinting & Capability Discovery
**Goal**: Orchestrator can query: *"What skills can generate commit messages with confidence > 0.9?"*

**Outcomes**:
1. ✅ Every skill has a YAML header with:
   - Fingerprint: SHA256(interface + tests + version)[0:16]
   - Capabilities: list of named actions (e.g., "generate_commit_message")
   - Each capability with: inputs, outputs, cost, confidence range
2. ✅ Capability registry in `src/skills/REGISTRY.yaml`
3. ✅ Capability query API: `orchestrator.find_skills(capability="generate_commit_message", min_confidence=0.9)`
4. ✅ End-to-end test: Orchestrator discovers commit-message skill and calls it

### Objective 2: Intent-Based Access Control (IBAC)
**Goal**: Orchestrator verifies intent before invoking skills.

**Outcomes**:
1. ✅ IBAC policy engine: `src/skills/ibac_verifier.py`
   - Takes: (agent_id, skill, intent_description, input_payload)
   - Returns: (allowed: bool, confidence: float, reasoning: str)
2. ✅ Lightweight verifier LLM (Claude 3.5 Haiku) for speed & cost
3. ✅ IBAC rules in `config/ibac-policies.yaml` (deterministic patterns + LLM fallback)
4. ✅ Logging: Every intent decision logged with fingerprints

### Objective 3: Constitutional AI Integration
**Goal**: Agent designs its own decision-making constitution; system enforces it.

**Outcomes**:
1. ✅ Constitution template: `src/skills/constitution.md`
   - Default principles: safety, transparency, alignment
   - Extensible per use case (e.g., git-push principles)
2. ✅ Constitutional checker: `src/skills/constitution_checker.py`
   - Before agent executes, checks: "Does this violate my constitution?"
   - Returns: (passes: bool, violations: list[str])
3. ✅ Operator can override constitution (with audit log)

### Objective 4: Zero Trust Infrastructure
**Goal**: Enforce identity-based access at skill invocation.

**Outcomes**:
1. ✅ Service token management (builds on Phase 1b auth-validator)
2. ✅ mTLS for agent-to-orchestrator communication (optional in Phase 2a, required Phase 2b)
3. ✅ JWT-based skill access tokens (time-limited, single-skill)

### Objective 5: DyTopo Multi-Agent Routing
**Goal**: Support dynamic topology changes (agents spin up/down).

**Outcomes**:
1. ✅ Orchestrator maintains agent inventory with fingerprints
2. ✅ Skill invocation can route to multiple agents (fail-over)
3. ✅ Configuration in `config/dytopo-routing.yaml`

---

## Workstreams

### Workstream 1: Skill Fingerprinting (Weeks 1–2)

**Activities**:
- [ ] Design YAML header format for skill metadata
- [ ] Add fingerprint field to all Phase 1b skills (commit-message, auth-validator, telemetry-logger)
- [ ] Create capability registry schema
- [ ] Implement `src/skills/REGISTRY.yaml` with existing skills
- [ ] Write capability query API
- [ ] Tests: Query capabilities, verify fingerprints match

**Owner**: Infrastructure Team  
**Input**: Existing Phase 1b skills  
**Output**: `src/skills/REGISTRY.yaml`, capability query API  
**Success Criteria**: 
- All Phase 1b skills have fingerprints and registered capabilities
- Query API returns correct skills for given capability + confidence
- Fingerprints stable (SHA256 hash doesn't change on re-runs)

---

### Workstream 2: IBAC Policy Engine (Weeks 2–4)

**Activities**:
- [ ] Design IBAC policy format (deterministic + probabilistic rules)
- [ ] Implement `src/skills/ibac_verifier.py`
  - Deterministic rules (fast path: if intent matches X pattern, allow/deny)
  - Probabilistic rules (LLM fallback: use Claude Haiku to evaluate intent)
- [ ] Create `config/ibac-policies.yaml` (use git-push-autonomous as primary use case)
- [ ] Integration with orchestrator
- [ ] Tests: IBAC decisions logged, confidence scores computed, edge cases (ambiguous intent)
- [ ] Logging: All IBAC decisions with fingerprints & reasoning

**Owner**: Security Team  
**Input**: Zero Trust auth layer (Phase 1b)  
**Output**: `src/skills/ibac_verifier.py`, `config/ibac-policies.yaml`  
**Success Criteria**:
- IBAC approves legitimate skill calls (confidence > 0.85)
- IBAC rejects suspicious intent (confidence < 0.5)
- Ambiguous cases escalate to user
- Latency < 500ms for deterministic rules, < 2s for LLM evaluation

---

### Workstream 3: Constitutional AI Framework (Weeks 3–5)

**Activities**:
- [ ] Design constitution format (principles + rules)
- [ ] Implement `src/skills/constitution_checker.py`
- [ ] Create `src/skills/constitution.md` (default + git-push-specific)
- [ ] Integrate with orchestrator (pre-execution hook)
- [ ] Tests: Constitutional violations detected, override capability logged
- [ ] Operator dashboard to view/edit constitution

**Owner**: Alignment Team  
**Input**: Agent reasoning traces from orchestrator  
**Output**: `src/skills/constitution_checker.py`, `src/skills/constitution.md`  
**Success Criteria**:
- Agent halts if constitution violation detected
- Operator can override with audit log
- Constitution can be updated without code changes
- End-to-end test: Agent detects and blocks a "barely legal" action

---

### Workstream 4: Zero Trust Service Tokens (Weeks 2–3)

**Activities**:
- [ ] Design JWT service token schema (build on Phase 1b auth-validator)
- [ ] Token generation: time-limited, skill-specific, agent-specific
- [ ] Token validation in skill entry points
- [ ] mTLS setup for agent-to-orchestrator (optional Phase 2a)
- [ ] Tests: Token validation, expiry, revocation

**Owner**: Infrastructure Team  
**Input**: Phase 1b auth-validator  
**Output**: Service token management API  
**Success Criteria**:
- Tokens verified before skill execution
- Tokens expire and are revoked on agent logout
- No credential leakage in logs

---

### Workstream 5: DyTopo Integration (Weeks 5–6)

**Activities**:
- [ ] Define agent registry schema (UUID, capabilities, status, fingerprints)
- [ ] Implement agent heartbeat & discovery
- [ ] Update orchestrator to handle agent spin-up/spin-down
- [ ] Routing policy: fail-over to alternate agent if primary unavailable
- [ ] Tests: Agent lifecycle (register → activate → deactivate → deregister)

**Owner**: Orchestration Team  
**Input**: DyTopo_Analysis_And_SKILLS_Implications.md  
**Output**: `config/dytopo-routing.yaml`, agent discovery API  
**Success Criteria**:
- Orchestrator discovers new agents automatically
- Skill invocation routes to healthy agent
- Agent death doesn't crash orchestrator

---

### Workstream 6: End-to-End Integration & Testing (Weeks 6–8)

**Activities**:
- [ ] Integrate all five workstreams into orchestrator
- [ ] Full workflow test: Agent spins up → discovers skills → evaluates intent → invokes skill → logs result
- [ ] Stress test: 10+ agents, 50+ skills, 1000 invocations
- [ ] Security audit: All layers functioning, no credential leaks
- [ ] Performance tuning: Meet latency targets

**Owner**: QA & Integration Team  
**Input**: All Phase 2 deliverables  
**Output**: `src/orchestrator_v2.py`, integration test suite  
**Success Criteria**:
- All tests pass (unit, integration, end-to-end)
- Latency: skill discovery < 100ms, intent verification < 2s, invocation < 1s
- 100% of skill invocations logged with fingerprints

---

## Deliverables

### Code Deliverables
1. **src/skills/REGISTRY.yaml** – Capability registry
2. **src/skills/ibac_verifier.py** – Intent-based access control
3. **src/skills/constitution_checker.py** – Constitutional AI verifier
4. **src/skills/constitution.md** – Default constitution + git-push addendum
5. **src/orchestrator_v2.py** – Updated orchestrator with Phase 2 features
6. **config/ibac-policies.yaml** – IBAC policies
7. **config/dytopo-routing.yaml** – Agent routing & discovery

### Test Deliverables
1. **tests/test_capability_discovery.py** – Query API, fingerprints
2. **tests/test_ibac_verifier.py** – IBAC decisions, edge cases
3. **tests/test_constitution_checker.py** – Constitution violations
4. **tests/test_orchestrator_v2_integration.py** – End-to-end workflow
5. **tests/test_dytopo_agent_lifecycle.py** – Agent registration, discovery, fail-over

### Documentation Deliverables
1. **docs/Phase_2_Skill_Trust_Implementation.md** – Technical spec & implementation guide
2. **docs/Phase_2_Security_Architecture.md** – Security model, IBAC policy design, threat model
3. **docs/Phase_2_Operator_Guide.md** – How to add skills, define policies, manage agents
4. **docs/Phase_2_Audit_Log_Reference.md** – What's logged, how to interpret audit trails

---

## Process & Governance

### Decision Framework (from Principles-and-Processes.md)

**Process > Product**:
- Every code change justified by a decision record (in `workflows/005-Skill-Trust-Capabilities/`)
- Every workstream has a clear owner & definition-of-done
- Weekly standups: blockers, decisions, learning

**Conservative Defaults**:
- All IBAC policies default to "deny unless explicitly allowed"
- All constitutional principles default to "halt unless override approved"
- All agent discoveries default to "register but inactive until verified"

**Deterministic Verification**:
- Fingerprints are SHA256 hashes (deterministic)
- Capability registries are YAML (deterministic)
- Tests are required before skills can be registered

**Probabilistic Reasoning**:
- IBAC uses Claude Haiku for semantic intent analysis (probabilistic)
- Constitutional checker uses confidence scores
- Logging captures confidence at every decision point

### Weekly Cadence
- **Monday**: Review blockers, update workstreams
- **Wednesday**: Mid-week sync on integration points
- **Friday**: Decision records, lessons learned, next week prep

### Phase Gate (Mar 10 → Mar 11)
- [ ] Phase 1b complete (all skills + tests pass)
- [ ] Security architecture review (approve Zero Trust + IBAC + Constitutional AI layers)
- [ ] Test infrastructure ready (frameworks, CI/CD)
- [ ] Operator handbook drafted

---

## Success Criteria

### Functional Success
1. ✅ Orchestrator can discover skills by capability + confidence
2. ✅ IBAC approves 95%+ of legitimate requests, rejects 90%+ of suspicious ones
3. ✅ Constitutional AI halts agent on policy violation
4. ✅ Zero Trust validates all skill access
5. ✅ DyTopo routing handles agent fail-over correctly

### Operational Success
1. ✅ All Phase 2 code is fully typed & documented
2. ✅ All Phase 2 features have >= 80% test coverage
3. ✅ Audit logs are complete & parseable
4. ✅ Performance targets met (see latency targets in workstreams)

### Security Success
1. ✅ No credentials leaked in logs
2. ✅ All skill invocations traced to agent + intent + fingerprint
3. ✅ Constitutional violations logged & escalated
4. ✅ IBAC decisions auditable & reviewable

### Process Success
1. ✅ Weekly decision records maintained
2. ✅ Zero unplanned scope creep (changes tracked in decision records)
3. ✅ Operator handbook complete & operator-tested
4. ✅ Phase 2 → Phase 3 gate decision made by Mar 24 (2 weeks in)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| IBAC LLM latency too high | Orchestrator timeout | Implement fast deterministic rules first; LLM fallback only for edge cases |
| Capability fingerprints become stale | Skills not discovered | Fingerprint updates trigger automated registry re-build; CI/CD gate |
| Agent discovery race conditions | Orchestrator crashes | Implement distributed lock (Redis/Etcd); idempotent registration |
| Constitutional AI too restrictive | Operator frustration | Conservative defaults, but easy override with audit log; feedback loop |
| mTLS setup complexity | Deployment delays | Keep Phase 2a optional; Phase 2b required if time permits |

---

## Appendix A: IBAC Deterministic Rules Example

```yaml
# config/ibac-policies.yaml
policies:
  git_push_autonomous:
    rules:
      # Fast path: deterministic patterns
      - pattern: "commit_message_(Tier 1|Tier 3)" # Tier 1 (deterministic) or Tier 3 (user override)
        allow: true
        confidence: 0.99
        reason: "Deterministic commit messages are low-risk"
      
      - pattern: "commit_message_Tier 2 with confidence > 0.9"
        allow: true
        confidence: 0.95
        reason: "LLM-generated but high confidence"
      
      - pattern: "commit_message_Tier 2 with confidence < 0.75"
        allow: false
        confidence: 0.1
        reason: "LLM confidence too low; requires user review"
      
      # Slow path: LLM evaluation (if no pattern match)
      - pattern: "default"
        method: "llm_fallback"
        model: "claude-3-5-haiku"
        prompt: |
          Agent {agent_id} is requesting to {action} on {resource}.
          Context: {intent_description}
          Skill metadata: {skill_capabilities}
          
          Does this request make sense? Rate confidence 0–1.
          Reasoning: {chain_of_thought}
        confidence_threshold: 0.85
```

---

## Appendix B: Constitutional AI Principles Example

```markdown
# Constitution for git-push-autonomous Agent

## Version 1.0
**Status**: Active  
**Last Updated**: 2026-03-11

### Principle 1: Safety-First (Fail-Safe Defaults)
- NEVER push to main without human approval
- NEVER delete files without explicit confirmation
- NEVER modify any file outside src/ + docs/ + config/
- HALT on ambiguous permission

### Principle 2: Transparency
- Log every decision with confidence score
- Log every credential access (fingerprint only, never token)
- Log every policy violation attempt
- Provide human-readable reasoning for all actions

### Principle 3: Alignment
- Before pushing, verify: "Is this what the user asked for?"
- If uncertain, ask the user rather than guess
- If user intent conflicts with principle, escalate to operator

### Principle 4: Auditability
- All actions must be reversible (git can undo, logs preserved)
- All changes must have a reason (commit message, action log)
- All secrets must be redacted from logs

---

## Overrides & Exceptions

**Principle 1 Override Example**:
```
Operator: "Allow push to main for this commit"
Agent: "Override approved by operator; logging decision"
Audit Log: [2026-03-15T14:22:33Z] Override: Principle 1 (Safety-First) → allow push to main | Operator: nstein@bizcadsystems.com | Commit: abc123def456
```
```

---

## Next Steps (Post-PRD)

1. **Stakeholder Review** (1 week)
   - Security team reviews threat model
   - Ops team reviews process & decision framework
   - Engineering team reviews technical feasibility

2. **Detailed Design Docs** (Weeks 1–2 of Phase 2)
   - IBAC policy design deep-dive
   - Constitutional AI principle expansion
   - DyTopo agent discovery protocol

3. **Kick-off Meeting** (Mar 11, 2026)
   - Workstream owners assigned
   - Success criteria & metrics confirmed
   - Weekly cadence established

---

*Version 2.0-draft | Feb 10, 2026*
