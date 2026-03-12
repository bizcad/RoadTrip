# Unified Authentication & Authorization Specification

**Project**: Purushottama Personal Assistant (PPA)
**Version**: 0.1-draft
**Date**: 2026-03-04
**Status**: Draft for review and discussion
**Author**: Nick Stein + Claude

---

## 1. Purpose

Define a single identity and authorization framework where **humans, agents, and code** are all first-class security principals. Every business decision made within the PPA ecosystem must be:

- **Precise**: The exact principal, action, resource, and context are known.
- **Traceable**: A complete audit trail links every decision to an identity chain.
- **Enforceable**: Policy violations are blocked deterministically before execution.

This spec unifies the existing Phase 1b auth-validator (4-layer model) with the broader PPA architectural vision (27 principles, SRCGEEE lifecycle, zero-trust agents).

---

## 2. Definitions

| Term | Meaning |
|------|---------|
| **Principal** | Any entity that can authenticate, be authorized, and take actions: human, agent, or code artifact. |
| **Human Principal** | A person with OIDC/password/MFA credentials (e.g., `bizcad`). |
| **Agent Principal** | An AI agent, background worker, orchestrator, or autonomous process with a workload identity. |
| **Code Principal** | A signed, attested code artifact (script, skill, tool) with provenance metadata. |
| **Delegation** | An explicit, scoped, time-boxed grant from one principal to another (e.g., human delegates to agent). |
| **PDP** | Policy Decision Point: the engine that evaluates allow/deny given principal + action + resource + context. |
| **PEP** | Policy Enforcement Point: the gateway/middleware/wrapper that calls the PDP and enforces the decision. |
| **SRCGEEE** | Sense, Retrieve, Compose, Gate, Execute, Evaluate, Evolve. The PPA pattern lifecycle. Pronounced "CIRC-gee". |
| **HITL** | Human In The Loop. Required for irreversible, high-risk, or spend actions. |
| **Provenance** | Verifiable chain of custody for a code artifact: who created it, how, when, with what tools. |

---

## 3. Design Principles

These derive from the 27 architectural principles and prior RBAC sessions.

### 3.1 Every Actor Is a Security Principal
No exceptions. Humans, agents, skills, scripts, and pipelines all carry identity. If something takes an action, it has a principal record.

### 3.2 Zero Trust by Default
- Every request is authenticated. No ambient authority.
- Short-lived credentials. No long-lived secrets outside vaults.
- Continuous evaluation, not one-time gate.

### 3.3 Least Privilege, Always
- Agents start with zero tools and zero permissions.
- Permissions are granted explicitly per delegation, per scope, per time window.
- Default deny. Every allow is an explicit policy statement.

### 3.4 Deterministic Authorization
- Same inputs always produce the same decision.
- No probabilistic or ML-based auth decisions. Auth is deterministic code (principle #1: AI figures out what to do, code does the work).
- Policies are version-controlled, tested, and deployed via CI/CD.

### 3.5 Human Governance at the Gate
- HITL is required for: irreversible actions, spend, reputation risk, unknown domains.
- Principle #26: Do not spend money, tokens, time, reputation, or other non-recoverable resources without HITL.
- Principle #27: Help is preferable to failure.

### 3.6 Traceable Decisions
- Every authorization decision is logged with: principal, action, resource, context, decision, reason, timestamp.
- Telemetry feeds into the Evaluate and Evolve phases of SRCGEEE.

### 3.7 Code as a Trusted (or Untrusted) Principal
- Code artifacts carry provenance (who made them, signed or not, test status).
- Unsigned or unattested code is untrusted by default.
- Supply chain trust: TDD, SOLID, reproducible results, fingerprinting (principle #7).

---

## 4. Principal Model

All three principal types share a common identity envelope with type-specific attributes.

### 4.1 Common Identity Envelope

Every principal carries:

| Field | Type | Description |
|-------|------|-------------|
| `principal_id` | string | Globally unique identifier (e.g., `human:bizcad`, `agent:rules-engine-v1`, `code:git-push-skill-1.0.3`) |
| `principal_type` | enum | `human`, `agent`, `code` |
| `display_name` | string | Human-readable name |
| `created_at` | datetime | When this principal was registered |
| `status` | enum | `active`, `suspended`, `revoked`, `expired` |
| `groups` | string[] | Group memberships for Layer 1 checks |
| `role` | string | Role assignment for Layer 2 checks |
| `role_rank` | integer | Numeric rank for comparison (1=lowest) |
| `trust_level` | enum | `untrusted`, `basic`, `verified`, `attested` |
| `credential_type` | string | How this principal authenticates |
| `delegation_chain` | DelegationRecord[] | Who delegated authority to this principal |
| `metadata` | object | Type-specific attributes (see below) |

### 4.2 Human-Specific Attributes

```yaml
metadata:
  mfa_validated: true
  mfa_method: "totp"          # totp | webauthn | sms | none
  session_id: "sess_abc123"
  session_expires_at: "2026-03-04T18:00:00Z"
  ip_address: "192.168.1.100" # For risk scoring (Phase 2+)
  device_trust: "managed"     # managed | personal | unknown
  github_user: "bizcad"
  email: "bizcad@example.com"
```

### 4.3 Agent-Specific Attributes

```yaml
metadata:
  agent_version: "1.0.3"
  runtime: "claude-code"        # claude-code | python | powershell | github-actions
  model_id: "claude-opus-4-6"   # If LLM-backed; null for deterministic agents
  spawn_reason: "user-request"  # user-request | scheduled | event-triggered | delegated
  parent_principal: "human:bizcad"  # Who invoked this agent
  tools_granted: []             # Starts empty; populated by delegation
  max_autonomy_level: "supervised" # supervised | semi-autonomous | autonomous
  sandbox_id: "sandbox-2026-03-04-001"
  ttl_minutes: 60              # Agent credential lifetime
  memory_tier: "fast"          # fast | slow | extra-slow (current operating tier)
```

### 4.4 Code-Specific Attributes

```yaml
metadata:
  artifact_type: "skill"       # skill | script | tool | library | pipeline
  version: "1.0.3"
  source_repo: "bizcad/RoadTrip"
  source_commit: "5c20400"
  signed: true
  signature_method: "cosign"   # cosign | gpg | none
  provenance_level: "slsa-2"  # none | slsa-1 | slsa-2 | slsa-3
  sbom_present: true
  test_status: "passing"      # passing | failing | untested | skipped
  test_coverage_pct: 92
  author_principal: "agent:commit-message-v1"
  reviewer_principal: "human:bizcad"
  fingerprint: "sha256:abc123..."
  build_environment: "github-actions-runner-ubuntu-22.04"
```

---

## 5. Authorization Layers (Extended from Phase 1b)

The existing 4-layer model is preserved and extended to handle all three principal types. Two new layers are added for delegation and risk.

### Layer Overview

| Layer | Question | Check Type | Short-Circuit |
|-------|----------|------------|---------------|
| **L0: Identity** | Is this principal authenticated and valid? | Credential verification | Yes |
| **L1: Visibility** | Can this principal see this skill/resource? | Group membership | Yes |
| **L2: Permission** | Does the principal have the role + MFA for this action? | Role rank + MFA | Yes |
| **L3: Tool Access** | Can the principal use this specific tool on this path? | Path/action allowlists | Yes |
| **L4: Resource Access** | Can the principal access this specific resource? | Branch/API/data restrictions | Yes |
| **L5: Delegation** | If acting on behalf of another, is the delegation valid? | Scope + expiry + chain | Yes |
| **L6: Risk Gate** | Does this action require HITL or additional approval? | Risk score + reversibility | Yes (blocks until approved) |

### Layer Evaluation Order

```
L0 → L1 → L2 → L3 → L4 → L5 → L6 → APPROVED
     (fail at any layer → return FORBIDDEN_LAYER_N with reason and recovery)
```

### 5.1 Layer 0: Identity Verification (NEW)

**Purpose**: Confirm the principal is who they claim to be.

**For humans**: Valid session token, OIDC, or PAT. Not expired. MFA state checked.
**For agents**: Valid workload identity (SPIFFE SVID, ephemeral token, or API key). TTL not exceeded. Parent principal verified.
**For code**: Signature verified. Provenance chain intact. Fingerprint matches registry.

```
L0 checks:
  if principal.status != "active":
    return FORBIDDEN_L0("principal is {status}")

  if principal_type == "human":
    if session_expired(principal.metadata.session_expires_at):
      return FORBIDDEN_L0("session expired", recovery="re-authenticate")

  if principal_type == "agent":
    if agent_ttl_exceeded(principal):
      return FORBIDDEN_L0("agent credential expired", recovery="respawn agent")
    if not verify_parent(principal.metadata.parent_principal):
      return FORBIDDEN_L0("parent principal invalid")

  if principal_type == "code":
    if principal.metadata.signed == false:
      if policy.require_signed_code:
        return FORBIDDEN_L0("unsigned code", recovery="sign artifact with cosign")
    if not verify_fingerprint(principal):
      return FORBIDDEN_L0("fingerprint mismatch", recovery="rebuild from trusted source")

  pass L0
```

### 5.2 Layer 1: Visibility (Existing, Extended)

Same as Phase 1b. Now applies uniformly:
- **Humans**: `user.groups` intersects `skill.allowed_groups`
- **Agents**: `agent.groups` (inherited from parent + explicitly granted) intersects `skill.allowed_groups`
- **Code**: Code principals inherit the group context of the invoking agent or human.

### 5.3 Layer 2: Permission (Existing, Extended)

Same role + MFA check. Extended:
- **Agents**: Role is inherited from delegation or explicitly assigned. MFA is inherited from the delegating human's MFA status at delegation time.
- **Code**: Role is the minimum of (author role, reviewer role, invoking principal role).

### 5.4 Layer 3: Tool Access (Existing)

Unchanged. Path allowlists and blocklists apply regardless of principal type.

### 5.5 Layer 4: Resource Access (Existing)

Unchanged. Branch, API, and data restrictions apply uniformly.

### 5.6 Layer 5: Delegation Verification (NEW)

**Purpose**: When an agent or code acts on behalf of another principal, verify the delegation chain.

```
L5 checks:
  if principal has delegation_chain:
    for each delegation in chain:
      if delegation.expired:
        return FORBIDDEN_L5("delegation expired at {expiry}")
      if requested_action not in delegation.allowed_actions:
        return FORBIDDEN_L5("action {action} not in delegated scope")
      if requested_resource not in delegation.allowed_resources:
        return FORBIDDEN_L5("resource {resource} not in delegated scope")
      if delegation.grantor.status != "active":
        return FORBIDDEN_L5("grantor principal revoked")

    pass L5 (delegation chain valid)

  else if principal_type == "agent" and policy.require_delegation:
    return FORBIDDEN_L5("agent has no delegation", recovery="request delegation from human")

  else:
    pass L5 (no delegation required or principal is human acting directly)
```

### 5.7 Layer 6: Risk Gate (NEW)

**Purpose**: Evaluate whether the action's risk level requires additional approval.

```
L6 checks:
  risk = calculate_risk(action, resource, context)

  risk factors:
    - irreversibility: {low: 0, medium: 20, high: 40, critical: 60}
    - spend_impact:    {none: 0, low: 10, medium: 25, high: 50}
    - reputation_risk: {none: 0, low: 10, medium: 25, high: 50}
    - blast_radius:    {self: 0, team: 10, org: 30, public: 50}
    - novelty:         {routine: 0, known: 10, novel: 30, unknown: 50}

  risk_score = weighted_sum(factors) normalized to 0-100

  if risk_score >= policy.hitl_threshold (default: 60):
    if not context.human_approval_present:
      return PENDING_L6("HITL required", risk_score=risk_score)
    else:
      pass L6 (human approved)

  if risk_score >= policy.elevated_logging_threshold (default: 30):
    flag_for_enhanced_audit()
    pass L6

  pass L6
```

---

## 6. Delegation Model

Delegation is the mechanism by which one principal grants scoped authority to another.

### 6.1 Delegation Record

```yaml
delegation:
  delegation_id: "del-2026-03-04-001"
  grantor: "human:bizcad"            # Who grants
  grantee: "agent:git-push-v1"      # Who receives
  granted_at: "2026-03-04T10:00:00Z"
  expires_at: "2026-03-04T11:00:00Z" # Max 1 hour for Phase 1

  scope:
    skills: ["git-push-autonomous"]
    actions: ["stage", "commit", "push"]
    resources:
      - type: "git-branch"
        pattern: "feature/*"
      - type: "file-path"
        pattern: "src/**"
    excluded_resources:
      - type: "file-path"
        pattern: "secrets/**"

  constraints:
    max_operations: 10              # Max number of actions before re-delegation
    require_dry_run_first: true     # Must succeed in dry-run before live execution
    allow_sub_delegation: false     # Grantee cannot delegate further
    require_audit_log: true         # All actions must be logged

  approval:
    method: "explicit-chat"         # explicit-chat | pre-approved-policy | mfa-confirmed
    approval_timestamp: "2026-03-04T10:00:01Z"
    approval_context: "User said 'push all changes' in Claude Code session"

  status: "active"                  # active | expired | revoked | exhausted
  revocation_reason: null
```

### 6.2 Delegation Rules

1. **Humans can delegate to agents**. Agents cannot self-delegate.
2. **Agents can invoke code**. The code inherits the agent's delegation scope (not more).
3. **Sub-delegation is off by default**. Must be explicitly enabled per delegation.
4. **Time-boxed**. Phase 1: max 1 hour. Phase 2: configurable per policy.
5. **Scope-limited**. Delegation cannot exceed the grantor's own permissions.
6. **Revocable**. Grantor can revoke at any time. Revocation is immediate.
7. **Audited**. Every delegation create/use/expire/revoke event is logged.

### 6.3 Delegation Chain Example

```
human:bizcad
  └─ delegates to agent:git-push-orchestrator
       scope: [stage, commit, push] on [feature/*] for [src/**, docs/**]
       expires: 1 hour
       │
       ├─ agent invokes code:rules-engine-v1.0
       │    (inherits scope: evaluate files in src/**)
       │    (code is signed, SLSA-2, tests passing)
       │
       ├─ agent invokes code:commit-message-v1.0
       │    (inherits scope: generate commit message)
       │
       └─ agent invokes code:auth-validator-v1.0
            (inherits scope: validate push permissions)
```

---

## 7. Trust Levels

Trust determines what a principal can do without additional verification.

| Trust Level | Meaning | Typical Principal | Can Do Without Approval |
|------------|---------|-------------------|------------------------|
| `untrusted` | Unknown or unverified | Unsigned code, unknown agent | Nothing. Blocked at L0. |
| `basic` | Authenticated but not attested | Human with password only, agent with API key | Read-only operations |
| `verified` | Authenticated + MFA or signed | Human with MFA, signed code, agent with SPIFFE SVID | Standard operations within delegation scope |
| `attested` | Full provenance chain, SLSA-3 | Code with full build provenance + signature + passing tests | Autonomous operations (still subject to risk gate) |

### Trust Escalation Path

```
untrusted → basic:    authenticate (password, API key, token)
basic → verified:     add MFA (human) or sign artifact (code) or workload attestation (agent)
verified → attested:  full provenance chain + SLSA + SBOM + test verification
```

---

## 8. Integration with SRCGEEE

Authorization is not a one-time check; it participates in every phase of the SRCGEEE (CIRC-gee) lifecycle.

| Phase | Auth Role |
|-------|-----------|
| **Sense** | Authenticate the principal initiating the request. Capture identity context. |
| **Retrieve** | Authorize memory tier access. Agents may only access memory within their delegation scope. |
| **Compose** | Verify that proposed actions are within authorized scope before planning. |
| **Gate** | **Primary enforcement point.** Run L0-L6 evaluation. HITL approval if required. This is where business decisions become enforceable. |
| **Execute** | PEP enforces the Gate decision. Token bound to execution scope. Credential expires at end. |
| **Evaluate** | Log decision outcomes. Compare actual actions vs. authorized scope. Flag drift. |
| **Evolve** | Update trust levels based on outcomes. Promote or demote principals. Adjust risk thresholds. Feed into telemetry. |

---

## 9. Audit & Telemetry Contract

Every authorization decision produces an audit record.

### 9.1 Decision Log Record

```yaml
decision_log:
  decision_id: "dec-2026-03-04-001"
  timestamp: "2026-03-04T10:05:23.456Z"

  principal:
    id: "agent:git-push-orchestrator"
    type: "agent"
    trust_level: "verified"
    delegation_chain: ["human:bizcad → agent:git-push-orchestrator"]

  request:
    action: "git-push"
    resource:
      type: "git-branch"
      name: "feature/auth-spec"
    context:
      environment: "development"
      session_id: "sess_abc123"
      srcgeee_phase: "gate"
      risk_factors:
        irreversibility: "low"
        spend_impact: "none"
        blast_radius: "self"

  evaluation:
    layers_evaluated: [0, 1, 2, 3, 4, 5, 6]
    layers_passed: [0, 1, 2, 3, 4, 5, 6]
    layers_failed: []
    decision: "APPROVED"
    risk_score: 15
    hitl_required: false
    evaluation_time_ms: 2

  outcome:
    executed: true
    success: true
    side_effects: ["commit 7a3b2c1 pushed to feature/auth-spec"]
```

### 9.2 Telemetry Dimensions

Track over time to support the Evaluate and Evolve phases:

| Metric | Description | Used For |
|--------|-------------|----------|
| `decisions_per_principal` | Count of auth decisions by principal | Anomaly detection |
| `denial_rate_by_layer` | % of denials at each layer | Policy tuning |
| `delegation_utilization` | % of delegated scope actually used | Scope tightening |
| `risk_score_distribution` | Histogram of risk scores | Threshold calibration |
| `hitl_trigger_rate` | How often HITL is invoked | Autonomy level tracking |
| `time_to_decision_ms` | Auth evaluation latency | Performance SLO |
| `trust_level_changes` | Promotions/demotions per principal | Trust system health |
| `drift_events` | Actions outside expected scope | Security monitoring |

---

## 10. Autonomy Levels

Agents operate at one of three autonomy levels, determined by delegation + risk + trust.

| Level | Label | HITL Requirement | Example |
|-------|-------|-----------------|---------|
| 1 | **Supervised** | Every action requires approval | Agent proposes, human approves each step |
| 2 | **Semi-autonomous** | Only high-risk actions need approval | Agent executes routine tasks; HITL for push-to-main, spend |
| 3 | **Autonomous** | No HITL except policy-mandated gates | Agent runs full SRCGEEE cycle; HITL only for risk_score >= threshold |

### Autonomy Determination

```
autonomy_level = min(
  delegation.max_autonomy_level,
  policy.principal_type_max_autonomy[principal_type],
  trust_based_autonomy(principal.trust_level)
)

where trust_based_autonomy:
  untrusted → 0 (blocked)
  basic     → 1 (supervised)
  verified  → 2 (semi-autonomous)
  attested  → 3 (autonomous, subject to risk gates)
```

---

## 11. Phase Roadmap

### Phase 1b (Current): Local Deterministic Auth
- **Status**: Implemented for git-push-autonomous
- **Principals**: Human only (bizcad), static config
- **Layers**: L1-L4 operational
- **Delegation**: Implicit (user runs skill = delegation)
- **Risk**: No formal risk scoring
- **Storage**: YAML config files
- **Provenance**: None

### Phase 2a: Unified Principal Registry
- Add L0 (identity verification) and L5 (delegation)
- Implement principal model for all three types
- Explicit delegation records with scope and expiry
- Agent principals with TTL and parent tracking
- Code principals with signature verification
- Local SQLite or YAML registry

### Phase 2b: Risk-Adaptive Gates
- Add L6 (risk gate)
- Risk scoring formula with configurable weights
- HITL integration: pause execution, request approval, resume
- Autonomy level calculation and enforcement

### Phase 3a: Supply Chain Trust
- Code signing with cosign/GPG
- Provenance tracking (SLSA attestations)
- SBOM generation and policy enforcement
- Trust level promotion based on provenance
- Fingerprint registry for known-good artifacts

### Phase 3b: External Identity Integration
- Replace local user config with Entra AD / OIDC
- SPIFFE/SPIRE for agent workload identities
- OAuth 2.0 Token Exchange (RFC 8693) for delegation
- Short-lived, proof-of-possession bound tokens

### Phase 4: Policy-as-Code Engine
- OPA or Cedar policy engine
- SpiceDB for relationship-based access control
- Policy CI/CD: version, test, deploy, rollback
- Shadow mode for policy changes before enforcement

### Phase 5: Learning & Optimization
- Telemetry-driven policy tuning
- Trust level auto-adjustment based on track record
- Anomaly detection for principal behavior drift
- Access review workflows

---

## 12. Compatibility with Existing Infrastructure

### 12.1 Existing Auth-Validator Skill

The current 4-layer model (`config/authorization.yaml`) maps directly:

| Current | Unified Spec |
|---------|-------------|
| Layer 1 (Group Membership) | L1: Visibility (unchanged) |
| Layer 2 (Role + MFA) | L2: Permission (unchanged) |
| Layer 3 (Tool Permissions) | L3: Tool Access (unchanged) |
| Layer 4 (Resource Access) | L4: Resource Access (unchanged) |
| (not present) | L0: Identity Verification (new) |
| (not present) | L5: Delegation (new) |
| (not present) | L6: Risk Gate (new) |

### 12.2 Existing Skills Framework

| Skill | Auth Integration |
|-------|-----------------|
| `git-push-autonomous` | Full L0-L6 evaluation. Orchestrates sub-skill auth. |
| `auth-validator` | Becomes the PDP implementation. Extended with L0, L5, L6. |
| `rules-engine` | Operates within L3 (tool access). Code principal with provenance. |
| `commit-message` | Operates within delegation scope. Agent principal. |
| `telemetry-logger` | Records L0-L6 decisions. Feeds Evaluate phase. |
| `blog-publisher` | L6 risk gate for public publishing (reputation risk). |

### 12.3 Existing Config Files

| File | Role |
|------|------|
| `config/authorization.yaml` | L1-L4 policy definitions (preserved, extended) |
| `config/safety-rules.yaml` | L3 file-level rules (preserved) |
| `config/telemetry-config.yaml` | Audit log configuration (extended) |
| `config/auth.yaml` | Dev credentials (Phase 2: replaced by identity provider) |

---

## 13. Threat Model (Key Scenarios)

| Threat | Mitigation |
|--------|-----------|
| Agent escalates own permissions | Delegation is immutable; agent cannot modify its own delegation record. L5 checks chain integrity. |
| Stolen agent token used elsewhere | Tokens are PoP-bound (DPoP/mTLS in Phase 3b). TTL limits exposure window. |
| Unsigned code injected into pipeline | L0 blocks unsigned code when `policy.require_signed_code = true`. |
| Human account compromised | MFA required at L2. Session TTL limits window. Anomaly detection in Phase 5. |
| Agent acts beyond delegated scope | L5 checks every action against delegation.allowed_actions and delegation.allowed_resources. |
| High-risk action without oversight | L6 risk gate requires HITL for risk_score >= threshold. Cannot be bypassed by agent. |
| Delegation chain too deep | Policy limit on chain depth (default: 2). Sub-delegation off by default. |
| Stale trust levels | Evolve phase adjusts trust based on telemetry. Access reviews in Phase 5. |

---

## 14. Open Questions for Discussion

1. **Principal registration**: Should agents self-register, or must a human explicitly register every agent principal?

2. **Delegation UX**: What does delegation look like in practice? Is "push all changes" in chat sufficient, or do we need a more formal approval flow?

3. **Code trust bootstrapping**: How do we establish trust for the first code artifacts before provenance infrastructure exists? Manual review + human attestation?

4. **Cross-repo delegation**: Can a delegation in RoadTrip grant access to roadtrip-blog, or are delegations always repo-scoped?

5. **Offline/disconnected mode**: What happens when the PDP is unreachable? Fail-closed (block everything) or cached-decision mode?

6. **Token storage**: Phase 1 uses `ProjectSecrets/PAT.txt`. What is the migration path to vault-based storage without breaking current workflows?

7. **Granularity of code principals**: Is every file a code principal, or only packaged skills/tools? What about ad-hoc scripts?

8. **Multi-model agent identity**: When an agent switches models (e.g., haiku for fast tasks, opus for complex ones), does the principal identity change?

9. **Risk weight calibration**: How should risk weights be calibrated initially? Expert judgment, historical incidents, or both?

10. **Revocation propagation**: When a human revokes a delegation, how quickly must all downstream agents stop? Immediate (pull model) or next-check (TTL model)?

---

## 15. Supporting Files

| File | Format | Purpose |
|------|--------|---------|
| `principal-identity.schema.json` | JSON Schema | Machine-readable contract for the principal identity model |
| `unified-auth-policy-model.yaml` | YAML | Example unified policy configuration showing all 7 layers |
| `principal-capability-matrix.csv` | CSV | Quick-reference matrix: who can do what at each trust level |

---

## 16. References

- Session Log 2026-03-03: RBAC for Agents and Humans (Zanzibar, SpiceDB, SPIFFE/SPIRE architecture)
- Session Log 2026-03-04: Pattern Recommender Spec, SRCGEEE lifecycle
- `skills/auth-validator/SKILL.md`: Existing 4-layer auth model
- `config/authorization.yaml`: Current policy configuration
- `PPA/spec/pattern_recommender_spec_v0_1.md`: SRCGEEE and governance integration
- Nick's 27 Architectural Principles (Session Log 2026-03-03, lines 224-277)
- RFC 8693: OAuth 2.0 Token Exchange
- SLSA Framework (Supply-chain Levels for Software Artifacts)
- Sigstore/cosign (keyless code signing)
- SPIFFE/SPIRE (workload identity)
- Google Zanzibar / SpiceDB (relationship-based access control)
