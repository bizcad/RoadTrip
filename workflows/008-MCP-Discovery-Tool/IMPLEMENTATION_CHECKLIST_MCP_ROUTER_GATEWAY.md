# Implementation Checklist: MCP Router Gateway

Workflow: 008-MCP-Discovery-Tool  
Date: 2026-02-16  
Purpose: Turn the working spec into an executable plan with security-first controls.

Related spec: WORKING_SPEC_MCP_ROUTER_GATEWAY.md

Related artifacts:

- GATEWAY_API_CONTRACT.md
- SKILL_SANDBOX_EXTERNAL_ROUTER_PATTERN.md

---

## 1) What this component is

Treat the MCP router gateway as both:

- Router: single protocol endpoint for RoadTrip clients.
- Firewall and policy boundary: default-deny control point for registration, routing, and invocation.

This is not just convenience architecture. It is a trust boundary that must reduce blast radius.

---

## 2) Standardization baseline (MCP interaction model)

For planning assumptions, standardize around these operations:

- Service discovery (list available services/tools).
- Service detail retrieval (schemas/metadata).
- Tool invocation (request and response pass-through with controls).
- Optional admin operations (register, unregister, update metadata/skills).

Implementation rule:

- Client-facing API remains stable.
- Downstream server differences are normalized in gateway adapters.
- Any non-standard behavior is wrapped in explicit compatibility adapters and logged.

---

## 3) Security control gates (must pass in order)

## Gate A: Identity and access

- [ ] Admin operations require authenticated principal.
- [ ] Admin operations require role-based authorization.
- [ ] Break-glass role is isolated and audited.
- [ ] Service-to-service auth between RoadTrip and gateway is enforced.

Exit criteria:

- Unauthorized register/unregister attempts are denied and logged.

## Gate B: Credential handling

- [ ] No API keys in source files, scripts, or workflow docs.
- [ ] Secrets loaded from runtime secret store only.
- [ ] Per-server credential scoping is enforced (no shared super-token).
- [ ] Secret rotation process is documented and tested.
- [ ] Outbound call logs redact secrets and auth headers.

Exit criteria:

- Secret scanning returns no hardcoded credentials.
- Rotation dry-run succeeds without service outage.

## Gate C: Routing policy and egress control

- [ ] Default deny for new downstream destinations.
- [ ] Explicit allowlist by host, port, protocol, and path pattern.
- [ ] DNS rebinding and internal-address egress protections are enabled.
- [ ] Timeout, retry, and payload limits are enforced per server/tool.
- [ ] Circuit-breaker and quarantine mode are available.

Exit criteria:

- Calls to non-allowlisted destinations are blocked and attributed.

## Gate D: Admission controls

- [ ] Discovery record exists for each candidate MCP server.
- [ ] Vetting report exists and is linked.
- [ ] Trust manifest status is approved for active release window.
- [ ] Version and fingerprint are pinned before registration.
- [ ] Revocation mechanism is tested.

Exit criteria:

- Unadmitted server invocation is impossible by policy.

## Gate E: Telemetry and audit

- [ ] Every call has correlation ID and actor context.
- [ ] Allow, deny, fail, and timeout decisions are structured events.
- [ ] Logs are immutable or append-only and retained per policy.
- [ ] Gateway events map into RoadTrip release evidence model.

Exit criteria:

- End-to-end trace exists from request to downstream response or deny decision.

---

## 4) Deployment topology decision matrix

## Option 1: Local or private-network gateway

- Pros:
  - Lower exposure surface.
  - Easier to enforce internal network policy.
- Risks:
  - Operational burden for uptime and patching.
  - Potential local secret sprawl if unmanaged.
- Use when:
  - Early phases, internal-only testing, high data sensitivity.

## Option 2: Hosted gateway (for example Vercel) + private tunnel or VPN

- Pros:
  - Simpler public endpoint operations.
  - Can centralize access from distributed clients.
- Risks:
  - Edge-hosted credentials risk if secret model is weak.
  - Additional trust in hosting provider and tunnel chain.
  - Misconfiguration can create accidental public exposure.
- Required controls:
  - Gateway admin plane never public without strong auth.
  - Private connectivity to sensitive downstream targets through tunnel/VPN.
  - Strict egress allowlist and WAF/rate limiting at edge.
  - Zero secret material in client-delivered bundles/logs.

Recommendation:

- Start with Option 1 for hardening.
- Promote to Option 2 only after Gate A-E are passing and incident runbooks are tested.

---

## 5) Work breakdown structure

## Phase 1: Contract and policy

- [ ] Define gateway API contract for RoadTrip adapter.
- [ ] Define admitted inventory schema.
- [ ] Define policy schema for routing and invocation controls.
- [ ] Define telemetry schema mapping and release evidence fields.

Deliverables:

- Gateway contract document.
- Policy examples and validation tests.

## Phase 2: Adapter and integration

- [ ] Implement RoadTrip gateway adapter in src/mcp/interactions.
- [ ] Route non-critical MCP calls through gateway in shadow mode.
- [ ] Add feature flag for direct-path fallback during cutover.

Deliverables:

- Functional adapter and shadow-mode execution logs.

## Phase 3: Security hardening

- [ ] Integrate secret provider and redaction middleware.
- [ ] Enforce admin authz and registration policy checks.
- [ ] Add deny-by-default egress rules and host allowlist.
- [ ] Add automated policy tests for known abuse paths.

Deliverables:

- Security test report and hardening checklist sign-off.

## Phase 4: Trusted admission path

- [ ] Connect workflow 006 trust outputs to registration pipeline.
- [ ] Enforce pinned version and fingerprint match checks.
- [ ] Implement revoke and quarantine actions.

Deliverables:

- Admission pipeline runbook and revocation test evidence.

## Phase 5: Cutover and operations

- [ ] Switch selected workflows to gateway-only mode.
- [ ] Validate telemetry completeness for release gates.
- [ ] Execute incident drills: key leak, server compromise, route abuse.
- [ ] Remove direct ungoverned MCP access paths.

Deliverables:

- Cutover report and operations handbook.

---

## 6) Abuse and failure tests (minimum set)

- [ ] Attempt unauthorized registration.
- [ ] Attempt invocation of unadmitted server.
- [ ] Attempt route to blocked destination.
- [ ] Attempt oversized payload.
- [ ] Simulate downstream timeout and repeated failures.
- [ ] Simulate credential leak and force rotation.
- [ ] Simulate compromised server and verify quarantine/revoke.

Success condition:

- Every scenario ends in deterministic deny, containment, or controlled degradation with complete audit records.

---

## 7) Definition of done

All are true:

- [ ] RoadTrip uses one MCP gateway endpoint by default.
- [ ] Direct ungoverned external MCP calls are disabled.
- [ ] Credential handling passes scan and rotation tests.
- [ ] Admission and revocation workflows are operational.
- [ ] E2E evidence supports trusted supply chain -> trusted inventory -> trusted workflow -> trusted outcomes.

---

## 8) Open decisions for architecture review

- [ ] Hosting choice for first production deployment.
- [ ] Required tunnel or VPN model for hosted edge route.
- [ ] Secret store and rotation authority.
- [ ] Retention window and legal/compliance requirements for gateway logs.
- [ ] Incident response SLOs for revocation and containment.

---

## 9) Next artifacts to add

- [ ] Gateway API contract document.
- [ ] Admitted inventory schema JSON/YAML.
- [ ] Policy schema and validation rules.
- [ ] Incident response runbook for gateway compromise.
- [ ] Topology diagram for selected deployment option.
