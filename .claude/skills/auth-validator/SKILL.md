---
name: auth-validator
version: specs-v1.0
description: Evaluates user authorization across 4 layers (skill availability, execution permission, tool-level access, resource-level access). Use when you need to verify that a user can execute a skill and its associated operations. Implements enterprise-ready authorization with MFA support and role-based access control.
license: Internal use. RoadTrip project.
---

# Auth Validator Skill

## Overview

Validates user authorization at runtime across four distinct layers, enabling secure execution of autonomous skills.

## Why 4 Layers?

Authorization requires checking at multiple levels:
1. **Layer 1 (Skill Visibility)**: Can user see this skill? (group membership)
2. **Layer 2 (Skill Execution)**: Can user execute this skill? (role + MFA)
3. **Layer 3 (Tool Access)**: Can user use specific tools within the skill? (fine-grained)
4. **Layer 4 (Resource Access)**: Can user access this resource? (git branches, file paths, external APIs)

Each layer must pass; failure at any layer blocks execution.

## Input

```json
{
  "user_identity": {
    "username": "bizcad",
    "groups": ["engineering-team", "platform-engineering"],
    "role": "Senior-Engineer",
    "mfa_validated": true,
    "mfa_method": "totp",
    "session_id": "sess_abc123"
  },
  "skill_name": "git-push-autonomous",
  "resource": {
    "type": "git-repository",
    "location": "origin/main"
  }
}
```

## Output

```json
{
  "decision": "APPROVED|FORBIDDEN_LAYER_1|FORBIDDEN_LAYER_2|FORBIDDEN_LAYER_3|FORBIDDEN_LAYER_4",
  "layers_passed": [1, 2, 3],
  "layers_failed": [4],
  "reason": "User lacks permission to push to origin/main (branch restriction)",
  "recovery_action": "Contact admin to whitelist your branch, or push to feature branch",
  "confidence": 1.0,
  "details": {
    "layer_1": {
      "status": "passed",
      "check": "group_membership",
      "user_groups": ["engineering-team"],
      "required_groups": ["engineering-team", "platform-engineering"],
      "matched": true
    },
    "layer_2": {
      "status": "passed",
      "check": "role_and_mfa",
      "user_role": "Senior-Engineer",
      "minimum_role": ["Developer", "Senior-Engineer", "Staff-Engineer"],
      "role_matched": true,
      "mfa_required": true,
      "mfa_validated": true,
      "mfa_method": "totp"
    },
    "layer_3": {
      "status": "passed",
      "check": "tool_permission",
      "allowed_tools": ["git-add", "git-commit", "git-push"],
      "requested_operations": ["git-add", "git-commit", "git-push"],
      "all_allowed": true
    },
    "layer_4": {
      "status": "failed",
      "check": "resource_access",
      "resource_type": "git-branch",
      "resource_name": "origin/main",
      "allowed_branches": ["feature/*", "develop"],
      "denied_reason": "main branch restricted to releases and hotfixes"
    }
  }
}
```

## Configuration

Reads: `config/authorization.yaml` and `config/auth.yaml`

```yaml
# config/authorization.yaml
authorization_policy:
  # Layer 1: Group-based skill visibility
  skills:
    git-push-autonomous:
      allowed_groups:
        - "engineering-team"
        - "platform-engineering"
  
  # Layer 2: Role-based execution
  roles:
    Developer:
      rank: 1
      skills: ["git-push-autonomous", "read-logs"]
    Senior-Engineer:
      rank: 2
      skills: ["git-push-autonomous", "read-logs", "deploy-staging"]
    Staff-Engineer:
      rank: 3
      skills: ["git-push-autonomous", "read-logs", "deploy-staging", "deploy-production"]
  
  # Layer 2: MFA requirements
  mfa_policy:
    git-push-autonomous:
      required: true
      accepted_methods: ["totp", "webauthn"]
  
  # Layer 3: Tool-level permissions
  tools:
    git-add:
      allowed_paths:
        - "src/**"
        - "docs/**"
        - "tests/**"
        - "config/**"
      blocked_paths:
        - "secrets/**"
        - ".env"
    
    git-commit:
      allowed_actions: ["create", "amend"]
      max_message_length: 500
    
    git-push:
      allowed_branches:
        - "feature/*"
        - "develop"
      blocked_branches:
        - "main"        # Protected: releases/hotfixes only
        - "production"
  
  # Layer 4: Resource access (git branches, external APIs)
  resources:
    git:
      branches:
        main:
          allowed_roles: []  # No one can push directly; use PR
          allowed_operations: ["read", "list"]
        develop:
          allowed_roles: ["Developer", "Senior-Engineer"]
          allowed_operations: ["read", "write", "merge"]
        "feature/*":
          allowed_roles: ["Developer", "Senior-Engineer", "Staff-Engineer"]
          allowed_operations: ["read", "write"] 

# config/auth.yaml (dev credentials, loaded at startup)
dev_credentials:
  github_user: "bizcad"
  github_pat: "${GITHUB_TOKEN}"
```

## Phase 1b Logic

```
For user identity and skill name:
  
  Layer 1: Check Group Membership
    if user.groups NOT in skill.allowed_groups:
      return FORBIDDEN_LAYER_1(reason="group not allowed")
    else:
      pass layer 1
  
  Layer 2: Check Role & MFA
    if user.role rank < skill.minimum_role rank:
      return FORBIDDEN_LAYER_2(reason="insufficient role")
    
    if skill.requires_mfa and not user.mfa_validated:
      return FORBIDDEN_LAYER_2(reason="MFA required but not validated")
    
    else:
      pass layer 2
  
  Layer 3: Check Tool Permissions
    for each tool operation in skill:
      if tool not in allowed_tools:
        return FORBIDDEN_LAYER_3(reason=f"{tool} not permitted")
      if resource_path not in allowed_paths:
        return FORBIDDEN_LAYER_3(reason=f"path {resource_path} blocked")
    
    else:
      pass layer 3
  
  Layer 4: Check Resource Access
    if resource_type == "git-branch":
      if resource_name not in allowed_branches:
        return FORBIDDEN_LAYER_4(reason=f"branch {resource_name} restricted")
    
    else if resource_type == "api-endpoint":
      if not user_has_api_key(user, resource):
        return FORBIDDEN_LAYER_4(reason="API credentials missing")
    
    else:
      pass layer 4
  
  All layers passed:
    return APPROVED(layers_passed=[1,2,3,4])
```

## Test Cases (Phase 1b MVP)

### Happy Path Tests
- **Test 1.1**: User in allowed group, passes all layers
- **Test 1.2**: User with MFA, passes all layers
- **Test 1.3**: Multiple groups, at least one matches

### Layer 1 Tests (Group Membership)
- **Test 2.1**: User not in any allowed group → FORBIDDEN_LAYER_1
- **Test 2.2**: User in one of multiple allowed groups → PASS
- **Test 2.3**: Empty groups list on policy (open skill) → PASS

### Layer 2 Tests (Role + MFA)
- **Test 3.1**: User role insufficient → FORBIDDEN_LAYER_2
- **Test 3.2**: MFA required but user not validated → FORBIDDEN_LAYER_2
- **Test 3.3**: MFA not required, user lacks it → PASS
- **Test 3.4**: User role exactly matches minimum → PASS
- **Test 3.5**: User role exceeds minimum → PASS

### Layer 3 Tests (Tool Permissions)
- **Test 4.1**: Tool not in allowed list → FORBIDDEN_LAYER_3
- **Test 4.2**: File path in blocked_paths → FORBIDDEN_LAYER_3
- **Test 4.3**: File path in allowed_paths → PASS
- **Test 4.4**: Multiple tools, all allowed → PASS
- **Test 4.5**: Multiple tools, one blocked → FORBIDDEN_LAYER_3

### Layer 4 Tests (Resource Access)
- **Test 5.1**: Branch not in allowed_branches → FORBIDDEN_LAYER_4
- **Test 5.2**: Branch in allowed_branches → PASS
- **Test 5.3**: Resource type not recognized → PASS (conservative: unknown resources not blocked)

### Edge Cases
- **Test 6.1**: Null/missing mfa_validated field → treat as false
- **Test 6.2**: Empty user groups → no matches → FORBIDDEN_LAYER_1
- **Test 6.3**: Policy with no resource restrictions → PASS

## Phase 2 Integration Points (Future)

- **Entra Integration**: Replace local group/role checks with Entra AD queries
- **Conditional Access Policies**: Device compliance, IP ranges, risk assessment
- **API Key Management**: Vault integration for tool-level credentials
- **Audit Logging**: Integration with telemetry-logger (Phase 1c)

---

**Status**: Phase 1b MVP. Core logic: 4-layer decision tree with deterministic rules.

**Dependencies**:
- `config/authorization.yaml` (policy definitions)
- `config/auth.yaml` (dev credentials)
- pyyaml (config loading)
- dataclasses (output serialization)

**Entry Point**: `AuthValidator.evaluate(user_identity, skill_name, resource) → AuthValidationResult`
