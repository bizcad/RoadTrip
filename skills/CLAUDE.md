# Autonomous Multi-Agent Workflow Pattern
**RoadTrip Skills Framework**
**Specs Version**: v1.0

---

## Overview

This directory contains Claude Skills designed as composable, autonomous agents that work together in a multi-agent orchestration pattern. Rather than building monolithic skills, we decompose complex workflows into:

- **Orchestrator Skills** — Decision-making and workflow coordination
- **Specialist Skills** — Cross-cutting concerns (auth, logging, validation, config)
- **Service Integrations** — Aspire, QuestionManager, external backends

This pattern enables:
- ✅ Single Responsibility (SOLID)
- ✅ Idempotent skill execution (can reset/recreate anytime)
- ✅ Graceful degradation (fail safely when dependencies unavailable)
- ✅ Feedback loops (telemetry drives Phase 2+ refinement)
- ✅ Transport abstraction (CLI/SDK/API swappable without logic changes)

---

## The Skill Composition Model

### Orchestrator → Specialists → Services

```
git-push-autonomous (Orchestrator)
    ↓ calls
┌───┬──────────┬─────────┬──────────┐
│   │          │         │          │
▼   ▼          ▼         ▼          ▼
telemetry  auth-validator rules-  git-
logger     (checks perms)  engine  operations
   ▼           ▼          ▼          ▼
   └───────────┴──────────┴──────────┘
           (calls)
          Services
    ┌──────────┬──────────┐
    ▼          ▼          ▼
Aspire    Question    GitHub
Config    Manager     SDK/API
```

### How It Works

1. **Orchestrator** (git-push-autonomous) evaluates: "Should I push these changes?"
2. Calls **specialist skills** in sequence:
   - `auth-validator`: "Am I authorized?" → calls Aspire auth service
   - `rules-engine`: "Do these files pass safety rules?" → loads rules from config
   - `telemetry-logger`: "Record this decision + reasoning"
3. **Result**: Structured decision with audit trail
4. **Execution**: If approved, calls git-operations (CLI/SDK interchangeably)
5. **Feedback**: Telemetry captured; Phase 2 learning updates rules

---

## Skill Idempotency Principle

**Every skill is idempotent:** Creating/recreating a skill should never fail due to conflicts.

- Skills read from configuration (don't hardcode rules)
- Skills append to telemetry (don't overwrite)
- Skills reference other skills by name (loose coupling)
- Skills validate dependencies before executing

**Implementation**: Skills check "has this already run?" before side effects.

---

## Design Constraints (SOLID Applied)

### Single Responsibility
- `git-push-autonomous`: Decision logic only
- `auth-validator`: Permission checks only  
- `rules-engine`: Rule evaluation only
- `telemetry-logger`: Logging only

### Open/Closed
- Skills **open** to new rules via configuration
- Skills **closed** for modification
- Rules live in data files; logic unchanged

### Liskov Substitution
- Git operations have an interface (execute command → return result)
- Can swap: CLI → GitHub SDK → API without changing decision logic
- Services have interfaces (auth, logging, config loading)

### Interface Segregation
- Skills don't need to know all system details
- They request what they need (e.g., "get rules for this file type")
- Services provide thin interfaces

### Dependency Inversion
- Skills depend on **abstractions** (Git interface, Auth service)
- Not concrete implementations (CLI, Aspire directly)
- Makes testing, swapping, upgrading seamless

---

## Phase Progression

### Phase 1: Foundation (Current)
- **Orchestrator**: git-push-autonomous (CLI-based)
- **Specialists**: auth, rules, telemetry (stubs/data-driven)
- **Transport**: PowerShell CLI (proven stable)
- **Decision Loop**: Log + analyze patterns
- **Goal**: Prove autonomy works; establish feedback loop

### Phase 2: Enhancement (Next)
- **Transport**: Swap CLI → GitHub SDK (better event visibility)
- **Telemetry**: Integrate with QuestionManager
- **Auth**: Integrate with Aspire
- **Decision Logic**: Same (transport abstraction works)
- **Learning**: Begin Phase 2 refinement (confidence scoring, pattern analysis)

### Phase 3: Optimization (Later)
- **Transport**: GitHub API (full control, parallelization)
- **Learning**: Auto-adjust rules based on telemetry patterns
- **Composition**: Add more specialist skills (security scan, code review, etc.)
- **Autonomy**: Multi-agent coordination (multiple orchestrators)

---

## Telemetry & Learning Loop

Every decision creates a **decision log entry**:

```json
{
  "timestamp": "2026-02-05T14:23:45Z",
  "orchestrator": "git-push-autonomous",
  "decision": "APPROVED",
  "reasoning": {
    "auth_validator": { "status": "PASS", "confidence": 0.99 },
    "rules_engine": { "status": "PASS", "blocked_files": [], "confidence": 0.95 },
    "telemetry_logger": { "status": "RECORDED" }
  },
  "files_affected": ["src/main.rs", "Cargo.toml"],
  "git_result": "SUCCESS",
  "commit_hash": "abc123def456"
}
```

**Phase 2 Learning**: Analyze these logs to:
- Identify safe file patterns (increase confidence)
- Detect false positives (refine rules)
- Tune decision thresholds

---

## Calling a Specialist Skill

```markdown
## When I need to validate rules:
Call the `rules-engine` skill with:
- `files`: ["path/to/file1", "path/to/file2"]
- `context`: "pre-commit validation"

It will return:
- `approved`: boolean
- `blocked_files`: [list with reasons]
- `confidence`: 0-1 score
```

---

## Error Handling & Graceful Degradation

**If a specialist skill fails:**
- Orchestrator logs the failure
- Falls back to conservative decision (e.g., don't push if auth-validator unavailable)
- Records why it fell back
- Operator can override (future feature)

**Example**:
```
Attempt auth-validator → Returns ERROR (Aspire service down)
Result: BLOCKED + "Auth service unavailable; cannot proceed safely"
Operator sees: Warning in logs; knows why push failed; can restart Aspire
```

---

## File Layout

```
skills/
├── CLAUDE.md                    ← You are here. Pattern guide.
├── git-push-autonomous/
│   ├── CLAUDE.md               ← Decision logic for git-push
│   ├── SKILL.md                ← Triggering + capabilities
│   ├── safety-rules.md          ← Exclusion patterns, validation rules
│   ├── decision-tree.md         ← Step-by-step decision flow
│   ├── examples.md              ← Usage scenarios
│   └── config/                  ← Data files (rules, templates)
│       ├── exclusions.yaml
│       ├── commit-templates.yaml
│       └── confidence-thresholds.yaml
├── telemetry-logger/
│   ├── CLAUDE.md               ← How telemetry drives learning
│   ├── SKILL.md
│   └── config/
│       └── telemetry-schema.json
├── auth-validator/
│   ├── CLAUDE.md
│   ├── SKILL.md
│   └── config/
│       └── scope-requirements.json
├── rules-engine/
│   ├── CLAUDE.md
│   ├── SKILL.md
│   └── config/
│       └── rule-sets.json
└── git-operations/              ← Phase 1: CLI adapter; Phase 2: SDK
    ├── CLAUDE.md
    └── SKILL.md
```

---

## Key Principles for Development

1. **Keep it dumb, make it deterministic**
   - Skills execute the same way every time (given same inputs)
   - Configuration drives behavior variation
   - Logs explain every decision

2. **Fail safely by default**
   - If in doubt, don't proceed
   - Record why you didn't proceed
   - Let operator/Phase 2 learning adjust thresholds

3. **Build feedback loops early**
   - Log everything, analyze later
   - Phase 1 establishes baseline; Phase 2 optimizes from data
   - Don't hard-code rules; make them data-driven

4. **Design for swapping**
   - CLI → SDK → API transitions should be frictionless
   - Auth providers, config sources can change
   - Specialist skills can be upgraded independently

---

## What Success Looks Like

✅ **Phase 1 Complete**: Autonomously stages/commits/pushes safe files, logs every decision, never requires user interaction  
✅ **Idempotent**: Skill can be recreated 10x without conflicts  
✅ **Observable**: Telemetry clearly explains what happened + why  
✅ **Ready for Phase 2**: Decision logs rich enough to drive learning  

---

## Next Steps

1. Review this pattern with team
2. Build `git-push-autonomous/` orchestrator + supporting docs
3. Implement specialist skills (telemetry, auth, rules)
4. Test Phase 1 with real commits
5. Analyze telemetry; plan Phase 2

---

**Last updated**: 2026-02-05  
**Pattern version**: 1.0  
**Status**: Ready for implementation
