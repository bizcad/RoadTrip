# Memory Tiers Specification

**Mapping the 3 SRCGEEE memory tiers to the 7-layer Cortex model**

---

## The Fundamental Insight

Memory is a database with code over the top. That is all there is: remember stuff and compute over it.
Everything else in this spec — tiers, retrieval speeds, classifiers, RBAC — is implementation detail
on top of that one truth.

**Memory chunks are subject to RBAC.** Secrets are just the memory class with the tightest RBAC.
`ISecretsProvider` is the retrieval interface for that class. The same pattern applies at every tier.

---

## The Problem This Solves

`SRCGEEE-DiSE-Synthesis.md` identifies multi-level memory as load-bearing infrastructure:

> Agent starts with absolute minimum context. Memory tiers supply what is needed on demand.

This document makes that concrete. The three tiers map onto the 7 Cortex layers. Agents don't need
to know about Cortex layers; they need to know which tier to pull from and what triggers that pull.

---

## Tier Mapping

| SRCGEEE Tier | Cortex Layers | Latency | Who Initiates |
|---|---|---|---|
| **Fast** | Layer 1 (Auto Memory) + Layer 2 (Session Bootstrap) | ~0ms — always present | Injected at invocation; no agent call needed |
| **Slow** | Layer 3 (Working Memory) + Layer 4 (Episodic Memory) + Layer 5 (Hybrid Search) + Layer 6 (Knowledge Graph) | ~100ms–2s | Agent requests on first reference to entity/decision/history |
| **Invention** | Layer 7 (RLM-Graph) + external research agents + code synthesis | ~5s–60s | Agent escalates when Slow tier returns no result or when the required capability doesn't exist yet |

> **Why "Invention" not "Research":** The Invention tier doesn't just look things up — it can
> synthesize or write code that is not yet in the system. Research implies retrieval; Invention
> implies creation. The tier handles both.

---

## Memory Class × RBAC

Every memory chunk carries a class that determines its RBAC profile. Classes are learned from
usage and discovery — they are not statically assigned at design time.

| Memory Class | RBAC Level | Retrieval Interface | Example |
|---|---|---|---|
| **Secrets** | Highest — principal-scoped, TTL-bound, blocked list enforced | `ISecretsProvider.GetBundleAsync()` | API keys, client secrets, OAuth tokens |
| **Attested patterns** | High — trust_level >= verified required to write | Slow tier (Episodic) | Avoidance rules, SLSA-attested triage patterns |
| **Domain knowledge** | Medium — scoped per Entra group (swarm boundary) | Slow tier (Knowledge Graph, Hybrid Search) | Legal precedents, product schemas, escalation paths |
| **Working state** | Session-scoped — principal's active session only | Fast→Slow (Working Memory) | Active goals, scratchpad, retry state |
| **Public patterns** | Low — readable by all agents with basic trust | Fast tier (MEMORY.md) | SRCGEEE loop contract, architecture decisions |

**Key principle:** Memory retrieval uses the same zero-trust posture as tool invocation.
Before any Retrieve call, the agent checks: *am I allowed to read this class for this principal?*

**Secrets are not memory in the general sense** — they flow through `ISecretsProvider` and are
never written to any general memory store. The RBAC pattern is the same; the implementation
channel is separate by design.

---

## What Each Tier Contains

### Fast Tier (always loaded)

```
MEMORY.md                   ← architecture decisions, confirmed patterns
Session Bootstrap context   ← active goals, incomplete items, last handoff
Agent seed block            ← identity, principal, loop, fitness metric
```

**Rules:**
- ≤ 200 lines total (Cortex hard limit for MEMORY.md)
- No session-specific detail; only durable facts
- Updated only when a fact is confirmed stable (Evolve phase writes here)
- Accessible to all agents with basic trust or higher

---

### Slow Tier (pulled on demand)

| Layer | When the Agent Pulls It | What It Returns |
|---|---|---|
| **Working Memory** (L3) | Agent needs to track sub-goals or state across multiple Execute cycles | Active goals, timestamped observations, key-value state |
| **Episodic Memory** (L4) | Agent sees a problem that may have been solved before | Ranked past-session chunks with similarity scores |
| **Hybrid Search** (L5) | Episodic or graph search alone returns weak results | Fused keyword + graph + (optional) vector results — 5-speed retrieval stack |
| **Knowledge Graph** (L6) | Agent encounters a named entity (person, system, project) | Relationship graph: who knows what, what depends on what |

**Pull trigger:** Any Retrieve phase query that returns fewer than 3 candidates from Fast tier
automatically escalates to Slow tier.

**Agent call pattern (pseudocode):**
```
candidates = retrieve_fast(query)
if len(candidates) < 3:
    candidates += retrieve_slow(query, tiers=["episodic", "graph", "hybrid"])
```

**5-speed retrieval within Slow tier** (from memory-substrate-spec-v0.1.md):
```
Speed 0: Exact / lexical (path, symbol, BM25, recency)
Speed 1: Metadata vector (one-line summary + intent JSON)
Speed 2: Structural neighbor (import graph, call graph, co-change)
Speed 3: Code semantic rerank (chunk embeddings + cross-encoder)
Speed 4: Execution-grounded validation (compile, type-check, unit smoke)
```

---

### Invention Tier (escalated for novel problems)

Triggered when Slow tier returns no result, or returns results with confidence < threshold,
**or when the required capability does not yet exist in the system**.

```
RLM-Graph (L7)              ← decompose complex queries that overflow context
External research agents    ← internet-access agents for live vendor knowledge
MCP vendor docs             ← live API schema lookups (Triage category 3)
Code synthesis agents       ← write new code blobs when no existing blob fits
```

**Rules:**
- Never triggered automatically — requires explicit agent decision at Gate phase
- Counts as a non-recoverable resource spend (HITL consideration for expensive calls)
- Results always written back to Slow tier (Episodic) and promoted to Fast tier if confirmed stable
- **Code synthesis outputs** are subject to the same SLSA attestation requirements as manually
  written code before they can be promoted to Slow tier as attested patterns

---

## Memory Lifecycle (Promotion / Demotion)

```
Invention tier result
        ↓  [Evaluate: confidence >= threshold]
Slow tier (Episodic / candidate state)
        ↓  [Evolve: 3+ successful uses; fact confirmed stable]
Fast tier (MEMORY.md / promoted state)
        ↓  [Evolve: fact contradicted or superseded]
Archived / deleted
```

Promotion is write-on-confirm. Demotion is write-on-contradiction.
Both happen in the **Evolve** phase — never mid-execution.

**Evaluate cadence (per memory-substrate-spec-v0.1.md):**
- Per-run: did retrieved memory improve completion? reduce retries? increase risk?
- Daily: re-score memory items, detect stale clusters, generate promotion/demotion candidates
- Weekly/Monthly: domain-pack re-tuning, policy calibration, compliance sweep

---

## Two Classifiers (Learned, Not Static)

Classifications emerge from usage and discovery — they are not hardcoded at design time.

### Retrieval Speed Classifier
Predicts which tier to query first.
- Inputs: task type, confidence, prior success on similar tasks, latency budget
- Output: Speed 0–4 starting point + tier escalation policy

### Content / Domain Classifier
Tags artifact semantics, sensitivity, domain, trust, lifecycle state.
- Inputs: content features + observed usage + outcome quality + source trust
- Output: memory class, domain overlay, lifecycle state, RBAC profile

Both classifiers run at **write-time and read-time**. Write-time classification seeds the record;
read-time classification adjusts for query context and current trust state.

---

## SRCGEEE Phase × Memory Tier

| Phase | Fast Tier | Slow Tier | Invention Tier |
|---|---|---|---|
| **Sense** | Identity, trust level, principal | — | — |
| **Retrieve** | Seed context; top-1 candidate if known | Pull top-5 NN candidates; search episodic for prior attempts | Escalate if no candidates; synthesize if capability missing |
| **Compose** | SRCGEEE loop contract | Prior composition patterns (episodic) | Novel composition for unseen task types |
| **Gate** | Policy-as-code rules | Prior gate decisions for similar risk profiles | External compliance lookups |
| **Execute** | Deterministic code; TTL-checked credentials via ISecretsProvider | Retry patterns; triage history | Vendor docs for API drift (MCP) |
| **Evaluate** | Completion signal | Prior fitness scores for comparison; daily/weekly re-scoring | — |
| **Evolve** | Write confirmed facts to MEMORY.md | Write session outcome to Episodic | Write novel patterns + synthesized code (with SLSA attestation) |

---

## Four Planes of the Memory System

From the Copilot 3/16 session critique: memory is not just retrieval. It needs four planes:

| Plane | What It Does | SRCGEEE Phase |
|---|---|---|
| **Prediction** | Probabilistic next-step selection — "what comes next?" | Retrieve (NN query) |
| **Retrieval** | Fast/Slow/Invention memory fetch and rerank | Retrieve, Compose |
| **Governance** | Persistence, decay, promotion/demotion, compliance | Evaluate, Evolve |
| **Assurance** | Audit, rollback, policy attestation, risk constraints | Gate, Execute |

The graph (Knowledge Graph, lineage, rollback anchors) serves **assurance and documentation**.
Probabilistic next-step selection is what the orchestrator actually uses to drive flow.
**Probability drives flow; graph guarantees coherence and accountability.**

---

## Minimal Agent Seed Context (Fast Tier Only)

```
IDENTITY:   {bot-name}, trust-level: {basic|verified|attested}
PRINCIPAL:  {human-sme-id}
LOOP:       SRCGEEE
MEMORY:     fast loaded; pull slow on <3 candidates; escalate to invention on miss/gap
FITNESS:    completion is success; non-completion routes to Evolve
SPEND:      never spend non-recoverable resources without HITL
HELP:       help is preferable to failure
TOOLS:      query NN embedding space; do not pre-load full tool list
SECURITY:   all principals zero-trust; carry RBAC; check least-privilege before each call
FAILURE:    document environment + hand off to failure workflow; re-enter SRCGEEE at Sense
```

**Token count target:** < 300 tokens. The rest of the agent's knowledge is retrieved, not loaded.

---

## What Lives Where (Reference)

| Artifact | Tier | Layer | Notes |
|---|---|---|---|
| Architecture decisions (confirmed) | Fast | L1 | MEMORY.md |
| Agent seed block | Fast | L1 | MEMORY.md |
| **Secrets / credentials** | **Not memory** | **—** | **ISecretsProvider — separate channel, same RBAC model** |
| Active goals | Fast→Slow | L2→L3 | Session Bootstrap → Working Memory |
| Past conversation chunks | Slow | L4 | Episodic index (SQLite or equivalent) |
| Code blob descriptors | Slow | L4+L5 | One-line summary + intent JSON + embedding |
| Code blobs (canonical) | Slow | L4 | SeaweedFS object plane (source-of-truth) |
| Relationship graph | Slow | L6 | Knowledge Graph (NetworkX or equivalent) |
| Complex multi-entity queries | Invention | L7 | RLM-Graph decomposition |
| Live vendor API docs | Invention | External | MCP vendor-docs tool |
| Synthesized code (new capability) | Invention→Slow | External→L4 | Written + attested → Episodic |
| Learned triage patterns | Slow→Fast | L4→L1 | Episodic → promote to MEMORY.md |
| Avoidance rules (bug immunity) | Fast | L1 | MEMORY.md (propagated via Evolve) |
| Tool lineage + fitness scores | Slow | L4 | Episodic (per DiSE Part 8/9) |
| Domain overlays (legal, AP, sales) | Slow | L4+L6 | Domain-specific pattern packs |

---

## Integration Points with Other Specs

| Spec | How Memory Tiers Connect |
|---|---|
| `SRCGEEE-DiSE-Synthesis.md` | This document is the concrete spec behind the "multi-level memory" divergence |
| `TRIAGE-DELEGATION.md` | Triage reads from Slow tier (case vault, execution logs, pattern store); writes fix outcome to Episodic |
| `AGENT-IDENTITY-INTEGRATION.md` | Secrets flow through ISecretsProvider (not memory). RBAC model is the same; implementation channel is separate. |
| `analysis/ppa/memory-substrate-spec-v0.1.md` | Physical substrate: SeaweedFS (blob plane) + CockroachDB (governance/event ledger) + local vector lane (Think Fast) |
| DiSE Part 9 (avoidance rules) | Bugs detected → avoidance rule written to Episodic → promoted to Fast (MEMORY.md) on confirmation |
| DiSE Part 11 (graduated monitoring) | Quality profile learned → Slow tier → statistical threshold promoted to Fast tier |

---

## Open Questions

- **Cortex deployment**: Does the swarm use Claude Cortex directly, or does PPA implement
  the layer interfaces natively against SeaweedFS + CockroachDB?
  Deferred until PPA Phase 2b (EventLedger feeds designed).

- **Cross-swarm memory sharing**: Memory is scoped per Entra group (same as vault access policy).
  Cross-swarm knowledge lives in a shared Knowledge Graph node if deliberately propagated via Evolve.
  Governance policy for deliberate propagation is a Phase 2b concern.

- **rockbot memory bootstrap**: rockbot starts hollow — no Episodic history.
  Proposed: read-only access to shared pattern-store at bootstrap; write access earned via
  `trust_level >= verified`. Deferred to Phase 3b (rockbot no longer hollow).

- **Invention tier attestation gate**: Code synthesized by Invention-tier agents must be attested
  before it can be promoted to Slow tier as a reusable pattern. What is the attestation workflow
  for synthesized code? Proposed: same SLSA pipeline as manually written code — synthesis is just
  a different author, not a different standard.
