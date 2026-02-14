# Short-Term Data Infrastructure Plan (Phase 1b-now)

**Version**: 1.0  
**Duration**: 4 weeks (2026-02-14 to 2026-03-14)  
**Status**: Ready for implementation  
**Owner**: System engineer + LLM code agent  
**Goal**: Establish metrics persistence and foundational self-improvement data pipeline

---

## Overview

This document specifies **exactly what to build this month** to enable self-improvement research. No optimization logic yet—pure data collection infrastructure.

**Success definition**: By 2026-03-14, the system captures and persists rich metrics for every skill execution, with zero impact on skill performance.

---

## Work Items (In Priority Order)

### Item 1: ExecutionMetrics Data Model

**Effort**: 4 hours  
**Owner**: LLM code agent (skeleton), human review  
**Files to create/modify**:
- `src/skills/models.py` (add `ExecutionMetrics` dataclass)

**Specification**:

```python
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import json

@dataclass
class ExecutionMetrics:
    """Metrics captured for a single skill execution.
    
    All fields are filled at specific lifecycle points:
    - Pre-execution fields: filled before skill runs
    - During fields: updated as execution proceeds
    - Post-execution fields: filled after skill completes
    
    IMMUTABLE: Once this object is serialized to JSON and logged,
    it must never be modified. Create new ExecutionMetrics for each execution.
    """
    
    # === EXECUTION IDENTITY (pre) ===
    execution_id: str  # UUID, unique per execution
    skill_name: str  # "git-push-autonomous", "blog-publish", etc.
    skill_version: str  # Semantic version of skill implementation
    orchestrator_version: str  # Version of orchestrator at execution time
    timestamp_start: str  # ISO8601 UTC, e.g., "2026-02-14T14:23:00Z"
    timestamp_end: Optional[str] = None  # Filled post-execution
    operator: str = "human"  # "human" or system/agent name
    environment: str = "prod"  # "local", "staging", "prod"
    
    # === EXECUTION OUTCOME (post) ===
    execution_succeeded: Optional[bool] = None  # True/False/None-if-interrupted
    execution_failed: Optional[bool] = None  # Inverse of succeeded
    error_category: Optional[str] = None  # "Security", "Auth", "Network", "Timeout", "Logic", "Unknown"
    error_code: Optional[int] = None  # Exit code or API error code
    error_reason: Optional[str] = None  # Human-readable error message (max 500 chars)
    
    # === PERFORMANCE (post) ===
    total_latency_ms: Optional[int] = None  # End-to-end time in milliseconds
    wall_clock_time_ms: Optional[int] = None  # Real elapsed time (including I/O)
    
    # === LLM TOKENS & COST (post) ===
    tokens_used: int = 0  # Total tokens (input + output)
    tokens_input: int = 0  # Input tokens only
    tokens_output: int = 0  # Output tokens only
    cost_usd: float = 0.0  # Actual cost incurred (8 decimal places)
    cost_tier: str = "Free"  # "Free", "Standard", "Premium"
    
    # === QUOTA & BUDGET (post) ===
    free_tier_quota_remaining: Optional[int] = None  # Tokens remaining in free tier
    free_tier_quota_pct_used: Optional[float] = None  # 0.0-100.0, % of daily quota consumed
    
    # === QUALITY (post) ===
    output_correct: Optional[bool] = None  # Oracle verification result
    confidence_score: Optional[float] = None  # 0.0-1.0, system's confidence in correctness
    decision_made: Optional[str] = None  # "APPROVE", "BLOCK", "PARTIAL", etc.
    
    # === METADATA ===
    input_hash: Optional[str] = None  # SHA256 of input
    output_hash: Optional[str] = None  # SHA256 of output
    skill_path_in_dag: Optional[str] = None  # "orchestrator -> rules-engine -> auth-validator -> executor"
    tags: dict = field(default_factory=dict)  # Extensible key-value pairs for future metrics
    
    def validate(self) -> bool:
        """Check that required fields are present.
        
        Returns:
            True if all critical fields populated; False otherwise.
        
        Raises:
            ValueError if critical fields missing.
        """
        required = ["execution_id", "skill_name", "skill_version", "timestamp_start", "timestamp_end"]
        missing = [f for f in required if getattr(self, f) is None]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return True
    
    def to_json(self) -> str:
        """Serialize to JSON string for JSONL logging.
        
        Returns:
            JSON string representation (one line, no newlines).
        """
        return json.dumps(asdict(self), default=str)
    
    @staticmethod
    def from_json(json_str: str) -> "ExecutionMetrics":
        """Deserialize from JSON string.
        
        Args:
            json_str: JSON string from JSONL file.
        
        Returns:
            ExecutionMetrics object.
        """
        data = json.loads(json_str)
        return ExecutionMetrics(**data)
```

**Testing**:
```python
# test_models.py
def test_execution_metrics_serialization():
    """Verify JSON round-trip fidelity."""
    metrics = ExecutionMetrics(
        execution_id="uuid-123",
        skill_name="git-push-autonomous",
        skill_version="0.1.0",
        timestamp_start="2026-02-14T14:23:00Z",
        timestamp_end="2026-02-14T14:23:05Z",
        # ... (fill in all fields)
    )
    
    json_str = metrics.to_json()
    metrics2 = ExecutionMetrics.from_json(json_str)
    
    assert metrics == metrics2, "Round-trip serialization failed"
```

**Acceptance Criteria**:
- [ ] Compiles without type errors
- [ ] Can serialize to JSON without loss
- [ ] Can deserialize from JSON back to identical object
- [ ] `validate()` catches missing required fields
- [ ] All 20+ fields have correct types and defaults

---

### Item 2: Telemetry Logger Enhancement

**Effort**: 6 hours  
**Owner**: LLM code agent + human review  
**Files to modify**:
- `src/skills/telemetry_logger.py` (add `log_execution_metrics()` function)

**Specification**:

```python
def log_execution_metrics(
    metrics: ExecutionMetrics,
    filepath: Path = Path("logs/execution_metrics.jsonl"),
    raise_on_error: bool = False
) -> bool:
    """Append execution metrics to immutable JSONL file.
    
    Args:
        metrics: ExecutionMetrics object to log.
        filepath: Path to JSONL file (created if missing).
        raise_on_error: If True, raise exception on I/O error. 
                        If False, log to stderr and continue (non-blocking).
    
    Returns:
        True if successfully logged; False if I/O error and raise_on_error=False.
    
    Side effects:
        - Creates logs/ directory if missing
        - Appends one JSON line to filepath
        - Flushes immediately (no buffering)
        - Logs I/O errors to stderr if raise_on_error=False
    
    Raises:
        ValueError: If metrics.validate() fails (malformed metrics)
        OSError: If write fails and raise_on_error=True
    
    Design notes:
        - Append-only: never modify or delete existing records
        - Non-blocking: if log write fails, don't crash skill execution
        - Atomic: use atomic write (write to temp file, then rename) to prevent corruption
    """
    
    # Validate metrics
    try:
        metrics.validate()
    except ValueError as e:
        raise ValueError(f"Metrics validation failed: {e}")
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Atomic append: write to temp file, then append to real file
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(metrics.to_json() + "\n")
            f.flush()  # Force immediate write
            os.fsync(f.fileno())  # Force sync to disk
        return True
    
    except OSError as e:
        if raise_on_error:
            raise
        else:
            import sys
            print(f"WARNING: Failed to log metrics: {e}", file=sys.stderr)
            return False
```

**Testing**:
```python
def test_log_execution_metrics():
    """Verify JSONL logging correctness."""
    tmpfile = Path(tempfile.mktemp(suffix=".jsonl"))
    
    # Log 10 metrics
    for i in range(10):
        metrics = ExecutionMetrics(...)
        log_execution_metrics(metrics, filepath=tmpfile, raise_on_error=True)
    
    # Verify file has 10 lines
    with open(tmpfile) as f:
        lines = f.readlines()
    assert len(lines) == 10, f"Expected 10 lines, got {len(lines)}"
    
    # Verify each line is valid JSON
    for line in lines:
        ExecutionMetrics.from_json(line)  # Should not raise
    
    tmpfile.unlink()
```

**Acceptance Criteria**:
- [ ] Metrics logged to JSONL file, one per line
- [ ] File auto-created if missing
- [ ] Append-only (no modification of existing records)
- [ ] Non-blocking failure (if log write fails, skill continues)
- [ ] Atomic writes (no partial/corrupted records even if process crashes)
- [ ] <1ms overhead per log call

---

### Item 3: Orchestrator Integration

**Effort**: 8 hours  
**Owner**: Human + LLM code agent  
**Files to modify**:
- `src/skills/git_push_autonomous.py` (orchestrator main function)

**Changes**:

1. **At execution start**:
   ```python
   def orchestrate_git_push(...) -> Result:
       execution_id = str(uuid.uuid4())
       timestamp_start = datetime.now(timezone.utc).isoformat()
       
       metrics = ExecutionMetrics(
           execution_id=execution_id,
           skill_name="git-push-autonomous",
           skill_version=__version__,
           timestamp_start=timestamp_start,
           operator="human",  # or get from config/env
           environment="prod",  # or get from config
       )
   ```

2. **Before each skill call**:
   ```python
   metrics.skill_path_in_dag += " -> rules-engine"
   step_start = time.time()
   
   try:
       rules_result = rules_engine.validate(config)
       step_end = time.time()
       # rules_engine is fast, typically <100ms
   except Exception as e:
       metrics.error_category = "rules-engine-failure"
       metrics.error_reason = str(e)
       metrics.execution_failed = True
       raise
   ```

3. **After each step, accumulate**:
   ```python
   metrics.total_latency_ms += int((step_end - step_start) * 1000)
   ```

4. **At execution end**:
   ```python
   metrics.timestamp_end = datetime.now(timezone.utc).isoformat()
   metrics.execution_succeeded = (final_result.success and not metrics.execution_failed)
   
   # Log atomically
   telemetry_logger.log_execution_metrics(metrics, raise_on_error=False)
   
   return final_result
   ```

5. **In exception handler**:
   ```python
   except Exception as e:
       metrics.timestamp_end = datetime.now(timezone.utc).isoformat()
       metrics.execution_failed = True
       metrics.error_reason = str(e)
       telemetry_logger.log_execution_metrics(metrics, raise_on_error=False)
       raise
   ```

**Testing**:
```python
def test_orchestrator_captures_metrics(tmp_path, monkeypatch):
    """Verify orchestrator logs metrics for successful and failed executions."""
    
    # Redirect logs to tmp directory
    metrics_file = tmp_path / "execution_metrics.jsonl"
    
    # Test 1: Successful execution
    result = git_push_autonomous.orchestrate(config, metrics_file=metrics_file)
    assert result.success
    assert metrics_file.exists()
    metrics = ExecutionMetrics.from_json(metrics_file.read_text().split('\n')[0])
    assert metrics.execution_succeeded
    assert metrics.total_latency_ms > 0
    
    # Test 2: Failed execution
    bad_config = Config(...)  # Invalid config
    result = git_push_autonomous.orchestrate(bad_config, metrics_file=metrics_file)
    assert not result.success
    lines = metrics_file.read_text().split('\n')
    assert len([l for l in lines if l]) >= 2  # At least 2 executions
```

**Acceptance Criteria**:
- [ ] Every orchestrator invocation produces one metrics record
- [ ] Metrics captured for success AND failure paths
- [ ] Latency measured correctly (within 10% of wall-clock time)
- [ ] Orchestrator latency increase <5% (metrics capture is cheap)
- [ ] All exceptions caught, metrics logged even on crash

---

### Item 4: Cost Tracking Implementation

**Effort**: 4 hours  
**Owner**: LLM code agent  
**Files to create/modify**:
- `src/skills/cost_calculator.py` (new file)

**Specification**:

```python
"""Cost calculation for skill executions.

Supports multiple pricing models:
- OpenAI: per-token pricing
- Azure Foundry: per-token or per-hour
- Free tiers: flat zero cost

Cost is calculated post-execution from token counts.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class PricingModel:
    """Pricing for a specific LLM."""
    model_name: str
    input_cost_per_1k_tokens: float  # $ per 1000 tokens
    output_cost_per_1k_tokens: float
    provider: str  # "openai", "azure-foundry", "free"

# Current pricing (update as vendor prices change)
PRICING_MODELS = {
    "gpt-4": PricingModel(
        model_name="gpt-4",
        input_cost_per_1k_tokens=0.03,  # $0.03 per 1K input tokens
        output_cost_per_1k_tokens=0.06,
        provider="openai"
    ),
    "gpt-3.5-turbo": PricingModel(
        model_name="gpt-3.5-turbo",
        input_cost_per_1k_tokens=0.0005,
        output_cost_per_1k_tokens=0.0015,
        provider="openai"
    ),
    "claude-3-opus": PricingModel(
        model_name="claude-3-opus",
        input_cost_per_1k_tokens=0.015,
        output_cost_per_1k_tokens=0.075,
        provider="anthropic"
    ),
    # Free tier models
    "free-tier-model": PricingModel(
        model_name="free-tier-model",
        input_cost_per_1k_tokens=0.0,
        output_cost_per_1k_tokens=0.0,
        provider="free"
    ),
}

def calculate_cost(
    model_name: str,
    tokens_input: int,
    tokens_output: int
) -> float:
    """Calculate cost for LLM invocation.
    
    Args:
        model_name: Model identifier (e.g., "gpt-4")
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
    
    Returns:
        Cost in USD, rounded to 8 decimal places
    
    Raises:
        ValueError: If model not found in pricing table
    """
    
    if model_name not in PRICING_MODELS:
        raise ValueError(f"Unknown model: {model_name}. Update PRICING_MODELS.")
    
    pricing = PRICING_MODELS[model_name]
    
    # Cost = (input_tokens / 1000) * input_price_per_1k + same for output
    input_cost = (tokens_input / 1000.0) * pricing.input_cost_per_1k_tokens
    output_cost = (tokens_output / 1000.0) * pricing.output_cost_per_1k_tokens
    
    total_cost = input_cost + output_cost
    
    # Round to 8 decimal places to avoid floating-point weirdness
    return round(total_cost, 8)

def get_cost_tier(model_name: str) -> str:
    """Determine pricing tier for a model."""
    pricing = PRICING_MODELS.get(model_name)
    if pricing:
        return "Free" if pricing.provider == "free" else "Paid"
    return "Unknown"
```

**Testing**:
```python
def test_cost_calculation():
    """Verify cost calculations match vendor pricing."""
    
    # Test GPT-4: 1000 input tokens, 500 output
    # Cost = (1000/1000)*0.03 + (500/1000)*0.06 = 0.03 + 0.03 = 0.06
    cost = calculate_cost("gpt-4", tokens_input=1000, tokens_output=500)
    assert cost == 0.06, f"Expected 0.06, got {cost}"
    
    # Test free tier
    cost = calculate_cost("free-tier-model", tokens_input=100000, tokens_output=50000)
    assert cost == 0.0, f"Free tier should cost 0, got {cost}"
```

**Acceptance Criteria**:
- [ ] Cost calculations match vendor docs
- [ ] Free tiers properly identified and zeroed
- [ ] Rounding handled correctly (8 decimal places)
- [ ] Pricing table easily updatable (no hardcoding in skill logic)

---

### Item 5: Free Tier Quota Tracking

**Effort**: 6 hours  
**Owner**: LLM code agent + human  
**Files to create/modify**:
- `src/skills/quota_tracker.py` (new file)

**Specification**:

```python
"""Track free tier quota consumption and availability.

Each external API has different quota:
- OpenAI: ~3.5M tokens/month free (varies by account)
- GitHub: 60 API calls/hour unauthenticated, 5000/hour authenticated
- Azure: varies by tier
- etc.

This module tracks against configured limits.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json

@dataclass
class QuotaLimit:
    """Quota limit for a specific API and period."""
    api_name: str  # "openai-gpt4", "github-rest", "azure-ai"
    limit: int  # Total quota (tokens or calls)
    period: str  # "day", "hour", "month"
    endpoint: str  # Where to check remaining quota (e.g., API header)

# Current quota limits (hardcoded from vendor docs; update quarterly)
QUOTA_LIMITS = {
    "openai-gpt4-daily": QuotaLimit(
        api_name="openai-gpt4",
        limit=100000,  # 100K tokens/day free tier estimate
        period="day",
        endpoint="openai-api-header"
    ),
    "github-rest-hourly": QuotaLimit(
        api_name="github-rest",
        limit=5000,  # Authenticated rate limit
        period="hour",
        endpoint="github-api-header"
    ),
}

@dataclass
class QuotaStatus:
    """Current quota consumption status."""
    api_name: str
    limit: int
    consumed_today: int
    remaining: int
    pct_used: float
    warning_level: str  # "GREEN" (<50%), "YELLOW" (50-80%), "RED" (>80%)
    days_until_reset: float
    
    def status_emoji(self) -> str:
        """Emoji for quick visual scanning."""
        return {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}.get(self.warning_level, "❓")

class QuotaTracker:
    """Track quota consumption against limits."""
    
    def __init__(self, state_file: Path = Path("logs/quota_state.json")):
        """Initialize quota tracker with persistent state."""
        self.state_file = state_file
        self._load_state()
    
    def _load_state(self):
        """Load quota state from disk."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {}
    
    def record_consumption(self, api_name: str, amount: int):
        """Record tokens/calls consumed against an API."""
        today = datetime.now().date().isoformat()
        
        if api_name not in self.state:
            self.state[api_name] = {}
        if today not in self.state[api_name]:
            self.state[api_name][today] = 0
        
        self.state[api_name][today] += amount
        self._save_state()
    
    def get_status(self, api_name: str) -> QuotaStatus:
        """Get current quota status for an API."""
        today = datetime.now().date().isoformat()
        limit_config = QUOTA_LIMITS.get(f"{api_name}-daily")
        
        consumed = self.state.get(api_name, {}).get(today, 0)
        remaining = max(0, limit_config.limit - consumed)
        pct_used = (consumed / limit_config.limit) * 100.0
        
        # Determine warning level
        if pct_used < 50:
            warning_level = "GREEN"
        elif pct_used < 80:
            warning_level = "YELLOW"
        else:
            warning_level = "RED"
        
        # Days until reset (assuming daily period)
        next_reset = datetime.now() + timedelta(days=1)
        days_until_reset = (next_reset.date() - datetime.now().date()).days
        
        return QuotaStatus(
            api_name=api_name,
            limit=limit_config.limit,
            consumed_today=consumed,
            remaining=remaining,
            pct_used=pct_used,
            warning_level=warning_level,
            days_until_reset=days_until_reset
        )
```

**Testing**:
```python
def test_quota_tracking(tmp_path):
    """Verify quota consumption is tracked correctly."""
    tracker = QuotaTracker(state_file=tmp_path / "quota_state.json")
    
    # Record consumption
    tracker.record_consumption("openai-gpt4", 10000)
    tracker.record_consumption("openai-gpt4", 5000)
    
    # Check status
    status = tracker.get_status("openai-gpt4")
    assert status.consumed_today == 15000
    assert status.pct_used == 15.0  # 15% of 100K
    assert status.warning_level == "GREEN"  # <50%
```

**Acceptance Criteria**:
- [ ] Quota consumption tracked per API per day
- [ ] Status accurately reflects 0-100% utilization
- [ ] Warning levels triggered at correct thresholds
- [ ] State persists across process restarts
- [ ] No performance impact (<1ms per call)

---

### Item 6: Baseline Computation Script

**Effort**: 4 hours  
**Owner**: LLM code agent  
**Files to create**:
- `scripts/compute_baselines.py` (new file)

**Specification**:

```python
#!/usr/bin/env python3
"""
Compute baseline metrics from JSONL execution log.

Baselines are statistical summaries of skill performance:
- Success rate, latency percentiles, cost, token usage, etc.

These baselines enable Phase 2a anomaly detection.
"""

from pathlib import Path
import json
import statistics
from collections import defaultdict
from ExecutionMetrics import ExecutionMetrics

def compute_baselines(metrics_file: Path) -> dict:
    """Compute baselines from execution metrics.
    
    Args:
        metrics_file: Path to execution_metrics.jsonl
    
    Returns:
        Dict of baselines keyed by skill_name
        
    Example output:
        {
            "git-push-autonomous": {
                "sample_size": 245,
                "period": "2026-02-07T00:00:00Z to 2026-02-14T23:59:59Z",
                "success_rate": 0.98,
                "success_rate_std_dev": 0.02,
                "latency_p50_ms": 3200,
                "latency_p95_ms": 8500,
                "latency_p99_ms": 12000,
                "latency_mean_ms": 3800,
                "latency_std_dev_ms": 2100,
                "cost_mean_usd": 0.0105,
                "cost_std_dev_usd": 0.0008,
                "tokens_mean": 350,
            }
        }
    """
    
    skills = defaultdict(list)
    
    # Parse JSONL
    with open(metrics_file) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                metrics = ExecutionMetrics.from_json(line)
                skills[metrics.skill_name].append(metrics)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipped malformed line: {e}")
    
    baselines = {}
    
    for skill_name, executions in skills.items():
        if not executions:
            continue
        
        # Success rate
        successes = [ex for ex in executions if ex.execution_succeeded]
        success_rate = len(successes) / len(executions)
        
        # Latencies
        latencies = [ex.total_latency_ms for ex in executions if ex.total_latency_ms]
        if latencies:
            latencies.sort()
            latency_p50 = latencies[len(latencies) // 2]
            latency_p95 = latencies[int(len(latencies) * 0.95)]
            latency_p99 = latencies[int(len(latencies) * 0.99)]
            latency_mean = statistics.mean(latencies)
            latency_std = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        # Costs
        costs = [ex.cost_usd for ex in executions]
        cost_mean = statistics.mean(costs) if costs else 0.0
        cost_std = statistics.stdev(costs) if len(costs) > 1 else 0.0
        
        # Tokens
        tokens = [ex.tokens_used for ex in executions if ex.tokens_used > 0]
        tokens_mean = statistics.mean(tokens) if tokens else 0
        
        baselines[skill_name] = {
            "sample_size": len(executions),
            "period": f"{executions[0].timestamp_start} to {executions[-1].timestamp_end}",
            "success_rate": round(success_rate, 4),
            "latency_p50_ms": int(latency_p50),
            "latency_p95_ms": int(latency_p95),
            "latency_p99_ms": int(latency_p99),
            "latency_mean_ms": int(latency_mean),
            "latency_std_dev_ms": int(latency_std),
            "cost_mean_usd": round(cost_mean, 8),
            "cost_std_dev_usd": round(cost_std, 8),
            "tokens_mean": int(tokens_mean),
        }
    
    return baselines

if __name__ == "__main__":
    import sys
    
    metrics_file = Path("logs/execution_metrics.jsonl")
    if not metrics_file.exists():
        print(f"Error: {metrics_file} not found")
        sys.exit(1)
    
    baselines = compute_baselines(metrics_file)
    
    # Print results
    for skill_name, baseline in baselines.items():
        print(f"\n=== {skill_name} ===")
        for key, value in baseline.items():
            print(f"  {key}: {value}")
    
    # Save to JSON
    output_file = Path("logs/baselines.json")
    with open(output_file, "w") as f:
        json.dump(baselines, f, indent=2)
    
    print(f"\nBaselines saved to {output_file}")
```

**Testing**:
```bash
# Generate test metrics
py scripts/generate_test_metrics.py --count 100

# Compute baselines
py scripts/compute_baselines.py

# Verify output
cat logs/baselines.json
```

**Acceptance Criteria**:
- [ ] Reads JSONL without corruption
- [ ] Computes accurate percentiles (manual check against sample data)
- [ ] Baseline stability (recomputing same data gives ±1% variation)
- [ ] Output JSON valid and human-readable

---

## Integration Checklist

Before July 31, 2026, verify:

- [ ] **Week 1 (Feb 14-20)**: ExecutionMetrics + telemetry logger working
  - [ ] 10+ manual executions logged
  - [ ] Each log entry valid JSON
  - [ ] No corruption on process restart
  
- [ ] **Week 2 (Feb 21-27)**: Orchestrator integration complete
  - [ ] All skill executions auto-capture metrics
  - [ ] git-push and blog skills both logging
  - [ ] Latency measurements within 10% accuracy
  
- [ ] **Week 3 (Feb 28-Mar 6)**: Cost tracking + quota monitoring
  - [ ] Cost calculations validate against vendor docs
  - [ ] Quota tracking reflects actual consumption
  - [ ] Zero false positives on quota alerts
  
- [ ] **Week 4 (Mar 7-14)**: Baseline computation + review
  - [ ] 1000+ execution records logged
  - [ ] Baselines computed and reviewed
  - [ ] Ready for Phase 2a anomaly detection

---

## Success Criteria (End of Phase 1b-now)

| Criterion | Target | Owner | Verification |
|-----------|--------|-------|--------------|
| Metrics logged | 100% of executions | Engineer | Query logs/execution_metrics.jsonl |
| Data fidelity | Zero corruption | Engineer | Round-trip serialization test |
| Cost accuracy | ±5% vs vendor | Engineer | Spot-check against invoices |
| Baseline stability | ±2% week-to-week | Engineer | Recompute, compare deltas |
| Performance impact | <1% overhead | Engineer | Compare latency before/after |
| Skill reliability | 100% logging regardless of result | Engineer | Test pass/fail scenarios |
| Documentation | All code documented | Engineer | 100% docstring coverage |

---

## Questions to Drive Design

1. **Free tier quota limits**: Where do we get authoritative numbers? Hardcode and update quarterly, or query APIs?
   - *Recommendation*: Hardcode with version date. Update quarterly as part of quarterly review.

2. **Cost attribution**: If orchestrator calls multiple skills, who gets blamed for the cost?
   - *Recommendation*: Log cost per skill. Aggregate at orchestrator level. 

3. **Metrics persistence format**: JSONL (append-only), CSV, database, or something else?
   - *Recommendation*: JSONL for now. CSV export for analysis. Optional database in Phase 2b.

4. **Baseline frequency**: Compute daily, weekly, or on-demand?
   - *Recommendation*: Weekly, frozen at week start (prevents chasing moving target).

5. **Attribution of multi-step operations**: Blog publish involves 5+ steps. When is it "complete"?
   - *Recommendation*: Define SLO per skill. Blog complete when Vercel deploy confirms.

---

**Document Status**: Ready for implementation.  
**Next Review**: 2026-02-21 (after Week 1 delivery).

