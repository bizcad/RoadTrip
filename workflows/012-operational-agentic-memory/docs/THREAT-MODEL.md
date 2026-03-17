# Threat Model — PPA Secrets Plane

**Scope**: The secrets plane described in this workflow (dual-vault, manifest resolver,
sync scripts, and naming convention). Does NOT cover the broader PPA principal model
or auth layers — those are in `unified-auth-spec-v0.2.md` Section 13.

---

## Assets

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Secret values (API keys, tokens) | Critical | Unauthorized access to external services, data breach, financial cost |
| Secrets manifest (key names only) | Medium | Reveals API integrations, attack surface map |
| Encrypted manifest `secrets-manifest.enc` | Low (without bootstrap key) | Leaks nothing without the decryption key |
| Bootstrap EC key (private) | Critical | Decrypts all manifests for all bots using that key |
| AKV access policies | High | Misconfiguration can grant cross-bot secret access |
| Vault OSS admin token | Critical | Root access to all secrets in the Vault instance |

---

## Threats and Mitigations

### T1: Bot reads another bot's secrets

**Description**: A legal-bot attempts to read `MARKETING_BOT__TWITTER__TWITTER_BEARER_TOKEN`.

**Mitigations**:
- Vault access policy restricts `secret/legal-bot/*` only — path-level enforcement at vault.
- AKV access policy restricts `legal-bot--*` only — path-level enforcement at AKV.
- Manifest blocked list rejects requests for `TWITTER_BEARER_TOKEN` at resolver layer (defense in depth).
- Entra RBAC: legal-bot's managed identity has no policy on marketing-bot paths.

**Residual risk**: Low. Three independent enforcement layers must all be misconfigured simultaneously.

---

### T2: Attacker reads secret key names from committed manifest

**Description**: Source code is public (or leaked). Attacker reads `secrets-manifest.enc`
and learns which APIs the bot is integrated with.

**Mitigations**:
- `secrets-manifest.enc` is a JWE Compact Serialization — ciphertext is opaque without the bootstrap key.
- Key names (not values) are encrypted inside the JWE payload.
- Bootstrap key is never in the repo.

**Residual risk**: Very low. An attacker needs the bootstrap EC private key to learn key names.

---

### T3: Secret values committed to source control

**Description**: Developer accidentally commits `secrets-manifest-with-values.json` or
an `.env` file containing actual secret values.

**Mitigations**:
- `secrets-manifest-with-values.json` must be in `.gitignore` — the sync script's `--input` file is never the schema or example files.
- `sync-secrets.py` accepts only an explicitly specified input file — no automatic discovery of value files.
- Pre-commit hook (recommended): scan staged files for patterns matching `_API_KEY` or `_SECRET` with adjacent non-placeholder values.

**Residual risk**: Medium without pre-commit hooks; low with them. **Recommendation: add a git pre-commit hook.**

---

### T4: Bootstrap EC private key leaked

**Description**: Local development key (`local-manifest-key.pem`) is accidentally committed.

**Mitigations**:
- `encrypt-manifest.py --generate-key` logs a warning and instructs adding the file to `.gitignore`.
- Key files are named `*.pem` — standard `.gitignore` templates include `*.pem`.
- If a local key is leaked: rotate immediately, re-encrypt all manifests using the new key, invalidate any bundles issued since the compromise.

**Residual risk**: Medium if `.gitignore` is not configured. Low if `.gitignore` includes `*.pem`.

---

### T5: HashiCorp Vault OSS admin token exposed

**Description**: `VAULT_TOKEN=root` used in local dev mode leaks into a CI log or env dump.

**Mitigations**:
- Dev-mode `root` token has no access to prod secrets (completely separate Vault instance).
- CI uses AppRole with a short-lived Secret ID, not the root token.
- `sync-secrets.py` reads `VAULT_TOKEN` from env, never from a file that could be committed.

**Residual risk**: Low for prod. Medium for local dev if CI environment is shared.

---

### T6: Secret bundle TTL not enforced

**Description**: A bot caches a `SecretBundle` beyond its `ExpiresAt`, continuing to use
credentials that should have been refreshed after a vault policy change.

**Mitigations**:
- `SecretBundle.IsValid` property gates all uses at the call site.
- `CompositeSecretsProvider.RefreshAsync` is called when the bundle is expired.
- Vault leases independently expire; a post-expiry API call will get a 401, triggering a refresh.

**Residual risk**: Low if consuming code always checks `IsValid`. Medium if the check is skipped.

---

### T7: CompositeSecretsProvider fallback masks vault unavailability

**Description**: Azure Key Vault is consistently unavailable (billing issue, misconfiguration).
The fallback silently serves HashiCorp Vault, masking the primary vault problem.

**Mitigations**:
- `CompositeSecretsProvider` logs at `Warning` level when falling back to secondary vault.
- Log: `"Composite: PRIMARY failed, attempting FALLBACK — bot={BotId} error={Error}"`.
- Monitoring: alert on sustained `Warning`-level fallback events in telemetry.
- The fallback is not silent — it is observable via structured logs.

**Residual risk**: Low with monitoring. Medium without an alert on sustained fallback events.

---

### T8: Manifest blocked list bypass via delegation

**Description**: An orchestrator delegates to a legal-bot with an explicit grant for
`TWITTER_BEARER_TOKEN`. The blocked list in the manifest should prevent this regardless
of delegation scope.

**Mitigations**:
- `SecretManifestResolver` enforces the blocked list before calling the provider.
- `SecretBlockedException` propagates immediately without fallback.
- The blocked list is baked into the encrypted manifest at the bot repo level — it is not runtime-configurable by the orchestrator.

**Residual risk**: Very low. The manifest is a code artifact — changing it requires a repo commit and new encrypted manifest.

---

## Explicitly Out of Scope

- **Token revocation latency**: Vault lease revocation propagation time is Vault's responsibility. Not modeled here.
- **Vault OSS HA/DR**: Vault OSS clustering and backup are infrastructure concerns, not application concerns.
- **Azure Key Vault quotas and throttling**: AKV rate limits under high bundle-fetch load.
- **JWE algorithm deprecation**: If ECDH-ES+A256KW is deprecated by a future JOSE RFC, manifests must be re-encrypted. This is a long-term operational risk, not an immediate threat.
- **Insider threat**: A developer with Vault admin access can read any secret. Access reviews (Phase 5) mitigate this.
- **Supply chain attacks on dependencies**: `azure-identity`, `hvac`, `joserfc` are trusted third-party packages. SBOM and dependency scanning are Phase 3a concerns.

---

## Recommended Immediate Actions (Pre-Phase 2a)

1. Add `*.pem` and `*-with-values.json` to global `.gitignore` in all bot repos.
2. Configure AKV access policies with path-level restrictions before writing any secrets.
3. Enable Vault OSS audit log (`vault audit enable file file_path=/var/log/vault/audit.log`).
4. Add a Grafana/Application Insights alert on sustained `CompositeSecretsProvider` fallback log events.
5. Rotate the local dev bootstrap key quarterly or on any team member departure.
