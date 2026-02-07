---
name: telemetry-logger
version: specs-v1.0
description: Records and structures telemetry data from autonomous operations. Use when you need to log decisions, results, and system state for audit trails, learning, and operator analysis. Integrates with logging backends (currently file-based, future Aspire/QuestionManager integration).
license: Internal use. RoadTrip project.
---

# Telemetry Logger Skill

## Overview

Logs structured telemetry from autonomous workflows. Phase 1: File-based. Phase 2: Integration with QuestionManager/Aspire.

## What It Logs

- **Decision points**: What was decided and why
- **Confidence scores**: How confident was each decision (0-1)
- **Execution results**: What succeeded, what failed, why
- **Timing**: When each step occurred
- **Context**: Files affected, branches, operators, etc.

## Input Format

```json
{
  "timestamp": "ISO8601",
  "orchestrator": "name",
  "decision": "APPROVED|BLOCKED|ERROR",
  "steps": [ { "name": "str", "status": "PASS|FAIL", "confidence": 0.0-1.0 } ],
  "context": { "files": [], "branch": "str" },
  "result": { "success": bool, "error": "str" }
}
```

## Output

```json
{
  "status": "RECORDED",
  "log_id": "uuid",
  "location": "path/to/log/file"
}
```

## Configuration

Reads: `config/telemetry-config.yaml`

```yaml
log_dir: logs/
log_level: DEBUG|INFO|WARN|ERROR
retention_days: 30
format: JSON  # Phase 1: JSON files; Phase 2: Aspire integration
```

## Phase 2 Integration (Placeholder)

- Send logs to QuestionManager for analysis
- Real-time dashboard of skill decisions
- Auto-detect patterns for learning

---

**Status**: Phase 1 stub. Core logic: append structured JSON to log file.
