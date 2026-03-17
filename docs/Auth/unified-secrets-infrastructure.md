# Session Replay: Secrets & Agent Identity Architecture

## Your First Task: Orient Before You Build
Read the following files in this order before generating anything:
1. `G:\repos\AI\RoadTrip\PromptTracking\Session Log 20260317.md`
2. `G:\repos\AI\RoadTrip\workflows\` — scan existing workflow folders to 
   understand naming and structural conventions
3. Read and understand my current G:\repos\AI\RoadTrip\analysis\unified-auth\ClaudeCode\unified-auth-spec-v0.2.md
4. Any existing `IConfiguration` or auth-related code in the RoadTrip workspace so generated code conforms to existing patterns

Do not generate any artifacts until you have completed this orientation step. 
Summarize what you found in 3-5 bullet points before proceeding, and flag 
any conflicts between the session log design decisions and existing code.

---

## Context
This session log records a design conversation covering:
- Centralized secrets management for a bot swarm (PPA architecture)
- Dual-vault strategy: Azure Key Vault (primary) + HashiCorp Vault OSS (fallback)
- ISecretsProvider abstraction with CompositeSecretsProvider
- SecretManifestResolver sidecar service
- JWE (RFC 7516) encrypted secret manifests baked into each bot repo
- Canonical secret naming convention (e.g. LEGAL_BOT__WESTLAW_API_KEY)
- Entra RBAC integration for agent principals
- Alignment with unified-auth-spec-v0_2.md principal model

The existing auth spec is at:
`G:\repos\AI\RoadTrip\` — locate unified-auth-spec-v0_2.md

---

## Output Destination
All artifacts go to:
`G:\repos\AI\RoadTrip\workflows\012-operational-agentic-memory\`

Create subfolders as appropriate for code, docs, and config. Follow the 
conventions you observed in existing workflow folders.

---

## Artifacts to Generate

### 1. Interface & Abstractions
`src/ISecretsProvider.cs`
- `ISecretsProvider` interface with Get, GetBundle, Refresh methods
- `SecretDescriptor` record (app_name, canonical_key, required, scopes, blocked)
- `SecretBundle` record (bot_id, secrets dictionary, issued_at, expires_at)

### 2. Implementations
`src/AzureKeyVaultProvider.cs`
- Implements ISecretsProvider against Azure Key Vault
- Uses DefaultAzureCredential
- Translates canonical names to AKV path convention (-- separator)

`src/HashiCorpVaultProvider.cs`
- Implements ISecretsProvider against HashiCorp Vault OSS
- Uses AppRole auth for now, SPIFFE/SPIRE hook for Phase 3b
- Translates canonical names to Vault path convention (/ separator)

`src/CompositeSecretsProvider.cs`
- Primary + fallback pattern
- Logs which vault served each request (for telemetry/audit)
- Respects TTL from SecretBundle

### 3. Secret Manifest Resolver
`src/SecretManifestResolver.cs`
- Reads and decrypts JWE-encoded secrets-manifest.enc from bot repo
- Uses Microsoft.IdentityModel.Tokens for JWE (ECDH-ES+A256KW / A256GCM)
- Resolves canonical names to vault paths via naming convention rules
- Enforces blocked list before any vault call
- Aspire sidecar-compatible (localhost HTTP endpoint)

### 4. Naming Convention Translator
`src/SecretNameTranslator.cs`
- Canonical form: {BOT_NAME}__{APP_NAME}__{KEY_NAME}
- Translates to: AKV format, Vault OSS format, env var format, 
  GitHub Secrets format, Vercel env format
- Unit testable, pure function, no dependencies

### 5. Secret Manifest Schema
`config/secrets-manifest.schema.json`
- JSON Schema for the unencrypted manifest structure
- Fields: bot_id, version, secrets[], blocked[]
- Matches SecretDescriptor shape

`config/secrets-manifest.example.json`
- Example for a legal-bot with 3 realistic entries
- Example for a marketing-bot with 3 realistic entries

### 6. Aspire Wiring
`src/SecretsExtensions.cs`
- Extension methods for IDistributedApplicationBuilder
- Registers CompositeSecretsProvider with correct provider order per environment
- Dev: UserSecrets → HashiCorp Vault OSS fallback
- Prod: Azure Key Vault → HashiCorp Vault OSS fallback
- CI: Environment variables → Azure Key Vault fallback

### 7. Sync Script
`scripts/sync-secrets.py`
- Reads secrets-manifest.json (unencrypted, local only, gitignored)
- Pushes values to Azure Key Vault via azure-keyvault-secrets SDK
- Pushes values to HashiCorp Vault OSS via hvac SDK
- Pushes to GitHub Secrets via PyGithub (optional flag)
- Pushes to Vercel env vars via requests (optional flag)
- Dry-run mode flag
- Never logs secret values, only key names

### 8. Encryption Utility
`scripts/encrypt-manifest.py`
- Takes secrets-manifest.json as input
- Produces secrets-manifest.enc (JWE compact serialization)
- Key source: Azure Key Vault EC key, or local PEM for dev
- Matching decrypt utility for local verification

### 9. Documentation
`docs/README.md`
- Architecture overview with ASCII diagram of the full secrets plane
- How the dual-vault fallback works
- Bootstrap secret pattern (one key unlocks everything)
- Local dev setup instructions

`docs/NAMING-CONVENTION.md`
- Canonical naming schema with full examples
- Translation table for all five target formats
- Rules for bot_name and app_name normalization

`docs/AGENT-IDENTITY-INTEGRATION.md`
- How this layer connects to unified-auth-spec-v0_2.md
- Where SecretManifestResolver fits in the SRCGEEE lifecycle
- How Entra RBAC groups map to secret bundle scopes
- Phase roadmap alignment (Phase 2a through Phase 3b)

`docs/THREAT-MODEL.md`
- Threats specific to this secrets plane
- Mitigations for each
- What is explicitly out of scope

### 10. Tests
`tests/SecretNameTranslatorTests.cs`
- Unit tests for all five translation formats
- Edge cases: special characters, long names, missing components

`tests/CompositeSecretsProviderTests.cs`
- Fallback behavior when primary vault fails
- TTL expiry behavior
- Blocked secret enforcement

---

## Constraints & Quality Gates
- All C# targets .NET 9 and is Aspire-compatible
- No secret values ever appear in any generated file
- All classes follow SOLID principles per the 27 architectural principles 
  in the session log
- Every public interface has XML doc comments
- Flag any design decision that conflicts with unified-auth-spec-v0_2.md
  rather than silently resolving it
- If you are uncertain about a convention in the existing codebase, 
  ask before inventing one

---

## Final Step
After all artifacts are generated, produce a single `GENERATION-REPORT.md` 
in the output root that lists:
- Every file created with a one-line description
- Any conflicts found with existing code
- Any design decisions you made that weren't explicit in the session log
- Open questions that should be added to Section 14 of the auth spec