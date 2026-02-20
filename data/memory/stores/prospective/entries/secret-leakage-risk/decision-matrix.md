# Secret Storage Decision Matrix (Fast Thinking)

## Goal
Minimize secret exposure while preserving local development velocity.

## Local/private options
- 1Password (desktop + CLI): strong UX, team sharing model, encrypted vaults.
- KeePass: offline/local-first, strong control, more manual operations.
- LastPass: possible option, but trust/perimeter posture should be reviewed carefully.
- .NET UserSecrets (localhost/dev): good for local dev app secrets, not a team secret authority.

## Industrial options
- Azure Key Vault + Entra: preferred for production-grade governance, RBAC, rotation, and audit.

## Interim policy
- Allowed for local development: encrypted local manager + gitignored references only.
- Preferred for shared/prod workflows: Key Vault + Entra-backed access control.
- Disallowed: storing secret values in repo docs/logs/memory artifacts.

## Why env vars alone are insufficient
- machine and shell scoped
- inconsistent across tools/sessions
- weak auditability and rotation discipline

## Working rule
Use env vars as delivery channel, not authority store.
