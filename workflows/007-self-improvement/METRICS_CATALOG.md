# Comprehensive Metrics Catalog for Self-Improving Skills

**Version**: 1.0  
**Status**: Foundation (to be expanded with operational data)  
**Last Updated**: 2026-02-14  
**Purpose**: Define all measurable dimensions of skill behavior, execution, and outcomes

---

## Overview & Taxonomy

Metrics are organized by **category** (what they measure), **priority** (reward function weight), and **collection point** (where/when captured).

**Three measurement moments**:
1. **Pre-execution**: Input validation, resource availability, estimated cost
2. **During execution**: Active resource usage, progress milestones
3. **Post-execution**: Outcomes, actual costs, duration, flags

---

## Category A: Reliability Metrics (α₁ = 0.50 weight)

### A1: Success & Failure Signals

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `execution_succeeded` | Operation completed as intended | Boolean | true/false | Post-exec | **Critical** |
| `execution_failed` | Operation completed but with errors | Boolean | true/false | Post-exec | **Critical** |
| `partial_success` | Some objectives achieved, not all | Boolean | true/false | Post-exec | High |
| `error_recoverable` | Error can be fixed by retry or fallback | Boolean | true/false | Post-exec | High |
| `error_permanent` | Error requires human intervention | Boolean | true/false | Post-exec | High |
| `timeout_occurred` | Execution exceeded max allowed time | Boolean | true/false | During | High |
| `resource_exhausted` | Execution hit resource (memory, API quota) limit | Boolean | true/false | During | High |
| `fallback_used` | Orchestrator fell back to conservative skill | Boolean | true/false | Post-exec | Medium |

### A2: Failure Classification

| Metric | Description | Type | Categories | Collection | Priority |
|--------|-------------|------|-----------|-----------|----------|
| `failure_category` | Type of failure encountered | Enum | Security, Auth, Validation, Network, Timeout, Logic, Unknown | Post-exec | High |
| `failure_reason` | Human-readable explanation | String | Free text | Post-exec | Medium |
| `failure_code` | Structured exit code | Int | 0-255 | Post-exec | High |
| `error_chain_length` | Number of errors before final state | Int | Count | Post-exec | Medium |

### A3: Reliability Aggregates (Time-Series)

| Metric | Description | Params | Collection | Priority |
|--------|-------------|--------|-----------|----------|
| `success_rate_1h` | % of executions that succeeded (last 1 hour) | Rolling window | Post-exec (continually) | **Critical** |
| `success_rate_1d` | % of executions that succeeded (last 24 hours) | Rolling window | Post-exec (daily) | **Critical** |
| `success_rate_7d` | % of executions that succeeded (last 7 days) | Rolling window | Post-exec (weekly) | High |
| `mean_time_between_failures` | Average time between consecutive failures | Statistic | Hours | Post-exec (rolling) | High |
| `failure_recovery_time` | Average time from failure to recovery | Statistic | Minutes | Post-exec (rolling) | Medium |
| `consecutive_failures_max` | Longest streak of failures (current session) | Integer | Count | Post-exec (per-session) | High |

---

## Category B: Cost & Resource Metrics (α₂ = 0.30 weight)

### B1: Financial Cost

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `cost_usd` | Actual cost incurred for execution | Float | $ USD | Post-exec | **Critical** |
| `cost_tier` | Which pricing tier was used | Enum | Free, Standard, Premium, Unknown | Post-exec | High |
| `tokens_used` | Total tokens consumed (all models combined) | Integer | Count | Post-exec | **Critical** |
| `tokens_input` | Input tokens only | Integer | Count | Post-exec | High |
| `tokens_output` | Output tokens only | Integer | Count | Post-exec | High |
| `cost_per_token` | Effective cost per token (includes batching overhead) | Float | $/token | Post-exec | Medium |
| `free_tier_quota_remaining` | Estimated free tier quota remaining after execution | Integer | Count (tokens/calls) | Post-exec | **Critical** |
| `free_tier_quota_pct_used` | % of daily/monthly free quota consumed | Float | 0-100% | Post-exec | **Critical** |

### B2: Resource Utilization

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `memory_peak_mb` | Peak memory usage during execution | Float | MB | During | Medium |
| `disk_io_mb` | Disk I/O performed | Float | MB | During | Low |
| `network_calls` | Number of external API calls | Integer | Count | During | High |
| `network_bytes_sent` | Bytes transmitted over network | Integer | Bytes | During | Medium |
| `network_bytes_received` | Bytes received over network | Integer | Bytes | During | Medium |
| `cache_hits` | Number of cache hits (if applicable) | Integer | Count | During | Medium |
| `cache_misses` | Number of cache misses | Integer | Count | During | Medium |

### B3: Budget & Quota Management

| Metric | Description | Params | Collection | Priority |
|--------|-------------|--------|-----------|----------|
| `daily_cost_sum` | Total cost for all executions today | Aggregated per day | Post-exec (daily) | High |
| `daily_cost_pct_of_budget` | % of daily budget consumed | Param: budget_usd_per_day | Post-exec (daily) | High |
| `quota_consumed_today` | API quota consumed today | Per-API tracked | Post-exec (daily) | **Critical** |
| `quota_renewal_date` | When quota resets (for free tiers) | Date | Config | Daily | High |
| `days_until_quota_reset` | Days remaining until quota resets | Integer | Daily | Daily | Medium |
| `projected_cost_end_of_month` | Extrapolated cost if execution rate continues | Float | $ USD | Post-exec (daily) | High |

---

## Category C: Performance & Speed Metrics (α₃ = 0.15 weight)

### C1: Latency & Timing

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `total_latency_ms` | End-to-end execution time | Integer | Milliseconds | Post-exec | **Critical** |
| `wall_clock_time_ms` | Real elapsed time (including I/O waits) | Integer | Milliseconds | Post-exec | High |
| `cpu_time_ms` | Time spent in actual computation | Integer | Milliseconds | Post-exec | Medium |
| `io_wait_time_ms` | Time spent waiting for I/O | Integer | Milliseconds | Post-exec | Medium |
| `network_latency_ms` | Time spent on network round-trips | Integer | Milliseconds | Post-exec | Medium |
| `time_to_first_result_ms` | Time until first meaningful output | Integer | Milliseconds | Post-exec | Medium |

### C2: Latency Aggregates & Percentiles

| Metric | Description | Params | Collection | Priority |
|--------|-------------|--------|-----------|----------|
| `latency_p50` | Median latency (50th percentile) | Time window (1h, 1d, 7d) | Post-exec (rolling) | **Critical** |
| `latency_p95` | 95th percentile latency | Time window | Post-exec (rolling) | High |
| `latency_p99` | 99th percentile latency | Time window | Post-exec (rolling) | High |
| `latency_mean` | Average latency | Time window | Post-exec (rolling) | High |
| `latency_std_dev` | Standard deviation of latency | Time window | Post-exec (rolling) | Medium |
| `latency_trend` | Is latency improving or degrading? | Slope over time window | Post-exec (rolling) | High |

### C3: Throughput

| Metric | Description | Params | Collection | Priority |
|--------|-------------|--------|-----------|----------|
| `executions_per_hour` | Throughput: skill executions per hour | Time window | Post-exec (hourly) | Medium |
| `items_processed_per_second` | If applicable: items/records processed | Depends on skill | Post-exec | Medium |
| `operations_per_dollar` | How many operations per dollar spent | Aggregated | Post-exec (daily) | Medium |

---

## Category D: Quality & Correctness Metrics

### D1: Output Quality

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `output_correct` | Output matches expected result (oracle-based) | Boolean | true/false | Post-exec | High |
| `output_complete` | All expected outputs produced | Boolean | true/false | Post-exec | Medium |
| `output_valid_format` | Output conforms to specified format | Boolean | true/false | Post-exec | High |
| `confidence_score` | System's confidence in correctness (0-1) | Float | 0.0-1.0 | Post-exec | **Critical** |
| `human_review_required` | Output flagged for human review | Boolean | true/false | Post-exec | High |

### D2: Semantic Quality (LLM-generated content)

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `semantic_similarity_vs_baseline` | Cosine similarity to reference output | Float | 0.0-1.0 | Post-exec | Medium |
| `keyword_coverage` | % of required keywords in output | Float | 0.0-1.0 | Post-exec | Medium |
| `tone_consistency` | Output maintains expected tone | Boolean | true/false | Post-exec | Low |
| `hallucination_detected` | System detected false/fabricated info | Boolean | true/false | Post-exec | High |

### D3: Data Integrity

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `checksum_verified` | Output checksum/hash matches expected | Boolean | true/false | Post-exec | High |
| `idempotency_verified` | Rerunning produces identical output | Boolean | true/false | Post-exec | High |
| `no_data_corruption` | No truncation, encoding errors, or loss | Boolean | true/false | Post-exec | High |

---

## Category E: Vigilance & Security Metrics (α₄ = 0.05 weight, always monitored)

### E1: Quota & Rate Limit Monitoring

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `free_tier_warnings_today` | # of near-quota warnings | Integer | Count | Post-exec (daily) | **Critical** |
| `rate_limit_hit` | Execution hit API rate limit | Boolean | true/false | Post-exec | **Critical** |
| `rate_limit_backoff_applied` | System backed off due to rate limit | Boolean | true/false | Post-exec | High |
| `quota_exhaustion_imminent` | Free tier quota will run out today | Boolean | true/false | Post-exec (hourly) | **Critical** |

### E2: Security & Anomaly Detection

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `api_call_pattern_normal` | API calls follow expected pattern | Boolean | true/false | Post-exec | High |
| `api_call_pattern_suspicious` | Unusual call frequency, destination, or payload | Boolean | true/false | Post-exec | **Critical** |
| `authentication_error` | Auth token failed or expired | Boolean | true/false | Post-exec | **Critical** |
| `unauthorized_access_attempt` | Attempted access to restricted resource | Boolean | true/false | Post-exec | **Critical** |
| `fingerprint_verified` | Skill fingerprint matches known good | Boolean | true/false | Pre-exec | High |
| `fingerprint_mismatch` | Skill fingerprint doesn't match baseline | Boolean | true/false | Pre-exec | **Critical** |

### E3: Vendor & Operational Monitoring

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `vendor_status` | Is external API healthy? | Enum | Up, Degraded, Down, Unknown | Pre-exec | High |
| `vendor_status_changed` | Vendor status different from 1h ago | Boolean | true/false | Pre-exec | High |
| `unusual_vendor_behavior` | API behaving unexpectedly (slow, rejecting, etc.) | Boolean | true/false | During/Post | Medium |
| `skill_version_deployed` | Version hash of skill in use | String | SHA256 | Pre-exec | High |
| `skill_modification_detected` | Skill code changed since last run | Boolean | true/false | Pre-exec | **Critical** |

---

## Category F: Metadata & Execution Context

### F1: Execution Environment

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `execution_id` | Unique identifier for this execution | UUID | String | Pre-exec | **Critical** |
| `skill_name` | Which skill was executed | String | Name | Pre-exec | **Critical** |
| `skill_version` | Version of the skill | String | Semantic | Pre-exec | **Critical** |
| `timestamp_start` | When execution started | ISO8601 | DateTime | Pre-exec | **Critical** |
| `timestamp_end` | When execution ended | ISO8601 | DateTime | Post-exec | **Critical** |
| `operator` | Who triggered this execution (human or system) | String | Username/ID | Pre-exec | High |
| `orchestrator_version` | Version of orchestrator in use | String | Semantic | Pre-exec | High |
| `environment` | Execution environment | Enum | Local, Dev, Staging, Prod | Pre-exec | High |

### F2: Input & Output Metadata

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `input_hash` | Hash of input data | String | SHA256 | Pre-exec | High |
| `input_size_bytes` | Size of input | Integer | Bytes | Pre-exec | Medium |
| `output_hash` | Hash of output data | String | SHA256 | Post-exec | High |
| `output_size_bytes` | Size of output | Integer | Bytes | Post-exec | Medium |
| `input_items_count` | Number of items processed (if applicable) | Integer | Count | Pre-exec | Medium |
| `output_items_count` | Number of items produced | Integer | Count | Post-exec | Medium |

### F3: Decision & Reasoning

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `decision_made` | Decision rendered by skill (APPROVE/BLOCK/etc.) | String | Enum | Post-exec | High |
| `confidence_in_decision` | Confidence score for decision | Float | 0.0-1.0 | Post-exec | High |
| `reasoning_summary` | Why this decision was made | String | Free text | Post-exec | Medium |
| `alternative_paths_considered` | How many alternative paths were evaluated | Integer | Count | Post-exec | Low |
| `human_override` | Decision was overridden by human | Boolean | true/false | Post-exec | High |

---

## Category G: System-Level Aggregate Metrics

These are computed from collections of individual execution metrics.

| Metric | Description | Computed From | Cadence | Priority |
|--------|-------------|---------------|---------|----------|
| `system_reliability_score` | Weighted composite of all reliability metrics | Success rates + error recovery + uptime | Hourly | **Critical** |
| `system_cost_efficiency_score` | Weighted composite of cost metrics | Token usage + cost targets + budget tracking | Daily | **Critical** |
| `system_performance_score` | Weighted composite of speed metrics | Latencies + throughput + SLO compliance | Hourly | High |
| `system_anomaly_score` | Deviation from baseline behavior | Zscore across all metrics | Real-time | **Critical** |
| `system_health_index` | Overall system health (0-100) | Composite of reliability, cost, performance, security | Hourly | High |

---

## Category H: Decision Outcomes & Self-Correction (α₅ = 0.10 weight)

AI agents must learn from repeated mistakes without explicit reprompting at the start of each session. This category tracks command execution history, error patterns, and user feedback to enable autonomous guardrail creation and continuous improvement.

### H1: Command & Decision Execution History

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `command_attempted` | The exact command or decision attempted | String | Command text | Pre-exec | High |
| `command_execution_result` | Success, error type, partial fail | Enum | Success, Error, PartialFail, Timeout | Post-exec | **Critical** |
| `error_message` | Actual error text from system | String | Free text | Post-exec | High |
| `is_repeated_error` | Is this the same error as a prior execution? | Boolean | true/false | Post-exec | **Critical** |
| `prior_occurrences_count` | How many times has this exact error occurred? | Integer | Count (lifetime) | Post-exec | High |
| `last_occurrence_timestamp` | When was this error last seen? | ISO8601 | DateTime | Post-exec | High |
| `correction_applied` | Did the system auto-correct after the error? | Boolean | true/false | Post-exec | High |
| `correction_description` | What correction was applied (e.g., py vs python) | String | Free text | Post-exec | Medium |
| `correction_successful` | Did the correction fix the problem? | Boolean | true/false | Post-exec | High |

### H2: Error Pattern Recognition & Prevention

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `error_pattern_id` | Unique hash of error signature | String | SHA256 hash | Post-exec | High |
| `error_pattern_category` | Classification of error type | Enum | Environment, Syntax, Permission, Resource, API, Logic, Unknown | Post-exec | High |
| `pattern_frequency_7d` | How often does this error occur (7-day window) | Integer | Count | Post-exec | **Critical** |
| `pattern_frequency_30d` | How often does this error occur (30-day window) | Integer | Count | Post-exec | High |
| `pattern_flagged_by_user` | User marked: "don't make this mistake again" | Boolean | true/false | User input | **Critical** |
| `guardrail_active` | Is there a guardrail preventing this error? | Boolean | true/false | Post-exec | **Critical** |
| `guardrail_configuration` | Details of guardrail (e.g., "use py not python on Windows") | String | Free text | Config | High |
| `sessions_since_guardrail_added` | How many sessions have run with this guardrail active? | Integer | Count | Post-exec | Medium |
| `guardrail_prevented_errors_count` | How many times this guardrail blocked the error | Integer | Count | Post-exec | High |
| `guardrail_effectiveness_pct` | % of would-be errors prevented by this guardrail | Float | 0-100% | Post-exec | Medium |

### H3: User Feedback & Workspace Configuration

| Metric | Description | Type | Units | Collection | Priority |
|--------|-------------|------|-------|-----------|----------|
| `user_feedback_action` | User response to decision/error (ACCEPT/REJECT/MODIFY) | Enum | Accept, Reject, Modify, NoGuidance | Post-exec | **Critical** |
| `feedback_timestamp` | When did user provide feedback | ISO8601 | DateTime | User input | High |
| `feedback_reason` | Why user accepted/rejected (user commentary) | String | Free text | User input | Medium |
| `user_allowed_for_workspace` | User clicked "allow this for workspace" button | Boolean | true/false | User input | High |
| `user_blocked_pattern` | User clicked "don't make this mistake again" button | Boolean | true/false | User input | High |
| `workspace_exception_created` | Exception rule added to workspace config | Boolean | true/false | Post-feedback | High |
| `workspace_exception_config` | What exception was added (config object) | String | YAML/JSON | Post-feedback | High |
| `feedback_acted_on` | Was user feedback converted into a guardrail? | Boolean | true/false | Post-feedback | High |
| `feedback_latency_minutes` | How long after error until user provided feedback | Integer | Minutes | Post-feedback | Medium |

---

## Collection Strategy: Where & When

### Persistent Storage (JSONL Format)

**File**: `logs/execution_metrics.jsonl`  
**Record per execution**: One JSON object per line, immutable  
**Schema**: See [metrics-schema.json](./metrics-schema.json) (to be designed in Phase 1b)

```json
{
  "execution_id": "uuid",
  "skill_name": "git-push-autonomous",
  "skill_version": "0.1.0",
  "timestamp_start": "2026-02-14T14:23:00Z",
  "timestamp_end": "2026-02-14T14:23:05Z",
  "execution_succeeded": true,
  "total_latency_ms": 5000,
  "tokens_used": 250,
  "cost_usd": 0.00,
  "cost_tier": "free",
  "free_tier_quota_remaining": 999750,
  "success_rate_1h": 1.0,
  "confidence_score": 0.99,
  "decision_made": "APPROVE",
  "output_hash": "abc123...",
  "command_attempted": "py scripts/test.py",
  "command_execution_result": "Success",
  "is_repeated_error": false,
  "prior_occurrences_count": 0,
  "correction_applied": false,
  "user_feedback_action": "Accept"
}
```

**Storage efficiency note**: JSONL format is ~2KB per execution. At 100 executions/day, that's 200KB/day or ~6MB per month—trivial by modern standards, similar to Layer 1-3 memory in the [7 levels of memory architecture](../../docs/7%20levels%20of%20memory.md). Retention of 90 days = ~18MB total.



### Real-Time Monitoring

**Data structure**: In-memory metrics buffer (last 1000 executions)  
**Updates**: Every execution appends new metrics  
**Queries**: Fast lookups for recent trends, percentiles, anomalies  
**Purpose**: Feed dashboard, trigger alerts, inform routing decisions

### Archive & Analysis

**Archival**: Daily snapshot of metrics to `logs/metrics_archive_YYYY-MM-DD.jsonl`  
**Purpose**: Historical analysis, trend detection, retrospective reviews  
**Retention**: 90 days rolling window (Phase 1b), expandable later

---

## Proposed Metrics Dashboard (Phase 2b+)

Once we have data flowing, visualize:

**Real-time pane** (updates per execution):
- Success rate (current 1h)
- Cost spent today ($ and % of daily budget)
- Free tier quota remaining
- P95 latency (current 1h)
- Active alerts (red if anomalies detected)

**Historical pane** (7-day view):
- Reliability trend (success rate over time)
- Cost trend ($ per day, free vs paid tier usage)
- Latency trend (p50, p95 over time)
- Top failing skills
- Cost per skill

**Anomaly pane**:
- Recent deviations from baseline
- Suggested optimizations
- Pending human approvals

---

## Feedback Mechanisms

### How Metrics Drive Optimization

1. **Operator review** (weekly)
   - Read metrics summary
   - Identify trends or anomalies
   - Approve/reject proposed changes

2. **Automated alerting** (continuous)
   - If success_rate_1h drops below 95%: notify operator
   - If free_tier_quota_pct_used > 80%: alert
   - If cost_usd > budget_daily: warn
   - **NEW**: If pattern_frequency_7d > 3 AND guardrail_active = false: suggest guardrail creation

3. **Learning from user feedback** (Category H - continuous)
   - User encounters error → System recognizes if it's a repeated pattern
   - User clicks "don't make this mistake again" → Guardrail created automatically
   - User clicks "allow for this workspace" → Workspace exception added
   - Next time the pattern is detected in ANY session → Guardrail activates, no re-prompt needed
   - Metrics track: guardrail_prevented_errors_count and guardrail_effectiveness_pct

4. **Optimization engine** (Phase 2b+)
   - Analyzes metrics holistically
   - Scores alternative routing strategies
   - Proposes changes with expected benefit
   - **NEW**: Uses H-category metrics to identify high-impact error patterns worth fixing globally

5. **Feedback loop closure**
   - Change deployed
   - Metrics re-baseline
   - Operator confirms improvement
   - If regression: auto-rollback

### Self-Correction Without Session Re-prompting

Example: `python` vs `py` on Windows

**Session 1:**
```
Error: python: command not found
System detects: prior_occurrences_count=2, pattern_frequency_7d=3
→ Offers suggestion: Try 'py' instead on Windows?

[✅ Allow for workspace]  [🚫 Don't make this mistake again]
```

**User clicks "Don't make this mistake again":**
- Sets: user_blocked_pattern = true
- Creates guardrail in workspace config
- Logs: guardrail_active = true, feedback_acted_on = true
- Logs: feedback_latency_minutes = 2

**Session 2 (20 days later, new investigation thread):**
```
System pre-check: guardrail_active = true for pattern_id=<python_vs_py_windows>
→ Suggests: 'py' instead of 'python' (Windows environment detected)
✅ User confirms or accepts default
→ Command succeeds without ever trying 'python'

Metrics logged:
  - correction_applied = true
  - correction_successful = true
  - guardrail_prevented_errors_count incremented
  - guardrail_effectiveness_pct updated
```

This leverages Layer 2 of the [7 levels of memory](../../docs/7%20levels%20of%20memory.md): **Session Bootstrap** automatically loads active guardrails at session start, eliminating repeated manual corrections.

---

## Challenges & Open Questions

**For Phase 1b discussion:**

1. **Attribution**: If a git push fails, was it the rules-engine? auth-validator? commit-message? or orchestrator logic? How do we decompose blame?
   - *Proposal*: Tag each metric with "skill_name" and "skill_phase" (Pre/During/Post). String path through DAG in orchestrator logs.

2. **Multi-step operations**: Blog publish involves git commit, git push, GitHub webhook, Vercel deploy. Where does "success" end?
   - *Proposal*: Define SLO per skill. Blog skill succeeds when Vercel deploy completes and webhook returns 200.

3. **Partial cost**: Some operations use free tier, some don't. How do we track hybrid?
   - *Proposal*: Every metric has `cost_tier` field. Aggregates separately track free vs paid.

4. **Cost forecasting**: We don't know price changes in advance. How do we forecast?
   - *Proposal*: Scenario-based modeling. "If cost stays current, we'll hit limit in X days." "If pricing doubles, we hit in Y days."

5. **Externalities**: Some skills call other APIs (weather data, maps). How do we attribute cost?
   - *Proposal*: Per-skill cost isolation. Each API call logged separately. Traceability to parent execution.

6. **Memory burden of Category H** (NEW): Isn't tracking every error pattern and guardrail expensive?
   - *Answer*: No. ~2KB per execution in JSONL format. 100 executions/day = 200KB/day = ~6MB/month. 90-day retention = ~18MB total. This fits Layer 1-3 of the [7 levels of memory architecture](../../docs/7%20levels%20of%20memory.md) and is "cheap enough to try" as mentioned in discovery.
   - *Risk*: If we add full tracing (stack dumps, screenshot logs), we'd balloon. But Category H stores only structured decision metadata, not raw I/O traces. Stay disciplined on what we persist.

---

## Next Steps

1. **Design metrics-schema.json**: Finalize JSONL schema for persistence
2. **Update skill models.py**: Add `ExecutionMetrics` dataclass
3. **Update orchestrator**: Capture metrics before/after each skill execution
4. **Update telemetry-logger**: Append metrics to `logs/execution_metrics.jsonl`
5. **Create queries**: Sample queries for common analysis patterns (success rate, cost trend, latency percentile)
6. **Phase 2a**: Add baseline computation and anomaly detection

---

**Document Status**: Ready for feedback. Metrics are expected to evolve as we collect operational data.  
**Next Review**: After Phase 1b data collection is operational.

