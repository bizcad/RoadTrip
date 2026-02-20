# RBAC Model (Draft)

## Roles

### Reader

- Can run read-only commands (`--info`, `--verify`, list/view operations)
- Cannot trigger mutation

### Contributor

- Can author specs/markdown/config proposals
- Cannot mutate controlled infrastructure directly

### Certifier

- Can approve/reject candidate promotion
- Can view test evidence and audit logs
- Cannot bypass policy controls

### System Mutator

- Automated execution identity
- Can run approved mutation paths only
- Must emit audit trail for every mutation

### Break-Glass Approver

- Grants emergency temporary elevation under incident process

## Permission Matrix (summary)

- Read-only operations: Reader+
- Candidate submission: Contributor+
- Promotion decision: Certifier+
- Controlled mutation: System Mutator only
- Emergency override: Break-Glass Approver + dual approval

## Enforcement Notes

- Deny-by-default for mutation permissions
- Time-bound tokens for elevated actions
- All mutation actions must be attributable and logged
