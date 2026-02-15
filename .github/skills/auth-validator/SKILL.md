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
  "confidence": 1.0
}
```

## Phase 1b Logic

Validates across 4 authorization layers with deterministic decision tree.

**Status**: Phase 1b MVP. Core logic: 4-layer decision tree with deterministic rules.
