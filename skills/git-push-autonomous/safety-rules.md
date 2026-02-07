# Safety Rules & Validation Logic

## Overview

This document defines what files are **excluded** (never auto-push) and what validation logic applies.

**Principle**: If a file could leak secrets, crash, or break reproducibility, it's blocked.

---

## Blocked Files (Explicit List)

### Credentials & Secrets
```
.env
.env.local
.env.*.local
.secrets
secrets/
credentials.json
aws-credentials
~/.ssh/  (if ever committed)
.private_key
*.key
*.pem
```

### Package Artifacts & Build Output
```
node_modules/
.npm/
dist/
build/
bin/
obj/
target/
.gradle/
venv/
__pycache__/
.venv/
site-packages/
```

### IDE & Local Configuration
```
.vscode/settings.json  (project-local settings)
.idea/
.DS_Store
Thumbs.db
*.swp
*.swo
~*.tmp
.eslintcache
.prettierignore
*.lock  (project-specific, not git-checked)
```

### Temporary & Cache Files
```
*.tmp
*.log
*.pid
*.lock (generated at runtime)
.cache/
.temp/
tmp/
temp/
```

### OS & System Files
```
.DS_Store
Thumbs.db
desktop.ini
```

### Development Databases & Large Files
```
*.db
*.sqlite
*.sqlite3
dump.sql
*.dump
coverage/
.nyc_output/
```

---

## Blocked Patterns (Regex)

In addition to explicit files, these **regex patterns** block files:

| Pattern | Reason | Example |
|---------|--------|---------|
| `^\.` | Hidden files (usually config) | `.gitignore` blocked |
| `^credentials/.*` | Any file in credentials/ dir | `credentials/api-key.json` blocked |
| `^secrets/.*` | Any file in secrets/ dir | `secrets/db-password.txt` blocked |
| `tmp.*\.log$` | Temp log files | `tmp-debug.log` blocked |
| `.*\.key$` | Key files | `private.key` blocked |
| `.*\.pem$` | PEM certificates | `cert.pem` blocked |
| `node_modules/.*` | Anything under node_modules | `node_modules/pkg/index.js` blocked |
| `dist/.*` | Distribution artifacts | `dist/index.js` blocked |

---

## Size Limits

**Max file size**: 50 MB (configurable)

- Rationale: GitHub warns on > 50MB; protects against accidental binary commits
- Action: File > 50MB → BLOCKED + warning
- Override: Can be configured per-project (future)

---

## Allowed Files (Examples)

These are **always allowed** (unless explicitly blocked above):

```
✓ src/
✓ lib/
✓ docs/
✓ tests/
✓ scripts/
✓ config/
✓ package.json (runtime dependencies)
✓ Cargo.toml (Rust deps)
✓ requirements.txt (Python deps)
✓ README.md
✓ LICENSE
✓ .gitignore (repo config)
```

---

## Validation Rules Engine

### Rule 1: Exclusion Check
**Input**: File path  
**Logic**:
```
if file matches blocked_files list → BLOCK
if file matches blocked_patterns regex → BLOCK
else → PASS
```

### Rule 2: Size Check
**Input**: File size (bytes)  
**Logic**:
```
if file_size > 50MB → WARN (but allow)
else → PASS
```

### Rule 3: Secret Pattern Scan (Future)
**Input**: File content  
**Logic**:
```
if content contains:
  - AWS_ACCESS_KEY_ID
  - DATABASE_PASSWORD
  - PRIVATE_KEY
  - (other patterns)
→ BLOCK + alert operator
else → PASS
```

### Rule 4: License Compliance (Future)
**Input**: File path
**Logic**:
```
if committing CODEOWNERS
and user ≠ codeowner
→ WARN + require approval
else → PASS
```

---

## Configuration Format

### exclusions.yaml
```yaml
# Blocked files (explicit)
blocked_files:
  - ".env"
  - ".env.local"
  - ".secrets"
  - "credentials.json"
  - ".DS_Store"
  - "Thumbs.db"

# Blocked paths (glob or regex)
blocked_patterns:
  - "^credentials/.*"
  - "^secrets/.*"
  - "tmp.*\\.log$"
  - "node_modules/.*"
  - "dist/.*"
  - "\\.key$"
  - "\\.pem$"

# Size limits
max_file_size_mb: 50

# Allowed to override (future)
allow_override: false
```

### How Operator Modifies Rules

**To allow a file**:
```yaml
# In exclusions.yaml
# Remove from blocked_files or blocked_patterns
```

**To block a new pattern**:
```yaml
blocked_patterns:
  - "my-new-pattern/.*"
```

**Changes take effect immediately**; next push re-evaluates.

---

## Decision Matrix

| File | Rules Pass | Confidence | Result |
|------|-----------|-----------|--------|
| `src/main.rs` | ✓ | 0.99 | APPROVE |
| `.env` | ✗ Blocks | 1.00 | BLOCK |
| `dist/bundle.js` | ✗ Blocks | 1.00 | BLOCK |
| `file > 50MB` | ⚠ Warn | 0.85 | APPROVE (warn) |
| `unknown-scan` | ? | 0.60 | BLOCK (fail-safe) |

---

## How This Feeds Phase 2 Learning

Each rejected push creates a signal:
```json
{
  "file": "secrets/api-key.json",
  "reason": "matches blocked pattern",
  "operator_override": false,
  "timestamp": "2026-02-05T14:00:00Z"
}
```

**Phase 2 analysis**:
- Pattern: Do rejected files form clusters? (e.g., all in `secrets/` dir)
- False positives: Do operators frequently override?
- Drift: Are new patterns emerging that should be blocked?

---

## Operator Overrides (Phase 2)

**Future feature** (not Phase 1):
```
"Push anyway; I know this .env is not secret"
→ Logs override reason + pushes
→ Feeds learning (false positive detected)
```

Currently: No overrides. Block = stop.

---

## Examples

### Example 1: Normal Files → PASS
Files: `src/main.rs`, `tests/unit.js`, `docs/API.md`

```
auth-validator: ✓ Valid git config
rules-engine:
  - src/main.rs: ✓ Allowed file
  - tests/unit.js: ✓ Allowed file
  - docs/API.md: ✓ Allowed file
Result: APPROVE
```

### Example 2: Includes Blocked File → BLOCK
Files: `src/main.rs`, `.env`

```
auth-validator: ✓ Valid git config
rules-engine:
  - src/main.rs: ✓ Allowed file
  - .env: ✗ Blocked (explicit)
Result: BLOCK_ALL
Reason: "Excluded files detected: .env"
```

### Example 3: Pattern Match → BLOCK
Files: `src/main.rs`, `credentials/db-password.txt`

```
auth-validator: ✓ Valid git config
rules-engine:
  - src/main.rs: ✓ Allowed file
  - credentials/db-password.txt: ✗ Blocked (pattern: ^credentials/.*)
Result: BLOCK_ALL
Reason: "Excluded files detected: credentials/"
```

### Example 4: Oversized File → WARN (Allow)
Files: `src/main.rs`, `video.mp4` (100 MB)

```
auth-validator: ✓ Valid git config
rules-engine:
  - src/main.rs: ✓ Allowed file
  - video.mp4: ⚠ Size exceeds 50MB (100MB)
Result: APPROVE (with warning)
Telemetry: Records size warning for operator awareness
```

---

## When Rules Need Update

**Scenario**: You have a legitimate `.env.example` file (not secret).

**Current behavior**: Blocked (matches `.env*`)  
**Solution**:
1. Add to allowlist in Phase 2 override system
2. Or: Rename to `env.example.yml` (doesn't match pattern)
3. Or: Operator reviews + approves override

---

## Testing Rules

### Test Cases for Validation

```yaml
test_cases:
  - name: "Allow normal source files"
    files: ["src/main.rs", "lib/utils.js"]
    expected: APPROVE
  
  - name: "Block .env files"
    files: [".env"]
    expected: BLOCK
  
  - name: "Block credentials pattern"
    files: ["credentials/api.key"]
    expected: BLOCK
  
  - name: "Block build artifacts"
    files: ["dist/bundle.js"]
    expected: BLOCK
  
  - name: "Warn on large files"
    files: ["video.mp4 (100MB)"]
    expected: APPROVE_WITH_WARNING
  
  - name: "Allow .gitignore"
    files: [".gitignore"]
    expected: APPROVE
```

---

## Maintenance

**Owner**: Project lead  
**Review cycle**: Monthly or when new secret types discovered  
**Change process**: Edit config section above → test cases → Phase 2 learns patterns  

---

**Last updated**: 2026-02-05  
**Version**: 1.0  
**Status**: Ready for Phase 1 testing
