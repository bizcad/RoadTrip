---
name: telemetry-logger
version: specs-v1.0
description: Records and structures telemetry data from autonomous operations. Logs decisions, results, and system state for audit trails and operator analysis.
license: Internal use. RoadTrip project.
---

# Telemetry Logger Skill

## Overview

Logs structured telemetry from autonomous workflows. Phase 1: File-based JSON logging. Phase 2: Integration with analytics backend.

## What It Logs

- **Decision points**: What was decided and why
- **Confidence scores**: How confident was each decision (0-1)
- **Execution results**: What succeeded, failed, and why
- **Timing**: When each step occurred
- **Context**: Files affected, branches, operators

## Input Format

```json
{
  "timestamp": "ISO8601",
  "orchestrator": "skill-name",
  "decision": "APPROVED|BLOCKED|ERROR",
  "steps": [
    {"name": "step1", "status": "PASS", "confidence": 0.95}
  ],
  "context": {"files": [], "branch": "main"},
  "result": {"success": true}
}
```

## Output

```json
{
  "status": "RECORDED",
  "log_id": "uuid-goes-here",
  "location": "logs/YYYY-MM-DD.jsonl"
}
```

## Configuration

Reads: `config/telemetry-config.yaml`

```yaml
log_dir: logs/
log_level: INFO
retention_days: 30
format: JSON
```

## Phase 2 Integration (Future)

- Real-time dashboard of skill decisions
- Analytics queries on decision patterns
- Auto-detect patterns for learning and optimization

---

**Status**: Phase 1 MVP
