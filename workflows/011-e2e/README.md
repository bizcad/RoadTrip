# Workflow 011: E2E Skill + MCP Workflow Execution

**Status**: Draft for tomorrow execution  
**Date**: 2026-02-16  
**Purpose**: Define a practical end-to-end path from vague user intent to trusted DAG execution.

---

## Scope

This workflow covers four linked tracks:

1. **DSL Terminology** for graph-based workflow authoring
2. **Node/Edge Connector Spec** for typed chaining and safe execution
3. **Skill Supply Chain Path** (`find -> test -> fingerprint -> register`)
4. **Real Workflow Run** (`select skills -> build DAG -> execute -> inspect artifacts`)

---

## Why this exists

The system differentiator is trusted execution.  
That requires both:
- a fluent graph-style workflow authoring model, and
- a trust-admission layer between suppliers (skills/MCPs) and users.

---

## Canonical Trust Hierarchy

Use this as the primary narrative for architecture and messaging:

1. **Trusted Supply Chain**
	- governance, vetting, provenance, and admission controls
2. **Trusted Capability Inventory**
	- admitted skills/MCPs with trust manifests and verification policy
3. **Trusted Workflow**
	- graph built from admitted capabilities with typed connectors and policy checks
4. **Trusted Actions & Outcomes**
	- verified execution results that are auditable and bounded by rollback/effect rules

Short form:

`trusted supply chain -> trusted capability inventory -> trusted workflow -> trusted actions and outcomes`

---

## Documents

- `DSL_TERMINOLOGY.md` — canonical terms and user-facing language
- `NODE_EDGE_CONNECTOR_SPEC.md` — technical connector and execution semantics
- `E2E_RUNBOOK.md` — tomorrow's operator checklist and definition of done

---

## Core design principle

**Probabilistic planning, deterministic execution.**

- LLM/prob hierarchy can transform vague user intent into candidate graph plans.
- Deterministic leaves execute only trusted, typed, policy-compliant nodes.
- Fatal failures halt at boundary and preserve pre-commit safety.
