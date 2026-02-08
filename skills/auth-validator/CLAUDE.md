---
name: auth-validator
version: v1.0
last_updated: 2026-02-07
author: Phase 1b Implementation
document_type: SKILL_DESIGN_SPECIFICATION
---

# auth-validator Design & Decision Tree

## Why 4-Layer Authorization?

Single authorization check can't express the nuance needed for autonomous skills:

1. **Group visibility** (Layer 1): Can you see this skill? (coarse-grained)
2. **Execution permission** (Layer 2): Can you run it? (role + MFA)
3. **Tool access** (Layer 3): Can you use these specific tools? (fine-grained)
4. **Resource access** (Layer 4): Can you access these branches/data? (protective)

**Example**: Developer "alice" might be in allowed group, have sufficient role, be able to use git-push tool, but only on feature/* branches—not main (protected).

## Design Pattern: Fail-Fast with Short-Circuit

```python
for layer in [1, 2, 3, 4]:
    if not layer.passes():
        return AuthzDecision.FORBIDDEN_LAYER_N(details)
return AuthzDecision.APPROVED
```

**Why?**
- Fast: Most denials happen in Layer 1-2
- Private: Doesn't reveal existence of resources user can't access
- Conservative: Extends principle of least privilege

## Authorization Config Structure

```yaml
# config/authorization.yaml

roles:
  Developer:
    rank: 1
  Senior-Engineer:
    rank: 2
  Staff-Engineer:
    rank: 3

skills:
  git-push-autonomous:
    allowed_groups:
      - "engineering-team"
      - "platform-engineering"
    minimum_role_rank: 1
    requires_mfa: true

resources:
  git:
    branches:
      main:
        allowed_roles: []  # Protected: use PRs
      develop:
        allowed_roles: [1, 2]  # Developer and above
      "feature/*":
        allowed_roles: [1, 2, 3]  # Everyone
```

## Decision Tree: Layer 1 (Group Membership)

```
IF skill.allowed_groups is empty:
    PASS (skill open to all)
ELSE IF user has any group in skill.allowed_groups:
    PASS
ELSE:
    FAIL (FORBIDDEN_LAYER_1)
```

**Speed**: O(n) where n = user groups (usually 3-5)

## Decision Tree: Layer 2 (Role & MFA)

```
IF user.role_rank < skill.minimum_role_rank:
    FAIL (INSUFFICIENT_ROLE)
    
IF skill.requires_mfa AND not user.mfa_validated:
    FAIL (MFA_REQUIRED)
    
PASS
```

**Speed**: O(1)

## Decision Tree: Layer 3 (Tool Permissions)

```
FOR EACH tool operation:
    IF tool NOT in skill.allowed_tools:
        FAIL (TOOL_NOT_PERMITTED)
    
    IF tool.has_path_restrictions:
        path = operation.resource_path
        
        # Check blocked_paths first (negative rules)
        FOR EACH blocked_pattern in tool.blocked_paths:
            IF path matches blocked_pattern:
                FAIL (PATH_BLOCKED)
        
        # Then check allowed_paths (positive rules)
        IF allowed_paths is not empty:
            found_match = false
            FOR EACH allowed_pattern in tool.allowed_paths:
                IF path matches allowed_pattern:
                    found_match = true
                    break
            IF not found_match:
                FAIL (PATH_NOT_ALLOWED)

PASS
```

**Pattern Matching**: Use fnmatch.fnmatch() (glob syntax)
- "src/**" matches any file under src/
- "*.py" matches any .py file
- "secrets/**" matches entire secrets/ directory

## Decision Tree: Layer 4 (Resource Access)

```
IF no resource specified:
    PASS
    
policy = look_up_resource_policy(resource)

IF policy is undefined:
    PASS (resource not in policy, treat as open)

allowed_roles = policy.allowed_roles

IF allowed_roles is empty:
    FAIL (RESOURCE_PROTECTED)

IF user.role_rank not in allowed_roles:
    FAIL (RESOURCE_FORBIDDEN)

PASS
```

**Speed**: O(1) with role ranking (no list search)

## Test Matrix (18+ tests)

### Happy Path (3 tests)
- User passes all 4 layers
- User in allowed group, sufficient role, MFA validated, all tools allowed, branch allowed
- User with MFA disabled, skill doesn't require MFA

### Layer 1: Group Membership (3 tests)
- User not in any allowed group → FORBIDDEN_LAYER_1
- User in one of multiple allowed groups → PASS
- Policy has no group requirements → PASS

### Layer 2: Role & MFA (4 tests)
- User role insufficient → FORBIDDEN_LAYER_2 (INSUFFICIENT_ROLE)
- MFA required but user not validated → FORBIDDEN_LAYER_2 (MFA_REQUIRED)
- MFA not required, user lacks it → PASS
- User role >= minimum → PASS

### Layer 3: Tool Permissions (5 tests)
- Tool not in allowed list → FORBIDDEN_LAYER_3 (TOOL_NOT_PERMITTED)
- File matches blocked_pattern → FORBIDDEN_LAYER_3 (PATH_BLOCKED)
- File in allowed_paths → PASS
- Multiple tools, all allowed → PASS
- Multiple tools, one blocked → FORBIDDEN_LAYER_3

### Layer 4: Resource Access (3 tests)
- Branch not in allowed list → FORBIDDEN_LAYER_4 (RESOURCE_FORBIDDEN)
- Branch in allowed list → PASS
- Resource not defined in policy → PASS (conservative: unknown resources open)

## Error Output Format

```json
{
  "decision": "FORBIDDEN_LAYER_3",
  "reason": "Cannot add file(s) to commit",
  "details": {
    "blocked_file": ".env",
    "matched_rule": "blocked_paths[0]",
    "rule_description": "Environment files containing secrets"
  },
  "recovery_action": "Remove .env from staging area: git reset .env"
}
```

**Why detailed errors?**
- User knows exactly what to fix
- No need for admin intervention
- Self-service recovery
- Teaches the security model

## Phase 2: Entra Integration Roadmap

When Entra AD added:

```python
# Phase 1b: Local config
groups = config.get("users")[user_id]["groups"]

# Phase 2: Entra API
from azure.identity import DefaultAzureCredential
from msgraph.core import GraphClient

client = GraphServiceClient(credential=DefaultAzureCredential())
groups = await client.users[user_id].member_of.get()
```

**Unchanged**:
- Decision logic (still 4 layers)
- Output interface (same JSON)
- Error messages (same recovery actions)

## Success Criteria (Phase 1b MVP)

- ✅ All 18+ unit tests passing
- ✅ SKILL.md documents all 4 layers
- ✅ Error messages are actionable
- ✅ AuthValidator ~150-200 lines (clean)
- ✅ Ready for orchestrator integration
