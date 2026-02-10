# RoadTrip Skills Framework: Principles and Processes

**Version**: 1.3
**Last Updated**: 2026-02-10  
**Status**: Active (Living Document)

---

## Table of Contents
1. [Project Vision](#project-vision)
2. [Core Principles](#core-principles)
3. [Software Engineering Standards](#software-engineering-standards)
4. [Skill Development Methodology](#skill-development-methodology)
5. [Code Organization](#code-organization)
6. [Quality & Review Process](#quality--review-process)
7. [Documentation Standards](#documentation-standards)
8. [Workflow Integration](#workflow-integration)

---

## Project Vision

The RoadTrip project aims to create a **self-organizing, self-documenting, and self-orchestrating multi-agent skill framework** that:

1. **Maximizes deterministic code**: Business logic, rules, safety checks → Python skills in `src/skills/`
2. **Delegates probabilistic tasks to LLMs**: Creative work, decision reasoning, code generation → Claude agents
3. **Enables cost-efficient skill composition**: Reusable skills orchestrated by a central coordinator
4. **Supports continuous expansion**: Ever-growing library of skills, each independently testable and deployable
5. **Maintains auditability**: Every decision logged with confidence scores and reasoning

**Current Focus**: `git-push-autonomous` workflow
- **Phase 1a**: Rules-engine proof of concept ✅ Complete
- **Phase 1b**: Auth validator, telemetry logger, commit message generator, orchestrator
- **Phase 2**: Content scanning, override mechanisms, learning loops

---

## Core Principles

### 1. Conservative Defaults (Fail-Safe)

**"If in doubt, block."**

- Default behavior blocks risky operations
- Operators must explicitly allow exceptions
- Better to reject a safe operation than permit an unsafe one
- Example: Missing config → block all files, not approve all

### 2. SOLID Software Engineering

**Our code is engineered for:**
- **Single Responsibility**: Each module has one reason to change
- **Open/Closed**: Extensible via config, not code modification
- **Liskov Substitution**: Interchangeable implementations of contracts
- **Interface Segregation**: Minimal, focused public APIs
- **Dependency Inversion**: High-level code depends on abstractions, not concretions

### 3. Deterministic Code, Probabilistic Reasoning

**Code layer** (deterministic):
- File validation (rules-engine)
- Git credential checks (auth-validator)
- Logging decisions (telemetry-logger)
- **These always produce the same output for the same input**

**Reasoning layer** (probabilistic):
- Claude generates commit messages
- Claude decides when to run the skill pipeline
- Claude learns from telemetry logs
- **These may vary; confidence scores reflect uncertainty**

### 4. Idempotent Evaluation, Intentional Artifacts

**Evaluation skills** (rules-engine, auth-validator) are pure functions:
- **Idempotent**: Running twice = same result (no mutations)
- **Deterministic**: Same input → identical output
- **Testable**: Can run in CI/CD loops without locks or cleanup

**Execution skills** (telemetry-logger, orchestrator) produce intentional artifacts:
- Log files, commit history, push results are the *point* of the system
- Artifacts are append-only and auditable
- Execution is idempotent in *effect* (re-pushing the same commit is a no-op)

The distinction: evaluation functions have no side effects; execution functions have *deliberate, logged* side effects.

### 5. Security-First Architecture

**Default posture:**
- Blocks secrets by design (`.env`, `.secrets`, SSH keys)
- Never logs credentials or sensitive contents
- Validates git permissions before pushing
- Logs all decisions with audit trail

### 6. Machine-Readable Code

**All code must be:**
- **Typed**: Full type hints for IDE support and static analysis
- **Documented**: Docstrings on every public function
- **Referenced**: Cross-links to specs and decision documents
- **Versioned**: Semantic versioning; backward compatibility maintained

### 7. Error Handling & Resilience

**"Fail safely, recover gracefully, explain always."**

Autonomous agents must handle errors without human intervention:

- **Graceful degradation**: If a specialist crashes (not just returns FAIL), the orchestrator catches the exception, logs it, and falls back to a conservative decision
- **Retry with backoff**: Network-dependent operations (git ls-remote, git push) retry up to 3 times with exponential backoff before declaring failure
- **Guardrails over gates**: Prefer warning + logging over hard blocking when the risk is low. Reserve hard blocks for security (credentials, secrets)
- **Structured error reporting**: Every failure includes: what failed, why, what was attempted, what the operator should do next
- **Exit codes map to recovery actions**: Each error code has a documented recovery path (see `skills/git-push-autonomous/decision-tree.md`)

**Error hierarchy** (most to least severe):
1. **Security violation** → Hard block, no retry, log immediately
2. **Auth failure** → Block, suggest credential fix, no retry
3. **Rules violation** → Block, list offending files, suggest removal
4. **Network timeout** → Retry with backoff, then block with explanation
5. **Telemetry failure** → Warn, continue (non-critical)

---

## Software Engineering Standards

### Code Quality Checklist

Every Python file MUST include:

```python
"""Module docstring explaining purpose, spec references, and design."""

from __future__ import annotations  # PEP 563: future annotations

from dataclasses import dataclass
from pathlib import Path

# Use type hints throughout
@dataclass
class MyClass:
    """Docstring with Args, Returns, Raises."""
    field: str
    value: int = 0

def my_function(x: str, y: int = 0) -> str:
    """Docstring with complete signature.
    
    Args:
        x: Description of x.
        y: Description of y.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When x is empty.
    """
    if not x:
        raise ValueError("x cannot be empty")
    return f"{x}:{y}"
```

### Python Version & Dependencies

- **Python**: 3.10+ (type hint support)
- **Core dependencies**: Only `pyyaml` (YAML parsing)
- **Test dependencies**: `pytest`
- **No external service calls**: All deterministic; stdout/stderr only

*See [Code Organization](#code-organization) section for full directory structure.*

### PowerShell & CLI Wrapper Standards

**CRITICAL: Never declare `-Verbose` or `-Confirm` parameters explicitly.**

PowerShell has built-in common parameters (`-Verbose`, `-Debug`, `-Confirm`, `-WhatIf`, `-ErrorAction`, `-WarningAction`, `-Verbose`, `-Verbose`, `-WarningVariable`, `-ErrorVariable`, `-OutVariable`, `-OutBuffer`). These are automatically added to every function—declaring them again causes a "duplicate parameter" error.

**❌ WRONG:**
```powershell
function bpublish {
    param(
        [string]$Title,
        [switch]$DryRun,
        [switch]$Verbose  # ❌ PowerShell already provides this!
    )
    # Error: "A parameter with the name 'Verbose' was defined multiple times for the command."
}
```

**✅ CORRECT:**
```powershell
function bpublish {
    param(
        [string]$Title,
        [switch]$DryRun
        # Don't declare -Verbose; PowerShell provides it automatically
    )
    
    # Check verbose state using automatic variable
    if ($VerbosePreference -eq "Continue") {
        Write-Host "Verbose output..."
    }
}
```

**Why this matters**: Users call functions with `-Verbose` by default; we must accept it transparently. Declaring it explicitly breaks the function entirely.

**Additional CLI wrapper rules:**
1. **Use dot-sourcing** (`. .\script.ps1`) not `Import-Module` for function loading
2. **Never use `Export-ModuleMember`** outside of actual modules (`.psm1` files)
3. **Prefer `$PSCmdlet.ShouldProcess()`** for dry-run / `-WhatIf` support
4. **Use Set-Alias** AFTER function definition, not before
5. **Color output** with `Write-Host -ForegroundColor` for user feedback
6. **Avoid PowerShell automatic variable names** in loops: use `$item` not `$error`, `$_`, or `$args`

*See [Phase 5 - CLI Integration](../workflows/PHASE-5-COMPLETION.md) for implementation examples.*

---

## Skill Development Methodology

### Phase Model: Proof-of-Concept First

**Lessons from Phase 1a:**

1. **Build one specialist first** (not all three at once)
   - Validates architecture before scaling
   - De-risks full framework build
   - Proves the skill pattern works

2. **Use POC to establish templates**
   - Each Phase 1b skill mirrors rules-engine structure
   - Same dataclass pattern → same models.py
   - Same CLI pattern → same argument parsing
   - Same test pattern → same fixtures and test matrix

3. **Spec-Driven Development**
   - Write SKILL.md (interface) before code
   - Write CLAUDE.md (reasoning) before code
   - Code implements the spec, doesn't define it

### The Skill Development Workflow

```
1. SPECIFICATION (Docs-First)
   - Create skills/my-skill/SKILL.md (interface & inputs/outputs)
   - Create skills/my-skill/CLAUDE.md (decision logic)
   - Review with domain expert
   - Iterate until spec is locked

2. CODE GENERATION (LLM Code Agent)
   - Agent reads SPEC from SKILL.md/CLAUDE.md
   - Generates src/skills/my-skill.py
   - Follows established patterns (models, config, logic)
   - Generates tests/test_my-skill.py
   - Outputs code for review (not yet committed)
   - *Current tooling: Claude Code — replaceable*

3. CODE REVIEW (Review Agent)
   - Check against SOLID principles
   - Verify idempotency & determinism
   - Scan for security issues
   - Validate machine readability
   - Run tests: pytest tests/test_my-skill.py -v
   - Approve or request changes
   - *Current tooling: GitHub Copilot — replaceable*

4. INTEGRATION (Human + Claude)
   - Commit to git: src/skills/my-skill.py + tests
   - Build Phase 1b orchestrator using this skill
   - Integration test with other skills
   - Update docs/README with new skill

5. DOCUMENTATION & DEPLOYMENT
   - Add skill to CLAUDE.md skill registry
   - Document outputs in code & specs
   - Add to orchestrator's step-by-step flow
   - Ready for Phase 2 enhancement
```

---

## Code Organization

### Directory Structure & Conventions

**`skills/` (Documentation)**
```
skills/
├── CLAUDE.md                    # Framework-level instructions
├── git-push-autonomous/
│   ├── SKILL.md                 # Spec: interface, triggers
│   ├── CLAUDE.md                # Reasoning: decision logic
│   ├── decision-tree.md         # Detailed workflows
│   ├── safety-rules.md          # Exclusion rules reference
│   └── examples.md              # Usage examples
├── auth-validator/
│   ├── SKILL.md
│   └── CLAUDE.md
├── rules-engine/
│   ├── SKILL.md
│   └── CLAUDE.md
└── telemetry-logger/
    ├── SKILL.md
    └── CLAUDE.md
```

**`src/skills/` (Implementation)**
```
src/skills/
├── __init__.py
├── models.py                    # All dataclasses, including stubs
├── config_loader.py             # Load config/*.yaml files
├── rules_engine.py              # Phase 1a ✅
├── auth_validator.py            # Phase 1b 🔄
├── telemetry_logger.py          # Phase 1b 🔄
├── commit_message.py            # Port from PowerShell
└── git_push_autonomous.py       # Orchestrator
```

**`tests/` (Test Suite)**
```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── test_rules_engine.py         # Phase 1a ✅
├── test_auth_validator.py       # Phase 1b 🔄
├── test_telemetry_logger.py     # Phase 1b 🔄
├── test_commit_message.py
└── test_git_push_autonomous.py  # Integration tests
```

### Module Responsibilities

| Module | Responsibility | Example |
|--------|-----------------|---------|
| `models.py` | Type definitions | `RulesResult`, `AuthResult`, `StepResult` |
| `config_loader.py` | Config I/O | Load YAML → typed dataclass |
| `*_engine.py` / `*_validator.py` / `*_logger.py` | Business logic | File checks, git auth, logging |
| `conftest.py` | Test fixtures | `sample_config`, `tmp_repo`, mocks |
| `test_*.py` | Unit + integration | All cases from YAML + edge cases |
| `skill_orchestrator.py` | Workflow orchestration | Calls specialists in sequence; manages exit codes; produces artifacts |

---

## Quality & Review Process

### Code Review Checklist

**Before code reaches main branch:**

- [ ] **Specification**: Does code implement SKILL.md exactly?
- [ ] **SOLID**: Single responsibility? Open/closed? Dependency inversion?
- [ ] **Idempotency**: Same input → same output? No side effects?
- [ ] **Security**: Conservative defaults? No credential leaks? Path normalization?
- [ ] **Types**: Full type hints? Docstrings on all public functions?
- [ ] **Tests**: 100% coverage of Phase N logic? Edge cases? Fixtures?
- [ ] **Determinism**: No randomness, no timestamps in logic (only logging)?
- [ ] **Documentation**: Cross-references to SKILL.md and CLAUDE.md?
- [ ] **Backward Compatibility**: Dataclass fields have defaults? Config has fallbacks?

### Testing Standards

**Every skill MUST pass:**

```bash
# Unit tests
pytest tests/test_my_skill.py -v

# Type checking (optional but recommended)
mypy src/skills/my_skill.py

# Coverage
pytest tests/test_my_skill.py --cov=src/skills.my_skill --cov-report=term-missing
```

**Test file MUST include:**

1. **Tests from spec** (built-in cases from config files)
2. **Edge cases** (empty lists, missing config, invalid input)
3. **Fixtures** (sample configs, temp repos, mocks)
4. **Confidence levels** (assert confidence 1.0 for blocks, 0.99 for approvals)

---

## Documentation Standards

### Three-Layer Documentation

**Layer 1: Code (Reference)**
```python
"""Rules Engine Skill - File safety validation.

Spec: skills/rules-engine/SKILL.md, skills/rules-engine/CLAUDE.md
Config: config/safety-rules.yaml
"""

@dataclass
class RulesResult:
    """Aggregate result from the rules-engine skill."""
    decision: str  # "APPROVE" | "BLOCK_ALL"
```

**Layer 2: Specs (Interface)**
```markdown
# SKILL.md - What it does
- Input: list of file paths
- Output: decision + blocked files
- Configuration: config/safety-rules.yaml

# CLAUDE.md - Why it decides that way
- Conservative defaults: block until proven safe
- Phase 1: explicit blocklist → patterns → size
- Phase 2: content scanning planned
```

**Layer 3: Framework (Learning)**
```markdown
# Principles-and-Processes.md
- How skills are built (POC → code gen → review → integration)
- Why SOLID matters (extensibility, testability)
- What determinism means (idempotent, side-effect-free)
```

### Documentation Files

| File | Purpose |
|------|---------|
| `skills/CLAUDE.md` | Framework instructions; skill registry |
| `skills/*/SKILL.md` | Interface spec: inputs, outputs, config |
| `skills/*/CLAUDE.md` | Decision logic: why decisions are made |
| `docs/Principles-and-Processes.md` | How we build; what we value |
| `docs/README_RoadTrip.md` | Project overview, getting started |
| `workflows/plan.md` | Master implementation plan (living artifact) |
| `workflows/NNN-name/plan.md` | Per-feature plans, reviews, execution records |

The `workflows/` directory captures **reproducible process artifacts** — plans, code reviews, and phase completion records. Each numbered workflow (e.g., `001-gpush-skill-set/`) represents a unit of work that can be replayed, reviewed, or used as a commit boundary.

---

## Workflow Integration

### How Skills Are Built

**Phase 1a (Complete)**: Rules Engine POC
- ✅ Spec complete (SKILL.md, CLAUDE.md)
- ✅ Code generated (src/skills/rules_engine.py)
- ✅ Tests passing (25/25)
- ✅ Review approved (SOLID, secure, deterministic)

**Phase 1b (Next)**: Three Specialists
1. `auth_validator.py` - Git credential/permission checks
2. `telemetry_logger.py` - JSONL decision logging
3. `commit_message.py` - Port from PowerShell

Then: `git_push_autonomous.py` (Orchestrator + CLI)

**Phase 2 (Next): Fingerprinting + Skill Discovery**

**Why Phase 2 Exists**: Phase 1b skills are deterministic and tested, but once deployed, how do we ensure they haven't been modified? How can we discover skills dynamically? How do we verify the skills we find are trustworthy?

**Strategic Context**: Validated by DyTopo research (Peking University / Georgia Tech, Feb 2026), which demonstrates that AI orchestration via semantic skill discovery achieves 8-billion-parameter model performance equivalent to 120-billion-parameter models. See [DyTopo_Analysis_And_SKILLS_Implications.md](./DyTopo_Analysis_And_SKILLS_Implications.md) for full analysis.

**Phase 2a (Q1 2026): Fingerprinting Infrastructure**
- ✅ **Objective**: Cryptographic attestation for Phase 1b skills (prevent tampering)
- ✅ **Deliverables**:
  - `SkillFingerprint` dataclass: `skill_id`, `version`, `code_hash` (SHA256), `capabilities_hash`, `max_execution_time_ms`, `allowed_external_calls`, `baseline_latency_avg_ms`, `baseline_success_rate`, `fingerprint_hash` (composite), `attestor_signature`  
  - Fingerprint generation logic (runs post-vetting)
  - Fingerprint verification check (runs pre-execution)
  - Vetting pipeline template: (1) static analysis (bandit, secret detection), (2) sandbox test, (3) fingerprint signature, (4) capability assertion
- 🎯 **Success Criteria**: All Phase 1b skills have signed fingerprints; runtime verification never fails on unmodified skills

**Phase 2b (Q2 2026): Skill Registry + Discovery**
- ✅ **Objective**: Enable dynamic skill discovery via semantic matching + trust scoring
- ✅ **Deliverables**:
  - `SkillContract` dataclass: `skill_id`, `version`, `query` (DyTopo descriptor: what I need), `key` (what I offer), `supported_operations`, `input_schema`, `output_schema`, `required_permissions`, `max_execution_time_ms`, `slo_latency_p99_ms`, `slo_success_rate`, `trust_score`, `known_limitations`
  - Skill registry backend (YAML/JSON storage; can upgrade to database later)
  - `find_nearest_skills(query, min_trust_score)` function (semantic search via embeddings + cosine similarity)
  - Trust scoring engine: `trust_score = f(test_pass_rate, fingerprint_match, production_success_rate)`
  - Capability introspection API (MCP-style: "What can this skill do?")
- 🎯 **Success Criteria**: Registry achieves >95% recall (Skill finds correct skills for queries); trust scores predict reliability (Pearson correlation > 0.7 with actual success); operator surveys show "discovery saves time vs manual mapping"

**Phase 2c (Optional - Q3 2026): Dynamic Topology Routing**
- ✅ **Objective**: Full semantic routing per DyTopo paper (ONLY if Phase 2b proves sufficient value)
- ✅ **Implementation**: Five-phase pipeline from DyTopo paper (descriptor generation → semantic graph induction → topological sequencing → routing → memory update)
- ✅ **Cost/Benefit**: Only pursue if Phase 2b discovery validation shows operational benefit exceeds implementation cost
- 🎯 **Decision Gate**: Before Phase 2c, evaluate:
  - Discovery success rate > 95% AND
  - Trust scores correlate with actual reliability > 0.7 AND  
  - Operator feedback is positive AND  
  - Cost of Phase 2c implementation justified by time savings
  - If any gate fails: **STOP**. Deterministic pyramid (Phase 2b) is sufficient for autonomous workflows.

**Key Principle**: "Finish what we started." Complete Phase 1b before moving to Phase 2a. Establish fingerprinting and discovery infrastructure in Phase 2a/2b. Only invest in full dynamic routing (Phase 2c) if operational metrics validate it.

---

## Version Control & Branching

### Commit Strategy: Conventional Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/) with `scope` = skill or module name.

**Format**: `type(scope): description`

| Type | When | Example |
|------|------|---------|
| `feat` | New skill or capability | `feat(rules-engine): implement file safety validation` |
| `fix` | Bug fix to existing skill | `fix(rules-engine): prevent .gitignore from being blocked` |
| `docs` | Specs, guides, comments | `docs(skills): add Principles-and-Processes guide` |
| `refactor` | Code restructuring | `refactor(models): extract BlockedFile to shared module` |
| `test` | Test additions/changes | `test(rules-engine): add edge cases for hidden files` |
| `chore` | Build, config, deps | `chore(deps): update pyyaml to 6.0.2` |

**Why formal**: Enables automated changelogs, version bumps, and aligns with `commit_message.py` auto-generation in Phase 1b.

---

## Learning & Iteration

### Feedback Loops

**From code errors** → Fix bugs → Update tests
**From test failures** → Refine specifications → Regenerate code
**From telemetry logs** (Phase 2) → Learn patterns → Auto-refine rules
**From reviews** → Establish patterns → Use in Phase 1b skills

### Continuous Improvement

- **Weekly**: Review test coverage, code churn, CI/CD failures
- **Monthly**: Assess skill utility, plan Phase N enhancements
- **Quarterly**: Re-examine SOLID principles, refactor if needed

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Test coverage | 100% of Phase N logic | ✅ 25/25 passing Phase 1a |
| Code review approval | 0 SOLID violations | ✅ Approved Phase 1a |
| Execution time | <5s per skill | ✅ Rules engine ~10ms |
| Security incidents | 0 credential leaks | ✅ No credentials stored |
| Determinism | 100% idempotent | ✅ Rules engine idempotent |
| Documentation | Every public function documented | ✅ 100% in Phase 1a |
| False positive rate | <5% of pushes blocked incorrectly | 📊 Tracking starts Phase 1b |
| Skills implemented | 4 specialists + 1 orchestrator | ✅ 1/4 specialists (rules-engine) |

---

## Contact & Questions

For questions about this framework:
1. See the relevant SKILL.md or CLAUDE.md
2. Check CODE_REVIEW_Phase1a.md for code quality examples
3. Review source code in src/skills/ for implementation details
4. Run `pytest tests/ -v` to validate the system

---

## Version Alignment

Versions are tracked **by layer**, not per-file. Bump the layer version when any artifact in that layer changes.

| Layer | Version | Scope | Where Tracked |
|-------|---------|-------|---------------|
| **Specs** | v1.0 | All `skills/*/SKILL.md`, `skills/*/CLAUDE.md`, `skills/CLAUDE.md` | `skills/CLAUDE.md` header |
| **Implementation** | 0.1.0 | All `src/skills/*.py`, `tests/`, `pyproject.toml` | `pyproject.toml` `version` field |
| **Docs** | v1.1 | `docs/`, `workflows/` | This document header |

**Phase 1a Alignment**
- Specs: v1.0 (`skills/rules-engine/SKILL.md`, `CLAUDE.md`)
- Implementation: 0.1.0 (`src/skills/rules_engine.py`, tests)
- Docs: v1.1 (this document + `workflows/plan.md`)

---

**Maintained by**: LLM code agents (currently Claude Code + GitHub Copilot)
**Last Review**: 2026-02-10
**Next Review**: 2026-03-10
