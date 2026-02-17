# SKILL Sandbox Pattern: Firewalled External Router

Workflow: 008-MCP-Discovery-Tool  
Date: 2026-02-16  
Status: Draft v0.1

Purpose: Define how candidate SKILLs that access external resources are executed in a sandbox through a firewalled external router, reducing direct exposure to RoadTrip core runtime.

---

## 1) Why this pattern exists

Candidate SKILLs and newly discovered MCP servers are high-uncertainty components.

Risks include:

- Leaking credentials on first integration.
- Data exfiltration through broad network paths.
- Unbounded calls to unknown external APIs.
- Prompt or tool output injection into trusted workflows.

Pattern objective:

- Isolate candidate execution, constrain egress, and observe behavior before promotion.

---

## 2) Pattern summary

- RoadTrip core does not call candidate external systems directly.
- Candidate SKILLs run in a sandbox execution plane.
- All outbound calls from sandbox flow through an external router with firewall policies.
- Router enforces allowlist, quotas, authn/authz, redaction, and telemetry.
- Promotion to admitted status requires sandbox evidence.

---

## 3) Logical topology

```
RoadTrip Core (trusted)
        |
        | controlled request
        v
Sandbox Skill Runner (isolated)
        |
        | outbound only via router
        v
External Router + Firewall Policies
        |
        | restricted allowlist destinations
        v
External APIs / MCP Servers
```

Optional hosted model:

- Router hosted on edge platform.
- Private tunnel or VPN from RoadTrip network to router admin and data planes.

---

## 4) Security controls (required)

## 4.1 Identity and auth

- Candidate runners authenticate to router using short-lived identities.
- Admin operations require stronger role and step-up authentication.

## 4.2 Credential safety

- No static API keys inside SKILL code or repository.
- Credentials issued per candidate and scoped per destination.
- Credentials rotated after each vetting cycle or incident.

## 4.3 Egress firewall policy

- Default deny all outbound destinations.
- Explicit allow by domain or IP, method, and path pattern.
- Block private and metadata network ranges unless explicitly required.

## 4.4 Data protection

- Request and response body size limits.
- Secret redaction before persistence.
- Optional content policy scanner for high-risk payloads.

## 4.5 Observability

- Full per-call telemetry with correlation IDs.
- Store denied and blocked events as first-class evidence.
- Maintain immutable audit stream for vetting committee review.

---

## 5) Candidate lifecycle through sandbox

1. Candidate admitted to sandbox-only trust state.
2. Candidate invoked only in sandbox context.
3. Router enforces strict outbound policy profile.
4. Telemetry and risk signals collected over defined test window.
5. Vetting review decides promote, continue-sandbox, or revoke.
6. Promotion updates trust state and policy profile for production.

---

## 6) Policy profiles

## Profile A: sandbox-strict

- Tight allowlist.
- Low rate limits.
- Small payload caps.
- Short timeouts.
- Mandatory content logging with redaction.

## Profile B: sandbox-expanded

- Expanded allowlist for deeper testing.
- Moderate rate and payload limits.
- Still blocked from core production data stores.

## Profile C: production-admitted

- Narrow, business-required allowlist only.
- Performance-tuned limits.
- Elevated reliability policies with strict trust mode.

---

## 7) Hosted external router notes

Using a hosted router can work if these are true:

- Admin plane is not internet-open without strong auth.
- Sensitive downstream targets are reachable only via private connectivity.
- Secrets are managed by hosted secret store integration, never in app config.
- Logs are exported to RoadTrip-controlled evidence storage.

Do not proceed with hosted router if:

- You cannot guarantee private connectivity for sensitive destinations.
- You cannot prove secret redaction and rotation in the hosting environment.

---

## 8) Minimum acceptance tests

- Candidate skill cannot access non-allowlisted endpoint.
- Candidate skill cannot run with expired credential.
- Sandbox-admitted candidate cannot execute in prod context.
- Router revoke blocks candidate immediately.
- All candidate calls generate complete telemetry records.

---

## 9) Promotion criteria to production

Candidate can be promoted only when:

- Security tests pass across abuse scenarios.
- Reliability and timeout behavior are within thresholds.
- No unresolved critical findings from telemetry review.
- Trust manifest and fingerprint are finalized.
- Production policy profile is reviewed and approved.

---

## 10) Immediate implementation tasks

- Define sandbox trust state and policy flags in admitted inventory schema.
- Add sandbox environment context to gateway invoke contract.
- Add policy profiles and validation tests.
- Add vetting report template section for sandbox telemetry evidence.
