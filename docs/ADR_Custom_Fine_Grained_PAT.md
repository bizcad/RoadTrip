# ADR: Custom Fine-Grained PAT for RoadTrip Automation

**Status**: Accepted  
**Date**: February 8, 2026  
**Decision**: Use custom fine-grained GitHub PAT scoped to `bizcad/RoadTrip` repo only  

---

## Context

RoadTrip needs automated git operations (stage, commit, push) for agentic workflows. This requires authentication credentials that work silently (no interactive prompts).

**Question**: Should we use:
- A) Custom fine-grained PAT (scoped to RoadTrip only, 90-day expiration)
- B) Reuse existing personal PAT (higher permissions, no expiration)
- C) GitHub App (higher security, more complex setup)
- D) Alternate token types (SSH deploy keys, OAuth tokens)

---

## Decision

**Use option A**: Custom fine-grained Personal Access Token, specifically for this automation.

### Why (from GitHub's recommendation)

| Criterion | Custom PAT | Reuse Personal | GitHub App |
|-----------|-----------|-----------------|-----------|
| **Least Privilege** | ✅ Scoped to RoadTrip only | ❌ Full account access | ✅ Best available |
| **Rotation** | ✅ Easy (revoke just this token) | ❌ Risky (revokes all access) | ✅ Supported |
| **Auditability** | ✅ Named "1-Button Automation" | ❌ Mixed with personal use | ✅ Named & logged |
| **Time-Limited** | ✅ 90-day default | ❌ Indefinite | ✅ Configurable |
| **Setup Complexity** | ✅ 5 minutes | ✅ ~2 minutes | ❌ ~30 minutes |
| **Security Risk** | ✅ Low (isolated scope) | ❌ High (full account) | ✅ Low (isolated app) |
| **Operational Load** | ✅ Rotation every 90 days | ❌ No rotation needed | ✅ Quarterly review |

**Recommendation from GitHub**: *"You should definitely create a separate, custom Personal Access Token specifically for this automation skill, rather than reusing any existing PAT."*

---

## Implementation

### PAT Configuration

```yaml
Token Name:      RoadTrip 1-Button Push Automation
Type:            Fine-grained (not classic)
Repository:      bizcad/RoadTrip only
Permissions:
  - Contents:    Read and Write (needed for git push)
  - Metadata:    Read (auto-included)
Expiration:      90 days
Rotation:        Quarterly (calendar reminder)
Storage:         Windows Credential Manager (encrypted per-user)
Access:          Via src/skills/token_resolver.py
```

### Security Model

**Principle**: If compromised, damage is limited to RoadTrip repo, time-limited to 90 days.

```
┌─────────────────────────────────────────────┐
│ GitHub Account (full access, never shared)  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Fine-Grained PAT     │
        │ (scoped, time-bound) │
        └──────────┬───────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Windows Credential Manager       │
    │ (encrypted, per-user)            │
    └──────────┬───────────────────────┘
               │
               ▼
    ┌──────────────────────────────────┐
    │ token_resolver.py (skill)        │
    │ (retrieves at runtime, logs only │
    │  metadata, not token)            │
    └──────────────────────────────────┘
```

### Consequences

**Advantages**:
- ✅ Complies with principle of least privilege
- ✅ Can revoke instantly if compromised
- ✅ Easier to audit (scope is explicit)
- ✅ GitHub natively supports fine-grained PATs
- ✅ No additional infrastructure needed
- ✅ Works with existing token_resolver skill

**Disadvantages**:
- ❌ Must rotate every 90 days (quarterly task)
- ❌ Only scoped to single repo (need separate token per org)
- ❌ Still requires secure storage (Windows Credential Manager)

---

## Alternatives Considered

### Option B: Reuse Existing Personal PAT

**Why rejected**:
- ❌ Violates least privilege (full account access)
- ❌ If leaked, attacker has all GitHub access
- ❌ Can't revoke just the automation without revoking everything
- ❌ No expiration (becomes stale security wise)
- ❌ Harder to audit (mixed with personal use)

**Use case**: For personal tools you fully control and understand

### Option C: GitHub App

**Why deferred** (Phase 2):
- ✅ Better security and audit trail
- ✅ Can be shared with other developers/tools
- ✅ Supports organization-wide access policies
- ❌ 30-minute setup vs. 5 minutes for custom PAT
- ❌ Overkill for single-repo POC
- Plan: If RoadTrip becomes shared/public tool, migrate to GitHub App

**Use case**: For tools that will be used across teams, or published publicly

### Option D: Other Token Types

**SSH Deploy Keys**: 
- ❌ Only grant read access (can't push)
- ❌ Repository-specific (not account-level)
- ✅ Considered for future read-only skills

**OAuth Tokens**:
- ❌ Require user interactive flow (no silent auth)
- ✅ Better for user-facing apps

---

## Decision Rationale

This is **pragmatic and secure**:

1. **For the POC Phase**: Custom fine-grained PAT is the right balance of security and simplicity
2. **Based on expert advice**: GitHub's official recommendation (via Copilot)
3. **Built into our architecture**: token_resolver.py is PAT-agnostic, works with any backend
4. **Future-proof**: Can migrate to GitHub App later without changing code
5. **Auditable**: All decisions and token metadata logged, never the token itself

---

## Implementation Checklist

- [x] Design token resolver skill (generic, backend-agnostic)
- [x] Create Windows Credential Manager storage backend
- [x] Create PowerShell setup script (setup-github-credentials.ps1)
- [x] Create authenticated git push wrapper (invoke-git-push-with-token.ps1)
- [x] Document best practices (Token_Management_for_Silent_Auth.md)
- [x] Create quick start guide (Token_Setup_Quick_Start.md)
- [ ] Add token rotation reminder (Phase 2)
- [ ] Add GitHub App alternative option (Phase 2)
- [ ] Add cross-platform support (macOS Keychain, Linux stores) (Phase 2)

---

## Blog Post Opportunities

This decision opens three interesting narratives:

1. **"How to Securely Automate Git Operations"**
   - Custom PATs as a security pattern
   - Principle of least privilege in practice
   - Token rotation as a feature, not overhead

2. **"Three Paths to Secure Credential Storage"**
   - PAT option (pragmatic for dev)
   - Entra/RBAC (enterprise scale)
   - GitHub App (at scale, public tools)
   - Trade-offs at each level

3. **"Token Management in Agentic Workflows"**
   - How to architect credential handling for AI skills
   - Keeping tokens out of logs/commits
   - Audit trails without exposing secrets
   - Integrating with Verified Agentic Work (VAW)

---

## References

- [GitHub Fine-Grained PAT Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/best-practices-for-using-github-securely)
- [Token Lifetime Management](Token_Management_for_Silent_Auth.md)
- [Quick Start Setup](Token_Setup_Quick_Start.md)

---

**Decision made**: February 8, 2026  
**Approval**: RoadTrip Core Team  
**Status**: Active (implementing Phase 1b)
