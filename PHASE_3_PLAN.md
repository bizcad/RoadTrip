# Phase 3 Plan: Skill Chaining & DAG Routing

**Date**: February 14, 2026  
**Status**: PLANNING  
**Depends On**: Phase 2c (complete) - entry_points ready

---

## Vision

Enable **multi-step workflows** by chaining skills together in dependency order. Skills execute as a directed acyclic graph (DAG) where output from one skill feeds into the next.

**Example Usage**:
```python
chain = (SkillChain()
    .add_skill("config_loader", {"config": "app.yaml"})
    .then("rules_engine", {"mode": "strict"})
    .then("commit_message", {})
    .then("git_push_autonomous", {})
)
result = chain.execute()
```

---

## Core Components

### 1. SkillDAG (WS4 - new workstream)
**File**: `src/skills/dag/skill_dag.py`

**Responsibility**: Model the directed acyclic graph of skills

**Key Class**:
```python
class SkillDAG:
    """Represents a directed acyclic graph of skills."""
    
    def __init__(self):
        self.nodes = {}          # skill_name -> SkillNode
        self.edges = {}          # skill_name -> [dependent_skill_names]
        self.execution_order = []
    
    def add_node(self, skill_name: str, entry_point: str, config: Dict) -> SkillNode
    def add_edge(self, from_skill: str, to_skill: str) -> None
    def validate() -> bool                    # Detect cycles, orphans
    def topological_sort() -> List[str]       # Get execution order
    def to_dict() -> Dict                     # Serialize for storage
    def from_dict(data) -> SkillDAG           # Deserialize
```

**Validation Rules**:
- No cycles (DAG requirement)
- All referenced skills must exist in registry
- Entry points must be valid Python files
- Config parameters must be serializable

---

### 2. DAGBuilder (WS5 - new workstream)
**File**: `src/skills/dag/dag_builder.py`

**Responsibility**: Fluent API for constructing DAGs

**Key Class**:
```python
class SkillChain:
    """Fluent builder for skill chains (linearized DAGs)."""
    
    def __init__(self, registry_reader: RegistryReader):
        self.dag = SkillDAG()
        self.registry = registry_reader
        self.last_skill = None
    
    def add_skill(self, skill_name: str, config: Dict = None) -> 'SkillChain'
    def then(self, skill_name: str, config: Dict = None) -> 'SkillChain'
    def branch(self, skill_name: str, config: Dict = None) -> DAGBuilder  # Split execution
    def merge(self) -> 'SkillChain'  # Rejoin branches
    def validate() -> bool
    def build() -> SkillDAG
    def execute(ctx: ExecutionContext) -> ExecutionResult
```

**Design Notes**:
- Linear chains are most common (`.then()` links sequentially)
- Branching allows parallel skill execution (TBD if needed for Phase 3)
- Validates after each operation (fail-fast)

---

### 3. DAGExecutor (WS6 - new workstream)
**File**: `src/skills/dag/dag_executor.py`

**Responsibility**: Execute DAG in correct order, manage state/context

**Key Class**:
```python
class ExecutionContext:
    """Holds execution state during DAG traversal."""
    
    def __init__(self):
        self.inputs = {}           # skill_name -> input config
        self.outputs = {}          # skill_name -> output data
        self.timestamps = {}       # skill_name -> execution time
        self.errors = {}           # skill_name -> error (if any)
        self.status = {}           # skill_name -> 'pending'|'running'|'success'|'failed'
    
    def set_output(self, skill_name: str, output: Any) -> None
    def get_input(self, skill_name: str) -> Dict
    def get_previous_output(self, skill_name: str, index: int = -1) -> Any
    def mark_complete(self, skill_name: str, duration: float) -> None
    def to_dict() -> Dict  # Serialize entire execution trace

class DAGExecutor:
    """Executes skills in DAG order with error handling."""
    
    def __init__(self, registry: RegistryReader, skill_loader: SkillLoader):
        self.registry = registry
        self.loader = skill_loader  # Dynamically imports skill modules
    
    def execute(self, dag: SkillDAG, ctx: ExecutionContext) -> ExecutionResult
    def _validate_dag_before_execution(dag) -> bool
    def _load_skill_module(entry_point: str) -> SkillModule
    def _execute_single_skill(skill, config, ctx) -> Any
    def _handle_skill_error(skill_name, error, ctx) -> None
```

**Execution Flow**:
1. Validate DAG (no cycles, all skills exist)
2. Get topological order
3. For each skill in order:
   - Load module via entry_point
   - Resolve input config (merge defaults + context data)
   - Execute skill
   - Capture output, timestamp
   - On error: log, mark as failed, optionally continue/abort

---

### 4. SkillLoader (WS7 - new workstream)
**File**: `src/skills/dag/skill_loader.py`

**Responsibility**: Dynamically import and instantiate skill classes

**Design**:
```python
class SkillLoader:
    """Load skill classes from Python modules at runtime."""
    
    def load_skill_class(self, entry_point: str) -> type
        # entry_point: "src/skills/config_loader.py"
        # Returns: ConfigLoaderSkill class
    
    def instantiate_skill(self, skill_class, config: Dict) -> SkillInstance
        # Create instance with config injected
    
    def extract_skill_interface(skill_class) -> SkillInterface
        # Returns: parameter names, types, required vs optional
```

**Key Challenge**: Skills may be BaseAgent subclasses, regular classes, or functions. Need to normalize interface.

---

### 5. ExecutionResult & Tracing
**File**: `src/skills/dag/execution_models.py`

**Classes**:
```python
class ExecutionResult:
    dag: SkillDAG
    context: ExecutionContext
    status: 'success' | 'partial_failure' | 'failure'
    error: Optional[str]
    total_duration: float
    
    def to_dict() -> Dict  # Serialize for audit
    def to_csv() -> DataFrame  # Export timeline

class ExecutionTrace:
    """Logs every step for debugging & audit."""
    skill_name: str
    status: str
    input_config: Dict
    output: Any
    duration: float
    timestamp: str
    error: Optional[str]
```

---

## Data Models & Storage

### SkillDAG Serialization (YAML)
```yaml
workflows:
  auto_commit_workflow:
    description: "Commit and push changes"
    version: "1.0"
    skills:
      - name: config_loader
        config: {config_file: "project.yaml"}
      - name: rules_engine
        config: {mode: "strict"}
      - name: commit_message
        config: {template: "auto"}
      - name: git_push_autonomous
        config: {force: false}
    edges: []  # Empty for linear chains
    created: "2026-02-14T00:00:00Z"
    updated: "2026-02-14T00:00:00Z"
```

### New Registry Features
- Store DAGs in registry/workflows/ directory
- List available workflows: `list-workflows`
- Get workflow details: `get-workflow {name}`
- Execute workflow: `run-workflow {name} --config file.yaml`

---

## Test Strategy

### Unit Tests (11 tests)

**SkillDAG** (3 tests):
- ✓ Add valid node
- ✓ Detect cycle (error)
- ✓ Topological sort returns correct order

**SkillChain Builder** (4 tests):
- ✓ Linear chain builds correctly
- ✓ Invalid skill name fails validation
- ✓ Duplicate skill names handled
- ✓ Empty chain validation

**DAGExecutor** (2 tests):
- ✓ Execute linear DAG successfully
- ✓ Handle skill error and continue/abort modes

**SkillLoader** (2 tests):
- ✓ Load skill from entry_point
- ✓ Instantiate with config injection

### Integration Tests (6 tests)

**End-to-End** (4 tests):
- ✓ Config→Rules→CommitMessage→GitPush workflow
- ✓ Output from one skill feeds into next
- ✓ Execution timeline captured
- ✓ Failure in middle skill halts chain

**Storage & Persistence** (2 tests):
- ✓ Save workflow DAG to YAML, reload, execute
- ✓ Export execution trace to CSV

### Total: 17 tests

---

## Phase 3 Workstreams (WS4-7)

| WS | Name | Owner | Responsibility |
|----|------|-------|-----------------|
| WS4 | SkillDAG | TBD | Model & validate DAGs |
| WS5 | DAGBuilder | TBD | Fluent chain API |
| WS6 | DAGExecutor | TBD | Execute in order, manage context |
| WS7 | SkillLoader | TBD | Dynamic module import |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Circular dependencies in DAG | Infinite loop | Topological sort validates before execution |
| Skill module import errors | Execution fails | SkillLoader try/catch with detailed error messages |
| Config mismatch (output → input) | Type errors | ExecutionContext type hints + validation |
| Missing entry_point files | Broken chain | Registry validation on DAG construction |
| Performance (large DAGs) | Slow workflows | Lazy loading, caching, async execution (Phase 4) |

---

## Success Criteria

### Functional
- ✓ Create skill chains with fluent API
- ✓ Execute 12 registered skills in dependency order
- ✓ Pass output from one skill to next automatically
- ✓ Handle errors gracefully (continue/abort modes)
- ✓ Capture full execution trace (timeline, outputs, errors)

### Quality
- ✓ 17/17 tests passing
- ✓ Zero warnings or errors
- ✓ Type hints on all classes/functions
- ✓ Comprehensive docstrings

### Backward Compatibility
- ✓ Existing Phase 2c tests still pass (20/20)
- ✓ Registry reader/writer unchanged
- ✓ Skill metadata unchanged

---

## Files to Create

### New Files
- `src/skills/dag/__init__.py` - Package init
- `src/skills/dag/skill_dag.py` - DAG model (150 lines)
- `src/skills/dag/dag_builder.py` - Fluent builder (200 lines)
- `src/skills/dag/dag_executor.py` - Executor & context (250 lines)
- `src/skills/dag/skill_loader.py` - Dynamic loader (100 lines)
- `src/skills/dag/execution_models.py` - Result/Trace/Errors (150 lines)
- `tests/test_phase_3_skill_dag.py` - Unit tests (350 lines)
- `tests/test_phase_3_integration.py` - E2E tests (400 lines)

### Config Files
- `config/workflows/` - New directory for DAG definitions

---

## Estimated Effort

| Component | Lines | Est. Time |
|-----------|-------|-----------|
| SkillDAG | 150 | 2h |
| DAGBuilder | 200 | 2h |
| DAGExecutor | 250 | 3h |
| SkillLoader | 100 | 1.5h |
| Models | 150 | 1h |
| Tests (17 total) | 750 | 4h |
| **Total** | **1,600** | **~13.5h** |

---

## Open Questions for Clarification

1. **Error Handling Mode**: On skill failure, should the chain:
   - `ABORT` - Stop immediately, return error (default)
   - `SKIP` - Skip failed skill, continue with next (if no dependency)
   - `RETRY` - Retry N times with backoff
   - Which should be the default?

2. **Output Passing**: When skill B depends on skill A's output, should we:
   - Auto-merge A's output into B's input config (implicit)
   - Require explicit mapping (`skill_b.input.data = skill_a.output`)
   - Support both modes?

3. **Parallel Execution**: For Phase 3, should we:
   - Only support linear chains (simpler, sufficient for MVP)
   - Support branching/parallel execution?
   - Defer to Phase 4?

4. **Skill Interface Normalization**: Should SkillLoader:
   - Assume all skills are BaseAgent subclasses?
   - Support arbitrary Python callables (functions)?
   - Require explicit skill descriptors in registry?

5. **Config Sources**: Should execution config come from:
   - Hard-coded in DAG definition
   - YAML workflow file
   - Runtime parameters
   - All three with priority?

---

## Next Steps (if approved)

1. Implement SkillDAG + validation
2. Build SkillChain fluent API
3. Implement DAGExecutor
4. Create SkillLoader
5. Write 17 tests
6. Integration testing
7. Documentation

---

**Status**: Ready for clarifications before implementation

