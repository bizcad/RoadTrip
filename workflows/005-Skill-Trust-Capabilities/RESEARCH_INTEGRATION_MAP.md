# Phase 2 Architecture: Research Integration Map

**Purpose**: Show how Phase 2 design integrates research from DyTopo, Zero Trust, IBAC, Constitutional AI  
**Status**: Planning complete  
**Date**: Feb 10, 2026  

---

## Research → Architecture Mapping

### 1. DyTopo (Dynamic Multi-Agent Topology Routing)

**Source**: `docs/DyTopo_Analysis_And_SKILLS_Implications.md`

**Core Concept**: 
- Agents form a dynamic graph; topology changes as agents spin up/down
- Skills are graph nodes; agents execute skills
- Routing decisions must adapt in real-time to agent availability

**Phase 2 Integration**:

| DyTopo Concept | Phase 2 Implementation |
|---|---|
| Agent registration | Workstream 5: Agent discovery via heartbeat + registry |
| Skill routing | Workstream 5: Query agent inventory ("Who can do X?") |
| Fail-over | Workstream 5: Automatic reroute to secondary if primary down |
| Topology awareness | Workstream 6: Orchestrator maintains live agent graph |
| Deterministic pyramid | All workstreams: Deterministic layer (IBAC rules) + probabilistic layer (LLM intent) |

**What We're Building**:
- `config/dytopo-routing.yaml`: Agent registry + routing policies
- `src/orchestrator_v2.py`: Updated orchestrator aware of agent topology
- `tests/test_dytopo_agent_lifecycle.py`: Register → activate → deactivate → deregister

**Why This Matters**: As we scale from 5 → 50 agents, manual routing becomes impossible. DyTopo tech enables auto-scaling.

---

### 2. Zero Trust for Agents (Kindervag, Forrester)

**Source**: `docs/Zero_Trust_For_Agents.md`

**Core Concept**:
- **Layer**: Never trust, always verify (identity)
- **Principle**: Assume breach (credentials could be stolen)
- **Control**: Pervasive throughout system, not just perimeter

**Phase 2 Integration**:

| Zero Trust Principle | Phase 2 Implementation |
|---|---|
| Verify identity | Workstream 4: JWT service tokens + mTLS |
| Least privilege | Workstream 4: Token scoped to single skill, time-limited |
| Assume breach | Workstream 6: Audit logs on *every* invocation; no silent failures |
| Micro-segmentation | Workstream 5: Agent registry groups by capability; routing isolates by scope |

**What We're Building**:
- `src/skills/token_validator.py`: Validate JWT before skill execution
- `config/ibac-policies.yaml`: Map identity (agent) to permissions (skills)
- `docs/Phase_2_Audit_Log_Reference.md`: Every invocation logged with identity + fingerprint

**Gap We Address**: Zero Trust alone doesn't catch "authorized malice" (valid token, wrong intent). IBAC + Constitutional AI fill this gap.

---

### 3. Intent-Based Access Control (IBAC)

**Source**: `docs/Gemini Pro 3-ZeroTrust and DyTopo research.txt` (Competing Frameworks section)

**Core Concept**:
- Traditional: Does Agent A have permission? (identity-based)
- IBAC: Does Agent A's request *make sense* given its stated intent? (semantic-based)

**Phase 2 Integration**:

| IBAC Concept | Phase 2 Implementation |
|---|---|
| Intent verification | Workstream 2: Verifier LLM evaluates "Does action match intent?" |
| Fast path (deterministic) | Workstream 2: Rules for common patterns (returns answer instantly) |
| Slow path (probabilistic) | Workstream 2: Claude Haiku for ambiguous cases (2s, cached) |
| Confidence scoring | Workstream 2: 0.0–1.0 score; escalate if < threshold (0.85) |
| Logging with reasoning | Workstream 6: Audit logs capture "Why did IBAC allow/deny this?" |

**What We're Building**:
- `src/skills/ibac_verifier.py`: Main IBAC engine
- `config/ibac-policies.yaml`: Deterministic rules + exception handling
- `tests/test_ibac_verifier.py`: Verify IBAC catches confused-deputy attacks

**Gap We Address**: Zero Trust + IBAC = checks both identity + semantics. Most attacks fail at one layer or the other.

---

### 4. Constitutional AI & Agent Integrity

**Source**: `docs/Gemini Pro 3-ZeroTrust and DyTopo research.txt` (Competing Frameworks section)

**Core Concept**:
- Don't just enforce rules from outside
- Give agent its own "constitution" (principles)
- Agent self-critiques *before* acting (faster + catches subtle misalignment)

**Phase 2 Integration**:

| Constitutional AI Concept | Phase 2 Implementation |
|---|---|
| Principles-based architecture | Workstream 3: Create `src/skills/constitution.md` with git-push principles |
| Self-critique | Workstream 3: Agent checks "Does this action violate my constitution?" |
| Operator override | Workstream 3: Operator can approve violating action (logged in audit) |
| Alignment feedback loop | Workstream 6: Logs show which principles are triggered; feed back to constitution design |
| Confidence in alignment | Workstream 3: Scoring (how confident is agent that action aligns?) |

**What We're Building**:
- `src/skills/constitution_checker.py`: Constitutional enforcement engine
- `src/skills/constitution.md`: Default constitution + git-push-specific principles
- `tests/test_constitution_checker.py`: Verify violations caught + logged

**Gap We Address**: Zero Trust + IBAC verify *policy compliance*. Constitutional AI verifies *value alignment* (subtle but important). Example:
- Zero Trust: "Can agent delete?" → Yes (has permission)
- IBAC: "Does agent's intent match?" → Yes (user asked to delete old cache)
- Constitutional AI: "Does deletion feel right?" → No, if deletion is production data instead of cache

---

### 5. eBPF Runtime Protection (Emerging Infrastructure)

**Source**: `docs/Gemini Pro 3-ZeroTrust and DyTopo research.txt` (Emerging Security Models section)

**Core Concept**:
- Kernel-level monitoring (can't be bypassed by user-space code)
- If agent tries something forbidden → kernel blocks it (no latency, instant veto)

**Phase 2 Integration**:

| eBPF Concept | Phase 2 Planning |
|---|---|
| Kernel-level enforcement | Phase 2 PRD: Mentioned as optional Phase 2b/3 enhancement |
| Real-time system call monitoring | Phase 3: If we deploy on Linux, consider Cilium/Tetragon |
| Unforgeable veto | Phase 3: Kernel-level "hard stop" for dangerous operations |

**What We're NOT Building in Phase 2**:
- eBPF integration is deferred (adds Linux-specific complexity)
- Mentioned in PRD as "defense in depth" path for future

**Why Defer**: 
- Phase 2 focuses on agent-level trust (identity + intent + alignment)
- eBPF is infrastructure-level trust (works best on Linux, not Windows)
- Phase 2 proves the model works; Phase 3 adds infrastructure hardening

---

## Layered Security in Phase 2

```
┌─────────────────────────────────────────────────────────────┐
│ Constitutional AI (Workstream 3)                            │
│ Agent principle checklist: "Does this violate constitution?"│
│ Example: git-push never pushes to main without approval    │
│ Speed: <100ms (local inference) + ~2s if LLM double-check │
└─────────────────────────────────────────────────────────────┘
                        ↑ (if approved)
┌─────────────────────────────────────────────────────────────┐
│ Intent-Based Access Control / IBAC (Workstream 2)           │
│ Verifier checks: "Does intent match the action?"            │
│ Example: Agent says "deleting cache" but action is risky   │
│ Speed: <100ms (deterministic rules) or ~2s (LLM fallback) │
└─────────────────────────────────────────────────────────────┘
                        ↑ (if intent clear)
┌─────────────────────────────────────────────────────────────┐
│ Zero Trust / Identity (Workstream 4)                        │
│ Traditional check: "Is this agent who they claim?"          │
│ Example: JWT token valid? Time not expired? Scope correct? │
│ Speed: <10ms (token validation)                            │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow**:
1. Agent presents JWT (token) → Zero Trust validates identity
2. Agent provides skill + context → IBAC verifies intent
3. Agent prepares to execute → Constitutional AI self-critiques
4. If all pass → Skill executes; result logged with fingerprints

**Failure Scenarios**:
- Invalid JWT? → Deny at Zero Trust layer (blocked instantly)
- Valid JWT but intent unclear? → Escalate at IBAC layer (ask user)
- Valid JWT + clear intent but violates constitution? → Halt at Constitutional layer (ask operator)

---

## Phase 2 vs. Phase 1 Comparison

| Aspect | Phase 1b | Phase 2 |
|--------|----------|---------|
| **Trust Model** | Rules-based (file validation) | Intent + Identity + Alignment |
| **Scalability** | Single orchestrator | Multi-agent with DyTopo |
| **Skill Discovery** | Hard-coded list | Capability-based query |
| **Security Layers** | 1 (Rules) | 3 (Zero Trust + IBAC + Constitutional) |
| **Latency Budget** | < 1s | < 2s (with caching) |
| **Audit Trail** | Log decisions | Log with fingerprints + reasoning |
| **Operator Involvement** | High (manual approval) | Medium (mostly automated; escalate edge cases) |

---

## Context & Decisions

### Why Three Layers Instead of One?

**Threat Surface**: As agent count grows (5 → 50 → 500), attack surface expands:
1. **Identity attacks**: Stolen JWT tokens → Zero Trust catches
2. **Semantic attacks**: Valid token, hallucinating intent → IBAC catches
3. **Alignment attacks**: Valid token + clear intent, but misaligned values → Constitutional AI catches

Each layer catches different attacks. Combined = defense in depth.

### Why IBAC + Constitutional AI Co-Exist?

**Different Problems**:
- **IBAC**: "Does this action match the agent's stated intent?" (Procedural correctness)
- **Constitutional AI**: "Does this action match the agent's value alignment?" (Value correctness)

**Example**:
```
Scenario: Agent proposes to "delete old log files"

IBAC Check:
  Intent: "Delete old log files"
  Action: "DELETE FROM logs WHERE date < 2026-01-01"
  Match: Yes (correct procedural alignment) ✅

Constitutional Check:
  Agent's Constitution: "Never delete production data"
  Is logs table production data? Yes (contains live access logs) ⚠️
  Match: No (value misalignment) ❌
  → HALT and escalate to operator
```

Both layers are necessary because they address different types of errors.

---

## Research Confidence Assessment

| Research Area | Source(s) | Confidence | Why |
|---|---|---|---|
| Zero Trust for Agents | Forrester, Kindervag | 0.95 | Well-established framework; used by major orgs |
| IBAC | Academic papers + startups | 0.85 | Emerging but solid research; proven in some productions |
| Constitutional AI | Anthropic + academic labs | 0.88 | Strong theoretical foundation; less production data available |
| DyTopo | Internal analysis (RoadTrip docs) | 0.80 | Sound reasoning; limited external validation |
| eBPF Integration | Container security research | 0.75 | Proven tech; less proven for agent workloads |

**Confidence Score Interpretation**:
- 0.95: This will work; minor tweaks expected
- 0.85: This will likely work; may need adjustments based on data
- 0.75: This is promising; requires close monitoring; may pivot if data contradicts

---

## Risk Mitigations Tied to Research

| Risk | Research-Based Mitigation |
|---|---|
| IBAC LLM calls are too slow | Use deterministic fast-path for 80% of cases; LLM fallback only for edge cases |
| Constitutional AI is too strict | Start with conservative principles; adjust based on operator feedback (monthly reviews) |
| Agent lifecycle gets complex | DyTopo tech simplifies routing; distributed systems research shows heartbeat approach is robust |
| Audit logs become too noisy | Log with fingerprints only (not secrets); store in time-series DB; query by confidence threshold |

---

## How Phase 2 Feeds Phase 3

**Phase 3 Vision** (post-May 3, if approved):
- 50+ agents, 100+ skills, 10k+ daily invocations
- Multi-datacenter orchestration (agents in different regions)
- Federated constitutional AI (different teams, different principles)
- eBPF integration for Linux-based agents

**Phase 2 Enables This By**:
- Proving IBAC model works (confidence > 0.9)
- Establishing DyTopo foundations (simple registry → distributed service discovery)
- Creating audit trails (Phase 3 uses these for learning loops)
- Running monthly reviews (Phase 3 has data to learn from)

---

## Glossary of Terms (For Reference)

| Term | Definition | Phase 2 Component |
|---|---|---|
| **Zero Trust** | Security model: never trust, always verify identity | Workstream 4 |
| **IBAC** | Intent-Based Access Control: verify intent matches action | Workstream 2 |
| **Constitutional AI** | Agent self-critique against principles before acting | Workstream 3 |
| **DyTopo** | Dynamic topology routing for multi-agent systems | Workstream 5 |
| **Service Token** | JWT scoped to single skill, time-limited | Workstream 4 |
| **Skill Fingerprint** | SHA256(interface + tests + version)[0:16] | Workstream 1 |
| **Capability** | Named action a skill can perform | Workstream 1 |
| **Confidence Score** | 0.0–1.0 metric for decision certainty | Workstreams 2, 3, 6 |
| **Escalation** | When human operator must review (confidence too low) | Workstreams 2, 3 |
| **Audit Trail** | Complete log of all decisions with fingerprints + reasoning | Workstream 6 |
| **Operator Override** | Allowing action that would normally be blocked (logged) | Workstream 3 |

---

## How to Use This Document

**For Architects**: 
- Verify Phase 2 design addresses all research areas
- Check confidence scores align with your own assessment
- Identify any gaps between research + implementation

**For Workstream Leads**:
- Understand your workstream's role in the larger security model
- Use this to communicate why your workstream matters
- Reference relevant research when proposing changes

**For Security Review Team**:
- Validate threat model is comprehensive
- Use research citations to strengthen security audit
- Identify any attack vectors we haven't addressed

**For Future Teams (Phase 3+)**:
- See how Phase 2 lays groundwork
- Understand research directions not yet implemented (eBPF, federated constitutional AI)
- Build on what Phase 2 learns

---

*Research Integration Map v1.0 | Feb 10, 2026*
