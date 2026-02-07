# Telemetry Logger: Decision Logic
**Specs Version**: v1.0

## Purpose

Record every decision, every step, every result for audit trail and Phase 2 learning.

## Design Principle: Observability Over Speed

- Longer to execute (I/O for logging)
- But: Operator can review every decision later
- Phase 2 learns from complete decision logs

## Phase 1 Reasoning

**Question**: "How do I record what just happened?"

**Answer** (structure the log):

```json
{
  "timestamp": "ISO8601",
  "log_id": "uuid",
  "orchestrator": "git-push-autonomous",
  "decision": "APPROVED|BLOCKED|ERROR",
  "confidence": 0.95,
  "steps": [
    { "step": 1, "name": "Check changes", "status": "PASS", "confidence": 0.99 },
    { "step": 2, "name": "Auth validation", "status": "PASS", "confidence": 0.99 },
    { "step": 3, "name": "Rules validation", "status": "PASS", "confidence": 0.95 },
    { "step": 4, "name": "Commit message", "status": "PASS", "confidence": 0.99 },
    { "step": 5, "name": "Git commit", "status": "PASS", "confidence": 0.99 },
    { "step": 6, "name": "Git push", "status": "PASS", "confidence": 0.99 }
  ],
  "context": {
    "files": [ "src/main.rs", "docs/README.md" ],
    "file_count": 2,
    "branch": "main",
    "repo": "/path/to/repo"
  },
  "result": {
    "status": "SUCCESS",
    "commit_hash": "abc123def456",
    "error": null
  }
}
```

## Log Format Choices

**Why JSON?**
- Queryable (jq, grep, parsing tools)
- Supports nested structure (steps, context, result)
- Human-readable + machine-processable

**Why structured fields?**
- Operator can ask: "What was blocked in last 10 pushes?"
- Phase 2 can analyze: "What confidence did auth-validator assign?"
- Audit trail: Each decision fully documented

## What NOT to Log

❌ Git credentials (even encrypted)  
❌ Actual file contents (only paths)  
❌ Operator personal data (unless needed for audit)

## Retention Policy

Phase 1: Keep all logs (no cleanup)  
Phase 2: Configurable retention (30-90 days)

---

## Phase 2 Enhancement: Integration with QuestionManager

Send logs to QuestionManager:
```
POST /logs/telemetry
{
  "log_id": "uuid",
  "log_data": { ... JSON ... }
}
```

QuestionManager benefits:
- Centralized log search + analytics
- Real-time dashboard
- Alerting on anomalies

## Learning Loop (Phase 2)

Analyze logs to detect:

**Pattern 1: Repeated Blocks**
```
"Over 7 days: .env blocked 5 times"
→ Recommendation: Add .env to gitignore template
```

**Pattern 2: Confidence Drift**
```
"Auth-validator confidence dropped from 0.99 to 0.85"
→ Alert: Aspire service degraded?
```

**Pattern 3: Success Rate**
```
"Success rate: 98% (42/43 pushes)"
→ Recommendation: Relax size warning threshold
```

---

**Status**: Phase 1 JSON logging implemented; Phase 2 QuestionManager integration designed.
