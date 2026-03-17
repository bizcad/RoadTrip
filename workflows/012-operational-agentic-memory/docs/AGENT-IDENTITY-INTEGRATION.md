# Agent Identity Integration

**How the Secrets Plane connects to `unified-auth-spec-v0.2.md`**

---

## The Real Purpose of This Layer

This layer has three responsibilities that are easy to conflate but distinct:

### 1. Adapter Pattern Over Heterogeneous KV Auth

The bot swarm is not homogeneous. It includes PPA (.NET/Aspire), rockbot (hollow, self-improving),
thepopebot, OpenClaw, and an indeterminate number of future bots — each with its own auth
conventions, SDKs, and security posture. The plethora of KV auth techniques across these bots
(API keys, bearer tokens, client secrets, OAuth flows, OIDC, AppRole) is the problem.

`ISecretsProvider` is the adapter interface. It provides a single uniform boundary:

```
OpenClaw (Python)        ──┐
rockbot (unknown runtime) ──┤
PPA (.NET/Aspire)        ──┤──► ISecretsProvider ──► CompositeSecretsProvider
thepopebot               ──┤                              ├── Azure Key Vault
any future bot           ──┘                              └── HashiCorp Vault OSS
```

The bot never calls a vault directly. It calls `ISecretsProvider.GetBundleAsync()` and gets
back exactly the credentials it declared it needs. The adapter absorbs the routing, translation,
and vault-specific auth details.

### 2. Security Gap Closure for Third-Party Bots

Not all bots in the swarm were designed with zero-trust in mind. Third-party or "hollow" bots
may carry ambient credentials, hardcoded keys, or no revocation mechanism. This layer:

- **Wraps** those bots behind `ISecretsProvider` so they receive credentials through the same
  controlled channel as first-party bots
- **Enforces** the blocked list: a bot cannot request secrets outside its manifest even if the
  underlying SDK would allow it
- **Scopes** TTL: credentials expire with the bot's delegation, not the underlying API key's
  expiry

This does not make an insecure bot fully secure — it closes the *credential acquisition* gap
and ensures audit visibility. Other gaps (code signing, provenance) are Phase 3a concerns.

### 3. The Gap in the Auth Spec

`unified-auth-spec-v0.2.md` defines a principal model (Section 4) and a delegation chain
(Section 5), but does not specify how agents *receive* the credentials they need to call
external services. This layer fills that gap:

```
Section 4: Principal Identity    ← who the agent IS (Entra identity, TTL, parent principal)
           ↕
[This layer: Secrets Plane]      ← what credentials the agent CAN ACCESS (vault-scoped bundle)
           ↕
Section 5: Delegation Chain      ← what the agent is AUTHORIZED to DO with those credentials
```

---

## Swarm Scale: This Is Not Just Two Bots

Legal-bot and marketing-bot are illustrative examples only. The real target is an
**indeterminate number of bots** serving many human principals across a company.

Human principals in this model are **subject matter experts (SMEs)** — not just admins.
A legal SME is the human principal for the legal-bot swarm. A marketing SME is the human
principal for the marketing-bot swarm. Bots talk to each other AND escalate to their
respective human principals when they hit a blockage.

RBAC exists precisely because this relationship is many-to-many and open-ended:

```
Human SME: Legal Team
  └── Entra Group: legal-bot-agents
        └── {N} legal-bot instances, each with its own Entra identity
              └── Can escalate to human:legal-sme-alice, human:legal-sme-bob

Human SME: Marketing Team
  └── Entra Group: marketing-bot-agents
        └── {M} marketing-bot instances
              └── Can escalate to human:marketing-sme-carol

... (indeterminate future bot types and SME groups)
```

A new bot type and a new human SME group can be onboarded by:
1. Creating an Entra group for the new bot type
2. Writing a `secrets-manifest.enc` for the bot with its declared credential needs
3. Assigning vault access policies for the group
4. Registering the human SME as a principal in the delegation model

No changes to `ISecretsProvider`, `CompositeSecretsProvider`, or `SecretManifestResolver`.

---

## Runtime Diversity: Aspire Is One Option Among Many

Aspire is a compelling host for PPA and .NET-native bots, but the swarm includes runtimes
that Aspire does not govern:

| Bot / Runtime | Secrets Integration Path |
|---------------|--------------------------|
| PPA (.NET 10 / Aspire) | `SecretsExtensions.AddPpaSecretsProvider()` wires in directly |
| rockbot (hollow — runtime TBD) | `ISecretsProvider` adapter provided when bot is bootstrapped via SRCGEEE |
| OpenClaw (Python) | `sync-secrets.py` fan-out to env vars; bot reads env; adapter wraps env reads |
| thepopebot (runtime unknown) | Same env var pattern, or direct `ISecretsProvider` binding if runtime permits |
| GitHub Actions bots | `sync-secrets.py --github` pushes to repo secrets; no runtime adapter needed |
| Future unknown bots | The adapter pattern accommodates any runtime that can read env vars or make HTTP calls |

The `SecretsExtensions.cs` Aspire wiring is the PPA-specific integration. The underlying
`ISecretsProvider` interface and `CompositeSecretsProvider` are runtime-agnostic.

---

## Where SecretManifestResolver Fits in SRCGEEE

| Phase | Secrets Plane Role |
|-------|--------------------|
| **Sense** | Agent principal is authenticated (L0). Identity known. |
| **Retrieve** | `SecretManifestResolver.ResolveAsync()` is called. JWE manifest decrypted. Blocked list enforced. Bundle fetched from vault. |
| **Compose** | Agent uses bundle values to construct external API calls. No vault contact during composition. |
| **Gate** | L6 risk gate evaluates whether the external calls are within allowed scope. Blocked-list violations are caught at Retrieve, before Gate. |
| **Execute** | Agent presents resolved credentials to external services. Bundle TTL checked before each call. |
| **Evaluate** | Bundle usage logged (key names only, never values). Composite provider records which vault served each request. |
| **Evolve** | Stale or over-scoped bundles trigger manifest version increment. Trust levels adjusted based on outcome. rockbot's manifest grows as SRCGEEE self-improvement fills in new capability requirements. |

---

## How Entra RBAC Groups Map to Secret Bundle Scopes

Each Entra group corresponds to a vault access policy and a set of declared scopes.
Legal and marketing are two examples of an open-ended set:

```
Entra Group: legal-bot-agents
  Vault policy:   Read secret/legal-bot/*  |  Deny secret/marketing-bot/*
  Manifest scopes: case-law-search, document-retrieval, llm-inference

Entra Group: marketing-bot-agents
  Vault policy:   Read secret/marketing-bot/*  |  Deny secret/legal-bot/*
  Manifest scopes: social-media-post, analytics-read, scheduled-post

Entra Group: {any-future-bot}-agents
  Vault policy:   Read secret/{any-future-bot}/*  |  Deny all others
  Manifest scopes: (declared at onboarding time)
```

When an agent is spawned, it presents its Entra identity to the vault. The vault enforces
path-level access; the manifest resolver enforces the blocked list. Both gates must pass.

---

## Trust Level Mapping

From `unified-auth-spec-v0.2.md` Section 7:

| Agent Trust Level | Secret Access |
|------------------|---------------|
| `untrusted` | No secret bundle issued. Blocked at L0. |
| `basic` | Bundle issued for optional secrets only. Required secrets blocked pending attestation. |
| `verified` | Full bundle issued per manifest. Standard operations. |
| `attested` | Full bundle + dynamic secret generation (Vault dynamic secrets for short-lived creds). |

Phase 1 treats all registered agents as `verified`. Trust level promotion is a Phase 2b/3a concern.
rockbot starts at `basic` (hollow — no attested code yet) and promotes as SRCGEEE fills it in.

---

## Phase Roadmap Alignment

### Phase 2a (this workflow — target)
- `ISecretsProvider` interface + dual-vault composite provider
- AKV + HashiCorp Vault OSS implementations
- `SecretManifestResolver` with JWE decryption
- `SecretNameTranslator` (pure function, runtime-agnostic)
- `sync-secrets.py` + `encrypt-manifest.py` scripts (support non-.NET bots via env fan-out)
- Per-manifest blocked list enforcement
- Aspire wiring for PPA; env var fan-out for other bot runtimes

### Phase 2b
- Risk gate (L6) integration: high-spend secrets require HITL before bundle is issued
- Bundle audit trail feeds `EventLedger` in SQL Server (Workflow 012)
- Delegation scope check: agent cannot request secrets outside its delegation
- Human SME escalation path wired to HITL gate for blocked or high-risk requests

### Phase 3a (Supply Chain Trust)
- Manifest provenance: `secrets-manifest.enc` is a code artifact with SLSA attestation
- Manifest fingerprint registered in the code principal registry
- Bundle issuance requires `trust_level >= verified`
- rockbot manifests gain provenance as self-improvement produces attested code artifacts

### Phase 3b (External Identity)
- Replace AppRole with SPIFFE/SPIRE JWT auth in `HashiCorpVaultProvider`
- Agents authenticate to Vault using their SPIFFE SVID — no static credentials at all
- `AzureKeyVaultProvider` continues to use Managed Identity (already zero-credential)
- Bootstrap key sourced via SPIFFE SVID rather than env var

---

## Resolved: Sub-Agent Role Asymmetry (formerly Q11)

**Triage authenticates independently — it does not inherit or receive a scoped-down copy of the
executor's bundle.** Each sub-agent role (executor, triage) has its own independently-declared
manifest and authenticates to `ISecretsProvider` separately. The parent can revoke either bundle
without affecting the other.

Key points:
- Triage has **broader read access** than the executor (case vault, logs, history, vendor docs via MCP)
- Triage has **limited write access** scoped to execution context only (env vars, command wrappers, retry schedule)
- Triage is **blocked** from executor-like writes (production data, executor code, arbitrary external APIs)
- L6 risk gate evaluates every triage fix before a retry is scheduled
- Triage can apply "stop-the-bleeding" mitigations (shell wrappers, env var injection, transient retries,
  vendor SDK bumps) and schedule executor retries without human intervention for low-risk fixes
- Novel or high-risk fixes escalate to HITL before the retry proceeds

See [`docs/TRIAGE-DELEGATION.md`](TRIAGE-DELEGATION.md) for the full bundle definition, stop-the-bleeding
fix categories, retry contract, and L6 gate policy.

---

## Open Questions (Candidates for Section 14 of Auth Spec)

*Q1 (sub-agent role asymmetry / bundle scope inheritance) was resolved — see the
"Resolved: Sub-Agent Role Asymmetry" section above and `TRIAGE-DELEGATION.md`.*

1. ~~**Vault sync consistency**~~ — **Resolved.** AKV primary, Vault OSS on cheap VPS (Fly.io / Hetzner)
   as backup, no reconciliation job, drift detected via auth failures → HITL. Phase gate to HCP Vault
   when customer-funded. See [`VAULT-SYNC-CONSISTENCY.md`](VAULT-SYNC-CONSISTENCY.md).

2. ~~**Manifest rotation**~~ — **Resolved.** Vault write is a precondition, not a concurrent
   operation. The natural workflow ordering (vault → manifest → deploy) eliminates the atomicity
   problem. See [`MANIFEST-ROTATION.md`](MANIFEST-ROTATION.md).

3. ~~**Blocked list enforcement level**~~ — **Resolved.** Application-layer enforcement is
   sufficient. Duplicating the blocked list at the vault policy layer creates a second policy
   surface that can drift from the manifest — the manifest IS the authoritative policy artifact.
   See [`BLOCKED-LIST-ENFORCEMENT.md`](BLOCKED-LIST-ENFORCEMENT.md).
