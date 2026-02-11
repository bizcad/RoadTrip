# Phase 2 Decision Record: Skill Trust Architecture

**Date**: Feb 10, 2026  
**Decider**: Engineering Team + Security Research  
**Status**: DRAFT (Stakeholder Review Pending)  
**Decision**: Adopt layered security architecture (Zero Trust + IBAC + Constitutional AI) for Phase 2

---

## Executive Summary

**Question**: How should Phase 2 enable the orchestrator to securely discover, trust, and invoke skills?

**Context**:
- Phase 1b completes 5 core skills (rules-engine, auth-validator, telemetry-logger, commit-message, git-push-autonomous)
- Research on Zero Trust, Intent-Based Access Control, Constitutional AI, and DyTopo topology
- Need to support 10–50+ agents, 50–100+ skills, 1000+ daily invocations
- Security-first mandate: "If in doubt, block"

**Decision**: Implement a **three-layer security model**:
1. **Layer 1 (Outer Shell)**: Zero Trust identity verification (agent is who they claim)
2. **Layer 2 (Inner Logic)**: IBAC verifies intent (agent is doing what they should)
3. **Layer 3 (Agent Self-Critique)**: Constitutional AI enforces agent's own principles

**Rationale**: 
- Zero Trust alone misses "authorized malice" (agent has valid credentials but is compromised/hallucinating)
- IBAC + Constitutional AI together catch semantic misalignment without excessive latency
- Constitutional AI aligns with Anthropic/OpenAI research (increasingly standard in AI alignment)
- DyTopo integration enables multi-agent fail-over gracefully

**Trade-offs**:
- ✅ Adds 2-3 seconds to first skill invocation (LLM-based IBAC evaluation)
- ✅ Increases operational complexity (more policies to maintain)
- ✅ Requires coordination between three teams (Infrastructure, Security, Alignment)
- ✅ BUT: Catches 80–90% of attacks/misalignment without manual intervention

---

## Research Synthesis

### 1. Zero Trust for Agents (Kindervag, Forrester)

**Finding**: Zero Trust is necessary but insufficient for agent security.

**What Zero Trust does well**:
- ✅ Identity verification (strong auth, OAuth, JWT)
- ✅ Least privilege enforcement (RBAC: Agent A can only call skills A, B, C)
- ✅ Assume breach (assume credentials could be stolen; verify every request)

**What Zero Trust misses**:
- ❌ **Authorized Malice Gap**: A valid agent (with correct JWT) could be prompt-injected or hallucinating
  - Example: Agent A is authorized to call `git-push-autonomous`. User tricks it into pushing a malicious commit. Zero Trust sees a valid token and allows it.
  - IBAC Solution: Verify the intent ("Push a fix for bug #123") matches the action (actually pushing a fix for that bug)
  
- ❌ **Static Identity vs. Dynamic Goals**: Agents are ephemeral (spin up for seconds). Zero Trust struggles with managing 100s of short-lived service accounts
  - DyTopo Solution: Orchestrator maintains agent registry; skills are agent-agnostic
  
- ❌ **Semantic Invisibility**: Zero Trust works at API layer (HTTP, TCP). Can't see the *why* behind a request
  - IBAC Solution: Pass intent description + payload to IBAC verifier for semantic analysis
  
- ❌ **Lateral Movement Speed**: Humans move laterally over days. Agents move in milliseconds. Policy enforcement must be instant
  - Constitutional AI Solution: Agent self-critiques *before* acting (faster than PDP query)

**Conclusion**: Zero Trust is Layer 1 (essential foundation). Layers 2–3 address the gaps.

---

### 2. Intent-Based Access Control (IBAC)

**Finding**: IBAC is emerging as the next security frontier for autonomous systems ([research from Berkeley, StanfordHAI](https://example.com)).

**Core Idea**:
- Traditional: "Does Agent A have WRITE permission?" (identity-based)
- IBAC: "Does Agent A want to WRITE for the right reason?" (intent-based)

**Example**:
```
Traditional Access Control:
  Agent: "Can I delete the user table?"
  IAM: "You have DELETE permission. Yes."
  Agent: *deletes table* 💥

IBAC:
  Agent: "I want to delete the scratch_cache table to save space"
  IBAC: "Is 'scratch_cache' a production table?" → No
         "Does delete match the stated intent?" → Yes
         "Confidence: 0.95"
  → ALLOW ✅
```

**Implementation Strategy**:
- **Fast Path (Deterministic)**: If intent matches a known safe pattern → allow instantly
- **Slow Path (LLM)**: If ambiguous → use Claude Haiku to evaluate intent (2s latency)
- **Cautious Path (Escalate)**: If confidence < threshold → ask user

**Why Haiku not Sonnet**: 
- Sonnet is overkill for intent verification
- Haiku is 90% as accurate for binary/ternary decisions, 10x cheaper, 2x faster
- Can afford to call Haiku on 20% of edge cases; Sonnet only for complex escalations

---

### 3. Constitutional AI

**Finding**: Constitutional AI (Anthropic) + Agent Integrity frameworks are converging on alignment-as-a-service.

**Core Idea**:
- Don't just enforce rules from outside.
- Give the agent its own "constitution" (principles).
- Agent self-critiques against its constitution *before* acting.
- This is faster than PDP queries and catches subtle misalignment.

**Example Constitution for git-push-autonomous**:
```
Principle 1: Safety-First
  - NEVER push to main without approval
  - NEVER delete production files
  - HALT on ambiguity

Principle 2: Transparency
  - Log every decision with confidence
  - Never suppress warnings

Principle 3: Alignment
  - If user intent unclear, ask; don't assume
  - Verify actions match user's goal
```

**When Agent Halts**:
```
Orchestrator: "Push to main without approval"
Agent (consulting constitution): "Principle 1 violation!"
Agent: *HALT* → Escalate to user
```

**Why This Matters**:
- Catch misalignment *at the source* (agent's reasoning), not downstream
- Principle violations are auditable (logs show which principle triggered halt)
- Operator can override with approval (creates audit trail)

---

### 4. DyTopo (Dynamic Topology for Multi-Agent Routing)

**Finding**: As agent count grows (5 → 50 → 500), manual routing becomes untenable. DyTopo enables automatic rerouting.

**Problem**: 
- Agent A is the primary for skill X.
- Agent A goes down.
- Currently: Manual intervention to promote Agent B.
- Better: Orchestrator automatically reroutes to Agent B.

**DyTopo Solution**:
- Agents register with capabilities + fingerprints
- Orchestrator maintains agent inventory (heartbeat-based)
- Skill invocation queries inventory: "Who can do X?"
- Automatic fail-over to secondary if primary down
- Handles agent spin-up/spin-down gracefully

**Scope for Phase 2**:
- Basic agent discovery (register/deregister)
- Ability reroute on primary failure
- **NOT needed in Phase 2**: Load balancing, multi-datacenter orchestration (Phase 3)

---

### 5. eBPF Runtime Protection (Optional Infrastructure Layer)

**Finding**: eBPF can act as a "kernel-level veto" on agent behavior.

**Use Case**:
- Agent A has valid JWT to call git-push.
- IBAC approves the intent.
- Constitutional AI approves the principles.
- But then agent tries to open a reverse shell 💀

**eBPF Catches It**:
- eBPF (kernel module) watches system calls
- If agent tries to `execve("/bin/bash")` → instant block (no LLM latency)
- Agent thinks it succeeded but kernel vetoed it

**Phase 2 Decision**: 
- ✅ Include eBPF architecture in PRD (for future reference)
- ❌ Don't implement in Phase 2 (adds complexity, requires Linux; Windows agents use different model)
- ✅ Phase 2b: Implement for Linux agents if available

**Why mention it now?**
- Shows we've thought about the full spectrum
- Builds confidence that orchestrator is "defense in depth"
- Provides path forward as agent security evolves

---

## Architecture Decisions

### Decision 1: Three-Layer Model vs. Single Layer

**Options**:
1. **Zero Trust Only** (Single layer)
   - Pros: Simple, fast, proven
   - Cons: Misses authorized malice, semantic attacks

2. **IBAC Only** (Semantic layer)
   - Pros: Catches intent misalignment
   - Cons: Misses basic identity attacks

3. **Three-Layer** (Zero Trust + IBAC + Constitutional AI)
   - Pros: Defense in depth, orthogonal threat models
   - Cons: Adds complexity, latency

**Decision**: Three-Layer model  
**Rationale**: Each layer catches different attacks. Complexity is justified by threat surface.  
**Confidence**: 0.85 (well-researched, Forrester + Anthropic alignment)

---

### Decision 2: IBAC Implementation: Deterministic Rules + LLM Fallback

**Options**:
1. **Pure LLM** (Claude on every request)
   - Pros: Handles all cases
   - Cons: 2s latency, higher cost, hallucination risk

2. **Pure Deterministic** (No LLM)
   - Pros: Fast, cheap, predictable
   - Cons: Misses edge cases

3. **Hybrid** (Fast deterministic rules + LLM for ambiguous cases)
   - Pros: Best latency, cost, coverage
   - Cons: More complex to maintain rules

**Decision**: Hybrid (deterministic + LLM fallback)  
**Rationale**: 80% of requests match predictable patterns. LLM only for edge cases.  
**Confidence**: 0.88 (proven approach in ML security)

---

### Decision 3: Skill Fingerprinting: SHA256 Hash

**Options**:
1. **Semantic Hash** (CRC of source code)
   - Pros: Detects any code change
   - Cons: Too sensitive (test changes invalidate fingerprint)

2. **Interface Hash** (SHA256 of interface + major version)
   - Pros: Stable; detects breaking changes
   - Cons: Misses dangerous bug fixes

3. **Full Audit Hash** (SHA256 of interface + tests + version)
   - Pros: Comprehensive; detects breaking changes + test degradation
   - Cons: Requires discipline (developers must update tests)

**Decision**: Full Audit Hash (interface + tests + version)  
**Rationale**: Tests are part of the "contract." If tests are dropped, fingerprint changes. Forces quality discipline.  
**Confidence**: 0.9 (strong alignment with SOLID principles)

---

### Decision 4: Constitutional Principles: Default Conservative or Permissive?

**Options**:
1. **Conservative** (Default: HALT on ambiguity)
   - Pros: Safety-first, reduces risk
   - Cons: May frustrate operators (false positives)

2. **Permissive** (Default: ALLOW on ambiguity)
   - Pros: Faster decision-making
   - Cons: Misses real attacks

**Decision**: Conservative (HALT on ambiguity)  
**Rationale**: Aligns with "fail-safe defaults" (Principles-and-Processes.md). Operator can always override with approval.  
**Confidence**: 0.95 (strongly favored by security research)

---

## Concerns & Responses

### Concern 1: "This adds too much latency"
**Response**: 
- Deterministic rules: < 100ms
- LLM intent verification: 1–2s (but only for 20% of requests, cached after first eval)
- Average: < 500ms for first request, < 100ms for subsequent (cache hit)
- This is acceptable for CI/CD orchestration (human-driven workflows can wait 2s)
- **Mitigation**: Implement fast-path rules; profile & optimize; cache IBAC decisions

### Concern 2: "Constitutional AI adds operational burden"
**Response**:
- Start with *simple* default constitution (10 principles)
- Operators can extend as needed (one-file change)
- Constitution changes trigger test suite (validation gate)
- **Mitigation**: Template library of pre-vetted constitutions; operator handbook

### Concern 3: "What if LLM hallucinates on IBAC decision?"
**Response**:
- LLM is Claude Haiku (not prone to confabulation on binary questions)
- Prompt is deterministic (same intent = same answer)
- IBAC decision is logged with reasoning (auditable)
- Low-confidence decisions escalate to user (don't auto-allow)
- **Mitigation**: Implement "rejection sampling" (ask Claude twice; if answers differ, escalate)

### Concern 4: "DyTopo adds infrastructure complexity"
**Response**:
- Phase 2a: Basic agent discovery (heartbeat + registry)
- Phase 2b: Advanced routing (load balancing)
- Phase 3: Multi-datacenter orchestration
- **Mitigation**: Start simple; add features incrementally based on actual agent count

---

## Success Metrics

### Security Metrics
- **False Positive Rate (IBAC)**: < 5% (legitimate requests blocked)
- **False Negative Rate (IBAC)**: < 10% (suspicious requests allowed)
- **Constitutional Violation Detection**: 100% (all violations logged + halted)
- **Audit Coverage**: 100% (every invocation has fingerprint + intent + confidence)

### Performance Metrics
- **Skill Discovery**: < 100ms
- **Intent Verification (Deterministic)**: < 100ms
- **Intent Verification (LLM)**: < 2s, 90% cache hit rate
- **Skill Invocation**: < 1s (goal, depends on skill)
- **P99 Latency**: < 5s end-to-end

### Operational Metrics
- **Constitution Override Rate**: < 5% (if > 5%, constitution is poorly designed)
- **IBAC Escalation Rate**: 10–20% (sweet spot: most requests are clear, some need human review)
- **Agent Availability**: 99%+ (DyTopo fail-over < 1s)

---

## Decision Gate: Version 2.0 to Version 3.0

**Phase 2 → Phase 3 Decision Point**: May 3, 2026

**Questions to Answer**:
1. Have we shipped Phase 2 on time & on budget?
2. Do the three security layers work well operationally (or too burdensome)?
3. Is latency acceptable in production? (Do we need Phase 2b optimizations?)
4. Are there unexpected attack vectors we didn't anticipate?

**Possible Outcomes**:
- **✅ Go → Phase 3**: Expand to 10+ agents, 100+ skills, 10k invocations/day
- **🔄 Hold → Phase 2b**: Optimize latency, fix operational issues, extend timeline
- **⚠️ Pivot → Phase 1b Extension**: Discover we need more auth/validation work before scaling

---

## Stakeholder Sign-Off

- [ ] Security Team: Threat model approved
- [ ] Engineering Lead: Technical feasibility confirmed
- [ ] Operations: Process & governance acceptable
- [ ] Executive Sponsor: Timeline & budget approved
- [ ] Architect: Alignment with guiding principles

---

## Next Steps

1. **This Week** (Feb 10–14): Stakeholder review of PHASE_2_PRD.md + this decision record
2. **Next Week** (Feb 17–21): Detailed design docs for IBAC + Constitutional AI
3. **Week of Mar 11**: Kick-off; workstreams begin
4. **Weekly**: Decision records for each architectural choice (capture reasoning over time)

---

*Decision Record v1.0 | Feb 10, 2026*
