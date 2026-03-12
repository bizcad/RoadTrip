Nick, here’s the **Unified Blueprint** you asked for—expressed as one global equation, a normalized decision contract, and an enforcement architecture you can apply to **every** request (humans, agents, and even code), including Accounts Payable.

***

## 1) Global Authorization Equation

> **ALLOW** ⇐ **Relationship** ∧ **Policy** ∧ **Context** ∧ **Evidence**  
> **DENY** otherwise.

*   **Relationship**: What relationships exist between **Subject** and **Resource** (ownership, membership, delegation, tenancy)? Model these in a **Zanzibar‑style ReBAC graph** (e.g., SpiceDB) so you can express “who can do what on which resource” without role explosion.
*   **Policy**: Attribute‑ and condition‑based rules (time, amount thresholds, environment, approvals) evaluated by a separate **policy engine** (OPA or Cedar) with local caching/sidecars for low latency.
*   **Context**: Runtime facts like environment (prod/stage), tenant, device/workload posture, risk score; fed into the PDP at decision time.
*   **Evidence**: Cryptographically verifiable identity & integrity signals: **SPIFFE/SPIRE workload SVIDs** and **human OIDC** for *who*, plus **SLSA provenance + Sigstore signatures** for *what code/artifact* is acting.

> **Identity is only evidence.** Authorization is always a **separate decision service** (PDP), not embedded implicitly in tokens or app code.

***

## 2) Normalized Vocabulary (applies to every request)

All calls—API, queue, workflow step, DB read/write—must be normalized into:

*   **Subject**: human OIDC user or agent SPIFFE ID (e.g., `spiffe://prod/agents/ap-bot`).
*   **Action**: verb being attempted (`pay_bill`, `submit_invoice`, `open_pr`).
*   **Resource**: the object in your graph (`ap.payment:123`, `repo:survey/ux`). ReBAC stores this consistently.
*   **Environment**: env/tenant/region/device/workload attributes (e.g., `env=prod`).
*   **Delegation**: optional “on‑behalf‑of” chain and scope; mint via **OAuth 2.0 Token Exchange (RFC 8693)** for proper `sub`/`act` semantics.
*   **Risk**: runtime score (anomaly/spend/novelty) that can trigger **step‑up approval** in policy.
*   **Evidence**: attestation bundle: SPIFFE/SPIRE SVID (mTLS/PoP), OIDC claims, **SLSA attestation + Sigstore verification** for code/artifacts.

***

## 3) Enforce at **every** boundary (never only at UI)

Place a **Policy Enforcement Point (PEP)** in front of **each hop**:

*   **API & service mesh**: Envoy/Istio with **ext\_authz** calling your PDP; OPA sidecar pattern is standard.
*   **Queues & event consumers**: consumer wrapper calls PDP before processing message.
*   **Workflow engines**: guard each step (especially “approve”/“disburse”).
*   **Data layer**: database row‑/column‑level security derived from PDP decisions and tenant/resource attributes.

***

## 4) Control‑Plane Architecture (how it fits together)

1.  **Identity Plane (input evidence only)**
    *   **Humans**: OIDC from your IdP.
    *   **Workloads/Agents**: **SPIFFE/SPIRE** to issue short‑lived SVIDs; mTLS between services; eliminates “secret zero.”

2.  **Authorization Data Plane (relationships)**
    *   **SpiceDB** (Zanzibar‑style) stores relationships & delegations; answers “can `subject` perform `permission` on `resource`?” at scale.

3.  **Policy Decision Plane (conditions)**
    *   **OPA/Cedar** service or sidecar; bundles for rules; decision logs on every check.

4.  **Evidence & Supply‑Chain Plane**
    *   CI produces **SBOM**, **SLSA provenance**, and **Sigstore** signatures for all agent‑produced artifacts; PDP can require verified provenance for sensitive actions.

5.  **Delegation & OBO**
    *   Use **RFC 8693 token exchange** to mint short‑lived, scoped tokens carrying `act` (actor) and `sub` (subject) with proof‑of‑possession/mTLS.

***

## 5) Decision API (one contract for everything)

**Request**

```json
{
  "subject": {
    "type": "agent",
    "spiffe_id": "spiffe://prod/agents/ap-minion",
    "oidc": null
  },
  "action": "pay_bill",
  "resource": "ap.payment:PAY-2026-000123",
  "environment": { "env": "prod", "tenant": "acme" },
  "delegation": {
    "on_behalf_of": "user:nicholas",
    "scope": ["pay_bill"],
    "token_exchange": { "rfc8693": true }
  },
  "risk": { "score": 72, "reasons": ["high_amount","new_vendor"] },
  "evidence": {
    "workload_attestation": { "spiffe": true, "expires_at": "2026-03-04T20:15Z" },
    "provenance": { "slsa": 3, "sigstore_verified": true }
  }
}
```

**Response**

```json
{
  "decision": "deny",
  "obligations": ["human_approval_required", "second_reviewer"],
  "reasons": ["amount_above_manager_threshold", "risk>70"],
  "audit": { "rebac_tuple": "ap.system#manager@user:nicholas", "policy_id": "ap/payments/cedar/v3" }
}
```

*   This **separates** identity/evidence from authorization and forces every caller to declare **Subject, Action, Resource, Environment, Delegation, Risk, Evidence**.

***

## 6) ReBAC Schema (SpiceDB) for **Accounts Payable**

```zed
definition user {}

definition agent {}

definition ap.system {
  relation viewer: user | agent
  relation submitter: user | agent
  relation reviewer: user
  relation manager: user
  relation delegated_agent: agent
  // Permissions
  permission view    = viewer + submitter + reviewer + manager
  permission submit  = submitter + delegated_agent
  permission review  = reviewer + manager
  permission approve = manager
  permission pay     = manager // final check gated by Policy
}
```

*   Relationships capture *who may interact* with AP; policy will handle conditions (amounts, hours, multi‑approvals).

***

## 7) Policy Layer Examples (Cedar/OPA)

**A) Amount thresholds + business hours + provenance required**

```cedar
// Allow managers to pay if small amount, proper env, and verified provenance
permit (
  principal, action == Action::"pay_bill", resource in AP::Payment
)
when {
  ap.is_manager(principal, resource) &&
  resource.amount < 5000 &&
  context.env == "prod" &&
  context.provenance.slsa >= 3 && context.sigstore.verified == true &&
  (context.time.hour >= 8 && context.time.hour <= 17)
};
```

*   Conditional policies are what OPA/Cedar are designed for; they read context (env, time) and external evidence (provenance) during the decision.

**B) Large payments require delegation + two approvals + OBO token**

```cedar
permit (
  principal, action == Action::"submit_payment_for_approval", resource in AP::Payment
)
when {
  ap.is_submitter(principal, resource) &&
  resource.amount >= 5000 &&
  context.delegation.valid == true
};

permit (
  principal, action == Action::"final_approve_payment", resource in AP::Payment
)
when {
  ap.is_manager(principal, resource) &&
  resource.approvals.count >= 2 &&
  context.delegation.rfc8693 == true // issued via token exchange
};
```

*   Use **RFC 8693 token exchange** to encode “on‑behalf‑of” semantics with clear actor vs subject.

**C) Only attested workloads may call AP at all**

```rego
package ap.guard

default allow = false

allow {
  input.evidence.workload_attestation.spiffe == true
  startswith(input.subject.spiffe_id, "spiffe://prod/agents/")
}
```

*   OPA sidecars handle these low‑latency checks adjacent to the service.

***

## 8) Evidence Handling (what “Evidence” means operationally)

*   **Workload attestation**: validate SPIFFE SVID (short‑lived X.509/JWT) and mTLS between services; no static keys.
*   **Human identity**: OIDC tokens validate “who,” not “may”; PDP decides authorization.
*   **Delegation**: only honor actions with valid, unexpired **RFC 8693** OBO token carrying `act` claim + proof‑of‑possession/mTLS.
*   **Code provenance**: CI must attach **SLSA provenance**; entries and artifacts are **Sigstore**‑signed and recorded in **Rekor**; PDP can deny actions unless `sigstore_verified==true`.
*   **SBOM**: include CycloneDX/SPDX SBOM and approve only if dependency posture passes.

***

## 9) Agent “Filtered Reality” (from your Ada/Darwin/Sun‑Tzu note)

From your uploaded memo, the idea is to **shape the agent’s world so illegal paths never appear**. We implement this by:

*   **Gating tools and context before the agent sees them**: PEP asks PDP *before* exposing a tool, prompt segment, dataset, or API; unauthorized tools never enter the agent’s tool list. (Deterministic pruning of the thought tree.)
*   **Deterministic checkpoints**: even if the agent proposes an action, the pipeline cannot proceed until policies pass (linters/tests/provenance gates). This mirrors standard OPA/sidecar and supply‑chain attestations.

This makes RBAC/ReBAC/ABAC the *terrain*, not a wall the agent hits later—exactly as your “invisible infrastructure” idea suggests (thanks, “Eureka Squad” file).

***

## 10) Operations & Guarantees

*   **Caching & consistency**: use PDP sidecar caches + Zanzibar token consistency in SpiceDB; keep TTLs short; measure p95/p99.
*   **Auditability**: log decision inputs/outputs (subject, action, resource, context, evidence, relationships used, policy ID). OPA decision logs + SpiceDB checks give complete traces.
*   **Step‑up**: decisions can return **obligations** (e.g., “human\_approval\_required”); repeat call after obligation satisfied.
*   **Every boundary**: gateways, consumers, workflow steps, and DB layers **all** call PDP; the UI is not a trust boundary.

***

## 11) 30‑Day Rollout (practical path)

1.  **Stand up** SpiceDB (single tenant) + OPA PDP service and instrument **decision logging only** (no enforcement).
2.  **Instrument** API gateway/mesh with ext\_authz to PDP (shadow mode).
3.  **Add SPIFFE/SPIRE** to agents/CI runners; move service‑to‑service auth to mTLS.
4.  **Introduce RFC 8693** for delegated actions; begin with read‑only scopes.
5.  **Enable supply‑chain evidence** (SLSA+Sigstore+SBOM) and add a policy: “deny payment unless provenance verified.”
6.  **Flip to enforce** on AP endpoints; add workflow step gates and DB RLS.

***

## 12) What you’ll get

*   **One global equation** for every request (ALLOW ⇐ Relationship ∧ Policy ∧ Context ∧ Evidence).
*   **Normalized contract** (Subject, Action, Resource, Environment, Delegation, Risk, Evidence).
*   **Defense‑in‑depth** enforcement at every boundary (API, queue, workflow, DB).
*   **Auditable trails** linking identity, relationships, policies, and verifiable code provenance.

***

## Want me to generate the first drop?

I can deliver, in your repos:

1.  **SpiceDB schema** (AP + shared foundations for other domains).
2.  **OPA/Cedar bundle** with the payment thresholds, business hours, two‑person approvals, and provenance gates.
3.  **PDP Decision API** scaffold + Envoy/OPA integration snippets for API, queue consumers, and workflow steps.
4.  **CI snippets** to emit SLSA attestations and **cosign** signatures (verify in PDP).

Which do you want first: **schema**, **policy**, **decision API**, or **CI provenance**?
