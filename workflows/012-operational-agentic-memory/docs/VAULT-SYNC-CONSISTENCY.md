# Vault Sync Consistency

**Resolved answer to Q1 (vault sync) from `docs/AGENT-IDENTITY-INTEGRATION.md`**

---

## Decision Summary

| Question | Decision |
|----------|----------|
| Primary vault | Azure Key Vault (AKV) |
| Backup vault | HashiCorp Vault OSS on a cheap VPS (Fly.io or Hetzner, ~$4/mo) |
| Sync trigger | `sync-secrets.py` on git push (deployment pipeline only) |
| Reconciliation job | None in Phase 1/2a |
| Drift detection | Natural — stale key → auth failure → triage → HITL |
| Consistency guarantee | Strong at deploy time; undetected drift window until next auth failure |
| Failover behavior | Fall back to Vault OSS; log to EventLedger; alert ops |
| Phase gate | Migrate to HCP Vault (IBM-managed) when a paying customer justifies the cost |

---

## Architecture

```
Deploy time (git push):
  sync-secrets.py
    ├── Write to AKV (primary)          ← strong consistency point
    └── Write to Vault OSS (backup)     ← best-effort; alert on failure, don't block deploy

Agent runtime (CompositeSecretsProvider):
  ├── Read from AKV (primary)           ← normal path
  ├── AKV unavailable → Read from Vault OSS (backup)
  │     └── May serve stale secret if backup was not synced at last deploy
  └── Both unavailable → block; escalate to HITL

Drift detection:
  No periodic diff job.
  Stale secret → auth failure on external API call
               → triage picks up failure
               → escalates to HITL
               → human investigates vault state
```

---

## Backup Vault Hosting

Vault OSS runs in a Docker container on a cheap VPS. Recommended providers:

| Provider | Cost | Notes |
|----------|------|-------|
| **Fly.io** | ~$3-5/mo | Docker-native, scales to zero, US/EU regions |
| **Hetzner** | ~€4/mo | 2 vCPU, 4GB RAM, reliable, Germany-based |

**Why a VPS and not a managed service:**
Vault OSS on a cheap VPS is free beyond hosting cost (~$4/mo). HCP Vault (IBM-managed,
equivalent reliability to AKV) carries a meaningful monthly fee that is not yet justified
for a dev-stage swarm. The VPS path preserves the migration: when a paying customer
justifies the spend, `HashiCorpVaultOptions.VaultAddress` is updated to the HCP endpoint
and auth method is updated — no architectural changes required.

**Vendor diversification:**
AKV is Azure-managed. The backup VPS (Fly.io / Hetzner) is a different infrastructure
vendor. A full Azure regional outage takes down AKV but leaves the backup available.

---

## Risk Acceptance — Phase 1/2a

**This is an explicitly accepted risk, not a design gap.**

The backup vault may experience:
- Undetected downtime if the VPS is offline and no agent has needed the fallback
- Stale secrets if `sync-secrets.py` failed on a prior deploy without alerting loudly enough
- A window between primary failure and HITL resolution where agents cannot proceed

**Why this risk is acceptable at this stage:**

1. AKV is the primary and has Azure's 99.9%+ SLA. The backup is rarely hit.
2. Drift manifests as an observable auth failure, not silent corruption. The signal reaches
   HITL through the normal triage → escalation path.
3. The `sync-secrets.py` backup write failure must produce a visible alert (log line, pipeline
   annotation, or notification) so ops knows the backup is stale — even if it does not block
   the deployment.
4. This risk profile is appropriate for a dev-stage system with no paying customers. A
   production-grade customer SLA justifies migrating to HCP Vault.

**What "magnificently fail" means in practice:**
> Agent reads from AKV → AKV down → falls back to Vault OSS → stale key returned →
> external API returns 401 → triage catches auth failure → escalates to HITL →
> human investigates → discovers vault sync issue → resolves manually.

The failure is detectable, traceable, and recoverable. It is loud enough to draw attention.

---

## sync-secrets.py Behavior

Current implementation writes to both vaults sequentially. Required behavior for this model:

- **If AKV write fails**: fail the deployment pipeline — primary must be current
- **If Vault OSS write fails**: log the failure prominently, continue deployment, set an
  alert that the backup is known-stale until manually resolved

No `--diff` or `--reconcile` flag is implemented in Phase 1/2a. A failed backup write is
the only drift signal at deploy time. Between deploys, auth failures are the drift signal.

---

## Phase Roadmap

### Phase 1/2a (current)
- Vault OSS on cheap VPS (Fly.io / Hetzner)
- No reconciliation job
- Failed backup write = alert + continue
- Drift detected via auth failures → HITL

### Phase 2b
- Add `sync-secrets.py --diff` flag for on-demand reconciliation
- Add EventLedger entry when fallback to backup vault is used (tracks how often primary
  fails and whether backup was stale at time of use)
- Consider automated key rotation for known-stale detections (removes HITL burden for
  routine drift)

### Phase 3+ (customer-funded)
- Migrate from Vault OSS / VPS to **HCP Vault (IBM-managed)**
- Update `HashiCorpVaultOptions.VaultAddress` to HCP endpoint
- Update auth method (AppRole → HCP service principal or token, both supported)
- No changes to `ISecretsProvider`, `CompositeSecretsProvider`, or calling code
- Decommission VPS

---

## Open Questions Deferred to Phase 2b

- **Missed backup write alerting**: How loudly does `sync-secrets.py` surface a failed
  backup write? Pipeline failure annotation only, or also a Slack/email notification?
- **EventLedger fallback tracking**: When an agent reads from the backup vault, should
  the EventLedger entry flag this so ops can see how often the primary is unavailable?
- **Automated key rotation on stale detection**: Can key rotation be triggered
  automatically when triage identifies a stale-key auth failure, without requiring HITL?
  (Deferred — requires triage having write access to vault manifests, which is currently blocked.)
