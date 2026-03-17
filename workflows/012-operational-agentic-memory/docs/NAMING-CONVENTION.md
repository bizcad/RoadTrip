# Secret Naming Convention

**Status**: Baseline for all PPA bot repos
**Owner**: PPA Architecture
**Related**: `SecretNameTranslator.cs`, `sync-secrets.py`

---

## Canonical Form

All secrets are identified by a three-segment canonical name:

```
{BOT_NAME}__{APP_NAME}__{KEY_NAME}
```

| Segment | Format | Example |
|---------|--------|---------|
| `BOT_NAME` | UPPER_SNAKE_CASE | `LEGAL_BOT` |
| `APP_NAME` | UPPER_SNAKE_CASE | `WESTLAW` |
| `KEY_NAME` | UPPER_SNAKE_CASE | `WESTLAW_API_KEY` |

Separator: double underscore `__` (a `.NET IConfiguration` hierarchy separator, enabling
`IConfiguration["LEGAL_BOT:WESTLAW:WESTLAW_API_KEY"]` when configured correctly).

### Normalization Rules

Input tokens may arrive in various forms. The translator normalizes before applying:

| Input form | Normalized to |
|------------|---------------|
| `legal-bot` | `LEGAL_BOT` |
| `legal_bot` | `LEGAL_BOT` |
| `LEGAL_BOT` | `LEGAL_BOT` (unchanged) |
| `westlaw` | `WESTLAW` |
| `Westlaw_API_Key` | `WESTLAW_API_KEY` |

Rule: uppercase everything, replace hyphens with underscores.

---

## Translation Table

Given canonical key `LEGAL_BOT__WESTLAW__WESTLAW_API_KEY`:

| Target | Format Rule | Result |
|--------|-------------|--------|
| **Canonical** | `{BOT}__{APP}__{KEY}` | `LEGAL_BOT__WESTLAW__WESTLAW_API_KEY` |
| **Azure Key Vault** | Lowercase, `__`→`--`, `_`→`-` | `legal-bot--westlaw--westlaw-api-key` |
| **HashiCorp Vault** | `{bot}/{app}/{KEY}` (bot+app lowercase-hyphen, key preserves case) | `legal-bot/westlaw/WESTLAW_API_KEY` |
| **Env Var** | UPPER_SNAKE (identity) | `LEGAL_BOT__WESTLAW__WESTLAW_API_KEY` |
| **GitHub Secret** | UPPER_SNAKE, no dashes | `LEGAL_BOT__WESTLAW__WESTLAW_API_KEY` |
| **Vercel Env** | UPPER_SNAKE (identity) | `LEGAL_BOT__WESTLAW__WESTLAW_API_KEY` |

### Why These Specific Translations?

**Azure Key Vault**: AKV secret names allow only alphanumeric characters and hyphens.
Forward slashes and underscores are not permitted. Double-dash (`--`) represents a
segment boundary while single-dash (`-`) represents an underscore within a segment.
The mapping is reversible: `legal-bot--westlaw--westlaw-api-key` can always be decoded
back to `LEGAL_BOT__WESTLAW__WESTLAW_API_KEY`.

**HashiCorp Vault**: Vault uses forward slashes as path separators in its KV engine.
The bot and app segments are lowercased for conventional Vault path style. The key
name preserves its original casing because Vault is case-sensitive.

**Env Var / GitHub / Vercel**: All three platforms use the same UPPER_SNAKE_CASE form.
The double-underscore separator is preserved. GitHub Actions secret names additionally
forbid dashes, but canonical names never contain dashes after normalization.

---

## Segment Naming Rules

### `BOT_NAME`

- Use the bot's canonical identifier in its most natural human-readable form
- Input as kebab-case (`legal-bot`) or UPPER_SNAKE_CASE (`LEGAL_BOT`)
- Examples: `LEGAL_BOT`, `MARKETING_BOT`, `TRIAGE_AGENT`, `ORCHESTRATOR`
- Must be stable: changing the bot name invalidates all existing vault paths

### `APP_NAME`

- The application, service, or vendor providing the credential
- Keep short and unambiguous
- Examples: `ANTHROPIC`, `WESTLAW`, `TWITTER`, `LINKEDIN`, `COURTLISTENER`, `GITHUB`
- Use the service's official name, not a nickname

### `KEY_NAME`

- The specific credential type within that application
- Must be UPPER_SNAKE_CASE
- Must include the credential type suffix for clarity
- Recommended suffixes:

| Credential Type | Suffix | Example |
|-----------------|--------|---------|
| API key | `_API_KEY` | `WESTLAW_API_KEY` |
| Bearer token | `_BEARER_TOKEN` | `TWITTER_BEARER_TOKEN` |
| Client secret | `_CLIENT_SECRET` | `LINKEDIN_CLIENT_SECRET` |
| Client ID | `_CLIENT_ID` | `LINKEDIN_CLIENT_ID` |
| Access token | `_ACCESS_TOKEN` | `GITHUB_ACCESS_TOKEN` |
| Webhook secret | `_WEBHOOK_SECRET` | `GITHUB_WEBHOOK_SECRET` |
| Connection string | `_CONNECTION_STRING` | `SQL_CONNECTION_STRING` |

---

## Full Example: Legal Bot

```
Bot ID:   legal-bot
App:      westlaw
Key:      WESTLAW_API_KEY

Canonical:   LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
AKV name:    legal-bot--westlaw--westlaw-api-key
Vault path:  secret/data/legal-bot/westlaw/WESTLAW_API_KEY
Env var:     LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
GitHub:      LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
Vercel:      LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
```

---

## Blocked List Convention

The `blocked` array in the manifest uses canonical KEY_NAME only (not the full canonical path):

```json
"blocked": ["TWITTER_BEARER_TOKEN", "LINKEDIN_CLIENT_SECRET"]
```

This is intentional: a legal-bot is blocked from accessing *any* bot's Twitter bearer token,
regardless of which bot or app segment it appears under. The resolver does a suffix match
against the KEY_NAME segment of any requested canonical key.

---

## Versioning & Stability

- Once a canonical key name is in production vault, treat it as immutable.
- To rename a key: add the new name, migrate all consumers, then delete the old name.
- Do not silently rename keys — existing bots will fail at startup if their manifest
  references a name that no longer exists in the vault.
- The `version` field in the manifest should be incremented on every schema change.
