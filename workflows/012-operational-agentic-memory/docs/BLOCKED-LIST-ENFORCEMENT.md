# Blocked List Enforcement Level

**Resolved answer to Q3 (blocked list enforcement) from `AGENT-IDENTITY-INTEGRATION.md`**

---

## Decision Summary

Application-layer enforcement via `SecretManifestResolver` is sufficient. Duplicating the
blocked list at the vault policy layer would create a second policy surface that can drift
from the manifest — making things worse, not better.

---

## Reasoning

The blocked list lives in `secrets-manifest.enc`, which is committed to the bot's repo
alongside its code. This gives it properties that a vault access policy does not have:

| Property | Manifest (app layer) | Vault policy (vault layer) |
|----------|---------------------|---------------------------|
| Version controlled | Yes — git history | No — vault config |
| Code reviewed | Yes — same PR as bot code | No — separate ops change |
| SLSA attestable (Phase 3a) | Yes — committed artifact | No |
| Drift risk | None — single source of truth | Yes — can diverge from manifest |
| Maintenance surface | One (the manifest) | Two (manifest + vault policy) |

Adding vault-level enforcement means maintaining two copies of the same policy. The copy
outside version control (the vault policy) is the harder one to audit and the more likely
to drift. This creates a false sense of defense-in-depth while actually introducing a new
failure mode.

---

## Why "Defense in Depth" Doesn't Apply Here

Defense in depth is valuable when two independent enforcement layers protect against
different failure modes. Here they would protect against the same failure mode
(a bot requesting a blocked secret) using the same data (the blocked list) — just in
two different places.

The scenario where vault-level enforcement adds real value is if `SecretManifestResolver`
itself is compromised or buggy. But bypassing application code requires compromising the
deployment pipeline — at which point the attacker has access to far more than just vault
routing. The vault policy adds no meaningful protection against that threat.

The genuine defense-in-depth measure is **Phase 3a SLSA attestation**: the manifest becomes
a formally attested code artifact, and bundle issuance requires `trust_level >= verified`.
That is a stronger guarantee than a manually configured vault policy.

---

## The Sequencing Parallel (from Q2)

Q2 (manifest rotation) established that the manifest is a **code artifact and the
authoritative source of truth** — the vault is populated from it, not the reverse. The
same principle applies here: the blocked list in the manifest IS the policy. Duplicating
it at the vault layer would invert the authority relationship.

---

## What Stays Unchanged

- `SecretManifestResolver` enforces the blocked list before any vault call (Phase 1/2a — current)
- `SecretBlockedException` does not trigger fallback in `CompositeSecretsProvider` (by design —
  a block is intentional policy, not a transient error)
- Vault access policies are scoped by Entra group (path-level: `read secret/{bot-name}/*`) —
  this provides coarse-grained isolation between bots, which is the appropriate role for
  vault policy. Fine-grained blocked list enforcement belongs in the application layer.

---

## Phase Roadmap

### Phase 1/2a (current)
- Blocked list enforced only in `SecretManifestResolver`
- Vault policies scoped by bot group (Entra RBAC path-level access)
- No duplication

### Phase 3a (Supply Chain Trust)
- Manifest committed as SLSA-attested code artifact
- Bundle issuance requires `trust_level >= verified`
- The attested manifest IS the formal policy — vault-level duplication is even less
  necessary once the artifact has provenance

---

## Open Questions Deferred

None. This question is fully resolved.
