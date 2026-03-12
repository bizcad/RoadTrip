Perfect—here’s a **PDP Decision API scaffold** and **Envoy/OPA integration** you can drop into your platform. It implements your unified equation:

> **ALLOW ⇐ Relationship ∧ Policy ∧ Context ∧ Evidence**; otherwise **DENY**.  
> (ReBAC via **SpiceDB/Zanzibar**; Policy via **OPA/Cedar**; enforced at **every boundary** using **Envoy ext\_authz** and sidecars.)

***

## 1) Decision API — normalized contract (one shape for API, queue, workflow, DB)

### Request (`POST /v1/authorize`)

```json
{
  "subject": { "type": "user|agent", "id": "user:nicholas", "spiffe_id": "spiffe://prod/agents/ap-minion" },
  "action": "pay_bill",
  "resource": { "kind": "AP::Payment", "id": "ACME-PAY-2026-0001" },
  "environment": { "env": "prod", "tenant": "acme", "time_hour": 10, "region": "us-west" },
  "delegation": { "rfc8693": true, "valid": true },    // On-behalf-of via OAuth 2.0 Token Exchange
  "risk": { "score": 65, "reasons": ["new_vendor"] },
  "evidence": {
    "workload_attestation": { "spiffe": true, "expires_at": "2026-03-10T23:59Z" },
    "provenance": { "slsa_level": 3, "sigstore_verified": true }
  }
}
```

*Notes*

*   **SPIFFE/SPIRE SVIDs** are identity **evidence** only (workload attestation); PDP still decides authorization.
*   **Delegation** is carried with **RFC 8693** OBO tokens (`act`/`sub` semantics, short‑lived and scoped).
*   **Provenance** expects **SLSA** attestations and **Sigstore** verification for sensitive operations (e.g., payments).

### Response

```json
{
  "decision": "allow|deny",
  "obligations": ["human_approval_required","second_reviewer_required"],
  "reasons": ["rebac_permission_missing","provenance_failed","outside_business_hours"],
  "audit": {
    "rebac_checked": { "permission": "pay", "resource": "ap_payment:ACME-PAY-2026-0001" },
    "policy_bundle": "ap/payments/bundle/v1",
    "correlation_id": "2e6f7d2a-31e7-44af-8d12-4a8c8a31a5e6"
  }
}
```

***

## 2) PDP service scaffold (C#/.NET 8 Minimal API)

> The PDP calls **SpiceDB** for the **relationship check** and **OPA** for the **policy** decision, then composes **ALLOW ⇐ ReBAC∧Policy** with your Context/Evidence. (SpiceDB exposes Zanzibar‑style Check/Expand/Lookup APIs; OPA serves policy bundles via HTTP/sidecar.)

> **Folder**: `pdp/`

### `Program.cs`

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.Extensions.Logging;
using System.Net.Http.Json;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient("spicedb");
builder.Services.AddHttpClient("opa");
var app = builder.Build();

app.MapPost("/v1/authorize", async (HttpContext ctx, IHttpClientFactory httpFactory, ILoggerFactory lf) =>
{
    var log = lf.CreateLogger("PDP");
    var req = await ctx.Request.ReadFromJsonAsync<AuthzRequest>();
    if (req is null) return Results.BadRequest("Invalid request");

    // 1) ReBAC (SpiceDB): check coarse permission (e.g., "pay") for subject→resource
    var rebac = await CheckRebacAsync(req, httpFactory);

    // 2) Policy (OPA): evaluate thresholds, business hours, risk, provenance, delegation
    var policy = await EvaluatePolicyWithOpaAsync(req, rebac, httpFactory);

    // 3) Compose
    var decision = new AuthzDecision
    {
        decision = (rebac.Allowed && policy.Allow) ? "allow" : "deny",
        obligations = policy.Obligations,
        reasons = policy.Reasons,
        audit = new AuditRecord
        {
            rebac_checked = new RebacAudit { permission = rebac.Permission, resource = $"{req.resource.kind}:{req.resource.id}" },
            policy_bundle = "ap/payments/bundle/v1",
            correlation_id = Guid.NewGuid().ToString()
        }
    };
    return Results.Json(decision);
});

app.Run();

// ------------ helpers ----------------

static async Task<RebacResult> CheckRebacAsync(AuthzRequest r, IHttpClientFactory f)
{
    var http = f.CreateClient("spicedb");

    // NOTE: Use official SpiceDB APIs or SDKs here.
    // Example (pseudo-HTTP): POST /v1/check { subject, permission, resource }
    // Real deployments often use gRPC with zedtokens for consistency.
    var permission = r.action switch
    {
        "pay_bill" => "pay",
        "final_approve_payment" => "approve",
        "submit_payment_for_approval" => "submit",
        _ => "view"
    };

    var payload = new
    {
        subject = r.subject.type == "agent" ? $"agent:{r.subject.spiffe_id}" : r.subject.id,
        permission,
        resource = $"{r.resource.kind}:{r.resource.id}",
        context = new
        {
            // pass tenant if you namespace by tenant
            tenant = r.environment.tenant,
            // pass caveat inputs (delegation scope & expiry) when checking delegated_agent
            required_scope = r.action,
            granted_scopes = new[] { "submit_invoice", "read" },
            now = DateTime.UtcNow,
            expires_at = DateTime.Parse("2026-03-10T23:59:00Z")
        }
    };

    var resp = await http.PostAsJsonAsync("/v1/check", payload);
    var ok = resp.IsSuccessStatusCode && (await resp.Content.ReadFromJsonAsync<SpiceCheckResp>())?.allowed == true;
    return new RebacResult { Allowed = ok, Permission = permission };
}

static async Task<PolicyResult> EvaluatePolicyWithOpaAsync(AuthzRequest r, RebacResult rebac, IHttpClientFactory f)
{
    var http = f.CreateClient("opa");
    var opaInput = new
    {
        input = new
        {
            subject = new { type = r.subject.type, spiffe_id = r.subject.spiffe_id, id = r.subject.id },
            action = r.action,
            resource = new { kind = r.resource.kind, id = r.resource.id, amount = r.resource.amount, approvals_count = r.resource.approvals_count, tenant = r.environment.tenant },
            environment = new { env = r.environment.env, time_hour = r.environment.time_hour },
            delegation = new { rfc8693 = r.delegation.rfc8693, valid = r.delegation.valid },
            risk = new { score = r.risk.score },
            evidence = new { provenance = new { slsa_level = r.evidence.provenance.slsa_level, sigstore_verified = r.evidence.provenance.sigstore_verified } },
            rebac = new { permission = rebac.Permission }
        }
    };

    // OPA REST API: POST /v1/data/ap/payments  (module returns allow/obligations/reasons)
    var resp = await http.PostAsJsonAsync("/v1/data/ap/payments", opaInput);
    var pr = await resp.Content.ReadFromJsonAsync<OpaDecision>();
    return new PolicyResult
    {
        Allow = pr?.result?.allow ?? false,
        Obligations = pr?.result?.obligations ?? Array.Empty<string>(),
        Reasons = pr?.result?.reasons ?? Array.Empty<string>()
    };
}

// ------------ contracts ----------------

record AuthzRequest(
    Subject subject, string action, Resource resource,
    Environment environment, Delegation delegation, Risk risk, Evidence evidence
);
record Subject(string type, string id, string spiffe_id);
record Resource(string kind, string id, long amount, long approvals_count);
record Environment(string env, string tenant, int time_hour, string region);
record Delegation(bool rfc8693, bool valid);
record Risk(int score, string[] reasons);
record Evidence(Provenance provenance);
record Provenance(int slsa_level, bool sigstore_verified);

record AuthzDecision
{
    public string decision { get; init; } = "deny";
    public IEnumerable<string> obligations { get; init; } = Array.Empty<string>();
    public IEnumerable<string> reasons { get; init; } = Array.Empty<string>();
    public AuditRecord audit { get; init; } = new();
}
record AuditRecord { public RebacAudit rebac_checked { get; init; } = new(); public string policy_bundle { get; init; } = ""; public string correlation_id { get; init; } = ""; }
record RebacAudit { public string permission { get; init; } = ""; public string resource { get; init; } = ""; }

record RebacResult { public bool Allowed { get; init; } public string Permission { get; init; } = ""; }
record PolicyResult { public bool Allow { get; init; } public IEnumerable<string> Obligations { get; init; } = Array.Empty<string>(); public IEnumerable<string> Reasons { get; init; } = Array.Empty<string>(); }
record SpiceCheckResp(bool allowed);
record OpaDecision(OpaResult result);
record OpaResult(bool allow, string[] obligations, string[] reasons);
```

**Why this shape**

*   Keeping **ReBAC** in **SpiceDB** avoids role explosion and centralizes relationships (Google Zanzibar model).
*   Running **OPA** as a sidecar or service next to workloads yields low‑latency decisions and simple bundle distribution.

***

## 3) Envoy + OPA/ExtAuthZ integration (API layer)

### Option A — Envoy → **OPA (sidecar)** (recommended for low latency)

Use the **OPA‑Envoy external authorization** pattern: Envoy calls OPA’s REST API; OPA evaluates your Rego and returns allow/deny; OPA can in turn call the PDP if you want to compose centrally. This pattern is widely documented and used in meshes and gateways.

```yaml
# envoy.yaml (snippet)
static_resources:
  listeners:
  - name: ingress_http
    address: { socket_address: { address: 0.0.0.0, port_value: 8080 } }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          route_config: { name: local_route, virtual_hosts: [ {name: backend, domains: ["*"], routes: [ { match: { prefix: "/" }, route: { cluster: app } } ] } ] }
          http_filters:
          - name: envoy.filters.http.ext_authz
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
              http_service:
                server_uri:
                  uri: http://opa:8181
                  cluster: opa
                  timeout: 0.5s
                path_prefix: /v1/data/ap/payments/allow
          - name: envoy.filters.http.router

  clusters:
  - name: app
    connect_timeout: 0.25s
    type: logical_dns
    lb_policy: round_robin
    load_assignment: { cluster_name: app, endpoints: [ { lb_endpoints: [ { endpoint: { address: { socket_address: { address: app, port_value: 8081 } } } } ] } ] }
  - name: opa
    connect_timeout: 0.25s
    type: logical_dns
    lb_policy: round_robin
    load_assignment: { cluster_name: opa, endpoints: [ { lb_endpoints: [ { endpoint: { address: { socket_address: { address: opa, port_value: 8181 } } } } ] } ] }
```

*   This is the classic **ext\_authz → OPA** sidecar design; OPA loads your `ap_payments.rego` bundle and answers immediately.

### Option B — Envoy → **PDP service** (central composition)

If you prefer central composition (ReBAC+Policy+Evidence in one hop), point `ext_authz` to `pdp:8080/v1/authorize` and have PDP call both SpiceDB and OPA itself (the scaffold above). Same Envoy pattern, different upstream.

***

## 4) Queue consumer pattern (Kafka/Azure SB/SQS/etc.)

> Every **message** is a potential boundary. Before processing, the consumer builds the **normalized request** and calls the PDP. If **deny** or **obligations** present, dead‑letter or enqueue an **approval** workflow. (Same PDP contract; same allow/deny semantics.)

```csharp
public sealed class PaymentQueueHandler
{
    private readonly HttpClient _pdp;
    public PaymentQueueHandler(IHttpClientFactory f) => _pdp = f.CreateClient("pdp");

    public async Task HandleAsync(QueueMessage msg)
    {
        var req = new AuthzRequest(
            subject: new("agent", id: "", spiffe_id: msg.SpiffeId),
            action: "pay_bill",
            resource: new("AP::Payment", msg.PaymentId, msg.Amount, msg.ApprovalsCount),
            environment: new("prod", msg.Tenant, DateTime.UtcNow.Hour, msg.Region),
            delegation: new(true, msg.OboValid),
            risk: new(msg.RiskScore, msg.RiskReasons),
            evidence: new(new(msg.SlsaLevel, msg.SigstoreVerified))
        );

        var resp = await _pdp.PostAsJsonAsync("/v1/authorize", req);
        var decision = await resp.Content.ReadFromJsonAsync<AuthzDecision>();
        if (decision?.decision == "allow")
        {
            await ProcessPayment(msg);
        }
        else
        {
            await ParkForHumanApproval(msg, decision?.obligations ?? Array.Empty<string>());
        }
    }
}
```

*   Running OPA/PDP next to consumers (sidecar or nearby service) keeps checks low‑latency and avoids UI-only enforcement.

***

## 5) Workflow step guard (e.g., orchestrator, Temporal, DTFx, custom)

> Treat **each step** (e.g., *DisburseFunds*, *IssueRemittance*) as a protected action. Build the normalized request (Subject, Action, Resource, Environment, Delegation, Risk, Evidence), call the PDP, and gate transitions on **allow**. This aligns with OPA’s “policy‑as‑code” applied at runtime—not just at the edge.

```csharp
public async Task<bool> DisburseFundsStep(WorkflowContext ctx, Payment pmt)
{
    var req = new AuthzRequest(
        subject: new(ctx.IsAgent ? "agent" : "user", ctx.UserId, ctx.SpiffeId),
        action: "pay_bill",
        resource: new("AP::Payment", pmt.Id, pmt.Amount, pmt.ApprovalsCount),
        environment: new(ctx.Env, ctx.Tenant, DateTime.UtcNow.Hour, ctx.Region),
        delegation: new(ctx.Obo, ctx.OboValid),
        risk: new(ctx.RiskScore, ctx.RiskReasons),
        evidence: new(new(ctx.SlsaLevel, ctx.SigstoreVerified))
    );
    var resp = await _pdp.PostAsJsonAsync("/v1/authorize", req);
    var decision = await resp.Content.ReadFromJsonAsync<AuthzDecision>();
    if (decision?.decision == "allow") return true;

    await CreateApprovalTask(pmt, decision?.obligations);
    return false;
}
```

***

## 6) Packaging: OPA bundle + PDP config

*   **OPA**: ship `ap_payments.rego` and `data.config.json` in a bundle; mount or serve from your bundle server to sidecars. This is the standard OPA deployment pattern in K8s and meshes.
*   **SpiceDB**: deploy as a managed authz graph, use **Check/Expand/LookupResources** and **caveats** for delegations (scope+expiry). This follows Zanzibar’s global‑scale ReBAC model.

***

## 7) Observability & audit (don’t skip)

*   **OPA decision logs**: enable and forward to your SIEM (contains input, decision, bundle hash). OPA recommends logging for compliance and debugging.
*   **SpiceDB zedtokens** and tuple audit: record the exact authorization snapshot used; this pattern comes from Zanzibar’s consistency model.
*   **Envoy ext\_authz metrics**: expose allow/deny counters, p95/p99 latencies for the authz hop; part of the standard Envoy filter metrics.

***

## 8) Security notes & defaults

*   **Deny‑by‑default** at PDP and in OPA/Cedar—only explicit **permit** passes. OPA docs promote this model.
*   Short‑lived **SPIFFE identities** and PoP/mTLS at every hop remove static secrets; industry‑standard for zero‑trust workload identity.
*   **RFC 8693** for any agent acting on behalf of a user; never “spoof” user identity inside the agent. Use `act` claim to preserve the actor chain.
*   Require **SLSA + Sigstore** evidence before high‑risk actions (e.g., `pay_bill`)—this is now mainstream supply‑chain hardening.

***

## 9) Ready to wire it into your repos?

I can generate:

1.  A **ready‑to‑commit** `pdp/` project (the .NET scaffold above),
2.  **Envoy** configs for both **OPA‑sidecar** and **PDP‑service** modes, and
3.  **Queue & workflow** helper packages that wrap the PDP call and normalize inputs.

Which target should I create first in your repo: **API Gateway (Envoy)**, **Queue Consumers**, or **Workflow Step package**?
