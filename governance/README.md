# Governance

This folder contains enforceable governance policies for controlled infrastructure and candidate certification.

## Documents

- `Controlled_Infrastructure_Policy.md` — policy baseline for infrastructure mutation control.
- `RBAC_Model.md` — role boundaries and permissions.
- `Certification_Checklist.md` — testable gate criteria for candidate code artifacts.
- `Trusted_Skill_Assembly_PRD.md` — feature PRD for contract-based multi-runtime skill execution, trusted supply chain, and incident-driven self-improvement.

## Scope

Governance applies to all contributors (human and agent) and all code paths that can mutate critical infrastructure.

## Controlled Infrastructure (minimum)

- Registry and registry builders
- Memory stores and memory mutators
- Orchestrator and workflow runners
- Policy/guardrail engines

## Principle

Default behavior is read-only. Mutation requires explicit authorization, traceability, and passing guardrail checks.
