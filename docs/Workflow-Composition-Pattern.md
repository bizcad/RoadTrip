# Workflow Composition Pattern

**Status**: Deferred Implementation (Phase 2a)  
**Decision Date**: 2026-02-14  
**Related**: Phase 2a plan, Conditional-Logic discussion

---

## Problem Statement

Current skill architecture uses single-path operations: `skill(input) → output`. However, real-world workflows require **branching logic** based on intermediate results:

```
SchemaExtractor(mcp) → {success, security_risk, auth_required}
                         ↓         ↓                ↓
                    Analyze   Escalate         SetupAuth
```

Without a composition pattern, we'd end up with:
- Cascading `if/elif/else` statements inside skills (violates separation of concerns)
- Monolithic workflow controller (hard to test, extend, reuse)
- No standardized way to represent branching (each team member invents their own)

---

## Solution: Linked-List Tree Pattern

A lightweight, pure-Python approach using node-based composition:

```python
class WorkflowNode:
    """A single step in a workflow with optional branching."""
    
    def __init__(self, skill, predicate=None, on_true=None, on_false=None):
        self.skill = skill              # Skill to execute
        self.predicate = predicate      # Function: Result → bool (optional)
        self.on_true = on_true          # Next node if predicate is True
        self.on_false = on_false        # Next node if predicate is False

class WorkflowExecutor:
    """Execute a linked-list workflow."""
    
    def execute(self, input_data, start_node):
        current = start_node
        result = input_data
        
        while current:
            # Execute skill
            result = current.skill(result)
            
            # Route based on predicate
            if current.predicate is None:
                # No decision: linear progression
                current = current.on_true
            elif current.predicate(result):
                current = current.on_true
            else:
                current = current.on_false
        
        return result
```

### Building a Workflow

```python
# Define nodes
extract = WorkflowNode(SchemaExtractor())
safe_branch = WorkflowNode(AnalyzePatterns())
escalate = WorkflowNode(SecurityReview())

# Wire together (linked list with branching)
extract.on_true = safe_branch
extract.on_false = escalate
extract.predicate = lambda r: not r.security_issues_found

# Execute
executor = WorkflowExecutor()
result = executor.execute(mcp_data, extract)
```

---

## Characteristics

| Aspect | Details |
|--------|---------|
| **Structure** | Binary tree (each node can branch on predicate) |
| **Traversal** | Linear execution with conditional jumps |
| **Composition** | Nodes link together via attributes |
| **Predicate** | Any callable that returns bool |
| **Terminal** | Node with `on_true=None` and `on_false=None` |
| **Infinite loops** | Possible if nodes cycle (caller responsibility to prevent) |

---

## When to Use

✅ **Use this pattern when:**
- Workflow has 2-8 decision points
- Each decision leads to alternative next steps
- Skills are independently testable
- You want workflow as data (composable, visualizable)

❌ **Don't use when:**
- All paths just continue linearly (overkill)
- You need parallel execution (different pattern)
- Decisions are deeply nested (>5 levels) - reconsider problem decomposition
- Workflow changes frequently based on config (consider a DSL/YAML instead)

---

## Example: Phase 2a MCP Analysis

```python
# Phase 2a workflow: Analyze MCP, escalate if issues found

extract_schema = WorkflowNode(SchemaExtractor())
analyze_patterns = WorkflowNode(PatternAnalyzer())
security_check = WorkflowNode(SecurityAudit())
escalate = WorkflowNode(HumanReview())
finalize = WorkflowNode(ResultsWriter())

# Linear path: extract → analyze → security → finalize
extract_schema.on_true = analyze_patterns
analyze_patterns.on_true = security_check
security_check.predicate = lambda r: r.risk_level > 5
security_check.on_true = escalate      # High risk: escalate first
security_check.on_false = finalize     # Low risk: straight to results

escalate.on_true = finalize            # After escalation, finalize

# Execute
executor = WorkflowExecutor()
result = executor.execute(mcp_data, extract_schema)
```

---

## Comparison to Alternatives

### Option 1: DAG Engine (Airflow, Prefect, etc.)

**Pros:**
- Distributed execution, monitoring dashboards, retry logic
- Industry standard, widely used

**Cons:**
- ❌ Heavy deployment (PostgreSQL, message broker, REST API)
- ❌ Learning curve (new syntax, configuration)
- ❌ Overkill for single-machine, <50-task workflows
- ❌ Adds devops complexity during Phase 3+

**Decision**: Defer until Phase 3 if we need: distributed execution, monitoring, or 50+ tasks.

### Option 2: Cascading If/Else (Inside Skills)

**Pros:**
- ✅ Simple for small workflows
- ✅ No new abstractions

**Cons:**
- ❌ Violates single responsibility (skill becomes controller)
- ❌ Hard to test workflow logic separately
- ❌ Difficult to visualize or reuse

**Decision**: Rejected for Phase 2a+ workflows.

### Option 3: Linked-List Tree (This Pattern)

**Pros:**
- ✅ Pure Python, no dependencies
- ✅ Composable and testable
- ✅ Easy to visualize (can draw as tree on paper)
- ✅ Scales to Phase 2a/2b needs
- ✅ Minimal overhead

**Cons:**
- ⚠️ No built-in monitoring or history
- ⚠️ No distributed execution
- ⚠️ Manual cycle-detection (caller responsibility)

**Decision**: Implement in Phase 2a for initial workflow composition.

---

## Implementation Plan

### Phase 2a (Starting Mar 10)
- [ ] Create `src/skills/workflow/workflow_node.py` with `WorkflowNode` class
- [ ] Create `src/skills/workflow/workflow_executor.py` with `WorkflowExecutor` class
- [ ] Write unit tests for node linking and predicate routing
- [ ] Update Phase 2a plan with example workflows using this pattern

### Phase 3 (If Needed)
- [ ] Consider upgrading to DAG engine if:
  - Workflows exceed 10-15 decision points, OR
  - Need distributed execution, OR
  - Require monitoring/audit trails

---

## Design Questions (For Future Sessions)

1. **Error propagation**: If a skill raises an exception, should workflow abort or route to fallback node?
2. **Result object**: What structure should skills return to make predicates clean? (Status enum? Dict with keys?)
3. **Workflow introspection**: Should we be able to serialize/deserialize workflows to YAML or JSON?
4. **Timeout handling**: Should WorkflowExecutor have per-node or global timeouts?
5. **Logging**: Should each node execution be logged? What level of detail?

---

## References

- [Session Log 2026-02-14](../PromptTracking/Session%20Log%2020260214.md) - Original discussion about conditional logic
- Phase 2a Plan (forthcoming)
- [Principles-and-Processes.md](Principles-and-Processes.md) - General architectural approach
