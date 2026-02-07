# Rules Engine: Decision Logic
**Specs Version**: v1.0

## Purpose

Determine if a set of files are safe to commit based on pre-configured rules.

## Design Principle: Conservative Defaults

- If in doubt, block
- Blocked files explicitly listed in config
- Patterns define what's dangerous (secrets, artifacts, etc.)

## Phase 1 Reasoning

**Question**: "Are these files safe to commit?"

**Answer** (evaluate each file):

1. **Explicit blocklist?** → Match `.env`, `.secrets`, etc. → BLOCK
2. **Pattern match?** → Match `^secrets/.*`, `node_modules/.*`, etc. → BLOCK
3. **Size check?** → File > 50MB? → WARN (allow but log)
4. **Content scan?** → (Phase 2; skipped now)

For each file:
- Pass all checks? → Confidence 0.99
- Warn? → Confidence 0.95 (minor issue)
- Blocked? → Confidence 1.00 (certain)

Aggregate:
- Any blocked → DECISION: BLOCK_ALL, confidence 1.00
- All pass → DECISION: APPROVE, confidence 0.99
- Some warn → DECISION: APPROVE_WITH_WARN, confidence 0.95

## Why Conservative?

Blocked files are rarely legitimate:
- `.env`: Always contains local secrets
- `node_modules/`: Never should be committed (use lockfile)
- `dist/`/`build/`: Generated; use build process
- Large files: Indicate accidental binary commit

If operator wants to commit a "blocked" file, they must:
1. Phase 1: Remove it or rename (enforce discipline)
2. Phase 2: Explicitly override + provide reason (auditable)

## Patterns: Regex vs Glob

Currently supporting regex for flexibility:
```
^secrets/.*       Matches: secrets/, secrets/db.yaml, etc.
.*\.key$          Matches: private.key, aws.key, etc.
node_modules/.*   Matches: anything under node_modules/
```

## Phase 2 Enhancement: Content Scanning

Add secret pattern detection:
```
AWS_ACCESS_KEY_ID=
DATABASE_PASSWORD=
PRIVATE_KEY
(future: pluggable secret detectors)
```

If content matches → BLOCK regardless of filename

## Learning Loop (Phase 2)

Track what gets blocked:
```json
{
  "file": ".env",
  "pattern": "explicit",
  "operator_override": false,
  "timestamp": "2026-02-05"
}
```

After 100 pushes:
- "Are patterns blocking legitimate files?" → Auto-refine
- "Are patterns catching real secrets?" → Confidence adjust
- "New patterns emerging?" → Update config

---

**Status**: Phase 1 logic implemented; Phase 2 content scanning designed.
