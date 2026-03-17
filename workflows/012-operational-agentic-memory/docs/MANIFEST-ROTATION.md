# Manifest Rotation

**Resolved answer to Q2 (manifest rotation) from `AGENT-IDENTITY-INTEGRATION.md`**

---

## Decision Summary

Manifest rotation is a **sequencing discipline**, not an atomicity problem. The vault is
populated as a precondition before the manifest is updated. At no point does a bot hold a
manifest that references a secret not yet in the vault.

---

## The Natural Workflow

```
1. Obtain credential from vendor (API key, client secret, etc.)
        ↓
2. Run sync-secrets.py → writes value to AKV (primary) + Vault OSS (backup)
        ↓  HARD STOP if this fails — do not proceed to step 3
3. Add entry to secrets-manifest.json (plaintext, gitignored)
        ↓
4. Run encrypt-manifest.py → produces new secrets-manifest.enc
        ↓
5. git commit + push (secrets-manifest.enc enters the repo)
        ↓
6. Bot deployment picks up new secrets-manifest.enc
   → decrypts manifest → declares new secret → finds it already in vault → works
```

The vault is always **ahead of or equal to** the manifest. A bot can only request secrets
it has declared; it declares only secrets the manifest contains; the manifest is only
updated after the vault write succeeds.

---

## Edge Cases

| Scenario | Risk | Outcome |
|----------|------|---------|
| Step 2 fails (vault write fails) | Operator does not proceed to step 3 | Safe — manifest never references the missing secret |
| Rolling deploy: old + new bot instances running simultaneously | Old bot uses old manifest; doesn't declare new secret; never requests it | Safe — old bot is unaffected |
| Rollback to previous bot version | Old manifest doesn't declare new secret | Safe — vault retains the value; nothing requests it; harmless |
| secrets-manifest.enc replaced in commit | Old `.enc` is gone in the same commit that adds the new one | Not stale — replacement is atomic at git commit level |

---

## Why "Atomicity" Is the Wrong Frame

The original question asked for a way to *simultaneously* update the manifest, push vault
values, and roll out the new bot version atomically. This framing assumes the three
operations are concurrent and need coordination. They are not:

- Vault write (step 2) is a **precondition** — it must complete before anything else
- Manifest update (steps 3-4) is **consequent** — it describes what is already in the vault
- Bot rollout (step 6) is **consequent** — it reads what the manifest describes

Treating this as a sequencing discipline (vault → manifest → deploy) eliminates the
coordination problem without requiring distributed transactions or deployment tooling.

---

## Operator Checklist for Adding a New Secret

1. [ ] Obtain the credential from the vendor
2. [ ] Add the value to `manifest-with-values.json` (plaintext, gitignored)
3. [ ] Run `py scripts/sync-secrets.py` — confirm both vault writes succeed
4. [ ] Add the entry to `secrets-manifest.json` (schema-validated, no values)
5. [ ] Run `py scripts/encrypt-manifest.py` — confirm round-trip with `--verify`
6. [ ] Commit and push (`secrets-manifest.enc` is the only secret-related file committed)
7. [ ] Deploy new bot version

**If step 3 fails:** stop. Do not update the manifest. Investigate the vault write failure.
The bot will continue running with the old manifest and old secrets until resolved.

---

## Removing a Secret

Removal follows the same ordering in reverse: remove from manifest first (deploy), then
clean up vault entries. A bot cannot request a secret it no longer declares, so the vault
entry becomes unreachable before it is deleted — no window where the bot requests something
already gone.

---

## Open Questions Deferred

None. This question is fully resolved by workflow ordering.
