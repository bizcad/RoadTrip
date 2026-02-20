# RoadTrip Codebase Navigation Map

> **Purpose**: Navigate the codebase by functional purpose, not just directory structure

Last Updated: 2026-02-19

---

## 🗺️ The Four Functional Paths

### 1️⃣ USER PATH: Execute Functionality

**What**: Run agents, workflows, and skills to accomplish tasks  
**Who**: End users (you, initially)  
**How**: CLI commands, Python scripts

#### Entry Points
| File | Command | Purpose |
|------|---------|---------|
| [src/orchestrator.py](src/orchestrator.py) | `py src/orchestrator.py` | Main workflow execution engine - chains skills together |
| [src/publish_blog.py](src/publish_blog.py) | `py src/publish_blog.py` | Interactive blog publishing |
| [src/orchestrate_blog_publish.py](src/orchestrate_blog_publish.py) | `py src/orchestrate_blog_publish.py` | Orchestrated blog publishing workflow |
| [scripts/commit_and_push_updates.py](scripts/commit_and_push_updates.py) | `py scripts/commit_and_push_updates.py` | Auto-commit and push using skills |
| [scripts/git_push.ps1](scripts/git_push.ps1) | `pwsh scripts/git_push.ps1` or `gpush` | PowerShell git push automation |
| [src/blog_publisher_cli.py](src/blog_publisher_cli.py) | `py src/blog_publisher_cli.py` | CLI interface for blog publishing |
| [src/view_registry.py](src/view_registry.py) | `py src/view_registry.py` | Browse registered skills |
| [src/list_skills.py](src/list_skills.py) | `py src/list_skills.py` | Quick skill enumeration |

#### Supporting Libraries
- [src/skills/\*.py](src/skills/) - All executable skills (auth, blog, commit, git-push, etc.)
- [config/\*.yaml](config/) - Configuration files for skills and workflows

---

### 2️⃣ DEVELOPER PATH: Build New Capabilities

**What**: Create agents, workflows, skills, and modules  
**Who**: You (as framework developer)  
**How**: Code editing, testing, registry management

#### Entry Points
| File | Command | Purpose |
|------|---------|---------|
| [src/registry_builder.py](src/registry_builder.py) | `py src/registry_builder.py --build --force` | Scan skills and rebuild registry |
| [src/agents/registry_agent.py](src/agents/registry_agent.py) | `py -m src.agents.registry_agent --list` | Manage skill registry (CRUD operations) |
| [src/agents/fingerprint_agent.py](src/agents/fingerprint_agent.py) | `py -m src.agents.fingerprint_agent` | Calculate skill fingerprints for trust |
| [scripts/discover_skills.py](scripts/discover_skills.py) | `py scripts/discover_skills.py` | Discover available skills |

#### Code Structure for Development
```
src/
├── orchestrator.py           # Core orchestration engine (START HERE for understanding execution)
├── agents/
│   ├── registry_agent.py     # Skill catalog management
│   └── fingerprint_agent.py  # Skill integrity verification
├── skills/
│   ├── {skill_name}.py       # Each skill module (e.g., blog_publisher.py)
│   └── models/               # Shared data models
└── mcp/                      # MCP (Model Context Protocol) integrations
    └── discovery/            # MCP server discovery

skills/                        # Skills as organized packages
├── auth-validator/
├── blog-publisher/
├── commit-message/
├── git-push-autonomous/
├── rules-engine/
└── telemetry-logger/
```

#### Development Workflows
1. **Create New Skill**:
   - Add skill module to `src/skills/` or create package in `skills/`
   - Define `execute()` function with standard signature
    - Run `py src/registry_builder.py --build --force`
    - Verify with `py src/view_registry.py`

2. **Create New Agent**:
   - Add agent to `src/agents/`
   - Define models in `*_models.py`
   - Implement `execute()` method
   - Add CLI interface in `main()`

3. **Create New Workflow**:
   - Define workflow in `workflows/{number}-{name}/`
   - Create YAML definition if needed
   - Use orchestrator to chain skills

---

### 3️⃣ SELF-HEALING PATH: Error Detection & Auto-Fix

**What**: Detect errors, analyze causes, apply or suggest fixes  
**Who**: System itself (autonomous)  
**How**: Error handlers, known solutions, telemetry analysis

#### Components
| File | Purpose |
|------|---------|
| [config/known-solutions.yaml](config/known-solutions.yaml) | Catalog of known errors and remediation steps |
| [config/safety-rules.yaml](config/safety-rules.yaml) | Safety constraints for autonomous operations |
| [src/orchestrator.py](src/orchestrator.py#L300-400) | Error handling and recovery logic (see `_execute_skill_with_recovery()`) |
| [governance/trust-model.md](governance/trust-model.md) | Trust scoring and verification model |
| [data/telemetry.jsonl](data/telemetry.jsonl) | Execution logs for pattern analysis |

#### How It Works
1. **Error Detection**: Skills return `SkillResult` with status ("SUCCESS" | "FAILED" | "SKIPPED")
2. **Solution Lookup**: Orchestrator checks `known-solutions.yaml` for matching error patterns
3. **Recovery**: Applies remediation steps or escalates to human
4. **Learning**: Logs execution metrics to `logs/execution_metrics.jsonl`

#### Entry Points (Future)
- Self-diagnostic runner (planned)
- Telemetry analyzer (planned)
- Auto-remediation agent (planned)

---

### 4️⃣ SAFETY PATH: Vetting & Policy Enforcement

**What**: Acquire, vet, catalog, and enforce policies on code/skills  
**Who**: System (with human oversight)  
**How**: Fingerprinting, trust scoring, authorization checks

#### Entry Points
| File | Command | Purpose |
|------|---------|---------|
| [src/agents/fingerprint_agent.py](src/agents/fingerprint_agent.py) | `py -m src.agents.fingerprint_agent` | Calculate cryptographic fingerprints |
| [src/skills/auth_validator.py](src/skills/auth_validator.py) | Run via orchestrator | Validate GitHub auth tokens |
| [scripts/generate_trust_scorecard.py](scripts/generate_trust_scorecard.py) | `py scripts/generate_trust_scorecard.py` | Generate trust scores for skills |
| [scripts/check_release_evidence.py](scripts/check_release_evidence.py) | `py scripts/check_release_evidence.py` | Verify release integrity |

#### Configuration
- [config/authorization.yaml](config/authorization.yaml) - Authorization rules
- [config/safety-rules.yaml](config/safety-rules.yaml) - Safety constraints
- [config/skills-registry.yaml](config/skills-registry.yaml) - Authoritative skill catalog with fingerprints

#### Safety Architecture
```
┌─────────────────────────────────────────────────────┐
│ Acquisition: Clone/download skill code              │
├─────────────────────────────────────────────────────┤
│ Fingerprinting: Calculate hash (deterministic)      │
├─────────────────────────────────────────────────────┤
│ Vetting: Test, verify behavior, assign trust score  │
├─────────────────────────────────────────────────────┤
│ Cataloging: Add to registry with metadata           │
├─────────────────────────────────────────────────────┤
│ Enforcement: Check authorization before execution   │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 By File Type & Purpose

### Executable Entry Points (Have `main()`)
*These files can be run directly from command line*

**Orchestration & Workflows**
- `src/orchestrator.py` - Main workflow engine
- `src/orchestrate_blog_publish.py` - Blog publishing workflow
- `src/publish_blog.py` - Interactive blog publisher

**Skills (Standalone)**
- `src/skills/git_push_autonomous.py` - Git operations
- `src/skills/commit_message.py` - Commit message generation
- `src/skills/blog_publisher.py` - Blog publishing
- `src/skills/token_resolver.py` - Token resolution

**Agents**
- `src/agents/registry_agent.py` - Registry management
- `src/agents/fingerprint_agent.py` - Fingerprinting (if standalone mode exists)

**CLI Tools**
- `src/blog_publisher_cli.py` - Blog publisher CLI
- `src/view_registry.py` - View registry CLI
- `src/list_skills.py` - List skills CLI
- `src/registry_builder.py` - Registry builder

**Scripts**
- `scripts/commit_and_push_updates.py` - Python git push
- `scripts/discover_skills.py` - Skill discovery
- `scripts/generate_trust_scorecard.py` - Trust score generation
- `scripts/check_release_evidence.py` - Release verification

### Libraries & Modules (Imported)
*These provide functionality but aren't run directly*

**Models**
- `src/agents/registry_models.py` - Registry data structures
- `src/agents/fingerprint_models.py` - Fingerprint data structures
- `src/skills/models/*.py` - Shared skill models

**Skills (Library Mode)**
All skills in `src/skills/` can be imported:
```python
from skills.commit_message import CommitMessageSkill
from skills.blog_publisher import BlogPublisherSkill
```

### Configuration Files
- `config/skills-registry.yaml` - Master skill registry
- `config/known-solutions.yaml` - Error remediation catalog
- `config/authorization.yaml` - Authorization rules
- `config/safety-rules.yaml` - Safety constraints
- `config/blog-config.yaml` - Blog settings
- `config/commit-strategy.yaml` - Commit message rules
- `config/telemetry-config.yaml` - Telemetry settings

### Documentation
- `README.md` - Project overview
- `RUNNING_THE_PROJECT.md` - How to run (this file's companion)
- `CODEBASE_MAP.md` - This file (navigation guide)
- `CLAUDE.md` - Claude AI context & custom commands
- `MEMORY.md` - Project memory & conventions
- `docs/` - All design docs, ADRs, research
- `workflows/` - Workflow plans and documentation

---

## 🎯 Common Tasks: Where to Start

### "I want to push code to GitHub"
```bash
# Quick way:
gpush "my commit message"

# Or Python way:
py scripts/commit_and_push_updates.py

# Or PowerShell directly:
pwsh scripts/git_push.ps1 -Message "message"
```

**What happens**: Uses `CommitMessageSkill` to generate message (if not provided), then commits and pushes

**Files involved**:
1. `scripts/git_push.ps1` - PowerShell automation
2. `scripts/commit_and_push_updates.py` - Python orchestration
3. `src/skills/commit_message.py` - AI commit message generation
4. `ProjectSecrets/PAT.txt` - GitHub token

---

### "I want to publish a blog post"
```bash
py src/publish_blog.py
# Or
py src/orchestrate_blog_publish.py
```

**What happens**: Validates content, generates metadata, publishes to blog

**Files involved**:
1. `src/publish_blog.py` OR `src/orchestrate_blog_publish.py` - Entry point
2. `src/skills/blog_publisher.py` - Blog publishing skill
3. `config/blog-config.yaml` - Blog configuration
4. `src/orchestrator.py` - Workflow execution (if using orchestrate version)

---

### "I want to see what skills exist"
```bash
# Detailed view:
py src/view_registry.py

# Quick list:
py src/list_skills.py
```

**What happens**: Reads `config/skills-registry.yaml` and displays

**Files involved**:
1. `src/view_registry.py` OR `src/list_skills.py`
2. `config/skills-registry.yaml` - The registry

---

### "I want to add a new skill"
1. Create skill file in `src/skills/my_skill.py`
2. Implement `execute()` function:
   ```python
   def execute(context: dict) -> SkillResult:
       # Your logic here
       return SkillResult(
           skill_name="my_skill",
           status="SUCCESS",
           output={"result": "data"}
       )
   ```
3. Rebuild registry:
   ```bash
   python src/registry_builder.py --build --force
   ```
4. Verify:
   ```bash
   python src/view_registry.py
   ```

**Files involved**:
1. `src/skills/my_skill.py` - Your new skill
2. `src/registry_builder.py` - Registry builder
3. `config/skills-registry.yaml` - Updated registry

---

### "I want to run a workflow"
```bash
python src/orchestrator.py
```

**Or programmatically**:
```python
from src.orchestrator import Orchestrator

orch = Orchestrator()
result = orch.run_workflow([
    ("commit_message", {"files": ["file1.py", "file2.py"]}),
    ("git_push", {"message": "generated message"})
])
```

**Files involved**:
1. `src/orchestrator.py` - Workflow engine
2. `src/skills/*.py` - Skills being chained
3. `config/skills-registry.yaml` - Skill metadata

---

### "I want to understand the architecture"
**Read in this order**:
1. `README.md` - High-level vision
2. `RUNNING_THE_PROJECT.md` - How to run
3. `CODEBASE_MAP.md` - This file (navigation)
4. `src/orchestrator.py` - Core execution logic
5. `workflows/PHASE_ARCHITECTURE_V1.md` - Architecture design
6. Skills in `src/skills/` - Individual capabilities

---

## 🔗 File Relationships & Dependencies

### Core Dependency Chain
```
User/CLI
    ↓
Entry Point Scripts (src/*.py, scripts/*.py)
    ↓
Orchestrator (src/orchestrator.py)
    ↓
Skills Registry (config/skills-registry.yaml)
    ↓
Skills Modules (src/skills/*.py)
    ↓
Models & Utilities (src/skills/models/*.py)
    ↓
External Services (GitHub, Blog API, etc.)
```

### What Imports What
- **Orchestrator** imports: Skills dynamically via `importlib`
- **Entry point scripts** import: Orchestrator, specific skills, agents
- **Skills** import: Models, utilities, external libraries
- **Agents** import: Models, registry/fingerprint utilities

### What Calls What
```
CLI Command
    ↓
Entry Point (e.g., orchestrate_blog_publish.py)
    ↓
Orchestrator.run_workflow([skill_list])
    ↓
Orchestrator._execute_skill(skill_name, config)
    ↓
skill_module.execute(context)
    ↓
Returns SkillResult
```

---

## 📂 Directory Purpose Guide

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `src/` | Core application code | orchestrator.py, skills/, agents/ |
| `scripts/` | Automation scripts | commit_and_push_updates.py, git_push.ps1 |
| `config/` | Configuration files | skills-registry.yaml, *.yaml configs |
| `skills/` | Skills as packages | auth-validator/, blog-publisher/, etc. |
| `data/` | Runtime data | telemetry.jsonl, memory/, mcp_cache/ |
| `docs/` | Documentation | ADRs, design docs, research |
| `workflows/` | Workflow definitions | Numbered workflow directories |
| `tests/` | Test files | test_*.py files |
| `logs/` | Log files | execution_metrics.jsonl, push.log |
| `governance/` | Governance docs | trust-model.md, policies |
| `infra/` | Infrastructure | PowerShell profiles, configs |
| `ProjectSecrets/` | Secret files (gitignored) | PAT.txt |
| `PromptTracking/` | Session logs | Session Log [DATE].md |

---

## 🚀 Quick Reference Matrix

| I want to... | Run this... | Which calls... |
|--------------|-------------|----------------|
| Push to GitHub | `gpush` | git_push.ps1 → commit_message skill |
| Publish blog | `py src/publish_blog.py` | blog_publisher skill |
| View skills | `py src/view_registry.py` | skills-registry.yaml |
| Add new skill | Edit `src/skills/new.py` | Then run registry_builder.py |
| Run workflow | `py src/orchestrator.py` | Skills from registry |
| Check trust | `py scripts/generate_trust_scorecard.py` | fingerprint_agent |
| Debug flows | Check `data/telemetry.jsonl` | Execution logs |

---

## 🧭 Navigation Tips

1. **Start with entry points** - Files with `main()` are your starting points
2. **Follow the orchestrator** - `src/orchestrator.py` is the heart of execution
3. **Check the registry** - `config/skills-registry.yaml` shows all available skills
4. **Read skill code** - Each skill in `src/skills/` is self-contained
5. **Use grep/search** - Search for function names to find usages
6. **Check workflows/** - See example workflow definitions
7. **Read RUNNING_THE_PROJECT.md** - Companion to this file with detailed usage

---

## 📝 Legend

- ✈️ User-facing functionality
- 🔧 Developer tools
- 🛡️ Safety & trust features
- 🔄 Self-healing components
- 📦 Libraries/modules
- ⚙️ Configuration
- 📖 Documentation

---

*This map is living documentation. Update it as the codebase evolves.*
