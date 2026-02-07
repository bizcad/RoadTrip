---
name: auth-validator
version: specs-v1.0
description: Validates git credentials and permissions before operations. Use when you need to check that the current user has authorization to push, create branches, or modify a repository. Phase 1: Local git config checks. Phase 2: Integration with Aspire auth service.
license: Internal use. RoadTrip project.
---

# Auth Validator Skill

## Overview

Validates that current user has authorization to execute git operations.

## What It Checks

### Phase 1 (Now)
- Git is installed and accessible
- `user.name` is configured
- `user.email` is configured
- Git remote (origin) is reachable
- User has push permission (credential test)

### Phase 2 (Future)
- Integration with Aspire auth backend
- Check MFA requirements
- Validate token expiry
- Permission scoping (branch-level)

## Input

```json
{
  "operation": "push|commit|branch",
  "target_branch": "main",
  "target_repo": "origin"
}
```

## Output

```json
{
  "decision": "PASS|FAIL",
  "reason": "string",
  "confidence": 0.0-1.0,
  "details": {
    "credentials_found": bool,
    "permissions": [ "push", "commit" ]
  }
}
```

## Configuration

Reads: `config/auth-config.yaml`

```yaml
require_mfa: false  # Phase 2 feature
token_check_interval: 3600  # seconds
allowed_operations: [ push, commit ]
```

## Phase 1 Logic

```
1. Check: git --version → installed?
2. Check: git config user.name → set?
3. Check: git config user.email → set?
4. Check: git remote -v → origin exists?
5. Test: git ls-remote origin HEAD → can connect?
Return: PASS if all checks succeed; FAIL otherwise
```

## Phase 2 Integration (Placeholder)

- Call Aspire auth service
- Verify OAuth credentials
- Check token expiry
- Validate permissions per branch

---

**Status**: Phase 1 stub. Core logic: Run local git config checks.
