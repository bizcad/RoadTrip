# Node/Edge Connector Spec (Draft v0.1)

## 1) Node contract

Each node MUST declare:

- `id`: unique node identifier
- `provider_type`: `skill | mcp`
- `provider_name`: capability source name
- `operation`: callable operation/tool name
- `mode`: `prob | deter`
- `effect_class`: `pure | staged | committing | irreversible`
- `input_schema`: JSON-schema-like typed contract
- `output_schema`: JSON-schema-like typed contract
- `timeout_ms`: execution timeout
- `retry_policy`: retry count/backoff conditions
- `trust_requirement`: minimum trust state required

### Example shape

```yaml
id: plan_route
provider_type: skill
provider_name: route_planner
operation: generate_route
mode: deter
effect_class: pure
input_schema:
  type: object
  required: [origin, destination]
output_schema:
  type: object
  required: [route, eta]
timeout_ms: 12000
retry_policy:
  max_retries: 1
  on: [timeout]
trust_requirement: allow_auto
```

---

## 2) Edge contract

Each edge MUST declare:

- `from_node`
- `from_port`
- `to_node`
- `to_port`
- `edge_type`: `data | control | conditional | error`
- `transform` (optional): mapping expression or adapter id
- `required`: bool

### Edge semantics

- `data`: moves typed payload between ports
- `control`: sequencing only
- `conditional`: route on predicate
- `error`: explicit failure path

---

## 3) Execution boundaries

- Nodes with `effect_class in [pure, staged]` MAY be dropped on fatal failure before commit barrier.
- Nodes with `effect_class in [committing, irreversible]` require commit policy.
- `irreversible` nodes require:
  - explicit policy allowance,
  - pre-checks,
  - audit intent,
  - rollback verification where possible.

---

## 4) Trust checks before invocation

Before executing any `deter` node, the engine checks:

1. trust manifest status (`allow_auto|manual_review|block`)
2. fingerprint/provenance alignment
3. policy controls for effect class
4. MCP introspection drift state (for `provider_type=mcp`)

If any blocking check fails -> `halt + route error edge`.

---

## 5) MCP import normalization

MCP tools are imported through canonicalization:

1. introspect MCP capability
2. map to node contract fields
3. store introspection snapshot + hash
4. assign trust requirement and effect class
5. register as executable node template

---

## 6) Compiler passes (pre-run)

1. graph lint (well-formed DAG / allowed cycles policy)
2. schema/type check on all edges
3. policy/effect check
4. trust admission check
5. plan materialization (runtime execution plan)

Only successful plans are executable.
