# Triage Delegation Model

**Resolved answer to Q11 from `AGENT-IDENTITY-INTEGRATION.md`**

---

## Overview

Triage is not a scaled-down executor. It is a **complementary capability tier** designed for
diagnosis, remediation, and retry coordination. Its secret bundle is independently declared and
independently revocable — it does not inherit from, nor is it scoped down from, the executor bundle.

The mental model is **SRE/DevOps on-call triage**: the on-call engineer reads broadly (logs,
runbooks, vendor docs) and applies targeted mitigations (config fix, retry, env var injection)
without modifying code or touching production data.

---

## Role Asymmetry: Executor vs. Triage

| Dimension | Executor | Triage |
|-----------|----------|--------|
| Manifest | Narrow, action-focused | Broad, diagnostic + remediation |
| Read access | Own task inputs only | Case vault, logs, history, vendor docs (MCP) |
| Write access | Outcome log only | Execution context (env vars, wrappers, retry schedule) |
| Code writes | Blocked | Blocked |
| Production data | Blocked | Blocked |
| Spawn agents | Blocked | Blocked (escalates to human SME or rockbot) |
| TTL | Short (task-scoped) | Longer (investigation-scoped) |
| Bundle origin | Independent manifest | Independent manifest |
| Authentication | `ISecretsProvider.GetBundleAsync(executor-manifest)` | `ISecretsProvider.GetBundleAsync(triage-manifest)` |

---

## Bundle Definition

```
TriageBundle {
    // Read: Diagnostics & History
    read: case-vault/*               // All failure cases and historical solutions
    read: execution-logs/*           // Logs from failed executor runs
    read: diagnostic-traces/*        // Error stacks, metrics, performance data

    // Read: Precedents & Learned Patterns
    read: previous-solutions/*       // What fixes worked before
    read: pattern-store/*            // SRCGEEE learned patterns (Evaluate outputs)

    // Read: Live Vendor Knowledge (via MCP)
    call: MCP_VENDOR_DOCS            // OpenAI, Azure, AWS, etc. schemas (always current)
    call: vendor-api-reference       // Direct API calls to fetch live vendor schema

    // Write: Execution Context ONLY
    write: execution-context/env-vars
    write: execution-context/command-wrappers
    write: execution-context/retry-schedule
    write: execution-context/package-manager  // Can trigger 'pip install' / 'npm install'
    write: triage-log/*              // Record of diagnosis, fix applied, retry outcome

    // Control: Scheduling & Escalation
    call: scheduler.retry-executor   // Invoke executor with modified context
    call: escalate-to-hitl           // Route novel/high-risk failures to human SME
    call: escalate-to-rockbot        // Phase 3b: route complex failures to rockbot once it is
                                     //           no longer hollow (SRCGEEE-filled capability)

    // Blocked (enforced at both manifest and vault policy levels)
    BLOCKED: write: executor-code
    BLOCKED: write: production-data
    BLOCKED: write: executor-persistent-state
    BLOCKED: call: arbitrary-external-apis
    BLOCKED: spawn: new-agents
}
```

---

## Stop-the-Bleeding Fix Categories

### Category 1 — Platform/Shell Mismatch (Low Risk)

**Pattern:** Executor fails due to platform/environment mismatch.

```
Executor fails: "python not found"
↓
Triage detects: Windows/WSL shell mismatch (PowerShell vs bash terminal)
↓
Triage injects: command wrapper (use 'py' on Windows, 'python3' on Linux)
↓
Triage schedules: executor retry with updated context
↓
Executor retries with correct command → SUCCESS
↓
Evaluate learns: "Windows detection → use 'py' wrapper"
Evolve: next executor manifest includes defensive shell wrapper
```

**L6 decision:** Auto-approve. Context change only; no code modified.

---

### Category 2 — Transient Infrastructure Failure (Low-Medium Risk)

**Pattern:** Executor fails due to intermittent infrastructure.

```
Executor fails: "Connection timeout" on database read
↓
Triage detects: transient network error (not permanent failure)
↓
Triage schedules: cron retry — 30s delay, max 3 attempts, exponential backoff
↓
Executor runs again with identical inputs → SUCCESS (DB recovered)
↓
Evaluate learns: "This DB operation is flaky; consider timeout config"
Evolve: next executor includes increased timeout or retry logic
```

**L6 decision:** Auto-approve. No code change; scheduled retry only.

---

### Category 3 — Vendor API/SDK Drift (Medium Risk — L6 Gated)

**Pattern:** Executor fails because a vendor changed their API or SDK.

```
Executor fails: "POST /v1/chat/completions returns 404"
↓
Triage calls: MCP_VENDOR_DOCS.query("openai", "chat-completions-endpoint", "current-version")
↓
MCP returns: {
  "deprecated": "/v1/chat/completions",
  "current":    "/v1/chat/legacy-endpoint",
  "reason":     "V1.10 migration — backward compat endpoint",
  "migration":  "..."
}
↓
Triage updates execution context: API_ENDPOINT = "/v1/chat/legacy-endpoint"
↓
[L6 GATE]: Is this fix attestable? Low-risk or novel?
  ✅ Documented vendor change → approve, proceed to retry
  ⚠️ Undocumented endpoint → escalate to human SME for HITL approval
↓
Executor retries with updated endpoint → SUCCESS
↓
Evaluate learns: "OpenAI endpoint changed; requires vendor doc monitoring"
Evolve: next executor includes fallback endpoint discovery or MCP vendor-docs tool call
```

**L6 decision:** Approve if attestable from vendor docs. Escalate if endpoint is undocumented.

---

### Category 4 — Missing or Uninjected Secrets (Low Risk)

**Pattern:** Executor fails because an expected env var was not injected at startup.

```
Executor fails: "API_KEY not found in environment"
↓
Triage detects: missing env var (not a code bug — provisioning gap)
↓
Triage fetches: standard value from vault using its own bundle (read: secret/config/*)
↓
Triage injects: API_KEY=$vault_value into executor context
↓
Executor retries → SUCCESS
↓
Evaluate learns: "This API key should be auto-injected; update onboarding"
Evolve: next executor provisioning includes standard env var injection
```

**L6 decision:** Auto-approve. Value sourced from vault (auditable), not hardcoded.

---

## The Retry Contract

When triage applies a fix and schedules a retry, the following contract governs the attempt sequence.
Delay values and attempt counts are per-manifest configurable; the values below are defaults.

```
Attempt 1: Immediate — same inputs + triage fix applied
Attempt 2: +30s (default) — if still failing, escalate timeout or widen fix
Attempt 3: +60s (default) — if still failing, escalate to human SME

If Attempt 3 fails, escalate package contains:
  ├── Original failure (error, stack trace, context)
  ├── Triage diagnosis (root cause assessment)
  ├── Fix applied (documented — what changed, why)
  ├── All retry attempt outcomes (logged)
  └── Triage recommendation (if any pattern match exists)
```

**If any retry succeeds:**
- Result proceeds to Evaluate phase
- Evaluate pattern-matches: "failure type → fix type → success"
- Evolve updates future executor manifest with the learned pattern

**If all retries fail:**
- Escalate to human SME
- SME has full diagnosis package — no repeat investigation needed
- SME can: approve a novel fix, write a new triage rule, update the executor manifest,
  or route to rockbot for deeper investigation

---

## L6 Gate Policy

The L6 risk gate evaluates every triage fix before the retry is scheduled:

### Auto-Approve
- Shell command wrapping (PowerShell ↔ WSL ↔ bash)
- Env var injection sourced from vault
- Retry scheduling (no code change, identical inputs)
- Standard SDK/package version bumps (within 1-2 minor versions, no breaking changes)
- Documented vendor API endpoint changes (attested by MCP vendor docs)

### Escalate to HITL
- Triage wants to modify executor code logic
- Triage wants to change an API endpoint to an undocumented one
- Triage wants to call an external API not declared in the triage manifest
- Triage wants to downgrade a package version (potential security implications)
- The proposed fix conflicts with a security policy in the blocked list

### Reject
- Any write to production data or production state
- Any write to executor persistent storage
- Any spawning of new agents without explicit human authorization
- Any fix that requires modifying the triage manifest itself at runtime
  *(rationale: runtime manifest self-modification is a privilege escalation path — triage
  could bootstrap expanded permissions for itself; the manifest must be committed and
  attested as a code artifact, not written at runtime)*

---

## Bundle Inheritance Answer

Triage authenticates **independently** to `ISecretsProvider` with its own manifest. It does not
inherit, receive a scoped copy of, or derive from the executor's bundle.

This is Option B from the design session (independent authentication with independently-declared
broader scope), selected because:

1. **Revocability is independent** — the parent can revoke triage without affecting executor,
   and vice versa
2. **Audit is clean** — each principal's vault access is independently logged; triage and
   executor accesses do not appear in the same audit trail entry
3. **Scope is explicit** — triage's broader read access and execution-context write access is
   declared in its own manifest, not implied by inheritance
4. **No scope creep via inheritance** — a scoped-down copy of the executor bundle would give
   triage executor-like secrets it doesn't need (e.g., external API keys for direct execution)

The triage manifest is committed alongside the bot code and is subject to the same SLSA
attestation requirements as the executor manifest (Phase 3a).

---

## SRCGEEE Phase Mapping

| Phase | Executor | Triage |
|-------|----------|--------|
| Sense | Input received; principal authenticated | — |
| Retrieve | Executor bundle fetched from vault | Triage bundle fetched from vault |
| Compose | Task composed from inputs | Triage diagnosis composed from logs + history |
| Gate | L6 evaluates executor intent | L6 evaluates triage fix before retry |
| Execute | Task executed against external systems | Retry scheduled; executor re-runs |
| Evaluate | Outcome logged to EventLedger | Triage diagnosis + fix logged to EventLedger |
| Evolve | — | Pattern from Evaluate → manifest update for next executor generation |

---

## Fast Feedback Loop

Active triage reduces self-improvement latency from hours to minutes:

**Without active triage (slow loop):**
```
Day 1: Executor fails → Evaluate logs it → Evolve updates manifest
Day 2: Next executor run uses updated manifest → may work
```

**With active triage (fast loop — nominal path, no HITL required):**
```
T+0:00  Executor fails
T+0:01  Triage diagnoses root cause + applies context fix
T+0:02  Executor retries → SUCCESS
T+0:03  Evaluate learns the fix pattern
T+0:04  Evolve updates executor manifest for next run
```

Feedback latency: reduced from ~24 hours to ~5 minutes (nominal).
When HITL is required (L6 escalation), the loop pauses until the human SME approves;
the learning still completes once escalation resolves.

---

## Open Questions Remaining

These are deferred to Phase 2b/3a and should be tracked in `unified-auth-spec-v0.2.md` Section 14:

- **Sub-agent TTL arithmetic**: When triage TTL expires mid-investigation but the executor
  retry is still pending, should the retry be cancelled or allowed to complete against the
  already-issued bundle?
- **Triage manifest versioning**: As triage learns new fix patterns, its manifest evolves.
  What is the deployment atomicity requirement for triage manifest updates?
- **Rockbot escalation path** *(Phase 3b)*: When triage escalates to rockbot instead of a
  human SME, what are rockbot's authorization boundaries? Can rockbot modify the triage
  manifest? This question is deferred until rockbot has been filled by SRCGEEE and has
  attest-level trust; for now, the escalation path is human SME only.
