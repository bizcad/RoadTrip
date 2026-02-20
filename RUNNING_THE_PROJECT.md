# How to Run RoadTrip: Entry Points & Usage Guide

> **Quick Start**: RoadTrip is a multi-functional AI agent framework. This guide explains all the ways to interact with and run functionality.

---

## Table of Contents
1. [Understanding the Four Paths](#understanding-the-four-paths)
2. [Navigating the Codebase](#navigating-the-codebase)
3. [User Path: Running Agents & Workflows](#user-path-running-agents--workflows)
4. [Developer Path: Building & Development](#developer-path-building--development)
5. [Self-Healing Path: Error Detection & Fixes](#self-healing-path-error-detection--fixes)
6. [Safety Path: Vetting & Policy Enforcement](#safety-path-vetting--policy-enforcement)
7. [Quick Reference: All Entry Points](#quick-reference-all-entry-points)

---

## Understanding the Four Paths

RoadTrip operates on **four distinct functional paths**:

```
┌────────────────────────────────────────────────────────────┐
│                    RoadTrip Framework                       │
├────────────────────────────────────────────────────────────┤
│ 1. USER PATH      │ Run agents, workflows, skills          │
│ 2. DEVELOPER PATH │ Build agents, workflows, code modules  │
│ 3. SELF-HEALING   │ Detect errors, analyze, auto-fix       │
│ 4. SAFETY PATH    │ Vet, catalog, enforce policy           │
└────────────────────────────────────────────────────────────┘
```

Each path has its own entry points and workflows. This separation ensures clarity and maintainability.

---

## Navigating the Codebase

### 🗺️ Navigation Tools

The codebase has comprehensive navigation documentation and tools:

#### **CODEBASE_MAP.md** - Visual Navigation Guide
```bash
# Read this file for a comprehensive map of the codebase
cat CODEBASE_MAP.md
```
**What it contains**:
- Files organized by the 4 functional paths
- Entry points vs libraries
- Common tasks with exact commands
- File relationships and dependencies
- Quick reference matrix

#### **navigate_codebase.py** - Interactive Navigation Tool
```bash
# Interactive mode (menu-driven)
py scripts/navigate_codebase.py

# Show files in a specific path
py scripts/navigate_codebase.py --path user

# Search for files
py scripts/navigate_codebase.py --search "blog"

# List all entry points
py scripts/navigate_codebase.py --entry-points

# List all skills
py scripts/navigate_codebase.py --skills

# Show how to accomplish a task
py scripts/navigate_codebase.py --task push_to_github

# List all common tasks
py scripts/navigate_codebase.py --list-tasks
```

#### **CODEBASE_INDEX_ENHANCED.json** - Structured Index
Machine-readable index with:
- Files classified by purpose, layer, and path
- Dependencies and relationships
- Entry points with commands
- Common tasks with step-by-step instructions
- Workflow definitions

**Pro Tip**: If you're lost, start with:
1. Read [CODEBASE_MAP.md](CODEBASE_MAP.md) for orientation
2. Run `py scripts/navigate_codebase.py --list-tasks` to see what you can do
3. Run `py scripts/navigate_codebase.py --path user` to see user-facing tools

---

## Developer Dashboard: Project State Tracking

### 🎛️ Purpose
Interactive CLI for tracking project state, viewing system status, and monitoring development progress.

### 🚀 Quick Start
```bash
# Launch dashboard (interactive menu)
py scripts/dev_dashboard.py

# Jump to specific menu
py scripts/dev_dashboard.py --menu 1   # Project State
py scripts/dev_dashboard.py --menu 3   # Skills Registry
py scripts/dev_dashboard.py --menu 6   # Codebase Navigation
```

### 📊 Available Menus

**Currently Implemented:**
1. **Project State** - Current phase, milestones, blockers, quick stats
3. **Skills Registry** - All registered skills with fingerprints and coverage
6. **Codebase Navigation** - Browse files by path, task, or skill

**Partially Implemented:**
2. **Memory System** - View 7 memory layers (Auto, Session, Working, etc.)
4. **Test Results** - Test status, coverage, history
5. **Execution History** - Telemetry and execution logs

**Coming Soon:**
7. **System Health** - Git status, dependencies, disk usage, error rates
8. **Settings & Secrets** - Config management and secret storage

### 🎯 Use Cases

**"Where are we?"** → Menu 1 (Project State)  
Shows current phase, next milestone, active skills, blockers

**"What skills exist?"** → Menu 3 (Skills Registry)  
Lists all skills with status, fingerprints, coverage

**"How do I find files?"** → Menu 6 (Codebase Navigation)  
Browse by functional path or search

**"What can I do?"** → Menu 6 → Common Tasks  
Shows recipes for push_to_github, run_tests, etc.

### 📚 Documentation
- **Design**: [DEV_DASHBOARD_DESIGN.md](DEV_DASHBOARD_DESIGN.md) - Full architecture and menu specifications
- **Usage**: [DEV_DASHBOARD_USAGE.md](DEV_DASHBOARD_USAGE.md) - How to extend and customize

### 🔧 Requirements
```bash
# Required
py -m pip install pyyaml

# Optional (for rich CLI with checkboxes)
py -m pip install prompt-toolkit
```

---

## User Path: Running Agents & Workflows

### ✈️ Purpose
Execute agents and workflows to accomplish tasks (blog publishing, git operations, data analysis, etc.)

### 🎯 Entry Points

#### 1. **Orchestrator** - Main workflow execution engine
```bash
# Run the orchestrator demo
py src/orchestrator.py
```
**What it does**: Loads skills from registry, chains them together, executes workflows  
**Use when**: You want to run a pre-defined skill chain  
**Input**: Workflow definition (list of skills + configs)  
**Output**: SkillResult objects with status, output, errors

#### 2. **Blog Publisher** - Publish blogs via skill orchestration
```bash
# Interactive mode
py src/publish_blog.py

# Via orchestrator
py src/orchestrate_blog_publish.py
```
**What it does**: Validates, generates, and publishes blog posts  
**Use when**: Publishing content to your blog  
**Requirements**: Blog config in `config/blog-config.yaml`

#### 3. **Git Push Autonomous** - Automated git operations
```bash
# Python version
py scripts/commit_and_push_updates.py

# PowerShell version (direct execution)
pwsh scripts/git_push.ps1 -Message "your commit message"

# Shortcut (from project root)
gpush "optional message"
```
**What it does**: Stages files, generates commit message (using AI skill), commits, pushes  
**Use when**: Pushing code changes  
**Requirements**: PAT token in `ProjectSecrets/PAT.txt`

#### 4. **View Registry** - Browse registered skills
```bash
py src/view_registry.py
```
**What it does**: Lists all skills in the registry with status, capabilities  
**Use when**: You want to see what skills are available

#### 5. **List Skills** - Quick skill enumeration
```bash
py src/list_skills.py
```
**What it does**: Scans and lists all discovered skills  
**Use when**: Quick check of available skills

---

## Developer Path: Building & Development

### 🔧 Purpose
Build new agents, workflows, skills, and code modules. Develop the framework itself.

### 🎯 Entry Points

#### 1. **Registry Builder** - Scan and catalog skills
```bash
# Information mode (read-only)
py src/registry_builder.py --info

# Verify registry is current
py src/registry_builder.py --verify

# Rebuild registry (mutating)
py src/registry_builder.py --build --force
```
**What it does**: Scans `src/skills/` directory, extracts metadata, builds `config/skills-registry.yaml`  
**Use when**: Adding new skills or updating skill metadata  
**Safety**: Default mode is read-only; requires `--force` to modify

#### 2. **Skill Discovery** - Find and analyze skills
```bash
py scripts/discover_skills.py
```
**What it does**: Deep scan of codebase to find skill implementations  
**Use when**: Auditing what skills exist vs what's registered

#### 3. **Fingerprint Agent** - Generate skill fingerprints
```bash
# Fingerprint one skill
py src/agents/fingerprint_agent.py --skill auth_validator

# Fingerprint all Phase 1b skills
py src/agents/fingerprint_agent.py --all

# Skip signing
py src/agents/fingerprint_agent.py --skill commit_message --no-sign
```
**What it does**: Generates cryptographic fingerprints for skills (SHA-256 hash)  
**Use when**: Validating skill integrity or after modifying skill code  
**Output**: Stores fingerprints in registry

#### 4. **Registry Agent** - Manage skill registration
```bash
# List all skills
py src/agents/registry_agent.py --list

# Search for skills
py src/agents/registry_agent.py --search "blog"

# Show skill details
py src/agents/registry_agent.py --detail auth_validator
```
**What it does**: CRUD operations on skill registry  
**Use when**: Managing skill lifecycle (add, update, remove, search)

#### 5. **Trust Scorecard Generator** - Generate trust reports
```bash
py scripts/generate_trust_scorecard.py --skill auth_validator --output data/trust-scorecard.json
```
**What it does**: Analyzes skill for security, tests, documentation; generates scorecard  
**Use when**: Vetting a new skill or auditing existing ones

#### 6. **MCP Discovery Client** - Discover MCP servers
```bash
py src/mcp/discovery/mcp_server_registry_client.py server1.py server2.py
```
**What it does**: Connects to MCP servers, discovers capabilities  
**Use when**: Integrating external MCP servers into RoadTrip

---

## Self-Healing Path: Error Detection & Fixes

### 🔍 Purpose
Detect errors, analyze failures, propose fixes, and adapt system behavior.

### 🎯 Entry Points

#### 1. **Adaptive Executor** - Self-adjusting skill execution
```python
# Import and use programmatically
from skills.adaptive_executor import AdaptiveExecutor

executor = AdaptiveExecutor()
result = executor.execute(skill_name="auth_validator", input_data={...})
```
**What it does**: Executes skills with automatic retry, fallback, and adaptation  
**Use when**: Running skills that may fail and need resilience  
**Features**: Tracks failure patterns, adjusts timeouts, suggests alternatives

#### 2. **Memory Loop Orchestrator** - Learn from past executions
```python
from skills.memory_loop_orchestrator import MemoryLoopOrchestrator

orchestrator = MemoryLoopOrchestrator()
result = orchestrator.run_with_memory(skill="commit_message", context={...})
```
**What it does**: Executes skills while recording outcomes; learns from past failures  
**Use when**: You want the system to remember and adapt over time  
**Storage**: Episodic memory in `data/memory/`

#### 3. **Verification Scripts** - Check system integrity
```bash
# Verify Phase 2c implementation
py verify_phase_2c.py

# Run test suite with coverage
pytest tests/ --cov=src --cov-report=html
```
**What it does**: Validates that system components are working correctly  
**Use when**: After major changes or before release

#### 4. **Export Audit Logs** - Analyze historical behavior
```bash
py scripts/export_phase2b_audit_logs.py --output data/audit-export.jsonl
```
**What it does**: Exports telemetry and execution logs for analysis  
**Use when**: Debugging failures or understanding system behavior over time

---

## Safety Path: Vetting & Policy Enforcement

### 🛡️ Purpose
Acquire, vet, catalog, and enforce policy on code (SKILLs, MCPs, custom modules).

### 🎯 Entry Points

#### 1. **Release Evidence Gate** - Verify release readiness
```bash
py scripts/check_release_evidence.py \
  --manifest workflows/010-memory-for-self-improvement/release-evidence-manifest.json \
  --report data/release-report.json
```
**What it does**: Checks that all required evidence exists before release (tests, docs, fingerprints)  
**Use when**: Pre-release verification  
**Decision**: Returns GO or NO-GO based on evidence

#### 2. **Generate Release Evidence Manifest** - Create evidence checklist
```bash
py scripts/generate_release_evidence_manifest.py
```
**What it does**: Generates a manifest of required evidence for a release  
**Use when**: Setting up a new release workflow

#### 3. **Trust Scorecard** - Security & quality assessment
```bash
py scripts/generate_trust_scorecard.py --skill <skill_name>
```
**What it does**: Analyzes skill against trust criteria (tests, docs, security, provenance)  
**Use when**: Deciding whether to trust and use a new skill  
**Output**: JSON report with scores and recommendations

#### 4. **Fingerprint Verification** - Validate code integrity
```python
from src.skills.registry.fingerprint_verifier import FingerprintVerifier

verifier = FingerprintVerifier()
result = verifier.verify(skill_name="auth_validator")
print(f"Valid: {result.is_valid}, Expected: {result.expected_fingerprint}")
```
**What it does**: Compares current skill hash against registered fingerprint  
**Use when**: Before executing a skill (ensures no tampering)

#### 5. **Auth Validator** - Enforce authorization policy
```python
from skills.auth_validator import AuthValidatorSkill

validator = AuthValidatorSkill()
result = validator.validate(
    action="git_push",
    resources=["github.com/bizcad/RoadTrip"],
    context={"user": "agent", "mode": "autonomous"}
)
```
**What it does**: Checks if action is allowed per `config/authorization.yaml`  
**Use when**: Before any privileged operation (git push, API calls, file writes)

#### 6. **Rules Engine** - Enforce safety rules
```python
from skills.rules_engine import RulesEngine

engine = RulesEngine()
decision = engine.evaluate(
    action="execute_skill",
    skill_name="blog_publisher",
    context={"source": "user", "approved": True}
)
```
**What it does**: Applies rules from `config/safety-rules.yaml`  
**Use when**: Enforcing policy before execution

---

## Quick Reference: All Entry Points

### By Language

**Python Scripts (src/)**
| File | Command | Purpose |
|------|---------|---------|
| `orchestrator.py` | `py src/orchestrator.py` | Main workflow execution engine |
| `publish_blog.py` | `py src/publish_blog.py` | Interactive blog publisher |
| `view_registry.py` | `py src/view_registry.py` | View skill registry |
| `list_skills.py` | `py src/list_skills.py` | List available skills |
| `registry_builder.py` | `py src/registry_builder.py --info` | Build skill registry |

**Python Scripts (scripts/)**
| File | Command | Purpose |
|------|---------|---------|
| `commit_and_push_updates.py` | `py scripts/commit_and_push_updates.py` | Auto commit + push |
| `check_release_evidence.py` | `py scripts/check_release_evidence.py` | Release gate validation |
| `generate_trust_scorecard.py` | `py scripts/generate_trust_scorecard.py --skill X` | Trust analysis |
| `discover_skills.py` | `py scripts/discover_skills.py` | Skill discovery |

**Python Agents (src/agents/)**
| File | Command | Purpose |
|------|---------|---------|
| `registry_agent.py` | `py src/agents/registry_agent.py --list` | Manage registry |
| `fingerprint_agent.py` | `py src/agents/fingerprint_agent.py --all` | Generate fingerprints |

**PowerShell Scripts (scripts/)**
| File | Command | Purpose |
|------|---------|---------|
| `git_push.ps1` | `pwsh scripts/git_push.ps1 -Message "msg"` | Git push with automation |
| *Alias: `gpush`* | `gpush "msg"` | One-command git workflow |

**PowerShell Scripts (infra/)**
| File | Command | Purpose |
|------|---------|---------|
| `RoadTrip_profile.ps1` | *Auto-loaded in VS Code terminal* | Project aliases & env setup |

### By Use Case

| I want to... | Run this... |
|--------------|-------------|
| Execute a workflow | `py src/orchestrator.py` |
| Publish a blog post | `py src/publish_blog.py` |
| Commit and push code | `gpush` or `py scripts/commit_and_push_updates.py` |
| See available skills | `py src/view_registry.py` |
| Register a new skill | `py src/registry_builder.py --build --force` |
| Generate skill fingerprint | `py src/agents/fingerprint_agent.py --skill <name>` |
| Check skill trust score | `py scripts/generate_trust_scorecard.py --skill <name>` |
| Verify release readiness | `py scripts/check_release_evidence.py` |
| Discover MCP servers | `py src/mcp/discovery/mcp_server_registry_client.py` |
| Run tests | `pytest tests/` |
| Validate authorization | Use `AuthValidatorSkill` programmatically |

---

## Common Workflows

### 1. **Add a New Skill**
```bash
# 1. Create skill in src/skills/my_skill.py
# 2. Write tests in tests/test_my_skill.py
pytest tests/test_my_skill.py

# 3. Rebuild registry
py src/registry_builder.py --build --force

# 4. Generate fingerprint
py src/agents/fingerprint_agent.py --skill my_skill

# 5. Generate trust scorecard
py scripts/generate_trust_scorecard.py --skill my_skill

# 6. Verify it's registered
py src/view_registry.py
```

### 2. **Execute a Custom Workflow**
```python
from src.orchestrator import Orchestrator

orch = Orchestrator()
workflow = [
    ("auth_validator", {"action": "git_push", "resources": ["repo"]}),
    ("commit_message", {"staged_files": ["file.py"]}),
    ("telemetry_logger", {"event": "workflow_complete"})
]
results = orch.run_workflow(workflow)
```

### 3. **Verify System Integrity Before Deployment**
```bash
# 1. Run all tests
pytest tests/ --cov=src

# 2. Check Phase 2c implementation
py verify_phase_2c.py

# 3. Generate release evidence
py scripts/generate_release_evidence_manifest.py

# 4. Validate release evidence
py scripts/check_release_evidence.py

# 5. If GO, proceed with deployment
```

### 4. **Debug a Failing Skill**
```bash
# 1. Export audit logs
py scripts/export_phase2b_audit_logs.py

# 2. Check skill fingerprint
py src/agents/fingerprint_agent.py --skill failing_skill

# 3. Run skill tests in isolation
pytest tests/test_failing_skill.py -v

# 4. Check trust scorecard
py scripts/generate_trust_scorecard.py --skill failing_skill
```

---

## Configuration Files

All entry points rely on configuration in `config/`:

| File | Purpose |
|------|---------|
| `authorization.yaml` | Authorization rules (what actions are allowed) |
| `blog-config.yaml` | Blog publishing settings |
| `commit-strategy.yaml` | Git commit message generation rules |
| `known-solutions.yaml` | Self-healing solutions catalog |
| `safety-rules.yaml` | Safety enforcement rules |
| `skills-registry.yaml` | Registered skills catalog |
| `telemetry-config.yaml` | Telemetry and logging settings |

---

## Environment Requirements

- **Python**: 3.11+ (tested on 3.11)
- **PowerShell**: 7.5+ (for PowerShell scripts)
- **Git**: 2.40+ (for git operations)
- **pytest**: For running tests
- **GITHUB_TOKEN**: PAT token in `ProjectSecrets/PAT.txt`

---

## Next Steps

1. **New to RoadTrip?** Start with `python src/orchestrator.py` to see skills in action
2. **Want to build something?** Follow the "Add a New Skill" workflow above
3. **Need to debug?** Check the "Debug a Failing Skill" workflow
4. **Before deployment?** Run the "Verify System Integrity" workflow

For more details, see:
- [README.md](README.md) - Project overview and architecture
- [CLAUDE.md](CLAUDE.md) - Custom commands and context
- [CODEBASE_INDEX.json](CODEBASE_INDEX.json) - Complete file catalog (generated)

---

**Last Updated**: 2026-02-19  
**Maintainer**: See [governance/GOVERNANCE.md](governance/GOVERNANCE.md)
