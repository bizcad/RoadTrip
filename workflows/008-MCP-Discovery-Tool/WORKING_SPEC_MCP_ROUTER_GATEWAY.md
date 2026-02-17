# Working Spec: MCP Router Gateway for RoadTrip

**Workflow**: 008-MCP-Discovery-Tool  
**Date**: 2026-02-16  
**Status**: Draft for implementation planning  
**Author intent**: Single MCP endpoint acting as a controlled router/aggregator to isolate downstream MCP servers from the RoadTrip runtime.

---

## 1) Problem Statement

RoadTrip currently has strong trust, safety, and telemetry controls for internal skills, but MCP ecosystem onboarding has two hard problems:

1. Discovery + vetting complexity at scale.
2. Security exposure when multiple MCP servers are connected directly into the runtime environment.

A single router/aggregator can reduce direct exposure by making all MCP traffic pass through one controlled boundary.

---

## 2) Goals and Non-Goals

## Goals

- Provide one MCP connection endpoint for agent clients.
- Isolate downstream MCP servers behind a gateway boundary.
- Enforce trust-admission policy before a server can be registered/used.
- Centralize telemetry and policy enforcement for MCP calls.
- Support dynamic registration only through controlled admin paths.

## Non-Goals

- Replacing RoadTrip skill orchestration logic.
- Replacing existing trust manifest/vetting workflows.
- Allowing direct bypass paths from orchestrator to untrusted MCP servers.

---

## 3) Security Position

The gateway is a **policy enforcement point**, not just a network hop.

Security value comes from:

- Single ingress/egress control plane for MCP tool traffic.
- Reduced blast radius from compromised/unreliable downstream servers.
- Deterministic policy checks before registration and invocation.
- Better incident response via one choke point for deny/disable operations.

Security failure mode to avoid:

- Treating centralization as security while leaving registration and egress unconstrained.

---

## 4) Target Architecture (Conceptual)

```
RoadTrip Orchestrator/Agent
        |
        |  MCP (single connection)
        v
+-----------------------------+
| MCP Router Gateway          |
| - admission checks          |
| - policy enforcement        |
| - authn/authz               |
| - telemetry + audit         |
| - timeout/retry/circuit     |
+-------------+---------------+
              |
              | controlled outbound only
              v
      [Admitted MCP Servers]
   (stdio and/or http transports)
```

### Trust boundaries

- Boundary A: RoadTrip runtime -> Gateway endpoint.
- Boundary B: Gateway -> downstream MCP servers.
- Boundary C: Admin registration/update APIs.

---

## 5) Admission and Runtime Control Model

## 5.1 Admission pipeline (mandatory)

No MCP server is routable until these pass:

1. Discovery record exists (source, metadata, capability claims).
2. Vetting evidence exists (security, quality, integration feasibility).
3. Trust manifest signed/approved for release window.
4. Version/fingerprint pinned in admitted inventory.
5. Registration request approved by policy and logged.

## 5.2 Runtime invocation policy (mandatory)

Every invoke path enforces:

- Server is in admitted inventory and not revoked.
- Requested tool is allowlisted for caller/context.
- Timeout, retry, payload size, and response size limits.
- Structured decision telemetry for allow/deny/fail.

---

## 6) Threat Model Summary

## Primary threats

- Unauthorized server registration.
- Confused deputy via broad tool passthrough.
- Data exfiltration from over-permissive downstream calls.
- Prompt/tool output injection from untrusted MCPs.
- Telemetry tampering or non-attributed events.

## Required mitigations

- Admin API authentication + role-based authorization.
- Default-deny registration and invocation policies.
- Egress allowlist by host/port/protocol.
- Per-server credential scope and secret isolation.
- Immutable/auditable logs with correlation IDs.
- Rapid revoke/disable path for admitted servers.

---

## 7) RoadTrip Mapping

## Existing assets this spec builds on

- Skill registry and trust orientation.
- Safety rules and authorization policy model.
- Telemetry-first release decisions.
- MCP acquisition workflow and catalog plans.

## Proposed mapping in repo

### A) Workflow and governance docs

- Extend Workflow 008 with gateway policy docs and operational runbooks.
- Link Workflow 006 trust admission outputs to gateway registration inputs.
- Link Workflow 011 E2E runbook to single-endpoint MCP execution.

### B) Runtime integration

- Keep RoadTrip orchestrator as decision layer.
- Add a gateway adapter in src/mcp/interactions for:
  - list services
  - get service details
  - invoke tool
  - admin registration flow (restricted)

### C) Data and policy artifacts

- Add admitted MCP inventory artifact (version + fingerprint pinned).
- Add gateway policy config for invocation constraints.
- Map gateway events into existing telemetry schema with explicit source="mcp_gateway".

Planned schema artifact filename:

- ADMITTED_INVENTORY_SCHEMA.yaml

---

## 8) Minimum Viable Controls (MVP)

MVP must include all of the following before production use:

1. Single endpoint routing enabled.
2. Registration blocked unless trust manifest + fingerprint are present.
3. Invocation default-deny with per-server/tool allowlists.
4. Timeout and rate-limit guardrails enabled.
5. Unified telemetry with correlation IDs across request chain.
6. Kill-switch to revoke one server and global disable switch.

---

## 9) Rollout Plan

## Phase 0: Design and policy lock

- Freeze control requirements.
- Define telemetry schema mapping and release criteria.

## Phase 1: Shadow mode

- Route non-critical MCP reads through gateway.
- Compare telemetry and failure modes against direct paths.

## Phase 2: Controlled cutover

- Move approved workflows to gateway-only path.
- Keep emergency rollback path for a defined period.

## Phase 3: Enforced mode

- Remove direct MCP access from orchestrator runtime.
- Admission + gateway controls become mandatory path.

---

## 10) Acceptance Criteria

This spec is considered implemented when:

- RoadTrip clients use one MCP endpoint by default.
- Unadmitted MCP server invocation is impossible by policy.
- Revocation propagates quickly and is auditable.
- Security and telemetry evidence supports release decision gates.
- E2E test run demonstrates trusted supply chain -> trusted inventory -> trusted workflow -> trusted outcomes.

---

## 11) Open Questions

1. Should admin registration be human-approved only or support signed automation tokens?
2. What is the allowed maximum blast radius for a compromised downstream MCP before automatic quarantine?
3. Which telemetry sink is authoritative for release gates when gateway and orchestrator disagree?
4. What is the default retention policy for gateway audit logs?

---

## 12) Immediate Next Steps

1. Add a companion implementation checklist doc in this folder.
2. Define admitted-inventory schema (name, version, fingerprint, trust status, revocation state).
3. Add adapter contract in src/mcp/interactions.
4. Add an E2E test scenario in Workflow 011 for gateway isolation and revoke behavior.
