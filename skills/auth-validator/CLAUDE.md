# Auth Validator: Decision Logic
**Specs Version**: v1.0

## Purpose

Verify current operator has authorization to perform git operations before any state change occurs.

## Design Principle: Fail Early

- Check credentials **before** staging/committing
- If auth fails, operator knows immediately
- No wasted work; clear error message

## Phase 1 Reasoning

**Question**: "Am I authorized to push?"

**Answer** (check these, in order):

1. **Is git installed?** → No → Exit with "git not found"
2. **Is user.name set?** → No → Exit with "config user.name"
3. **Is user.email set?** → No → Exit with "config user.email"
4. **Is origin remote reachable?** → No → Exit with "origin not found"
5. **Can I authenticate?** → No → Exit with "can't authenticate"

If all checks pass → Confidence 0.99 → Return PASS

## Phase 2 Enhancement

Integrate with Aspire service:
- Check token expiry
- Verify MFA if required
- Validate permission scope

Result: Same interface, richer checks.

## Confidence Scoring (Phase 2)

```
Local checks: 0.99 confidence (very reliable)
Aspire token: 0.95 confidence (can expire)
MFA status: 0.98 confidence
Overall: min(confidences)
```

## Graceful Degradation

**If Aspire service down** (Phase 2):
- Fall back to local checks
- Log "Aspire unavailable; using local auth"
- Confidence: 0.85 (lower; can't verify token)
- Decide: Block if operator wants full auth, pass if local OK

---

**Status**: Phase 1 logic implemented; Phase 2 design ready.
