# Agent Memory System - Batch 1 Utility Skills

**Agent Role**: Batch 1 Utilities (Skill Implementation)  
**Task**: Implement 8 utility skills for CSV, YAML, JSON, File operations  
**Timeline**: Feb 21 - Mar 10, 2026  
**Status**: Waiting to start  

---

## Task Definition (From SKILL_ACQUISITION_ROADMAP.md)

### Objective
Build 8 foundational utility skills that provide input parsing and data handling.

### Skills to Implement

1. **CSV Reader** - Parse CSV files into structured data
2. **CSV Writer** - Generate CSV from structured data
3. **YAML Reader** - Parse YAML files
4. **YAML Writer** - Generate YAML output
5. **JSON Reader** - Parse JSON files
6. **JSON Writer** - Generate JSON output
7. **File Reader** - Read text files with encoding handling
8. **File Writer** - Write text files safely

### Success Criteria
- [ ] All 8 skills implemented with consistent interface
- [ ] Each skill has comprehensive docstring
- [ ] Unit tests for each (error handling, edge cases)
- [ ] Integration tests (end-to-end)
- [ ] SkillMetadata created for each (fingerprinting ready)
- [ ] Can be called via RoadTrip orchestrator interface
- [ ] ErrorHandling for common failures
- [ ] Performance acceptable (<100ms for typical operations)

### Deliverables
1. `src/skills/utilities/` directory with 8 skill files
2. `tests/skills/utilities/` with comprehensive tests
3. `src/skills/utilities/UTILITIES_REGISTRY.md` - Skill catalog
4. `workflows/006-Skill-Acquisition/Batch-1/PROGRESS.md` - Weekly updates

---

## Skill Interface Standard

All skills must follow this pattern:

```python
@dataclass
class UtilitySkillInput:
    """Standard input for utility skills"""
    filepath: str
    encoding: str = "utf-8"
    # skill-specific fields
    
@dataclass  
class UtilitySkillOutput:
    """Standard output for utility skills"""
    success: bool
    data: Any
    error: Optional[str]
    metadata: Dict  # timing, size, etc.

async def execute(input: UtilitySkillInput) -> UtilitySkillOutput:
    """Skill entry point"""
```

---

## Parallel Track Strategy

**Important**: This track is INDEPENDENT of MCP work.

- Can start whenever (Feb 21 recommended)
- No dependency on registry or MCP catalog
- Will be merged to main by Mar 10
- Cannot block other work
- Good for learning SkillMetadata structure

---

## What You'll Learn

### Core Concepts
- RoadTrip skill interface
- ExecutionMetrics integration (when available from Phase 1b)
- Error handling patterns
- Testing patterns for orchestration

### Shared Infrastructure
- Look at `src/skills/models/fingerprint.py` (already created)
- SkillMetadata structure (important for registry)
- SkillCapability definitions

---

## Implementation Notes

### File Handling
- Use pathlib for cross-platform paths
- Handle encoding errors gracefully
- Log file sizes for metrics

### Data Handling
- CSV: Use pandas or csv module
- YAML: Use pyyaml
- JSON: Use standard json module
- File: Use modern pathlib API

### Error Handling
Create custom exceptions:
```python
class FileNotFoundError(Exception): ...
class EncodingError(Exception): ...
class ParseError(Exception): ...
```

---

## Testing Strategy

### Fixture Data
```
tests/fixtures/data/
├── sample.csv
├── sample.yaml
├── sample.json
├── large_file.txt
└── file_with_encoding_issues.txt
```

### Test Categories
1. **Happy Path**: Normal usage
2. **Error Cases**: Missing files, bad encoding, parse errors
3. **Edge Cases**: Empty files, special characters, large files
4. **Performance**: Typical operational latency

---

## Timeline

**Week 1 (Feb 21-27)**: Design & Scaffolding
- [ ] Define UtilitySkillInput/Output dataclasses
- [ ] Create test fixtures
- [ ] Build CSV Reader/Writer (most common)

**Week 2 (Feb 28-Mar 6)**: Implementation
- [ ] YAML Reader/Writer
- [ ] JSON Reader/Writer
- [ ] File Reader/Writer
- [ ] Error handling for all

**Week 3 (Mar 7-10)**: Testing & Documentation
- [ ] Unit tests complete
- [ ] Integration tests
- [ ] Documentation
- [ ] Ready to merge

---

## Dependencies

### Python Packages
```
pyyaml>=6.0      # YAML support
pandas>=1.5.0    # CSV support (optional, csv module works too)
```

### RoadTrip Code
- `src/skills/models/fingerprint.py` - SkillMetadata structure
- `src/orchestrator/` - When available, integration point

---

## What to Output

### Registry Entry
Each skill needs entry:
```yaml
csv_reader:
  name: "CSV Reader"
  version: "1.0.0"
  capability: "data_input"
  input_type: "csv_file"
  output_type: "structured_data"
  options:
    - delimiter
    - encoding
    - has_header
```

### Test Results
```
tests/skills/utilities/
├── test_csv_reader.py
├── test_csv_writer.py
├── test_yaml_reader.py
├── test_yaml_writer.py
├── test_json_reader.py
├── test_json_writer.py
├── test_file_reader.py
├── test_file_writer.py
└── conftest.py  (fixtures)
```

---

## Integration Points

When Phase 1b is ready:
- Report execution metrics from each skill
- Log success/failure to ExecutionMetrics

When Phase 2 is ready:
- Add skill fingerprints to registry
- Make available for DAG composition

---

## Blockers & Risks

### None anticipated
- Skills are simple, well-defined
- No external dependencies (registry, MCPs)
- Standard Python libraries sufficient

### Nice to Have
- Streaming support (for large files)
- Compression handling (.gz, .zip)
- Database connectors

---

## Next Agent Should Know

### Input
- No external input needed
- Start from scratch with fixtures

### Output  
- 8 working utility skills
- Comprehensive test suite
- Ready to integrate with ExecutionMetrics
- Merged to main by Mar 10

### For Phase 2a Integration
- Orchestrator will call these via standard interface
- Metrics automatically collected
- Can be composed in DAG workflows

---

## References

### Standards
- RoadTrip SkillMetadata: `src/skills/models/fingerprint.py`
- Orchestrator interface: [TBD - check src/orchestrator/]

### Examples
- Similar utilities from other systems
- Python standard library docs

---

## Memory Update Guide

Update this file as you work:

**What I Discovered**:
- Which libraries work best
- Edge cases in file handling
- Performance characteristics
- Encoding handling patterns

**What I Implemented**:
- Each skill as completed
- Test results
- Documentation updates

**Blockers & Issues**:
- Any problems with specific libraries
- Cross-platform compatibility issues
- Performance bottlenecks

**Next Agent Should Know**:
- Lessons learned
- Recommendations for Phase 2 skills
- Patterns to replicate

---

## Quick Start Checklist

- [ ] Create fixtures directory
- [ ] Define UtilitySkillInput/Output
- [ ] Implement CSV Reader/Writer
- [ ] Create unit tests
- [ ] Verify integration point exists
- [ ] Start YAML and JSON

---

**Recommended Start**: Feb 21, 2026  
**Expected Finish**: Mar 10, 2026  
**Branch**: feature/batch-1-utilities  
**Merge Target**: main@Mar 10

Let me know when you're ready to start!
