Created: 2026-02-06
Status: Phase 1a COMPLETE, Phase 1b PLANNED
Plan version: 1.1

Strategic Goals

Self-organizing, self-documenting, self-orchestrating agents — Build an autonomous skill framework following SOLID principles, where an orchestrator composes specialist skills to perform work without human intervention.
Ever-expanding skill library — Skills, MCPs, and tools are modular units the orchestrator can choose from for any workflow. New skills slot in without modifying existing code.
Delegate probabilistic tasks to LLM cost-efficiently — The orchestrator decides when to call an LLM vs. when deterministic code suffices. LLM calls are reserved for ambiguous judgment; everything else is rules-based.
Maximize deterministic code — Safety rules, auth checks, file validation, and telemetry are pure code. Only commit-message generation and future code-review touch LLM inference.


Approach: Rules Engine First (Proof of Concept)
Build the rules-engine specialist + its dependencies as a working proof of concept, then expand to remaining skills.

Current Inventory
SkillRoleDocsCodegit-push-autonomousOrchestrator5 filesNone yetauth-validatorSpecialist2 filesNone yetrules-engineSpecialist2 filesBuild firsttelemetry-loggerSpecialist2 filesNone yet
Config ready: config/safety-rules.yaml, config/telemetry-config.yaml
Existing PowerShell: scripts/git_push.ps1 (preserved, not replaced)

Phase 1a: Rules Engine Proof of Concept
What We Build Now
src/
└── skills/
    ├── __init__.py
    ├── models.py          # Shared dataclasses (RulesResult, BlockedFile)
    ├── config_loader.py   # Load safety-rules.yaml, resolve paths from repo root
    └── rules_engine.py    # File safety validation against config rules

tests/
├── __init__.py
├── conftest.py            # Shared fixtures (temp dirs, sample configs)
└── test_rules_engine.py   # Unit tests using 6 built-in test cases from config

pyproject.toml             # Minimal: name, version, dependencies=[pyyaml, pytest]
Step 1: Models (src/skills/models.py)
Dataclasses defining the rules-engine contract from skills/rules-engine/CLAUDE.md:
python@dataclass
class BlockedFile:
    path: str
    reason: str        # "explicit_blocklist" | "pattern_match" | "size_limit"
    matched_rule: str  # The specific rule that triggered

@dataclass
class RulesResult:
    decision: str           # "APPROVE" | "BLOCK_ALL" | "BLOCK_SOME"
    approved_files: list    # Files that passed all checks
    blocked_files: list     # List of BlockedFile
    confidence: float       # 0.0-1.0
    warnings: list          # Size warnings, etc.
Also define stubs for AuthResult, TelemetryEntry, StepResult so they exist for later phases.
Step 2: Config Loader (src/skills/config_loader.py)

Auto-detect repo root via git rev-parse --show-toplevel
Load config/safety-rules.yaml using PyYAML
Parse into typed structure: blocked_files, blocked_patterns, max_file_size_mb, allowed_paths
Missing config = conservative defaults (block everything)
Expose: load_safety_rules(config_dir=None) -> SafetyRulesConfig

Key file: config/safety-rules.yaml (authoritative data source)
Step 3: Rules Engine (src/skills/rules_engine.py)
Single public function:
pythondef evaluate(files: list[str], repo_root: str, config: SafetyRulesConfig = None) -> RulesResult
Phase 1 logic (from skills/rules-engine/SKILL.md):

Allowed-path check first - If file matches allowed paths (src/, docs/, tests/, config/, etc.), skip to size check
Explicit blocklist - Match against blocked_files list (.env, .secrets, credentials.json, etc.)
Regex pattern match - Match against blocked_patterns (^\., ^credentials/.*, .*\.key$, etc.)
File size check - Files >50MB get a warning (not a block)
Aggregate decision:

Any blocked → BLOCK_ALL (all-or-nothing, per examples.md Example 9)
All pass → APPROVE
Size warnings → APPROVE with warnings



Confidence: 0.99 for clean APPROVE, 1.0 for BLOCK (certain).
Technical note: Pattern ^\. blocks hidden files, but .gitignore is in allowed paths. Check allowed first.
Step 4: Tests (tests/test_rules_engine.py)
Use the 6 test cases already defined in config/safety-rules.yaml:

Normal source file → APPROVE
.env file → BLOCK (explicit blocklist)
credentials/token.json → BLOCK (pattern match)
Large file (>50MB) → APPROVE with warning
node_modules/package.json → BLOCK (pattern match)
Mixed safe + unsafe files → BLOCK_ALL

Additional tests:

Empty file list → APPROVE
.gitignore → APPROVE (allowed path takes precedence)
Missing config → conservative default (block all)
Config with no blocked patterns → APPROVE all

Step 5: Packaging (pyproject.toml)
toml[project]
name = "roadtrip-skills"
version = "0.1.0"
dependencies = ["pyyaml>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
Verification (Rules Engine POC)

Run tests: pytest tests/test_rules_engine.py -v
Manual test: Load actual config/safety-rules.yaml, evaluate a list of files from the repo
Edge case: Create temp .env file path, verify it blocks with reason "explicit_blocklist"
Config missing: Call with no config, verify conservative blocking


Phase 1b: Remaining Skills (After POC Validated)
Once the rules-engine POC works, expand in this order:
#ModuleWhat It Adds1auth_validator.pyGit credential/permission checks2telemetry_logger.pyJSONL decision logging3commit_message.pyPort from PowerShell GenerateCommitMessage4git_push_autonomous.pyOrchestrator: 7-step workflow + CLI5Integration testsFull end-to-end with temp git repos6Shell integrationgpush-safe alias in PowerShell profile
Each module follows the same pattern: models → config → implementation → tests.

Critical Files Reference
FilePurposeconfig/safety-rules.yamlBlocklist data, patterns, size limits, test casesskills/rules-engine/SKILL.mdRules engine interface specskills/rules-engine/CLAUDE.mdDecision logic and confidence scoringskills/git-push-autonomous/safety-rules.mdDetailed exclusion rules documentationskills/git-push-autonomous/CLAUDE.mdSpecialist contracts (JSON schemas)scripts/git_push.ps1Reference implementation (lines 93-193 for commit message port)

Technical Considerations

Allowed vs blocked precedence: Check allowed paths first, then blocked. Prevents .gitignore being caught by ^\. pattern.
Cross-platform subprocess: subprocess.run(capture_output=True, text=True, timeout=N) for git commands.
File size for deleted files: Skip size check for files not on disk (git status D).
Windows path handling: Use pathlib.PurePosixPath for git paths, pathlib.Path for OS paths.
Config location: Resolve relative to repo root (auto-detected), not CWD.


Execution Record
Phase 1a: Rules Engine POC — COMPLETE (2026-02-06)
Files created:
FileLinesPurposesrc/skills/__init__.py0Package initsrc/skills/models.py~75Dataclasses: BlockedFile, RulesResult, SafetyRulesConfig + stubs for AuthResult, TelemetryEntry, StepResultsrc/skills/config_loader.py~65Loads config/safety-rules.yaml via PyYAML, auto-detects repo root, conservative defaults when config missingsrc/skills/rules_engine.py~175Core evaluate(): allowed paths → explicit blocklist → regex patterns → size check → aggregate decisiontests/__init__.py0Package inittests/conftest.py~55Shared pytest fixtures: sample_config, conservative_config, permissive_config, tmp_repotests/test_rules_engine.py~23025 tests across 3 test classespyproject.toml~12Project packaging: PyYAML + pytest
Test results: 25/25 passed (0.17s)
Key design decisions locked in:

Allowed paths checked BEFORE blocked patterns (prevents .gitignore false positive)
BLOCK_ALL is all-or-nothing (per examples.md Example 9)
Missing config = conservative defaults (pattern .* blocks everything)
Size warnings don't block, only inform
Confidence: 0.99 (approve), 0.95 (approve with warnings), 1.0 (block)

Phase 1b: Remaining Skills — NEXT
#ModuleStatusDependencies1auth_validator.pyNot startedmodels2telemetry_logger.pyNot startedmodels, config_loader3commit_message.pyNot startedNone (port from PowerShell)4git_push_autonomous.pyNot startedAll above5Integration testsNot startedAll above6Shell integration (gpush-safe)Not startedOrchestrator

Process Documentation
This plan is maintained as a living artifact:

Location: workflows/plan.md (repo) + Claude plan cache
Purpose: Evaluation, documentation, learning, revision
Updates: Appended after each implementation phase with execution record
Workflow pattern: Plan → Validate → Implement → Test → Record → Next phase