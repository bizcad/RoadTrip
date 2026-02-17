# Gateway API Contract (RoadTrip MCP Router)

Workflow: 008-MCP-Discovery-Tool  
Date: 2026-02-16  
Status: Draft v0.1

Purpose: Define a stable contract between RoadTrip and the MCP Router Gateway so implementation, policy enforcement, and testing can proceed in parallel.

---

## 1) Design principles

- Single client endpoint for RoadTrip runtime.
- Default-deny policy posture.
- Deterministic error semantics.
- Full traceability through correlation and decision IDs.
- Backward-compatible contract versioning.

---

## 2) Transport and envelope

## Base URL

- Gateway endpoint is environment-specific (local, private, hosted).

## Protocol

- HTTPS required outside local dev.
- JSON request and response bodies.

## Required headers

- X-Request-Id: caller-generated UUID.
- X-Actor-Id: authenticated caller identity.
- X-Policy-Context: workflow or execution context label.
- Authorization: bearer token or mTLS-bound identity token.

## Standard response envelope

All responses use:

```json
{
  "success": true,
  "requestId": "uuid",
  "decisionId": "uuid",
  "timestamp": "2026-02-16T12:00:00Z",
  "data": {},
  "error": null,
  "meta": {
    "contractVersion": "2026-02-16.v1",
    "gatewayVersion": "string"
  }
}
```

Error envelope:

```json
{
  "success": false,
  "requestId": "uuid",
  "decisionId": "uuid",
  "timestamp": "2026-02-16T12:00:00Z",
  "data": null,
  "error": {
    "code": "POLICY_DENY",
    "message": "Invocation denied by policy",
    "details": {
      "reason": "tool_not_allowlisted"
    }
  },
  "meta": {
    "contractVersion": "2026-02-16.v1",
    "gatewayVersion": "string"
  }
}
```

---

## 3) Consumer operations

## 3.1 List services

Method and path:

- GET /api/services

Query params:

- includeTools: boolean (default true)
- includeSkills: boolean (default false)
- trustState: admitted|quarantined|revoked|all (default admitted)

Success data shape:

```json
{
  "services": [
    {
      "name": "filesystem",
      "displayName": "Filesystem MCP",
      "description": "Read write local files",
      "trustState": "admitted",
      "version": "1.2.0",
      "fingerprint": "sha256:...",
      "tools": [
        { "name": "read_file", "description": "Read file content" }
      ]
    }
  ]
}
```

## 3.2 Get service details

Method and path:

- GET /api/services/{serviceName}

Success data shape:

```json
{
  "service": {
    "name": "filesystem",
    "trustState": "admitted",
    "version": "1.2.0",
    "fingerprint": "sha256:...",
    "toolSchemas": [
      {
        "name": "read_file",
        "inputSchema": { "type": "object" },
        "outputSchema": { "type": "object" }
      }
    ],
    "policy": {
      "allowed": true,
      "limits": {
        "timeoutMs": 30000,
        "maxPayloadBytes": 262144
      }
    }
  }
}
```

## 3.3 Invoke tool

Method and path:

- POST /api/services/{serviceName}/tools/{toolName}/invoke

Request body:

```json
{
  "input": {},
  "execution": {
    "timeoutMs": 30000,
    "idempotencyKey": "optional-uuid"
  },
  "policyContext": {
    "workflowId": "wf-011",
    "stage": "runtime",
    "riskTier": "standard"
  }
}
```

Success data shape:

```json
{
  "result": {
    "content": [],
    "raw": {}
  },
  "enforcement": {
    "policyDecision": "ALLOW",
    "appliedLimits": {
      "timeoutMs": 30000,
      "maxPayloadBytes": 262144
    }
  },
  "downstream": {
    "latencyMs": 123,
    "attempts": 1
  }
}
```

---

## 4) Admin operations (restricted)

## 4.1 Register service

Method and path:

- POST /api/admin/services

Request body:

```json
{
  "name": "candidate-weather",
  "displayName": "Candidate Weather",
  "description": "Weather MCP for evaluation",
  "transportType": "http",
  "endpoint": {
    "url": "https://example.com/mcp"
  },
  "admission": {
    "trustManifestId": "tm-2026-02-16-001",
    "version": "0.9.1",
    "fingerprint": "sha256:...",
    "expiresAt": "2026-03-01T00:00:00Z"
  },
  "policy": {
    "toolAllowlist": ["get_forecast"],
    "timeoutMs": 15000,
    "maxPayloadBytes": 131072,
    "egressProfile": "restricted-http"
  }
}
```

Policy requirements:

- Registration denied if trust manifest or fingerprint is missing.
- Registration denied if trust state is not admitted or sandbox-admitted.

## 4.2 Revoke service

Method and path:

- POST /api/admin/services/{serviceName}/revoke

Request body:

```json
{
  "reason": "compromise-suspected",
  "ticketId": "INC-12345",
  "effectiveMode": "immediate"
}
```

Effect:

- New invokes blocked immediately.
- Existing sessions drained or terminated per policy.

## 4.3 Update policy

Method and path:

- PUT /api/admin/services/{serviceName}/policy

Request body:

```json
{
  "toolAllowlist": ["read_file"],
  "timeoutMs": 10000,
  "maxPayloadBytes": 65536,
  "rateLimit": {
    "requestsPerMinute": 60
  }
}
```

---

## 5) Error taxonomy

Standard error codes:

- AUTHN_REQUIRED
- AUTHZ_DENIED
- POLICY_DENY
- TRUST_NOT_ADMITTED
- SERVICE_NOT_FOUND
- TOOL_NOT_FOUND
- DOWNSTREAM_TIMEOUT
- DOWNSTREAM_UNAVAILABLE
- PAYLOAD_TOO_LARGE
- RATE_LIMITED
- VALIDATION_ERROR
- INTERNAL_ERROR

Contract rule:

- Gateway never returns ambiguous freeform failure strings without a code.

---

## 6) Policy and trust semantics

Service states:

- admitted: routable for production contexts.
- sandbox-admitted: routable only in sandbox contexts.
- quarantined: blocked except admin diagnostics.
- revoked: blocked.

Invocation must include policy context and environment label:

- environment: dev|sandbox|prod
- trustMode: strict|relaxed-test

Prod policy rule:

- Only admitted services are invocable in prod with strict trustMode.

---

## 7) Telemetry contract

Each request emits at least:

- requestId
- decisionId
- actorId
- serviceName
- toolName
- policyDecision
- trustState
- latencyMs
- downstreamStatus
- errorCode (if any)
- timestamp

Required sink compatibility:

- Must map to RoadTrip evidence pipeline fields used by release gates.

---

## 8) Versioning and compatibility

- Contract version in response meta.contractVersion.
- Additive changes are minor-compatible.
- Breaking changes require new contractVersion and migration note.

---

## 9) Conformance tests

Minimum test suite:

- list services returns only admitted by default.
- register denied without trust manifest.
- invoke denied for unallowlisted tool.
- sandbox-admitted service denied in prod context.
- revoke blocks subsequent invokes immediately.
- every response includes requestId and decisionId.

---

## 10) Open implementation decisions

- Final auth mechanism: mTLS, JWT, or both.
- Idempotency behavior for invoke retries.
- Session draining policy on revoke.
- Max payload defaults by risk tier.
