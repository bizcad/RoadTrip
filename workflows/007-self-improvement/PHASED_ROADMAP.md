# Self-Improvement Roadmap: Phased Implementation

**Version**: 1.0  
**Status**: Foundation  
**Last Updated**: 2026-02-14  
**Purpose**: Map self-improvement development to existing RoadTrip phases with specific deliverables and integration points

---

## Executive Summary

Self-improvement is **not a separate project**—it's integrated into your existing Phase 1b/2a/2b/2c roadmap:

- **Phase 1b-now**: Data collection infrastructure (metrics capture, persistence)
- **Phase 2a**: Baseline establishment, anomaly detection, notification system
- **Phase 2b**: Optimization engine, guided ranking, A/B testing framework
- **Phase 2c**: Bounded autonomous routing changes, skill parameter tuning
- **Phase 3+**: Skill modification, new skill proposal, full ecosystem learning

---

## PHASE 1b: Foundation (Now → End of March 2026)

**Goal**: Collect rich execution metrics for every skill invocation. Zero optimization logic yet. Foundation for everything that follows.

### 1b.1: Metrics Data Model

**Deliverable**: Update `src/skills/models.py` with `ExecutionMetrics` dataclass

```python
@dataclass
class ExecutionMetrics:
    """Metrics captured for every skill execution."""
    
    # Execution identity
    execution_id: str  # UUID
    skill_name: str
    skill_version: str
    orchestrator_version: str
    timestamp_start: datetime
    timestamp_end: datetime
    operator: str  # "human" or system/agent name
    environment: str  # "local", "staging", "prod"
    
    # Reliability
    execution_succeeded: bool
    execution_failed: bool
    error_category: Optional[str]  # "Security", "Auth", "Network", "Timeout", "Logic"
    error_code: Optional[int]
    error_reason: Optional[str]
    
    # Performance
    total_latency_ms: int
    wall_clock_time_ms: int
    
    # Cost
    tokens_used: int
    tokens_input: int
    tokens_output: int
    cost_usd: float
    cost_tier: str  # "Free", "Standard", "Premium"
    
    # Quota tracking
    free_tier_quota_used_today: int
    free_tier_quota_remaining: int
    free_tier_quota_pct_used: float
    
    # Quality
    output_correct: bool
    confidence_score: float
    decision_made: Optional[str]  # "APPROVE", "BLOCK", etc.
    
    # Metadata
    input_hash: str  # SHA256
    output_hash: str
    skill_path_in_dag: str  # "orchestrator -> rules-engine -> auth-validator -> execution"
    
    def to_json(self) -> str:
        """Serialize to JSON for JSONL append."""
        return json.dumps(asdict(self), default=str)
```

**Success Criteria**:
- [ ] Dataclass compiles without errors
- [ ] All mandatory fields present (no Optional fields in critical section)
- [ ] Type hints complete
- [ ] Docstrings on all fields
- [ ] Integration test: can serialize/deserialize 100 times without loss

### 1b.2: Telemetry Logger Skill Enhancement

**Deliverable**: Update `src/skills/telemetry_logger.py` to write metrics to JSONL

```python
def log_execution_metrics(metrics: ExecutionMetrics, filepath: Path = Path("logs/execution_metrics.jsonl")):
    """Append execution metrics to immutable JSONL file.
    
    Args:
        metrics: ExecutionMetrics object from skill execution
        filepath: Where to append (default: logs/execution_metrics.jsonl)
    
    Returns:
        Success: True if logged, False if I/O error (but doesn't block execution)
    
    Side effect:
        Appends one line (JSON) to JSONL file
    """
```

**Implementation notes**:
- Append-only: never modify existing lines
- Non-blocking: if log write fails, don't crash skill execution (log to stderr, continue)
- Buffering: flush immediately (don't batch; we want real-time data)
- Path creation: auto-create `logs/` directory if missing

**Success Criteria**:
- [ ] 1000 consecutive metrics logged without corruption
- [ ] Each line valid JSON (can parse individually)
- [ ] Metrics persisted after process restart
- [ ] Log append takes <1ms (negligible overhead)

### 1b.3: Orchestrator Integration

**Deliverable**: Update `src/skills/git_push_autonomous.py` orchestrator to:
- Capture timestamp, skill_version, environment before each skill call
- Capture outcomes, latency, cost after each skill call
- Build ExecutionMetrics object
- Pass to telemetry_logger.log_execution_metrics()

**Pseudo-code**:
```python
def orchestrate_git_push(config: GitPushConfig, operator: str = "human") -> Result:
    execution_id = str(uuid.uuid4())
    timestamp_start = datetime.now(timezone.utc)
    
    try:
        # PRE-EXECUTION
        rules_result = rules_engine.validate(config)
        
        # CAPTURE METRICS
        metrics = ExecutionMetrics(
            execution_id=execution_id,
            skill_name="git-push-autonomous",
            skill_version=__version__,
            timestamp_start=timestamp_start,
            timestamp_end=None,  # Fill after
            operator=operator,
            execution_succeeded=False,  # Update after
            ...
        )
        
        # EXECUTION
        if rules_result.decision == "APPROVE":
            auth_result = auth_validator.check_git_credentials()
            if auth_result.authenticated:
                push_result = execute_git_push()
                metrics.execution_succeeded = push_result.success
        
        # POST-EXECUTION
        metrics.timestamp_end = datetime.now(timezone.utc)
        metrics.total_latency_ms = int((metrics.timestamp_end - timestamp_start).total_seconds() * 1000)
        
        # LOG
        telemetry_logger.log_execution_metrics(metrics)
        
        return push_result
    
    except Exception as e:
        metrics.execution_failed = True
        metrics.error_category = classify_error(e)
        metrics.timestamp_end = datetime.now(timezone.utc)
        telemetry_logger.log_execution_metrics(metrics)
        raise
```

**Success Criteria**:
- [ ] Every skill execution produces one metrics record
- [ ] Metrics JSON valid and parseable
- [ ] Orchestrator latency increase <5% (metrics capture is cheap)
- [ ] No skill failures due to metrics capture logic

### 1b.4: Cost Tracking Implementation

**Deliverable**: Add cost calculation per skill execution

For **OpenAI/GPT models**:
```python
def calculate_openai_cost(model: str, tokens_input: int, tokens_output: int) -> float:
    """Calculate cost for OpenAI API call."""
    pricing = {
        "gpt-4": {"input": 0.00003, "output": 0.00006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        # ... more models
    }
    cost = tokens_input * pricing[model]["input"] + tokens_output * pricing[model]["output"]
    return round(cost, 8)
```

For **Azure/Foundry models**: Use invoice/usage API if available; otherwise estimate  
For **free tier models**: cost_usd = 0.0, but set cost_tier = "Free" for tracking  
For **non-LLM skills** (rules-engine, auth-validator): cost_usd = 0.0

**Success Criteria**:
- [ ] All skills populate cost_usd field correctly
- [ ] Free tier operations marked as free (not missing)
- [ ] Cost calculations match vendor pricing docs
- [ ] Cumulative daily cost matches expected usage

### 1b.5: Free Tier Quota Tracking

**Deliverable**: Monitor free tier consumption and alert

```python
def track_free_tier_quota(config: QuotaConfig) -> QuotaStatus:
    """Check free tier quota remaining for each external API."""
    
    status = {
        "openai_gpt4_daily_limit": 100000,  # tokens
        "openai_gpt4_remaining_today": 95500,  # from API or log
        "openai_gpt4_pct_used_today": 4.5,
        "github_api_remaining": 4950,  # from API rate limit headers
        "github_api_limit": 5000,
        "github_api_pct_used": 1.0,
        "warning_level": "GREEN",  # RED if >80%, YELLOW if >50%
    }
    
    return status
```

**Integration**:
- Query quota status before each skill execution
- Log quota status in ExecutionMetrics
- Alert if any quota >80%
- Alert if any quota exhausted

**Success Criteria**:
- [ ] Daily quota consumption tracked accurately
- [ ] Alerts sent if quota >80%
- [ ] Alerts sent if quota exhausted mid-day
- [ ] Operator can see "X days until quota resets"

### 1b.6: Baseline Metrics Computation

**Deliverable**: Compute baseline metrics from first week of data

```python
def compute_baselines(metrics_file: Path, window_days: int = 7) -> BaselineMetrics:
    """Compute baseline metrics for each skill from historical data."""
    
    baselines = {
        "skill": "git-push-autonomous",
        "period": "2026-02-07 to 2026-02-14",
        "sample_size": 245,
        "success_rate": 0.98,
        "latency_p50_ms": 3200,
        "latency_p95_ms": 8500,
        "latency_p99_ms": 12000,
        "avg_tokens_per_execution": 350,
        "avg_cost_per_execution": 0.0105,
        "cost_tier_breakdown": {"Free": 180, "Standard": 65},
    }
    
    return baselines
```

**Integration**: Compute once per week; used in Phase 2a for anomaly detection

**Success Criteria**:
- [ ] Baseline computed from first 100+ executions
- [ ] Baselines stable (don't change >5% week-to-week if skill unchanged)
- [ ] Baselines exported to CSV for operator review

---

## PHASE 2a: Monitoring & Anomaly Detection (Q1 2026 → Q2 2026)

**Goal**: Establish baseline behavior, detect anomalies, enable human-guided optimization.

### 2a.1: Anomaly Detection Engine

**Deliverable**: Real-time anomaly scoring

```python
def detect_anomalies(execution: ExecutionMetrics, baseline: BaselineMetrics) -> AnomalyScore:
    """Detect deviations from baseline behavior."""
    
    # Success rate anomaly
    success_zscore = (execution.execution_succeeded - baseline.success_rate) / baseline.success_std_dev
    
    # Latency anomaly (if latency > p95 baseline, it's unusual)
    latency_percentile = percentile_from_sample(execution.total_latency_ms, baseline.latency_distribution)
    
    # Cost anomaly
    cost_zscore = (execution.cost_usd - baseline.cost_mean) / baseline.cost_std_dev
    
    # Quota consumption anomaly
    quota_pct_rate = execution.free_tier_quota_pct_used / execution.tokens_used
    quota_rate_zscore = zscore(quota_pct_rate, baseline.quota_rate_mean, baseline.quota_rate_std_dev)
    
    # Composite anomaly score
    anomaly_score = max(abs(success_zscore), latency_percentile_zscore, abs(cost_zscore), abs(quota_rate_zscore))
    
    return AnomalyScore(
        is_anomaly=(anomaly_score > threshold=3.0),
        score=anomaly_score,
        deviations={
            "success_zscore": success_zscore,
            "latency_percentile": latency_percentile,
            "cost_zscore": cost_zscore,
        }
    )
```

**Success Criteria**:
- [ ] Anomaly detection triggers on known anomalies (<5% false negative)
- [ ] <5% false positive rate on normal operations
- [ ] Real-time (detects within 1 execution, not waiting for aggregation)

### 2a.2: Notification System

**Deliverable**: Send alerts to operator on anomalies/failures

**Channels**:
- **Email (daily digest)**: Summary of anomalies from last 24h
- **Slack webhook (real-time)**: Critical anomalies (success_rate drop >10%, quota exhaustion imminent)
- **Log file**: Machine-readable event log (`logs/anomalies.jsonl`)
- **Dashboard (optional)**: Real-time visualization

**Alert types**:
| Event | Severity | Trigger | Action |
|-------|----------|---------|--------|
| Success rate drops <95% | 🔴 Critical | 5 consecutive failures | Notify + auto-investigate |
| Free tier quota >80% | 🟠 Warning | Quota consumption | Daily email digest |
| Free tier quota >95% | 🔴 Critical | Quota consumption | Real-time Slack alert |
| Latency p95 >2x baseline | 🟠 Warning | Latency anomaly | Daily email digest |
| Cost spike >2x baseline | 🟠 Warning | Cost anomaly | Daily email digest |
| Fingerprint mismatch | 🔴 Critical | Security anomaly | Real-time Slack alert |
| Vendor API degraded | 🟠 Warning | Vendor status | Real-time Slack + email |
| Quota exhausted TODAY | 🔴 Critical | Hard limit hit | Real-time Slack alert + pause skill |

**Success Criteria**:
- [ ] Operator receives 3-5 actionable notifications per week
- [ ] <10% noise/false alerts
- [ ] Alerts actionable (not just "something is different")

### 2a.3: Integrate with Fingerprinting (Phase 2a proper)

**Deliverable**: Pre-execution fingerprint verification for skills

Before running a skill:
- Compute fingerprint of current skill code (SHA256)
- Compare to baseline fingerprint from deployment
- If mismatch: flag (skill was modified), proceed with caution
- Log fingerprint in ExecutionMetrics

*See [Principles-and-Processes.md](../../docs/Principles-and-Processes.md) Phase 2a for full fingerprinting spec.*

### 2a.4: Weekly Review Process

**Deliverable**: Structured review cadence for operator

**Weekly review agenda** (30 min):
1. Anomalies: Review last week's alerts, investigate root causes
2. Baselines: Are baselines still valid? Any drift?
3. Cost: Did we stay within budget? Quota status?
4. Performance: Any latency regressions?
5. Proposals: System ready to propose optimizations (Phase 2b)?

**Output**: Operator feedback captured in `logs/weekly_review_YYYY-WXX.md`

---

## PHASE 2b: Guided Optimization (Q2 2026 → Q3 2026)

**Goal**: System proposes optimizations, operator approves/rejects, approved changes are deployed and monitored.

### 2b.1: Optimization Engine

**Deliverable**: Analyze metrics, propose improvements

**Analysis patterns**:

1. **Skill ranking by reliability**
   ```
   SELECT skill_name, AVG(execution_succeeded) as success_rate
   FROM execution_metrics
   WHERE timestamp > now() - INTERVAL 7 days
   GROUP BY skill_name
   ORDER BY success_rate DESC
   ```
   → If skill A has 99% success and skill B has 95%, prefer A when both are applicable

2. **Cost-by-skill analysis**
   ```
   SELECT skill_name, SUM(cost_usd), COUNT(*), SUM(cost_usd)/COUNT(*) as avg_cost
   FROM execution_metrics
   WHERE cost_tier = 'Free'
   GROUP BY skill_name
   ORDER BY SUM(cost_usd) DESC
   ```
   → If skill A is free but slower, and skill B is paid but faster, compare ROI

3. **Latency percentiles by time-of-day**
   ```
   SELECT EXTRACT(HOUR FROM timestamp_start) as hour, 
          PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_latency_ms)
   FROM execution_metrics
   GROUP BY hour
   ORDER BY hour
   ```
   → If latency spikes at 2-3 PM, maybe schedule intensive operations off-peak

4. **Free tier quota utilization**
   ```
   SELECT DATE(timestamp_end), 
          MAX(free_tier_quota_pct_used),
          AVG(free_tier_quota_remaining)
   FROM execution_metrics
   WHERE cost_tier = 'Free'
   GROUP BY DATE(timestamp_end)
   ```
   → If consistently using 40% of daily quota, we have runway for 2.5 days at this rate

### 2b.2: Ranking Strategies

**Deliverable**: Score candidate routing strategies

Define alternative DAG paths and compare:

```python
class RoutingStrategy:
    name: str  # "conservative", "cost-optimized", "speed-optimized"
    description: str
    expected_success_rate: float
    expected_cost: float
    expected_latency_ms: float
    reasoning: str
```

**Example**:
```python
strategies = [
    RoutingStrategy(
        name="current_deployment",
        description="rules-engine -> auth-validator -> executor",
        expected_success_rate=0.98,
        expected_cost=0.0105,
        expected_latency_ms=3500,
        reasoning="Conservative, proven in production"
    ),
    RoutingStrategy(
        name="candidate_A",
        description="rules-engine -> SKIP auth-validator -> executor",
        expected_success_rate=0.97,  # Slightly lower risk
        expected_cost=0.0095,  # 10% cheaper (skip a network call)
        expected_latency_ms=2800,  # 20% faster
        reasoning="Remove auth-validator if rule-engine already covers it"
    ),
    RoutingStrategy(
        name="candidate_B",
        description="rules-engine -> auth-validator -> executor (v2)",
        expected_success_rate=0.99,  # Improved version
        expected_cost=0.0105,
        expected_latency_ms=3500,
        reasoning="New version of auth-validator has better caching"
    ),
]

# Score each strategy
for strategy in strategies:
    score = RewardFunction.score(
        reliability=strategy.expected_success_rate,
        cost=strategy.expected_cost,
        speed=strategy.expected_latency_ms
    )
    print(f"{strategy.name}: score={score:.3f}")
```

### 2b.3: A/B Testing Framework

**Deliverable**: Deploy candidate strategies to small % of traffic, measure outcomes

```python
class ExperimentConfig:
    experiment_id: str  # UUID
    name: str  # "speed-optimization-v1"
    control_strategy: RoutingStrategy  # Current deployment
    treatment_strategy: RoutingStrategy  # Candidate
    traffic_split: float  # 0.0-1.0, e.g., 0.1 = route 10% to treatment
    duration_days: int  # How long to run experiment
    success_criteria: Dict[str, float]  # e.g., {"success_rate": 0.95, "cost_usd": 0.01}
```

**Implementation**:
- Operator specifies experiment config
- Orchestrator randomly classifies each invocation (90% control, 10% treatment)
- Both paths execute independently (not A/B, but parallel execution)
- Results logged separately
- After duration expires, compare outcomes
- If treatment > control on reward function, promote treatment to default

**Success Criteria**:
- [ ] At least 5 experiments run in Phase 2b
- [ ] System proposes 2-3 optimizations per week
- [ ] Operator approves 50%+ of proposals
- [ ] Approved optimizations measured improvement (success_rate, cost, or latency)

### 2b.4: Approval & Deployment Workflow

**Deliverable**: Structured approval process

1. **System proposes optimization**
   ```
   Proposal: Move to candidate_A strategy
   Rationale: 20% faster (-700ms), 10% cheaper (-0.001 USD), 
              same reliability (delta=-0.1% within margin). 
              Risk: low (auth-validator removal validated in 100-execution sandbox test)
   Operator approval: [APPROVE] [REJECT] [DEFER]
   ```

2. **Operator approves** (or system auto-approves if within guardrails)

3. **Change deployed**
   - Update orchestrator config or routing decision
   - Deploy to staging first (if applicable)
   - Monitor metrics for 1 hour
   - If success_rate doesn't drop >5%, proceed to prod

4. **Monitor for regression**
   - Track metrics closely for 24 hours
   - If anomaly detected, auto-rollback + notify operator
   - If success, archive experiment results

5. **Retrospective**
   - Document what worked, what didn't
   - Update baselines
   - Loop back to optimization engine

---

## PHASE 2c: Bounded Autonomous Routing (Q3 2026 → Q4 2026)

**Goal**: System makes smart routing decisions autonomously, within guardrails. Operator notified, can override.

### 2c.1: Guardrail Definition

**Deliverable**: Define bounds on autonomous changes

```python
class AutonomyGuardrails:
    max_success_rate_reduction: float = 0.02  # Don't reduce reliability >2%
    min_reliability_threshold: float = 0.95  # Never go below 95% success
    max_cost_increase: float = 1.1  # Don't increase cost >10%
    max_latency_increase: float = 1.2  # Don't increase latency >20%
    cooldown_between_changes_hours: int = 6  # Wait 6 hours between routing changes
    max_consecutive_failures_before_revert: int = 3  # Auto-revert after 3 failures
    approval_required_for_new_skills: bool = True  # Always require human approval for new skills
```

### 2c.2: Autonomous Decision Engine

**Deliverable**: System decides routing without operator approval (if within guardrails)

```python
def make_routing_decision(
    available_strategies: List[RoutingStrategy],
    current_metrics: Dict[str, float],
    guardrails: AutonomyGuardrails
) -> Tuple[RoutingStrategy, ApprovalStatus]:
    """
    Select best strategy within guardrails.
    
    Returns:
        (selected_strategy, approval_status=AUTO or DEFERRED)
    """
    
    best_score = None
    best_strategy = None
    approval_required = False
    
    for strategy in available_strategies:
        # Check guardrails
        if not violates_guardrails(strategy, current_metrics, guardrails):
            new_score = RewardFunction.score(strategy)
            if new_score > best_score:
                best_score = new_score
                best_strategy = strategy
        else:
            approval_required = True  # This strategy violates guardrails
    
    if best_strategy.name == current_strategy.name:
        return best_strategy, ApprovalStatus.NO_CHANGE  # No improvement
    
    if approval_required:
        return best_strategy, ApprovalStatus.DEFERRED  # Need operator approval
    else:
        return best_strategy, ApprovalStatus.AUTO_APPROVED  # Within guardrails
```

### 2c.3: Rollback Mechanism

**Deliverable**: Automatic rollback if metrics degrade

```python
def monitor_and_rollback_if_needed(
    deployed_strategy: RoutingStrategy,
    baseline_metrics: BaselineMetrics,
    max_consecutive_failures: int = 3
) -> RollbackDecision:
    """
    Monitor deployed strategy for regressions.
    If success rate drops too much, auto-rollback.
    """
    
    recent_executions = get_last_n_executions(n=max_consecutive_failures)
    failure_count = sum(1 for ex in recent_executions if not ex.execution_succeeded)
    
    if failure_count >= max_consecutive_failures:
        return RollbackDecision(
            action="ROLLBACK",
            reason=f"{failure_count} consecutive failures",
            notify_operator=True
        )
    
    return RollbackDecision(action="CONTINUE")
```

### 2c.4: Operator Notification & Override

**Deliverable**: Operator aware of all autonomous changes, can override

Every autonomous routing change triggers:
- Notification email: "System changed routing to strategy X. Reason: Y. New metrics: Z."
- Log entry in `logs/autonomous_decisions.jsonl`
- Operator can override: "Revert to previous strategy"

---

## PHASE 3: Skill Self-Modification (Q4 2026+)

**Goal**: System modifies existing skills, proposes new skills, vets them, deploys them.

### 3.1: Skill Parameter Tuning

**Example**: Rules engine has a size threshold for "large file". Currently 1MB. Metrics show 10% of blocks are on large files that could be processed. System proposes lowering threshold to 2MB, tests it, measures outcome.

### 3.2: New Skill Proposal

**Example**: System observes that 30% of git operations are re-pushes (same commit). System proposes new skill "deduplication-filter" that detects and skips re-pushes. System writes code, generates tests, submits for human review.

### 3.3: Skill Vetting Pipeline

Before deploying a proposed skill:
1. **Static analysis**: Bandit, type checking, secret detection
2. **Sandbox testing**: Run on 1000 synthetic test cases
3. **Fingerprinting**: Compute security/capability hash
4. **Human code review**: Operator or designated reviewer
5. **Staged rollout**: Deploy to 10% of traffic, monitor
6. **Promotion**: If metrics good, promote to 100%

---

## Integration Timeline

```
NOW (2026-02-14)
  ├─ Phase 1b-now: Metrics capture infrastructure
  │   ├─ Week 1: ExecutionMetrics dataclass + telemetry logging
  │   ├─ Week 2: Orchestrator integration (capture metrics for all skills)
  │   ├─ Week 3: Cost tracking + free tier quota monitoring
  │   └─ Week 4: Baseline computation
  │
  ├─ 2026-03-31: Phase 1b complete, 1000+ execution records
  │
  ├─ 2026-04-30: Phase 2a complete (anomaly detection, baseline established)
  │
  ├─ 2026-06-30: Phase 2b complete (optimization engine, 5+ proposals tested)
  │
  ├─ 2026-09-30: Phase 2c complete (bounded autonomy working, operator trust high)
  │
  └─ 2026-12-31: Phase 3 beginning (skill self-modification engine)
```

---

## Success Metrics

| Milestone | Criterion | Owner | Check-in |
|-----------|-----------|-------|----------|
| **1h after Phase 1b-now start** | Configuration complete, first metric logged | Engineer | Daily standup |
| **2 weeks** | 100 execution records logged with zero corruption | Engineer | Weekly review |
| **1 month (Phase 1b-end)** | 1000+ records logged; baselines computed; zero production impact | Engineer | Monthly review |
| **Phase 2a-end** | Operator receives 1+ actionable optimization per week | System architect | Weekly email digest |
| **Phase 2b-end** | Operator approves 50%+ of proposed optimizations | Operator + architect | Monthly reflection |
| **Phase 2c-end** | System makes 10+ autonomous changes confidently; operator trust > 8/10 | Operator survey | Monthly review |
| **Phase 3-end** | New skill proposed & deployed successfully | System architect | Quarterly |

---

## Risks & Mitigations (Per Phase)

### Phase 1b Risks
| Risk | Mitigation |
|------|-----------|
| Metrics overhead slows skills | Capture metrics async; benchmark overhead <1% |
| Metrics corruption or loss | Append-only JSONL; daily backups; integrity checks |
| Cost tracking inaccuracies | Validate against vendor invoices; human review |

### Phase 2a Risks
| Risk | Mitigation |
|------|-----------|
| Too many alerts; operator fatigue | Filter alerts by severity; weekly digest summarization |
| False anomalies on normal variation | Set thresholds conservatively; require persistence (not one-off) |
| Baseline instability | Freeze baseline for first 2 weeks; only update weekly |

### Phase 2b Risks
| Risk | Mitigation |
|------|-----------|
| Operator ignores proposals | Ensure proposals are well-reasoned; demonstrate ROI with data |
| Wrong winners in A/B test | Run sufficiently long (≥100 samples); monitor for confounds |

### Phase 2c Risks
| Risk | Mitigation |
|------|-----------|
| Runaway optimization | Guardrails enforced in code; rollback on anomaly; operator override |
| Cascading failures | Cooldown periods between changes; auto-revert trigger low |

### Phase 3 Risks
| Risk | Mitigation |
|------|-----------|
| Skill modification goes wrong | Sandbox testing; code review; staged rollout; easy revert |
| New skills interact badly | Isolation + integration tests; monitor metrics closely |

---

## Open Questions (For You to Guide)

1. **Cost tracking fidelity**: Should Phase 1b track actual Azure spend (via APIs) or estimate from token counts?
   - *Tradeoff*: API calls add latency/cost, but estimates can be inaccurate

2. **Quota monitoring frequency**: Poll free tier quota every execution, hourly, or daily?
   - *Tradeoff*: Frequent polling catches problems early but adds calls; rare polling is cheap but slower

3. **Notification channels**: Email (batch), Slack (real-time), or both?
   - *Recommendation*: Both. Email for weekly digest, Slack for critical alerts.

4. **Operator approval SLA**: How fast should operator review proposals?
   - *Recommendation*: Weekly standup is fine for Phase 2b; can automate later if patterns emerge.

5. **Skill versioning**: Should Phase 2c/3 create new skill versions, or modify existing?
   - *Recommendation*: Use semantic versioning. Parameter tuning = patch bump. New features = minor/major.

---

**Document Status**: Ready for feedback. Will evolve based on Phase 1b operational experience.  
**Next Review**: After Phase 1b data infrastructure deployed.

