# RoadTrip Platform Naming Layer
**Gap 1 Implementation — From Session Log 2026-03-19**

> **Purpose:** Give canonical platform-surface names to code that already exists in `src/skills/` and `.claude/skills/`. No rewrites. No new code. Names create gravity — they make the architecture legible to collaborators, bots, and future platform documentation.

---

## The Core Insight: You Have Three Platforms, Not One Folder

RoadTrip's `src/skills/` directory contains three distinct platforms that happen to live in the same folder. Naming them makes the architecture visible.

| Platform Name | What It Is | Frontier Analogue |
|---|---|---|
| **RoadTrip.Context** | Memory, secrets, retrieval, session state | Business Context Layer |
| **RoadTrip.Execute** | SRCGEEE runtime, skill orchestration, push pipeline | Agent Execution |
| **RoadTrip.Assurance** | Trust scoring, attestation, telemetry, rules | Evaluation + Governance |

Plus a fourth that Frontier does not have:

| Platform Name | What It Is | Why It Matters |
|---|---|---|
| **RoadTrip.Acquire** | Skill scanning, registry validation, trust gating for new skills | Supply-chain safety before a skill is admitted |

---

## RoadTrip.Context — The Memory & Identity Platform

**One-line definition:** Gives every agent a filtered, RBAC-checked view of what it needs to know before acting.

### Code that belongs here today

| File | Role in Context |
|---|---|
| `src/skills/memory_loop_orchestrator.py` | Master coordinator — runs the full WS-A/B/C/D cycle: bootstrap → index → retrieve → consolidate → promote |
| `src/skills/episodic_index.py` | SQLite-backed retrieval index; answers "what happened that's relevant to this query?" |
| `src/skills/session_bootstrap.py` | Loads recent failures, active skills, pending reminders at session start |
| `src/skills/memory_tagger.py` | Annotates telemetry events with semantic tags before indexing |
| `src/skills/memory_store_transition.py` | Manages promotion/demotion between memory tiers (Fast → Slow → Invention) |
| `src/skills/token_resolver.py` | Resolves auth tokens from vault/env — the ISecretsProvider adapter entry point |
| `src/skills/auth_validator.py` | RBAC check for agents: git config, SSH key, GITHUB_TOKEN, branch permissions |
| `src/skills/auth_validator_models.py` | Data shapes for auth decisions |
| `src/skills/config_loader.py` | Loads YAML config with conservative defaults — no config = block everything |

### Name suggestions for documentation and APIs

```
RoadTrip.Context.Memory          ← MemoryLoopOrchestrator + EpisodicIndex
RoadTrip.Context.Session         ← SessionBootstrap
RoadTrip.Context.Identity        ← AuthValidator + TokenResolver
RoadTrip.Context.SecretsAdapter  ← TokenResolver → ISecretsProvider pattern
```

### What this enables
Any agent in the swarm calls `RoadTrip.Context` before acting. It gets back:
- A filtered memory pack (RBAC-checked, tier-appropriate)
- Identity confirmation (auth token, branch permission)
- Session state (recent failures, active skills)

This is your answer to Frontier's "Business Context Layer" — but with provable RBAC boundaries instead of opaque enterprise connectors.

---

## RoadTrip.Execute — The SRCGEEE Runtime Platform

**One-line definition:** The 7-stage pipeline that turns a request into a safe, attested, logged action.

### SRCGEEE stage → code mapping

| Stage | Name | Code |
|---|---|---|
| **S** — Sense | `RoadTrip.Execute.Sense` | `sensation_capture.py` — captures raw input, clipboard, file events |
| **R** — Retrieve | `RoadTrip.Execute.Retrieve` | `memory_loop_orchestrator.py` (retrieval phase), `episodic_index.py` |
| **C** — Compose | `RoadTrip.Execute.Compose` | `commit_message.py`, `adaptive_executor.py` — builds the action artifact |
| **G** — Gate | `RoadTrip.Execute.Gate` | `preflight.py`, `rules_engine.py`, `auth_validator.py`, `trust_scorecard.py` |
| **E** — Execute | `RoadTrip.Execute.Run` | `executor.py`, `git_push_autonomous.py` |
| **E** — Evaluate | `RoadTrip.Execute.Evaluate` | `release_evidence_gate.py`, `telemetry_logger.py` |
| **E** — Evolve | `RoadTrip.Execute.Evolve` | `memory_loop_orchestrator.py` (consolidation + promotion phase) |

### Orchestration layer

| File | Role |
|---|---|
| `src/skills/skill_orchestrator.py` | Chains skills in dependency order (auth → rules → commit → push → log) |
| `src/skills/skill_orchestrator_models.py` | Data shapes for orchestration results |
| `src/skills/git_push_autonomous.py` | Full pipeline implementation: status → auth → rules → message → push |
| `src/skills/adaptive_executor.py` | Adapts execution strategy based on context (dry-run, rollback-available, etc.) |
| `src/skills/preflight.py` | Pre-execution gate: checks conditions before any action fires |
| `src/skills/executor.py` | Core execution engine — runs the composed action |

### Name suggestions

```
RoadTrip.Execute.Pipeline        ← SkillOrchestrator (the chain runner)
RoadTrip.Execute.Gate            ← Preflight + RulesEngine + AuthValidator
RoadTrip.Execute.Push            ← GitPushAutonomous (the canonical push workflow)
RoadTrip.Execute.Compose         ← CommitMessage + AdaptiveExecutor
```

### The key differentiator
Each stage is **explicit, observable, and independently gateable**. This is what Frontier cannot replicate — Frontier's pipeline is opaque. Your SRCGEEE loop produces causal traces: you know *which stage* caused what outcome, not just that something happened.

---

## RoadTrip.Assurance — The Trust & Evidence Platform

**One-line definition:** Every artifact that passes through Execute gets scored, attested, and logged. No model grades its own homework.

### Code that belongs here today

| File | Role in Assurance |
|---|---|
| `src/skills/trust_scorecard.py` | Evaluates skills against 6 gates: fingerprint, provenance, security review, test coverage, capability fit, author reputation. Produces `ALLOW_AUTO / MANUAL_REVIEW / BLOCK` |
| `src/skills/release_evidence_gate.py` | Pre-release gate: blocks promotion unless evidence bundle is complete |
| `src/skills/rules_engine.py` | File-level safety: allowed paths, blocked patterns, BLOCK_ALL enforcement |
| `src/skills/telemetry_logger.py` | Writes structured JSONL to `data/telemetry.jsonl` — every decision logged with stage, confidence, reasoning |
| `src/skills/telemetry_logger_models.py` | Data shapes for telemetry events |
| `src/skills/models.py` | Shared dataclasses across all 4 skills |

### The TrustScorecard output (already built)

```json
{
  "schema": "roadtrip-trust-bundle/v1",
  "release_id": "...",
  "skill": { "name": "git-push-autonomous" },
  "decision": "ALLOW_AUTO",
  "score": 90,
  "max_score": 100,
  "blocking_failures": [],
  "gate_results": [
    { "gate_name": "fingerprint_verified", "passed": true, "blocking": true, "score_weight": 25 },
    { "gate_name": "version_provenance_verified", "passed": true, "blocking": true, "score_weight": 20 },
    { "gate_name": "security_review_passed", "passed": true, "blocking": true, "score_weight": 20 },
    { "gate_name": "test_coverage_minimum", "passed": true, "blocking": true, "score_weight": 15 }
  ],
  "evidence": { "test_evidence": "...", "security_evidence": "..." }
}
```

This *is* your scorecard. It just needs to be emitted after every EVOLVE cycle.

### Name suggestions

```
RoadTrip.Assurance.Scorecard     ← TrustScorecard + evaluate_skill()
RoadTrip.Assurance.ReleaseGate   ← ReleaseEvidenceGate
RoadTrip.Assurance.Rules         ← RulesEngine (file-level safety)
RoadTrip.Assurance.Telemetry     ← TelemetryLogger (the audit trail)
RoadTrip.Assurance.Bundle        ← build_trust_bundle() — the evidence artifact
```

### What this enables
When external pressure requires audit documentation (Frontier governance initiative, compliance, enterprise customers), you point to `RoadTrip.Assurance.Bundle` — a structured, version-controlled evidence artifact per skill per release. No other agentic platform produces this automatically.

---

## RoadTrip.Acquire — The Skill Supply Chain Platform

**One-line definition:** Before a skill joins the swarm, it passes a trust gate. This is what prevents supply-chain compromise.

### Code that belongs here today

| File | Role in Acquire |
|---|---|
| `src/skills/skill_scanner.py` | Scans skill directories, reads metadata, feeds trust evaluation |
| `src/skills/registry_list.py` | Canonical list of admitted skills and their metadata |
| `src/skills/yaml_redirect_validator.py` | Validates YAML front-matter and redirect configs — blocks malformed skill definitions |
| `src/skills/notebook_query.py` | Queries NotebookLM for skill research and capability matching |
| `config/skills-registry.yaml` | Source of truth for admitted skills (fingerprint, version, author, coverage) |

### Name suggestions

```
RoadTrip.Acquire.Scanner         ← SkillScanner
RoadTrip.Acquire.Registry        ← RegistryList + skills-registry.yaml
RoadTrip.Acquire.Validator       ← YamlRedirectValidator
RoadTrip.Acquire.TrustGate       ← evaluate_registry() from trust_scorecard.py
```

### Why this is your moat
Frontier admits agents by enterprise IT policy. RoadTrip admits skills by evidence: fingerprint + provenance + security review + test coverage. A skill that fails any blocking gate never runs. This is the compiler-like determinism that separates your architecture from every vendor platform.

---

## The Full Name Map (one-page reference)

```
RoadTrip Platform
│
├── RoadTrip.Context              ← "Give me what I need to know before acting"
│   ├── .Memory                   ← MemoryLoopOrchestrator + EpisodicIndex
│   ├── .Session                  ← SessionBootstrap
│   ├── .Identity                 ← AuthValidator + TokenResolver
│   └── .SecretsAdapter           ← ISecretsProvider pattern (CompositeSecretsProvider)
│
├── RoadTrip.Execute              ← "Run the 7-stage SRCGEEE loop"
│   ├── .Sense                    ← SensationCapture
│   ├── .Retrieve                 ← EpisodicIndex (retrieval phase)
│   ├── .Compose                  ← CommitMessage + AdaptiveExecutor
│   ├── .Gate                     ← Preflight + RulesEngine + AuthValidator + TrustScorecard
│   ├── .Run                      ← Executor + GitPushAutonomous
│   ├── .Evaluate                 ← ReleaseEvidenceGate + TelemetryLogger
│   └── .Evolve                   ← MemoryLoopOrchestrator (consolidation + promotion)
│
├── RoadTrip.Assurance            ← "Prove that what ran was safe and what was learned is valid"
│   ├── .Scorecard                ← TrustScorecard
│   ├── .ReleaseGate              ← ReleaseEvidenceGate
│   ├── .Rules                    ← RulesEngine
│   ├── .Telemetry                ← TelemetryLogger
│   └── .Bundle                   ← build_trust_bundle() — the evidence artifact
│
└── RoadTrip.Acquire              ← "Gate what joins the swarm"
    ├── .Scanner                  ← SkillScanner
    ├── .Registry                 ← RegistryList + skills-registry.yaml
    ├── .Validator                ← YamlRedirectValidator
    └── .TrustGate                ← evaluate_registry()
```

---

## Recommended Next Steps (sequenced)

1. **Add a `platform_surface` field to `skills-registry.yaml`** for each skill — one line per skill mapping it to `Context / Execute / Assurance / Acquire`. Zero code change, immediate legibility gain.

2. **Update `.claude/skills/INDEX.md`** to group skills under the four platform names instead of a flat list.

3. **Emit `RoadTrip.Assurance.Bundle` after every EVOLVE cycle** — `trust_scorecard.build_trust_bundle()` is already written. Wire it into `memory_loop_orchestrator.run_cycle()` as the final output artifact.

4. **Use these names in all future session logs and planning docs** so future Claude sessions and collaborators inherit the vocabulary without needing to reverse-engineer the code structure.

---

*Generated: 2026-03-19 | Source: Session Log 20260319 lines 243-286 | Grounded in: src/skills/ actual code inventory*
