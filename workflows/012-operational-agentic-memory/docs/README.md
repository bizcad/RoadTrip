# PPA Secrets Infrastructure

**Workflow**: 012 — Operational Agentic Memory
**Status**: Design artifact — Phase 2a target
**Auth dependency**: `unified-auth-spec-v0.2.md`
**Related spec**: Session Log 2026-03-17 (secrets architecture design session)

---

## Overview

This layer provides centralized, role-scoped secrets management for the PPA bot swarm.
Every bot is a security principal (per `unified-auth-spec-v0.2.md` Section 4). This layer
ensures each bot gets exactly and only the secrets it declared it needs — no more, no less.

The design solves three distinct problems:
1. **Secret Inventory** — which bot needs which secrets, and why (manifest)
2. **Secret Storage** — durable, resilient vault with no single point of failure (dual-vault)
3. **Secret Delivery** — right secrets to the right runtime at the right time (provider chain)

---

## Architecture

```
                    ┌────────────────────────────────────────────┐
                    │             BOT PROCESS (e.g. legal-bot)   │
                    │                                            │
                    │  SecretManifestResolver                    │
                    │    ├── reads secrets-manifest.enc (JWE)    │
                    │    ├── enforces blocked list               │
                    │    └── calls CompositeSecretsProvider      │
                    └──────────────────┬─────────────────────────┘
                                       │
                    ┌──────────────────▼─────────────────────────┐
                    │         CompositeSecretsProvider            │
                    │                                            │
                    │   PRIMARY               FALLBACK           │
                    │  (Prod: AKV)          (Prod: Vault OSS)    │
                    │  (Dev:  Vault OSS)    (Dev:  UserSecrets)  │
                    │  (CI:   Env Vars)     (CI:   AKV)          │
                    └──────┬──────────────────────┬──────────────┘
                           │                      │
               ┌───────────▼───────┐  ┌───────────▼───────────────┐
               │  Azure Key Vault   │  │  HashiCorp Vault OSS       │
               │  (Entra Managed   │  │  (AppRole → SPIFFE Phase 3b│
               │   Identity)       │  │   self-hosted)             │
               └───────────────────┘  └───────────────────────────┘
                           │                      │
                           └──────────┬───────────┘
                                      │ sync via
                              scripts/sync-secrets.py
                                      │
                    ┌─────────────────▼──────────────────────────┐
                    │  Local secrets-manifest-with-values.json    │
                    │  (GITIGNORED — local operator use only)     │
                    └────────────────────────────────────────────┘
```

---

## The Bootstrap Secret Pattern

Every JWE-encrypted manifest needs one key to decrypt it. That bootstrap key is
the single trust anchor — everything else is derived from it.

| Environment | Bootstrap Key Source |
|-------------|---------------------|
| Production  | Entra Managed Identity → Azure Key Vault EC key (no static credential) |
| CI          | Environment variable `JWE_BOOTSTRAP_KEY_PEM` injected by CI platform |
| Local dev   | Local PEM file at `JWE_KEY_PATH` (gitignored, generated via `encrypt-manifest.py --generate-key`) |

This is the direct implementation of unified-auth-spec-v0.2 Section 3.2:
*"Short-lived credentials. No long-lived secrets outside vaults."*

The bootstrap key itself is a long-lived EC key — but it lives only in Key Vault
(prod) or local disk (dev), never in the repo.

---

## Dual-Vault Fallback

The `CompositeSecretsProvider` attempts the primary vault first. On any transient
failure (network partition, Azure outage, cost concern), it falls back to the secondary
vault transparently. The calling bot never knows which vault answered.

**Why dual-vault?**

| Concern | Solo AKV | Solo Vault OSS | Dual |
|---------|----------|----------------|------|
| Vendor lock-in risk | Azure only | OSS project risk | Neither is a SPOF |
| Local dev | `az login` friction | Native | Vault handles local |
| Dynamic agent secrets | Static only | Full dynamic | Vault mints, AKV backs up |
| Aspire integration | First-class | Custom | AKV for prod, Vault for dev |
| Exit ramp | None | Full | Full |

---

## How Secret Bundles Map to Agent RBAC

Each bot's Entra identity maps to a Key Vault access policy:

```
Entra Group: legal-bot-agents
  └── Key Vault Policy: GET/LIST secrets/legal-bot/*
  └── Vault OSS Policy: read secret/legal-bot/*

Entra Group: marketing-bot-agents
  └── Key Vault Policy: GET/LIST secrets/marketing-bot/*
  └── Vault OSS Policy: read secret/marketing-bot/*
```

When the Aspire host spawns a legal-bot, the bot authenticates with its Entra identity,
and the provider resolves only the keys in its manifest — the AKV/Vault policies enforce
that it cannot read marketing-bot keys even if it tried.

---

## Local Dev Setup

1. **Install HashiCorp Vault OSS** and start in dev mode:
   ```powershell
   vault server -dev -dev-root-token-id="root"
   $env:VAULT_ADDR = "http://localhost:8200"
   $env:VAULT_TOKEN = "root"
   ```

2. **Generate a local EC key** for manifest encryption:
   ```powershell
   py scripts/encrypt-manifest.py --generate-key --key-output local-manifest-key.pem
   # Add local-manifest-key.pem to .gitignore
   ```

3. **Encrypt your bot manifest**:
   ```powershell
   py scripts/encrypt-manifest.py `
     --input config/secrets-manifest.example.json `
     --output secrets-manifest.enc `
     --key-pem local-manifest-key.pem `
     --verify
   ```

4. **Sync secrets to local Vault**:
   ```powershell
   # Create a local manifest-with-values.json (gitignored) with actual values
   py scripts/sync-secrets.py `
     --manifest secrets-manifest-with-values.json `
     --vault `
     --dry-run  # remove --dry-run when ready to write
   ```

5. **Configure Aspire** with local options:
   ```csharp
   builder.Services.AddPpaSecretsProvider(builder.Environment, new PpaSecretsOptions
   {
       HashiCorpVaultAddress = "http://localhost:8200",
       DevRoleId = "your-approle-role-id",      // from dotnet user-secrets
       DevSecretId = "your-approle-secret-id",  // from dotnet user-secrets
   });
   ```

---

## Files in This Artifact Set

| File | Purpose |
|------|---------|
| `src/ISecretsProvider.cs` | Core interface + `SecretDescriptor` + `SecretBundle` records |
| `src/AzureKeyVaultProvider.cs` | AKV implementation via `DefaultAzureCredential` |
| `src/HashiCorpVaultProvider.cs` | Vault OSS implementation via AppRole (Phase 3b: SPIFFE) |
| `src/CompositeSecretsProvider.cs` | Primary + fallback composition with vault telemetry |
| `src/SecretManifestResolver.cs` | JWE manifest decrypt + blocked list enforcement |
| `src/SecretNameTranslator.cs` | Canonical ↔ 5-format name translation (pure function) |
| `src/SecretsExtensions.cs` | Aspire `IServiceCollection` wiring per environment |
| `config/secrets-manifest.schema.json` | JSON Schema for manifest validation |
| `config/secrets-manifest.example.json` | legal-bot + marketing-bot examples |
| `scripts/sync-secrets.py` | Fan-out secrets to AKV, Vault OSS, GitHub, Vercel |
| `scripts/encrypt-manifest.py` | JWE encrypt/decrypt + key generation utility |
| `docs/NAMING-CONVENTION.md` | Canonical naming schema + translation table |
| `docs/AGENT-IDENTITY-INTEGRATION.md` | How this connects to unified-auth-spec-v0.2 |
| `docs/THREAT-MODEL.md` | Threats and mitigations for the secrets plane |
| `tests/SecretNameTranslatorTests.cs` | Unit tests for all 5 translation formats |
| `tests/CompositeSecretsProviderTests.cs` | Fallback, TTL, and blocked-secret tests |
