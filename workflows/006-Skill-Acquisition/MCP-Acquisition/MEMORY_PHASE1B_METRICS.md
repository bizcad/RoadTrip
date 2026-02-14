# Agent Memory System - Phase 1b Execution Metrics

**Agent Role**: Phase 1b Metrics Foundation  
**Task**: Build ExecutionMetrics infrastructure for self-improvement learning  
**Timeline**: Feb 14 - Mar 10, 2026  
**Status**: Waiting to start  

---

## Task Definition (From SELF_IMPROVEMENT_ROADMAP.md)

### Objective
Create foundational execution metrics collection system that enables the three self-improvement phases (Phase 2a anomalies, Phase 2b learning, Phase 3 optimization).

### Core Problem We're Solving
Without observability, we can't improve:
- No metrics → Can't detect anomalies
- No anomalies → Can't learn bidirectionally  
- No learning → Can't optimize execution

---

## What Gets Measured

### Per-Skill Metrics
```
ExecutionMetric:
  - skill_id: str
  - execution_id: UUID
  - timestamp: datetime
  
  # Lifecycle
  - started_at: datetime
  - completed_at: datetime
  - total_duration_ms: float
  - status: "success" | "failure" | "timeout"
  
  # Inputs & Outputs
  - input_size_bytes: int
  - output_size_bytes: int
  - input_complexity: float  # TBD metric
  
  # Costs & Resources
  - api_calls_count: int
  - api_calls_cost: float  (if LLM/external)
  - memory_used_mb: float
  - token_usage: dict  (for LLM skills)
  
  # Outcomes
  - success_flag: bool
  - error_category: str  (if failed)
  - error_message: str
  - warning_count: int
  - validation_passed: bool
  
  # Quality Signals
  - user_satisfaction: Optional[float]  (1-5 Likert)
  - correctness_score: Optional[float]  (0-1)
  - latency_acceptable: bool
```

### Aggregated Metrics (For Skill Profiling)
```
SkillProfile:
  - skill_id: str
  - total_executions: int
  - success_rate: float
  - mean_duration_ms: float
  - p50_duration_ms: float
  - p95_duration_ms: float
  - p99_duration_ms: float
  - failure_categories: Dict[str, count]
  - cost_per_execution: float  (if applicable)
  - quality_score: float  (aggregate)
```

---

## Implementation Scope

### What's IN Scope
1. **Data Model** - ExecutionMetric dataclass with full schema
2. **Collection Infrastructure**
   - Decorator: `@track_execution()` for skills
   - Context manager: `with track_execution():` pattern
3. **Storage**
   - SQLite database: `execution_metrics.db`
   - Schema with proper indexes
4. **Query APIs**
   - Get metrics for skill
   - Get metrics for date range
   - Get metrics by status
5. **Aggregation**
   - SkillProfile calculation
   - Statistics computation
6. **Export**
   - Export to CSV for analysis
   - Export to JSON for external tools

### What's OUT of Scope (For Phase 2+)
- Anomaly detection (Phase 2a)
- Learning from anomalies (Phase 2b)
- Optimization recommendations (Phase 3)
- Orchestrator integration (Phase 2)

---

## Data Model (Detailed)

### ExecutionMetric (Collection Unit)
```python
@dataclass
class ExecutionMetric:
    """Single skill execution record"""
    metric_version: str = "1.0"  # For schema evolution
    
    # IDs
    skill_id: str
    execution_id: UUID = field(default_factory=uuid4)
    job_id: Optional[str] = None  # Parent job if batched
    
    # Lifecycle (all timings in UTC)
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    status: Literal["running", "success", "failure", "timeout"] = "running"
    
    # Input Characterization
    input_size_bytes: Optional[int] = None
    input_hash: Optional[str] = None  # For duplicate detection
    input_complexity: Optional[float] = None
    input_summary: Optional[str] = None  # Free text description
    
    # Output Characterization
    output_size_bytes: Optional[int] = None
    output_quality: Optional[float] = None  # 0-1, filled by validator
    output_summary: Optional[str] = None
    
    # Costs & Resources
    api_calls_count: int = 0
    api_calls_cost_usd: float = 0.0
    memory_used_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # LLM-Specific (if applicable)
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    
    # Error/Warning Info
    error_occurred: bool = False
    error_category: Optional[str] = None  # 
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    warning_count: int = 0
    warnings: List[str] = field(default_factory=list)
    
    # Quality Signals
    validation_passed: bool = True
    correctness_score: Optional[float] = None  # 0-1 (when available)
    user_feedback_received: bool = False
    user_satisfaction: Optional[int] = None  # 1-5 Likert
    
    # Metadata
    agent_id: Optional[str] = None  # If run by agent
    environment: Optional[str] = None  # prod/test/dev
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class ExecutionMetricError:
    """Error category definitions"""
    categories = {
        "timeout": "Execution exceeded time limit",
        "out_of_memory": "Memory exhausted",
        "api_error": "External API failure",
        "input_validation": "Input didn't meet requirements",
        "output_validation": "Output failed quality check",
        "unknown": "Unclassified error",
    }
```

### SkillProfile (Aggregation Unit)
```python
@dataclass
class SkillProfile:
    """Aggregate statistics for a skill"""
    skill_id: str
    calculated_at: datetime
    
    # Execution counts
    total_executions: int
    successful_executions: int
    failed_executions: int
    timeout_executions: int
    
    # Success metrics
    success_rate: float  # 0-1
    failure_categories: Dict[str, int]
    
    # Duration metrics (milliseconds)
    mean_duration_ms: float
    median_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    stddev_duration_ms: float
    
    # Cost metrics
    total_api_calls: int
    mean_api_calls_per_execution: float
    total_cost_usd: float
    mean_cost_per_execution: float
    
    # Quality metrics
    mean_correctness_score: float
    mean_quality_score: float
    mean_output_size_bytes: float
    
    # Feedback
    total_feedback_responses: int
    mean_user_satisfaction: float
    
    # Trend indicators (for Phase 2)
    getting_faster: Optional[bool] = None  # TBD calculation
    getting_cheaper: Optional[bool] = None
    success_rate_trend: Optional[str] = None  # "up", "down", "stable"
```

---

## Storage Design

### SQLite Schema

```sql
-- Main metrics table
CREATE TABLE execution_metrics (
    execution_id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,
    job_id TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    total_duration_ms REAL,
    status TEXT,
    input_size_bytes INTEGER,
    output_size_bytes INTEGER,
    input_hash TEXT,
    api_calls_count INTEGER DEFAULT 0,
    api_calls_cost_usd REAL DEFAULT 0,
    memory_used_mb REAL,
    error_occurred BOOLEAN DEFAULT 0,
    error_category TEXT,
    error_message TEXT,
    validation_passed BOOLEAN DEFAULT 1,
    correctness_score REAL,
    user_satisfaction INTEGER,
    environment TEXT,
    tags TEXT,  -- JSON array
    INDEX(skill_id),
    INDEX(status),
    INDEX(started_at),
    INDEX(error_occurred)
);

-- Aggregated profiles (materialized view equivalent)
CREATE TABLE skill_profiles (
    skill_id TEXT PRIMARY KEY,
    calculated_at TIMESTAMP,
    total_executions INTEGER,
    success_rate REAL,
    mean_duration_ms REAL,
    p95_duration_ms REAL,
    -- ... other fields
);

-- Error catalog (reference)
CREATE TABLE error_categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT,
    description TEXT,
    severity TEXT,  -- low/medium/high/critical
);
```

---

## API Design

### Collection Interface
```python
# Decorator pattern
@track_execution(skill_id="csv_reader", environment="prod")
async def read_csv(filepath: str) -> DataFrame:
    ...

# Context manager pattern
with track_execution("json_writer") as context:
    result = json.dumps(data)
    context.record_output_size(len(result))

# Direct API
metrics = ExecutionMetricsCollector()
metrics.start_execution("skill_id")
# ... do work ...
metrics.end_execution(status="success", output_size_bytes=1024)
```

### Query Interface
```python
collector = ExecutionMetricsCollector()

# Get recent metrics
metrics = collector.get_metrics(
    skill_id="csv_reader",
    time_range=(start, end),
    status_filter="success"
)

# Get skill profile
profile = collector.get_skill_profile("csv_reader")

# Get error analysis
errors = collector.get_error_analysis("json_writer", limit=10)

# Export for analysis
collector.export_csv("metrics_export.csv")
collector.export_stats_json("stats.json")
```

---

## Implementation Phases

### Phase 1: Data Model & Storage (Week 1)
- [ ] Define ExecutionMetric dataclass with all fields
- [ ] Define SkillProfile dataclass
- [ ] Create SQLite schema
- [ ] Create database initialization code

### Phase 2: Collection Mechanisms (Week 2)
- [ ] Decorator `@track_execution()`
- [ ] Context manager implementation
- [ ] Direct API collector class
- [ ] Automatic status recording

### Phase 3: Query & Analysis (Week 2-3)
- [ ] Query builders
- [ ] Aggregation calculations
- [ ] Statistical functions (p95, stddev, etc.)
- [ ] Export functions

### Phase 4: Testing & Documentation (Week 3)
- [ ] Unit tests for data model
- [ ] Integration tests for collection
- [ ] Query API tests
- [ ] Documentation

---

## Testing Strategy

### Fixtures
```
tests/executor/metrics/fixtures/
├── sample_executions/
│   ├── success_cases.json
│   ├── failure_cases.json
│   └── edge_cases.json
└── expected_profiles/
    └── skill_profiles.json
```

### Test Categories
1. **Data Model** - All fields, validation, serialization
2. **Collection** - Decorator, context manager, direct API
3. **Storage** - SQLite operations, schema, indexing
4. **Queries** - All query patterns, filtering, aggregation
5. **Statistics** - Percentile calculation, trend detection
6. **Export** - CSV, JSON format verification

---

## Integration Points (Future)

### For Phase 2a (Anomaly Detection)
- API to fetch metrics by time window
- API to get statistical baselines
- API to mark anomalies

### For Phase 2b (Bidirectional Learning)
- API to correlate executions with learnings
- API to flag executions for review
- API to record corrective actions

### For Phase 3 (Optimization)
- API to track optimization experiments
- API to compare baseline vs. optimized
- API to generate improvement recommendations

---

## Success Criteria

- [ ] ExecutionMetric captures all required fields
- [ ] SQLite schema normalized and performant
- [ ] @track_execution() decorator works transparently
- [ ] Query APIs return correct aggregations
- [ ] Unit tests >90% coverage
- [ ] Can export 10,000 metrics in <1 second
- [ ] SkillProfile calculations verified
- [ ] Documentation complete

---

## Dependencies

### Python Packages
```
sqlalchemy>=2.0       # ORM optional, but helpful
pydantic>=2.0         # Validation
python-dateutil>=2.8  # Date handling
```

### RoadTrip Code
- None initially (standalone)
- Will integrate with skills in Phase 2

---

## Blockers & Risks

### Potential Issues
- SQLite performance with large metric volumes
- Query optimization for time-range queries
- UUID vs. string for IDs (performance consideration)
- Timestamp UTC normalization across OS platforms

### Mitigation
- Plan for time-series database migration (Phase 3)
- Index strategy defined upfront
- Use datetime.utcnow() consistently
- Test on both Windows and Linux

---

## Memory Update Guide

As you work, update this section:

**What I Discovered**:
- Database performance characteristics
- Best practices for metrics collection
- Statistical calculation nuances
- Integration constraints

**What I Implemented**:
- Each component as completed
- Test coverage for each module
- Documentation updates

**Blockers & Issues**:
- Any performance issues
- Query optimization challenges
- Schema evolution considerations

**Recommendations for Phase 2**:
- What metrics to prioritize for anomaly detection
- How to expose API to Phase 2a agent
- Schema extensions needed

---

## Quick Start Checklist

- [ ] Create `src/metrics/` directory
- [ ] Define ExecutionMetric dataclass
- [ ] Implement SQLite storage
- [ ] Create @track_execution() decorator
- [ ] Build query APIs
- [ ] Create test fixtures
- [ ] Verify export functions

---

**Timeline**: Feb 14 - Mar 10, 2026  
**Branch**: feature/phase-1b-metrics  
**Merge Target**: main@Mar 10  
**Priority**: MEDIUM (enables Phase 2, but no external blockers)

Let me know when you're ready to start!
