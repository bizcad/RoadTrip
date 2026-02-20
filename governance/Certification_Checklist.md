# Certification Checklist (Guardrail Policy)

Use this checklist for any candidate artifact containing executable code (skill, script, workflow runner, mutator).

## A. Classification

- [ ] Classified as `infrastructure` or `user-facing`
- [ ] If `infrastructure`, no-arg behavior is read-only + info output
- [ ] Mutation capability documented

## B. Safe Defaults

- [ ] Running with no parameters does not mutate state
- [ ] Output explains safe commands and mutation requirements
- [ ] Dangerous examples are not shown in exploratory output

## C. Mutation Guardrails

- [ ] Mutation requires explicit opt-in flags
- [ ] Mutation path supports dry-run/read-only mode
- [ ] Unsafe mutation attempts fail closed with non-zero exit
- [ ] Safety warnings are clear and actionable

## D. Test Evidence

- [ ] Test: no-arg -> read-only info
- [ ] Test: mutation without force -> blocked
- [ ] Test: explicit mutation gate works as designed
- [ ] Test: audit/log event emitted on mutation path

## E. Governance & Access

- [ ] RBAC mapping assigned
- [ ] Artifact can run under execution wrapper if missing native controls
- [ ] Promotion approved by certifier

## F. Registry/Memory/Orchestrator Specific

- [ ] Registry mutation is system-controlled
- [ ] Memory mutation follows policy and audit requirements
- [ ] Orchestrator/workflow runners treated as controlled infrastructure

## Decision

- [ ] APPROVE
- [ ] APPROVE WITH CONDITIONS
- [ ] REJECT

## Reviewer Notes

- Risk summary:
- Conditions/remediation:
- Evidence links:
