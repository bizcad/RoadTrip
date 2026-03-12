Awesome—here’s a **ready‑to‑drop OPA/Cedar policy bundle** that enforces your global equation for AP **payments**:

> **ALLOW ⇐ Relationship ∧ Policy ∧ Context ∧ Evidence**; otherwise **DENY**  
> (ReBAC/SpiceDB gives *Relationship*; OPA/Cedar enforce *Policy/Context/Evidence*.)

The bundle covers:

*   **Payment thresholds** (small vs. large amounts)
*   **Business hours** windows
*   **Two‑person approvals** for large payments
*   **Provenance gates** (require **SLSA** attestation + **Sigstore** verification)
*   **Delegation/OBO** (RFC 8693) for agent actions
*   A normalized **decision response** including **obligations** (e.g., “second\_reviewer\_required”).

> **Deployment note**: Run the PDP as an OPA sidecar (or service) at every boundary (API/mesh/queues/workflows) using Envoy `ext_authz`, a recommended low‑latency pattern in OPA and cloud docs.  
> **Supply‑chain evidence** is produced in CI (SLSA provenance + Sigstore/`cosign` signatures) and verified at decision time.  
> **Delegation** tokens for “on‑behalf‑of” are minted via **OAuth 2.0 Token Exchange (RFC 8693)**; policy checks their presence for sensitive actions.

***

## 0) Bundle Layout

    authz/
      cedar/
        schema.cedar
        policies.cedar
        tests/
          cases.json
      opa/
        ap_payments.rego
        data.config.json
        tests/
          ap_payments_test.rego

***

## 1) **Cedar** — schema + policies

> Cedar is ideal for concise, attribute‑rich allow rules; default is **deny‑by‑default**. You can run Cedar in your PDP service or translate these conditions into OPA. (Keep ReBAC outside in SpiceDB.)

### `cedar/schema.cedar`

```cedar
// ========== Entity & Action schema ==========
entity User {}
entity Agent {}
entity Group {}

entity AP::Payment {
    // attributes supplied as resource context
    amount: Long,
    approvals_count: Long,
    tenant: String
}

action "submit_payment_for_approval" appliesTo {
  principal: [User, Agent],
  resource: AP::Payment
}

action "final_approve_payment" appliesTo {
  principal: [User],
  resource: AP::Payment
}

action "pay_bill" appliesTo {
  principal: [User, Agent],
  resource: AP::Payment
}

// Decision context (environment + evidence)
context {
  env: String,                       // "prod" | "stage" ...
  time_hour: Long,                   // 0..23 (server-localized hour)
  risk_score: Long,                  // 0..100
  delegation: { rfc8693: Bool, valid: Bool },     // OBO & validity
  provenance: { slsa_level: Long, sigstore_verified: Bool },
  rebac_permission: String           // e.g., "pay"
}
```

### `cedar/policies.cedar`

```cedar
// ========== Business-hours guard (applies to all pay actions) ==========
forbid (principal, action == "pay_bill", resource in AP::Payment)
when { context.time_hour < 8 || context.time_hour > 17 };

// ========== Provenance gate for ALL pay actions ==========
forbid (principal, action == "pay_bill", resource in AP::Payment)
when { !(context.provenance.sigstore_verified) || context.provenance.slsa_level < 3 };

// ========== Only allow if ReBAC granted the coarse permission ("pay") ==========
forbid (principal, action == "pay_bill", resource in AP::Payment)
when { context.rebac_permission != "pay" };

// ========== Small payments: manager or delegated agent with OBO ==========
permit (principal, action == "pay_bill", resource in AP::Payment)
when {
  resource.amount < 5000 &&
  // env must be prod and risk below 70
  context.env == "prod" && context.risk_score < 70 &&
  // Either a human manager (checked in ReBAC) or an agent with OBO token
  (isUser(principal) || (isAgent(principal) && context.delegation.rfc8693 && context.delegation.valid))
};

// ========== Large payments: require 2 approvals and human finalization ==========
permit (principal, action == "pay_bill", resource in AP::Payment)
when {
  resource.amount >= 5000 &&
  context.env == "prod" &&
  resource.approvals_count >= 2 &&
  // final pay must be human; agents can submit/prepare but not finalize
  isUser(principal) &&
  context.delegation.valid == true // if acting for a business user, OBO token present
};

// ========== Approvals flow ==========
permit (principal, action == "submit_payment_for_approval", resource in AP::Payment)
when {
  context.env in ["prod","stage"] &&
  (isUser(principal) || (isAgent(principal) && context.delegation.rfc8693 && context.delegation.valid))
};

permit (principal, action == "final_approve_payment", resource in AP::Payment)
when {
  context.env == "prod" &&
  isUser(principal) &&
  // risk-adaptive: if risk >= 70, require at least 2 approvals prior to final approve
  (context.risk_score < 70 || resource.approvals_count >= 2)
};
```

**Why these elements**

*   **Business hours & risk** in policy ensures contextual control, recommended when enforcing at the PEP/PDP boundary.
*   **Provenance gates** (SLSA≥3 + Sigstore verification) guarantee code/artifact integrity before money moves.
*   **ReBAC permission check** ensures the principal is related to the resource via SpiceDB (manager/payer) before Cedar evaluates conditions.
*   **OBO (RFC 8693)** required for agent‑initiated payment flows.

***

## 2) **OPA** — Rego module mirroring Cedar logic

> Use OPA as the PDP (service or sidecar) behind Envoy `ext_authz`. Deploy bundles and keep TTL/caching short for low‑latency decisions.

### `opa/data.config.json` (tunable knobs)

```json
{
  "ap": {
    "business_hours": { "start": 8, "end": 17 },
    "small_amount_limit": 5000,
    "risk_stepup_threshold": 70,
    "min_slsa_level": 3
  }
}
```

### `opa/ap_payments.rego`

```rego
package ap.payments

default allow := false
default obligations := []
default reasons := []

config := data.ap

# Input contract (normalized):
# input = {
#   "subject": {"type": "user"|"agent", "spiffe_id": "...", "oidc": {...}},
#   "action":  "pay_bill" | "submit_payment_for_approval" | "final_approve_payment",
#   "resource": {"kind":"AP::Payment","id":"...","amount":n,"approvals_count":n,"tenant":"acme"},
#   "environment":{"env":"prod","time_hour":n},
#   "delegation":{"rfc8693":bool,"valid":bool},
#   "risk":{"score":n},
#   "evidence":{"provenance":{"slsa_level":n,"sigstore_verified":bool}},
#   "rebac":{"permission":"pay"|"approve"|"submit"}   # set by SpiceDB check upstream
# }

# --- Common guards ---------------------------------------------------------

business_hours_violation {
  input.action == "pay_bill"
  h := input.environment.time_hour
  h < config.business_hours.start
} {
  input.action == "pay_bill"
  h := input.environment.time_hour
  h > config.business_hours.end
}

provenance_violation {
  input.action == "pay_bill"
  not input.evidence.provenance.sigstore_verified
} {
  input.action == "pay_bill"
  input.evidence.provenance.slsa_level < config.min_slsa_level
}

rebac_not_granted {
  input.action == "pay_bill"
  input.rebac.permission != "pay"
}

# --- Small payments (< limit) ----------------------------------------------

small_payment_ok {
  input.action == "pay_bill"
  input.resource.amount < config.small_amount_limit
  input.environment.env == "prod"
  input.risk.score < config.risk_stepup_threshold
  # human OR agent-with-OBO
  input.subject.type == "user"  # human manager confirmed by ReBAC
} {
  input.action == "pay_bill"
  input.resource.amount < config.small_amount_limit
  input.environment.env == "prod"
  input.risk.score < config.risk_stepup_threshold
  input.subject.type == "agent"
  input.delegation.rfc8693
  input.delegation.valid
}

# --- Large payments (>= limit) ---------------------------------------------

large_payment_ok {
  input.action == "pay_bill"
  input.resource.amount >= config.small_amount_limit
  input.environment.env == "prod"
  input.resource.approvals_count >= 2
  input.subject.type == "user"      # finalization must be human
  input.delegation.valid            # if acting on behalf, OBO token validated upstream
}

# --- Approvals flow --------------------------------------------------------

submit_ok {
  input.action == "submit_payment_for_approval"
  input.environment.env == "prod" or input.environment.env == "stage"
  (input.subject.type == "user") or (input.subject.type == "agent" and input.delegation.rfc8693 and input.delegation.valid)
}

final_approve_ok {
  input.action == "final_approve_payment"
  input.environment.env == "prod"
  input.subject.type == "user"
  # risk-adaptive: if high risk, must have 2 approvals already
  (input.risk.score < config.risk_stepup_threshold) or (input.resource.approvals_count >= 2)
}

# --- Decision composition --------------------------------------------------

# Obligations for unmet conditions (used by orchestrator to trigger human steps)
collect_obligations[ob] {
  input.action == "pay_bill"
  input.resource.amount >= config.small_amount_limit
  input.resource.approvals_count < 2
  ob := "second_reviewer_required"
}
collect_obligations[ob] {
  input.action == "pay_bill"
  input.risk.score >= config.risk_stepup_threshold
  ob := "human_approval_required"
}

# Reasons (diagnostics)
collect_reasons[r] { business_hours_violation; r := "outside_business_hours" }
collect_reasons[r] { provenance_violation;    r := "provenance_failed" }
collect_reasons[r] { rebac_not_granted;       r := "rebac_permission_missing" }

allow {
  not business_hours_violation
  not provenance_violation
  not rebac_not_granted

  small_payment_ok
} {
  not business_hours_violation
  not provenance_violation
  not rebac_not_granted

  large_payment_ok
} {
  submit_ok
} {
  final_approve_ok
}

obligations := {o | collect_obligations[o]}
reasons := {r | collect_reasons[r]}
```

### Example **input** & **output**

```json
// input (agent trying to pay a big bill)
{
  "subject":{"type":"agent","spiffe_id":"spiffe://prod/agents/ap-minion"},
  "action":"pay_bill",
  "resource":{"kind":"AP::Payment","id":"ACME-PAY-2026-0001","amount":19000,"approvals_count":1,"tenant":"acme"},
  "environment":{"env":"prod","time_hour":10},
  "delegation":{"rfc8693":true,"valid":true},
  "risk":{"score":65},
  "evidence":{"provenance":{"slsa_level":3,"sigstore_verified":true}},
  "rebac":{"permission":"pay"}
}
```

```json
// decision
{
  "result": {
    "allow": false,
    "obligations": ["second_reviewer_required"], 
    "reasons": []
  }
}
```

> OPA sidecar/service & decision logging patterns are documented in OPA’s deployment guidance; Envoy `ext_authz` is a common integration.

***

## 3) Tests

### `opa/tests/ap_payments_test.rego`

```rego
package ap.payments

import data.ap.payments

test_small_payment_ok_human {
  input := {
    "subject": {"type":"user"},
    "action": "pay_bill",
    "resource": {"kind":"AP::Payment","id":"x","amount":1200,"approvals_count":0,"tenant":"acme"},
    "environment":{"env":"prod","time_hour":9},
    "delegation":{"rfc8693":false,"valid":false},
    "risk":{"score":10},
    "evidence":{"provenance":{"slsa_level":3,"sigstore_verified":true}},
    "rebac":{"permission":"pay"}
  }
  allow with input as input
}

test_large_payment_needs_two_approvals {
  input := {
    "subject": {"type":"user"},
    "action": "pay_bill",
    "resource": {"kind":"AP::Payment","id":"x","amount":9000,"approvals_count":1,"tenant":"acme"},
    "environment":{"env":"prod","time_hour":11},
    "delegation":{"rfc8693":true,"valid":true},
    "risk":{"score":20},
    "evidence":{"provenance":{"slsa_level":3,"sigstore_verified":true}},
    "rebac":{"permission":"pay"}
  }
  not allow with input as input
  obligations with input as input == {"second_reviewer_required"}
}

test_provenance_required {
  input := {
    "subject": {"type":"user"},
    "action": "pay_bill",
    "resource": {"kind":"AP::Payment","id":"x","amount":1000,"approvals_count":0,"tenant":"acme"},
    "environment":{"env":"prod","time_hour":9},
    "delegation":{"rfc8693":false,"valid":false},
    "risk":{"score":10},
    "evidence":{"provenance":{"slsa_level":2,"sigstore_verified":false}},
    "rebac":{"permission":"pay"}
  }
  not allow with input as input
  reasons with input as input contains "provenance_failed"
}
```

***

## 4) How this plugs into your **Unified Blueprint**

*   **Relationship** (SpiceDB) answers *“Who is related to the payment with permission ‘pay’?”*; we pass the result in `rebac.permission`.
*   **Policy + Context** (OPA/Cedar) enforce business hours, thresholds, risk step‑up, and approvals.
*   **Evidence** requires **SLSA≥3** + **Sigstore‑verified** artifacts for the calling workflow or agent, aligning with modern supply‑chain guidance.
*   **Delegation** uses **RFC 8693** OBO tokens for agents acting for humans.

***

## 5) Optional: Envoy → OPA wiring (sketch)

At the API gateway or service mesh, call OPA (PDP) with a normalized input each time you hit payment endpoints or workflow steps. OPA then returns `{ allow, obligations, reasons }`, which the orchestrator can use to either continue or collect human approvals. This sidecar model is a well‑documented pattern for high‑throughput, low‑latency enforcement.

***

## Want me to push this into your repo?

I can:

1.  Add these files under `authz/` with a **Makefile** to run OPA tests,
2.  Generate a **decision‑API** shim so your services call the PDP uniformly, and
3.  Add **CI steps** to emit SLSA + `cosign` signatures and have the PDP verify them at runtime.

Which do you want next—**repo patch** for the bundle, or the **decision‑API** shim?
