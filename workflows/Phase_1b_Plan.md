# Phase 1b: Skill Framework Expansion & Orchestrator Design

**Version**: 1.0  
**Status**: Planning → Execution  
**Target Completion**: TBD  
**Primary Product**: Process Improvement Documentation  
**Secondary Product**: Reusable Skill Templates (Python + C# Portability)

---

## Executive Summary

Phase 1b transforms RoadTrip from a proof-of-concept (rules-engine) into an **enterprise-grade skill framework** by:

1. **Building three specialist skills** (auth-validator, telemetry-logger, commit-message)
2. **Designing skill_orchestrator** with intelligent decision-making (cost optimization, multi-language support)
3. **Implementing structured error handling** (Microsoft pattern: 5-level hierarchy)
4. **Establishing process logging/analysis framework** (foundation for continuous improvement)
5. **Ensuring C# portability** (skills callable via MCP from .NET)

**Strategic Insight**: This phase proves the reusable skill methodology can scale beyond one workflow and across languages.

---

## Part 1: Design Considerations for skill_orchestrator

### 1.1 Orchestrator's Role (Decision Framework)

The orchestrator is **not** the business logic. It is the **decision engine** that routes work to specialists and decides which approach to use.

```
┌─────────────────────────────────────────────────┐
│           User Input                            │
│    (git-push-autonomous task request)           │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────▼─────────────┐
    │  skill_orchestrator       │
    │  (decision engine)        │
    │                           │
    │  1. Load skill context    │
    │  2. Assess requirements   │
    │  3. Choose approach       │
    │  4. Chain specialists     │
    │  5. Handle errors         │
    │  6. Return + log result   │
    └────────────┬──────────────┘
                 │
    ┌────────────┴─────────────────────────────┐
    │                                           │
    │      Call Specialists in Sequence        │
    │                                           │
    ├─────────────┬──────────────┬──────────────┤
    ▼             ▼              ▼              ▼
auth_validator  rules_engine  commit_msg   telemetry_logger
(check perms)   (validate)   (generate)   (record decision)
    │             │              │              │
    └─────────────┴──────────────┴──────────────┘
                 │
                 │ (Decision Result)
    ┌────────────▼─────────────────┐
    │  Execution Phase              │
    │  (if approved)                │
    ├───────────────────────────────┤
    │  git add → commit → push      │
    │  (with structured logging)    │
    └───────────────────────────────┘
```

### 1.2 Orchestrator's Responsibilities (SOLID: Single Responsibility)

**The orchestrator decides:**
- ✅ Which skills to run and in what order
- ✅ Whether to use deterministic or AI-enhanced approach
- ✅ How to handle failures at each stage
- ✅ What to log and audit

**The orchestrator does NOT:**
- ❌ Validate files (rules-engine does)
- ❌ Check permissions (auth-validator does)
- ❌ Generate commit messages (commit-message does)
- ❌ Log to files (telemetry-logger does)

---

### 1.3 Three Critical Decision Points

#### **Decision 1: Commit Message Generation Approach**

**Context**: Generating thoughtful commit messages is costly (LLM calls). But generic messages hurt readability.

**Solution: Tier 1 → Tier 2 → Tier 3 Fallback (Cost-Optimized)**

```python
def decide_commit_message_approach(changed_files: list[str], 
                                   staged_diffs: str,
                                   use_ai: bool = True) -> CommitMessageApproach:
    """
    Orchestrator decides which approach to use based on file patterns.
    
    Tier 1 (Deterministic, Cost: $0):
    - File-based heuristics (extract category from path)
    - Diff heuristics (count +/-, parse meaningful hunks)  
    - Pattern matching (test files, doc files, etc.)
    - Confidence score based on signal clarity
    - Returns: "Auto-generated (99% confidence)" for clear signals
    
    Tier 2 (Hybrid LLM, Cost: $0.001-0.01):
    - Only invoked when Tier 1 confidence < 0.85
    - LLM prompt: "These diffs are: [unclear]. Generate 1-2 sentence summary."
    - Returns: "AI-enhanced (87% confidence)" if LLM confidence > threshold
    
    Tier 3 (User Override, Cost: $0):
    - If `-Message "Custom message"` provided → use it directly
    - Bypasses Tier 1 & Tier 2
    
    Default Behavior:
    - Tier 1 runs always (deterministic)
    - Tier 2 runs only if: (a) Tier 1 confidence low AND (b) use_ai=True
    - Fallback to Tier 1 if Tier 2 fails or is disabled
    
    Benefit: 
    - ~90% of commits use Tier 1 (cheap/fast)
    - ~10% of complex commits use Tier 2 (better readability, low cost)
    - User can override anytime with -Message
    """
    
    # Tier 1: Deterministic approach
    tier1_result = deterministic_commit_message(changed_files, staged_diffs)
    tier1_confidence = tier1_result.confidence
    
    # Decision: Should we call LLM?
    if tier1_confidence >= 0.85:
        return tier1_result  # Tier 1 is good enough
    
    if not use_ai:
        return tier1_result  # AI disabled, use Tier 1 fallback
    
    # Tier 2: Invoke LLM for ambiguous cases
    try:
        tier2_result = ai_enhanced_commit_message(changed_files, staged_diffs)
        if tier2_result.confidence >= 0.75:
            return tier2_result  # LLM worked well
    except Exception as e:
        log_warning(f"Tier 2 failed: {e}, falling back to Tier 1")
    
    # Fallback: Tier 1 is reliable
    return tier1_result
```

**Orchestrator-Level Control**:
```yaml
# In config or SKILL.md
commit_message:
  strategy: "hybrid"  # or "deterministic" or "ai"
  tier1_confidence_threshold: 0.85
  tier2_confidence_threshold: 0.75
  tier2_enabled: true
  max_tier2_cost: 0.01  # Stop using Tier 2 if budget exceeded in session
```

---

#### **Decision 2: Multi-User / Enterprise Auth Context**

**Context**: Phase 1a assumes local development. Phase 1b must support:
- Multiple users (different identities)
- CI/CD pipelines (service principals)
- Role-based access (Developer, Architect, Platform-Eng)
- Conditional access (MFA, device compliance)

**Solution: 4-Layer Authorization Check**

```python
def decide_authorization(skill_name: str, 
                        user_context: IdentityContext,
                        resource: Optional[str] = None) -> AuthzDecision:
    """
    Orchestrator checks authorization at four layers before skill execution.
    
    Layer 1: Skill Availability
    - Question: Can user SEE this skill?
    - Check: SKILL.md:authorization.allowed_groups contains user's groups
    - Fail: AuthzDecision.SKILL_NOT_AVAILABLE → hide from user
    
    Layer 2: Skill Execution
    - Question: Can user RUN this skill?
    - Check: User has minimum_role + no conditional_access violations
    - Fail: AuthzDecision.SKILL_FORBIDDEN → show skill but block execution
    
    Layer 3: Tools Within Skill
    - Question: Which tools can this skill use?
    - Check: Per-tool permissions (file access, git operations)
    - Fail: AuthzDecision.TOOL_FORBIDDEN → run skill, but gate tool calls
    
    Layer 4: Resource Access
    - Question: Can skill access target resource (git repo, file)?
    - Check: Git credentials valid, file paths allowed
    - Fail: AuthzDecision.RESOURCE_FORBIDDEN → meaningful error message
    
    Orchestrator Logic:
    - Check Layer 1 before showing skill to user
    - Check Layer 2 before executing skill
    - Check Layer 3 before calling each tool
    - Check Layer 4 at execution time
    - Short-circuit on first failure (fast path)
    """
    
    # Layer 1: Skill Availability
    skill_def = load_skill(skill_name)
    if not skill_def.has_group(user_context.groups):
        return AuthzDecision.SKILL_NOT_AVAILABLE
    
    # Layer 2: Skill Execution
    if not user_context.has_role(skill_def.authorization.minimum_role):
        return AuthzDecision.SKILL_FORBIDDEN
    
    if skill_def.authorization.requires_mfa and not user_context.mfa_validated:
        return AuthzDecision.SKILL_FORBIDDEN_MFA_REQUIRED
    
    # Layer 3: Tools within skill
    # (auth-validator skill checks this and returns list of allowed tools)
    
    # Layer 4: Resource access
    if resource and not can_access_resource(user_context, resource):
        return AuthzDecision.RESOURCE_FORBIDDEN
    
    return AuthzDecision.APPROVED
```

**SKILL.md Enhancement**:
```yaml
---
name: git-push-autonomous
version: 1.0.0

authorization:
  minimum_role: "Developer"  # Layer 2 check
  allowed_groups:
    - "engineering-team"
    - "platform-engineering"
  conditional_access:
    require_mfa: true  # Layer 2 check
    allowed_devices: "compliant"
    max_file_size_mb: 100  # Layer 3 check
    allowed_extensions:
      - ".py"
      - ".md"
      - ".yaml"
      - ".json"
      - ".txt"

# New: Tool-level permissions (Layer 3)
tools:
  git:
    allowed_commands:
      - "add"
      - "commit"
      - "push"
    allowed_branches:
      - "main"
      - "develop"
      - "feature/*"
  filesystem:
    allowed_paths:
      - "src/"
      - "docs/"
      - "tests/"
    blocked_paths:
      - "config/secrets/"
      - ".github/"
---
```

---

#### **Decision 3: Error Handling Strategy (Graceful Degradation)**

**Context**: Autonomous agents must handle failures without blocking.

**Solution: Structured Error Hierarchy (Microsoft Pattern)**

```python
from enum import IntEnum
from dataclasses import dataclass

class ErrorLevel(IntEnum):
    """Error hierarchy: guides orchestrator recovery behavior."""
    
    SECURITY_VIOLATION = 1     # Never retry, hard block
    AUTH_FAILURE = 2            # Block, suggest fix
    RULES_VIOLATION = 3         # Block, list violations
    NETWORK_FAILURE = 4         # Retry with backoff
    TELEMETRY_FAILURE = 5       # Warn, continue

@dataclass
class StructuredError:
    """Every failure provides context for recovery."""
    level: ErrorLevel
    code: str                    # e.g., "BLOCKED_FILE", "AUTH_MFA_REQUIRED"
    message: str                 # What failed
    reason: str                  # Why it failed
    details: dict                # What to fix
    recovery_action: str         # What operator should do
    loggable: bool               # Can this be logged? (not credentials)
    
    def __str__(self):
        return f"""
Error [{self.code}]
What happened: {self.message}
Why: {self.reason}
What to do: {self.recovery_action}
Details: {self.details}
"""

# Example: File blocked by rules-engine
error = StructuredError(
    level=ErrorLevel.RULES_VIOLATION,
    code="SECURITY_FILE_BLOCKED",
    message="Cannot push .env file",
    reason="File matches pattern: .env (credentials)",
    details={
        "file": ".env",
        "matched_rule": "blocked_patterns[2]",
        "rule_description": "Environment files containing secrets"
    },
    recovery_action="Remove .env and try again",
    loggable=True
)

# Example: MFA required
error = StructuredError(
    level=ErrorLevel.AUTH_FAILURE,
    code="MFA_REQUIRED",
    message="Multi-factor authentication required",
    reason="Skill requires MFA; your session lacks MFA validation",
    details={
        "skill": "git-push-autonomous",
        "required_mfa": True,
        "your_mfa_status": "not_validated"
    },
    recovery_action="Authenticate with MFA and try again",
    loggable=True
)
```

**Orchestrator Error Handling Logic**:

```python
def handle_skill_result(skill_name: str, 
                       result: SkillResult) -> ContinueOrStop:
    """
    Orchestrator decides: continue workflow or stop?
    """
    if result.success:
        return ContinueOrStop.CONTINUE
    
    error = result.error
    
    if error.level == ErrorLevel.SECURITY_VIOLATION:
        # Never retry, stop immediately
        log_error(error, severity="CRITICAL")
        return ContinueOrStop.STOP_HARD
    
    if error.level == ErrorLevel.AUTH_FAILURE:
        # Block, show recovery action
        log_error(error, severity="HIGH")
        print(error)  # User sees recovery action
        return ContinueOrStop.STOP_HARD
    
    if error.level == ErrorLevel.RULES_VIOLATION:
        # Block, show violations
        log_error(error, severity="HIGH")
        print(error)
        return ContinueOrStop.STOP_HARD
    
    if error.level == ErrorLevel.NETWORK_FAILURE:
        # Retry with backoff
        log_warning(error)
        retries = 3
        backoff_ms = 500
        for attempt in range(retries):
            try:
                result = retry_skill(skill_name, backoff_ms)
                if result.success:
                    return ContinueOrStop.CONTINUE
            except Exception:
                backoff_ms *= 2
        
        # All retries exhausted
        log_error(error, severity="HIGH", context="after 3 retries")
        return ContinueOrStop.STOP_HARD
    
    if error.level == ErrorLevel.TELEMETRY_FAILURE:
        # Non-blocking, warn and continue
        log_warning(error, severity="LOW")
        print(f"Non-critical issue: {error.message}. Continuing...")
        return ContinueOrStop.CONTINUE
    
    return ContinueOrStop.STOP_HARD  # Unknown error = conservative
```

---

### 1.4 Orchestrator Architecture (Pseudocode)

```python
class SkillOrchestrator:
    """
    Main orchestration engine for skill composition.
    
    Responsibilities:
    - Load user context (identity, permissions, environment)
    - Load skill definitions from skills/ folder
    - Execute skills in sequence with decision logic
    - Handle errors gracefully
    - Produce structured audit trail
    """
    
    def __init__(self, config_dir: Path, skills_dir: Path):
        self.config = load_config(config_dir)
        self.skills = load_skill_definitions(skills_dir)
        self.auth_service = AuthService(self.config)
        self.logger = TelemetryLogger()
    
    async def execute_workflow(self, 
                              workflow_name: str,
                              user_input: str,
                              identity: IdentityContext) -> WorkflowResult:
        """
        Main entry point for skill orchestration.
        """
        
        # Step 1: Load workflow definition
        workflow = load_workflow(workflow_name)  # e.g., "git-push-autonomous"
        
        # Step 2: Check overall authorization (Layer 1)
        authz = self.decide_authorization(workflow.primary_skill, identity)
        if authz != AuthzDecision.APPROVED:
            return WorkflowResult(
                success=False,
                error=StructuredError(
                    level=ErrorLevel.AUTH_FAILURE,
                    code=f"WORKFLOW_FORBIDDEN_{authz}",
                    message=f"You cannot run {workflow_name}",
                    reason="See details below",
                    details={"authz_decision": authz},
                    recovery_action="Contact admin for access"
                )
            )
        
        # Step 3: Prepare execution context
        context = ExecutionContext(
            workflow=workflow,
            identity=identity,
            config=self.config,
            decisions=[]  # Trail of all decisions made
        )
        
        # Step 4: Execute skill chain
        for skill_spec in workflow.skill_chain:
            skill_result = await self.execute_skill(
                skill_spec.name,
                user_input,
                context
            )
            
            # Log decision
            context.decisions.append({
                "skill": skill_spec.name,
                "result": skill_result.success,
                "error": skill_result.error if not skill_result.success else None,
                "timestamp": datetime.now(),
                "duration_ms": skill_result.duration_ms,
            })
            
            # Handle error
            action = self.handle_skill_result(skill_spec.name, skill_result)
            
            if action == ContinueOrStop.STOP_HARD:
                return WorkflowResult(
                    success=False,
                    error=skill_result.error,
                    decisions_made=context.decisions
                )
            
            # Continue to next skill
        
        # Step 5: All skills passed, proceed to execution
        return WorkflowResult(
            success=True,
            decisions_made=context.decisions,
            execution_result=await self.execute_approved_workflow(context)
        )
    
    async def execute_skill(self,
                           skill_name: str,
                           input_data: str,
                           context: ExecutionContext) -> SkillResult:
        """Execute a single skill with error handling."""
        
        try:
            skill = self.skills[skill_name]
            
            # Load the appropriate implementation
            if skill_name == "auth-validator":
                result = await auth_validator.evaluate(
                    user_context=context.identity,
                    config=context.config
                )
            elif skill_name == "rules-engine":
                result = await rules_engine.evaluate(
                    files=parse_files_from_input(input_data),
                    config=context.config
                )
            elif skill_name == "commit-message":
                approach = self.decide_commit_message_approach(input_data)
                result = await commit_message.generate(
                    changed_files=input_data,
                    approach=approach
                )
            elif skill_name == "telemetry-logger":
                result = await telemetry_logger.log(
                    decisions=context.decisions,
                    identity=context.identity
                )
            
            return result
        
        except Exception as e:
            # Unexpected error = security-conservative
            return SkillResult(
                success=False,
                error=StructuredError(
                    level=ErrorLevel.TELEMETRY_FAILURE,  
                    code="SKILL_CRASHED",
                    message=f"Skill {skill_name} failed unexpectedly",
                    reason=str(e),
                    details={"exception": type(e).__name__},
                    recovery_action="Contact admin with error code",
                    loggable=False  # Don't log exception details
                )
            )
```

---

## Part 2: Phase 1b Specialist Skills

### 2.1 auth-validator Skill (4-Layer Authorization)

**Responsibility**: Evaluate user authorization at runtime

**Type**: Evaluation skill (pure function, deterministic)

**Inputs**:
- User identity (from session context)
- Skill to authorize
- Resource being accessed (optional)

**Outputs**:
```python
@dataclass
class AuthValidationResult:
    decision: str                    # "APPROVED", "FORBIDDEN_LAYER_N", etc.
    layers_passed: list[int]         # [1, 2] means layers 1-2 passed
    reason: str                      # User-facing explanation
    recovery_action: Optional[str]   # What to do if blocked
    confidence: float                # 0.95-1.0 (auth is binary)
```

**Spec File** (`skills/auth-validator/SKILL.md`):
- Will be created with 4-layer decision logic documented
- References Entra integration pattern from DotNetSkills

**Test Matrix**:
- Layer 1: Group membership check
- Layer 2: Role + MFA check
- Layer 3: Tool permission check
- Layer 4: Git credential check
- Plus: Happy path, all layers passing

---

### 2.2 telemetry-logger Skill (DEFERRED TO PHASE 1C)

**Status**: ⏸️ **Deferred until Aspire infrastructure available**

**Rationale**: Aspire provides better telemetry/observability framework. Building telemetry-logger now would need rework in Phase 1c when Aspire is introduced. Better to wait and design it properly.

**Phase 1b Alternative**: Orchestrator logs decisions to structured JSON (stdout/file) for immediate analysis. Not as robust as dedicated skill, but sufficient for Phase 1b process documentation.

**Scheduled for Phase 1c**: Full telemetry-logger skill with:
- JSONL format for append-only logs
- Integration with Aspire diagnostics
- Immutable once written (append only, no modification)
- Includes: timestamp, user, decision, confidence, reason
- Full queryability for pattern analysis, compliance audits, learning loops

---

### 2.3 commit-message Skill (Tier 1→2→3 Approach)

**Responsibility**: Generate semantic commit messages cost-effectively

**Type**: Decision skill (pure for Tier 1, probabilistic for Tier 2)

**Inputs**:
- Changed files list
- Staged diffs
- Strategy (deterministic/hybrid/ai)

**Outputs**:
```python
@dataclass
class CommitMessageResult:
    message: str
    approach_used: str               # "tier1", "tier2", "tier3"
    confidence: float                # 0.75-1.0
    cost_estimate: float             # $ spent on LLM calls
    reasoning: str                   # Why this message was chosen
```

**Spec File** (`skills/commit-message/SKILL.md`):
- Documents Tier 1 patterns (file extensions, directory structure)
- Documents Tier 2 prompts (what LLM is asked)
- Documents Tier 3 override (-Message parameter)

**Test Matrix**:
- Single file add → Tier 1
- Multi-category changes → Tier 2
- User-provided message → Tier 3
- Cost tracking

---

### 2.4 skill-orchestrator Skill (Composition Engine)

**Responsibility**: Coordinate specialist skills into workflows

**Type**: Orchestration skill (meta-skill that calls other skills)

**This is the centerpiece** that implements all three decision points from Section 1.3

**Spec File** (`skills/skill-orchestrator/SKILL.md`):
- Documents workflow YAML format
- Documents decision trees for each integration point
- References error hierarchy

---

## Part 3: Process Improvement & Analysis Framework

### 3.1 Logging Strategy (Living Audit Trail)

Every decision is logged in **structured, queryable format**:

```json
{
  "timestamp": "2026-02-07T14:32:45.123Z",
  "session_id": "sess_abc123def456",
  "user": "bizcad",
  "workflow": "git-push-autonomous",
  "phase": "initialization",
  
  "decisions": [
    {
      "decision_name": "commit_message_approach",
      "decision_value": "tier1",
      "confidence": 0.99,
      "factors_considered": {
        "file_count": 1,
        "categories": ["src"],
        "complexity_score": 0.2
      },
      "reasoning": "Single-category, low complexity → deterministic message"
    },
    {
      "decision_name": "authorization_layer_1",
      "decision_value": "approved",
      "confidence": 1.0,
      "factors_considered": {
        "user_groups": ["engineering-team"],
        "skill_required_groups": ["engineering-team", "platform-engineering"]
      },
      "reasoning": "User in allowed group"
    }
  ],
  
  "errors": [],
  "duration_ms": 245,
  "cost_estimate_usd": 0.0
}
```

### 3.2 Analysis Queries (Process Improvement)

Examples of questions we'll ask of the logs:

1. **Adoption**: "How often is Tier 2 (LLM) used? What triggers it?"
2. **Cost**: "What's average cost per workflow run? Trends over time?"
3. **Failures**: "What error patterns repeat? What causes auth failures?"
4. **User experience**: "How long do workflows take? Bottlenecks?"
5. **Policy effectiveness**: "Are our safety rules catching bad files? False positives?"
6. **Process improvements**: "If we changed rule X, how many runs would differ?"

### 3.3 Analysis Deliverables (Phase 1b Documentation)

During Phase 1b execution, we will produce:

- **Log Analysis Notebook**: Jupyter notebook showing patterns
- **Decision Tree Visualization**: Graph of auth/commit message decisions
- **Cost Report**: LLM usage and $ analysis
- **Error Taxonomy**: Categorized failures with recovery paths
- **Process Improvement Recommendations**: Based on logs

---

## Part 4: C# Portability (Skills as RPCs)

### 4.1 Design Principle

**Skills are language-agnostic** via MCP (Model Context Protocol).

A Python skill running in RoadTrip can be called from C# DotNetSkills:

```csharp
// In C# DotNetSkills
var mcpClient = new McpClient("python-roadtrip-server");

var result = await mcpClient.CallToolAsync("rules-engine", new {
    files = changedFiles,
    config_dir = "/path/to/config"
});

// Returns: JSON with decision, blocked_files, confidence, etc.
```

### 4.2 Portability Checklist for Each Skill

Every skill must:

- ✅ **Export JSON schema** for inputs/outputs
- ✅ **Have CLI interface** (can run standalone)
- ✅ **Have MCP interface** (can be called via RPC)
- ✅ **Document assumptions** (Python 3.10+, dependencies)
- ✅ **Be rewritable in C#** (no Python-specific tricks)

Example: `rules-engine` callable as:
```bash
# CLI (Python)
python -m src.skills.rules_engine evaluate \
  --files src/app.py config/secrets.yaml \
  --config config/

# MCP (callable from any language)
POST /mcp-server/tools/rules-engine
{
  "files": ["src/app.py", "config/secrets.yaml"],
  "config_dir": "/path/to/config"
}
```

---

## Part 5: Execution Plan & Checkpoints

### 5.1 Skill Development Order (Phase 1b)

1. **auth-validator** (simplest: just checks identity context)
   - Fast iteration, low complexity
   - Enables testing of orchestrator's authz layer

2. **commit-message** (moderately complex: Tier 1→2→3 logic)
   - Demonstrates cost optimization
   - Can be tuned based on Phase 1b execution logs

3. **skill-orchestrator** (most complex: assembles others)
   - Built last, uses all two specialists
   - End-to-end integration testing
   - Orchestrator logs decisions to JSON (temporary, until Aspire)

**Deferred to Phase 1c**:
- **telemetry-logger** (full skill with Aspire integration)
  - Waits for Aspire infrastructure
  - Will properly handle observability/telemetry
  - Better design once Aspire is available

### 5.2 Quality Gates Per Skill (Phase 1b)

Each of the 3 Phase 1b skills must pass:

- ✅ **Spec Review**: SKILL.md + CLAUDE.md match reality
- ✅ **Code Review**: SOLID principles, type hints, docstrings
- ✅ **Test Coverage**: 25+ tests (minimum, per Phase 1a model)
- ✅ **C# Portability Audit**: Can this be rewritten cleanly?
- ✅ **Integration Test**: Works via MCP interface
- ✅ **Documentation**: Examples showing Tier 1/2/3, error cases

**Note**: Processing/telemetry logging (deciding between approaches, capturing decisions) is handled by orchestrator directly in Phase 1b, not by a dedicated skill. Deferred to Phase 1c when Aspire infrastructure ready.

### 5.3 Checkpoints (Go/No-Go)

| Milestone | Definition | Owner |
|-----------|-----------|-------|
| **auth-validator MVP** | Passes 15 tests, SKILL.md approved | Code + Review |
| **commit-message MVP** | Tier 1 + Tier 2 working, cost tracking on | Code + Review |
| **skill-orchestrator Alpha** | Chains 2 skills, happy path works, JSON logging working | Code + Review |
| **Phase 1b Complete** | All 3 skills + orchestrator + execution log analysis | Review + Analysis |
| **Phase 1c Prep** | Plan telemetry-logger with Aspire framework | Planning |

---

## Part 6: Process Documentation (Primary Deliverable)

### 6.1 What We're Capturing

During Phase 1b, we'll log and analyze:

1. **Design decisions**: Why we chose Tier 1→2→3, why 5-error levels, etc.
2. **Trade-offs**: Cost vs. quality, determinism vs. flexibility
3. **Lessons learned**: What worked, what didn't, why
4. **Patterns discovered**: Reusable templates for future skills
5. **Failure modes**: How errors happen, how we recover

### 6.2 Deliverables

By end of Phase 1b, we will have produced:

- **Phase_1b_Execution_Log.md** (this will grow as we build)
  - Weekly progress updates
  - Decision rationale
  - Blockers and resolutions
  - Lessons learned
  
- **Skills_Development_Template.md** (for Phase 1c+ skills)
  - Checklist for SKILL.md structure
  - Checklist for test matrix
  - Checklist for C# portability
  
- **Error_Handling_Playbook.md** (guide for operators)
  - Decision tree for each error code
  - Recovery actions
  - When to escalate
  
- **Cost_Optimization_Report.md** (LLM usage analysis)
  - Tier 1/2/3 distribution
  - Average cost per run
  - Recommendations for tuning thresholds
  
- **Orchestrator_Design_Document.md** (technical deep-dive)
  - Decision logic for auth/commit-message/error handling
  - JSON logging schema
  - Extension points for Phase 1c
  
- **Process_Improvement_Recommendations.md** (for Phase 1c+)
  - What to measure next
  - Telemetry-logger integration with Aspire
  - How to extend skill framework

### 6.3 Who Reviews This?

- **Code Review Agent** (checks implementation against specs)
- **Process Review Agent** (checks logging completeness)
- **Domain Expert** (you, providing guidance + clarifications)

---

## Part 7: Open Questions & Clarifications

### Q1: User Context Loading

**DECIDED**: Use git config + secrets/settings for dev

- **Approach**: Read user identity from `git config user.name` and `git config user.email`
- **Dev Auth**: Hard-code credentials in `config/auth.yaml` (or environment variables)
- **Runtime**: GitHub will prompt for login/PAT via standard git flow (already working with git_push.ps1)
- **Enterprise**: Will extend in Phase 2 when Entra integration needed

**Implementation**:
```python
# In auth-validator
from pathlib import Path
import subprocess

def get_current_user() -> str:
    """Get user from git config."""
    result = subprocess.run(
        ["git", "config", "user.name"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def get_git_credentials() -> dict:
    """Load credentials from config/auth.yaml for dev."""
    config = load_yaml(Path("config/auth.yaml"))
    return config.get("dev_credentials", {})
```

**Auth Config** (`config/auth.yaml`):
```yaml
dev_credentials:
  github_user: "bizcad"
  github_pat: "${GITHUB_TOKEN}"  # Or read from env var
```

### Q2: Workflow Definition Format

**DECIDED**: YAML (for C#/TypeScript portability)

- **Format**: YAML workflow files in `workflows/` folder
- **Benefit**: Language-agnostic (C# and TS can parse YAML easily)
- **Example**: `workflows/git-push-autonomous.yaml`

**Workflow YAML Structure**:
```yaml
name: git-push-autonomous
version: 1.0.0

skill_chain:
  - skill: auth-validator
    inputs:
      user: "${CURRENT_USER}"
      resource: "origin/main"
  
  - skill: rules-engine
    inputs:
      files: "${STAGED_FILES}"
      config_dir: "config/"
    stop_on_error: true
  
  - skill: commit-message
    inputs:
      changed_files: "${CHANGED_FILES}"
      diffs: "${STAGED_DIFFS}"
      strategy: "hybrid"  # Tier 1→2→3
  
  - action: git-push
    if: "${all_skills_passed}"
```

**Orchestrator loads** this YAML and executes skill chain sequentially.

**Phase 1c+**: Same YAML can be loaded by C# `System.Text.Json` or TS ecosystem.

### Q3: MCP Server Implementation

**DECIDED**: Defer to Phase 1c

- **Phase 1b**: Skills run standalone (CLI callable)
- **Phase 1c+**: Implement MCP server when needed for DotNetSkills integration
- **Benefit**: Simpler Phase 1b, focus on core orchestration logic

**Portability Achieved**: Via YAML workflows + JSON I/O (no MCP needed for initial handoff)

### Q4: LLM Cost Budget & Tracking

**DECIDED**: Option C - Track but don't block (with future cost skill)

- **Approach**: Log cost per run, but allow unlimited Tier 2 calls
- **Tracking**: Each Tier 2 call logged with model, tokens, cost
- **Future**: Phase 1c+ will add dedicated cost-tracking skill
- **Multi-vendor**: Plan for MCP/skill to query vendor account balances
- **Metric**: Track tokens used per model for optimization

**Config**:
```yaml
commit_message:
  strategy: "hybrid"
  cost_tracking: true
  tier2_confidence_threshold: 0.75
  # No hard limit; track for later optimization
```

**Cost Skill (Phase 1c)**:
- Query OpenAI/Anthropic/other vendor for account balance
- Report tokens used by model/date
- Historical cost trends
- Multi-vendor aggregation

---

## Summary

Phase 1b is **not just coding skills**—it's establishing the reusable framework and capturing the methodology for continuous improvement.

**Key Success Metrics** (UPDATED):
- ✅ 3 skills shipped (auth, commit-msg, orchestrator) + deferred telemetry to Phase 1c
- ✅ 75+ tests passing (3 skills × 25 tests)
- ✅ Comprehensive process documentation
- ✅ Cost-optimized decisions (Tier 1→2→3 model with tracking)
- ✅ C# portability validated (YAML workflows)
- ✅ Analysis framework operational (JSON decision logs)
- ✅ All design questions answered ✅

**Next Step**: Begin auth-validator implementation with detailed execution logging.

**Estimated Timeline**: 2 weeks for auth-validator + commit-message MVP, 1 week for orchestrator integration
