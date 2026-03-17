# Pattern Recommender Spec (PPA)
Version: 0.1-draft  
Date: 2026-03-02  
Status: Draft

## 1) Purpose
Create a maintainable, improvable Pattern Recommender that helps the PPA map natural-language problems to software patterns without topping out over time.

Design intent:
- Keep probabilistic reasoning in recommendation and exploration.
- Keep deterministic behavior in code execution, validation, and governance.
- Make pattern choices auditable, measurable, and easy to revise.

---

## 2) Position on Pattern Catalogs (Wikipedia + historical sources)
Starting with a historically significant catalog is a good foundation, but not enough by itself.

Strengths of a canonical catalog (like Wikipedia and GoF lineage):
- Shared vocabulary across humans and agents.
- Good first-pass taxonomy (creational, structural, behavioral).
- Fast onboarding and explainability.

Limitations:
- Pattern descriptions are static; your scenarios are dynamic.
- Catalogs do not encode your constraints (risk, reversibility, budget, RBAC, HITL rules).
- New architectures (LLM orchestration, policy gating, eval loops) need modern pattern composition beyond classic catalogs.

Conclusion:
- Use catalog patterns as base primitives.
- Add a PPA-specific layer: governance patterns, agent orchestration patterns, memory retrieval patterns, and failure-handling patterns.

---

## 3) Core Meta-Pattern (SRCGEEE)
Assumed expansion of SRCGEEE:
- Sense
- Retrieve
- Compose
- Gate
- Execute
- Evaluate
- Evolve

### 3.1 Canonical Naming and Pronunciation
- Canonical acronym: `SRCGEEE`
- Canonical pronunciation: `CIRC-gee`
- One-line definition: Closed-loop pattern discovery and execution lifecycle for the PPA.
- Canonical expansion: Sense, Retrieve, Compose, Gate, Execute, Evaluate, Evolve.
- Documentation style rule: Use `SRCGEEE (pronounced CIRC-gee)` on first mention in each document, then use `SRCGEEE` only.
- Speech system note: Add `CIRC-gee` and `SRCGEEE` as linked lexical variants in speech-to-text and text-to-speech vocabularies.

Use SRCGEEE as the recommender control loop:
1. Sense: Normalize problem statement into structured scenario.
2. Retrieve: Fetch candidate patterns and prior decisions.
3. Compose: Build 2-4 candidate pattern bundles.
4. Gate: Apply risk, security, and HITL policy checks.
5. Execute: Select plan and generate deterministic implementation path.
6. Evaluate: Score outcome quality and fit.
7. Evolve: Update memory weights, retire weak patterns, promote strong ones.

---

## 4) Thinking-Speed Memory Architecture
Use all three tiers. They serve different latency/risk needs.

### 4.1 Fast Thinking (hot path)
Purpose:
- Sub-second retrieval for common scenarios.

Data:
- Pattern summaries
- Recently successful pattern bundles
- Top constraints and anti-pattern flags

Storage profile:
- Small indexed cache
- TTL + recency/frequency weighting

When to use:
- Low risk, known domain, high confidence, reversible actions.

### 4.2 Slow Thinking (deep local memory)
Purpose:
- Better fit for nuanced tradeoffs and historical similarity.

Data:
- Decision records
- Postmortems
- Architecture notes
- Benchmarks and failure classes

Storage profile:
- Structured store with semantic retrieval + metadata filters

When to use:
- Medium risk, non-trivial constraints, uncertainty above threshold.

### 4.3 Extra Slow / Careful Research
Purpose:
- High-assurance reasoning before costly or irreversible actions.

Data:
- External literature
- Standards/policy docs
- Cross-repo references
- Comparative evaluations

Storage profile:
- Research workspace, curated snapshots, citation trails

When to use:
- High risk, high novelty, low confidence, policy ambiguity, or spend/impact gates.

### 4.4 Tier Routing Rule
Route by Risk x Novelty x Irreversibility:
- Fast: low-low-low
- Slow: any medium
- Extra Slow: any high OR policy gate triggered

---

## 5) Pattern Recommender Functional Spec

### Inputs
- Natural-language scenario
- Context metadata (domain, stack, constraints, objectives)
- Governance policy (RBAC, HITL triggers, spend limits)
- Memory retrieval results (fast/slow/extra)

### Outputs
- Ranked pattern recommendations
- Pattern bundle rationale
- Confidence + uncertainty scores
- Required gates (HITL required/optional/not required)
- Deterministic implementation plan skeleton

### Non-functional requirements
- Deterministic output format (JSON)
- Explainable scoring
- Reproducible recommendation given same inputs and memory snapshot
- Full telemetry (latency, cost, override rate, post-deploy outcome)

---

## 6) JSON Schema (Recommendation Contract)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://roadtrip.local/schemas/pattern-recommender-result.schema.json",
  "title": "PatternRecommenderResult",
  "type": "object",
  "required": [
    "requestId",
    "timestampUtc",
    "scenario",
    "candidates",
    "selected",
    "governance",
    "scores",
    "explainability"
  ],
  "properties": {
    "requestId": { "type": "string", "minLength": 8 },
    "timestampUtc": { "type": "string", "format": "date-time" },
    "scenario": {
      "type": "object",
      "required": ["summary", "domain", "constraints", "objectives"],
      "properties": {
        "summary": { "type": "string", "minLength": 10 },
        "domain": { "type": "string" },
        "constraints": {
          "type": "array",
          "items": { "type": "string" }
        },
        "objectives": {
          "type": "array",
          "items": { "type": "string" }
        },
        "riskLevel": {
          "type": "string",
          "enum": ["low", "medium", "high", "critical"]
        },
        "noveltyLevel": {
          "type": "string",
          "enum": ["low", "medium", "high"]
        },
        "irreversibilityLevel": {
          "type": "string",
          "enum": ["low", "medium", "high"]
        }
      }
    },
    "candidates": {
      "type": "array",
      "minItems": 1,
      "maxItems": 8,
      "items": {
        "type": "object",
        "required": [
          "candidateId",
          "patternNames",
          "bundleType",
          "rationale",
          "score",
          "tradeoffs"
        ],
        "properties": {
          "candidateId": { "type": "string" },
          "patternNames": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string" }
          },
          "bundleType": {
            "type": "string",
            "enum": [
              "single-pattern",
              "composite-pattern",
              "orchestration-pattern",
              "governance-pattern"
            ]
          },
          "rationale": { "type": "string" },
          "tradeoffs": {
            "type": "array",
            "items": { "type": "string" }
          },
          "score": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
          },
          "determinismScore": { "type": "number", "minimum": 0, "maximum": 100 },
          "maintainabilityScore": { "type": "number", "minimum": 0, "maximum": 100 },
          "riskScore": { "type": "number", "minimum": 0, "maximum": 100 },
          "reversibilityScore": { "type": "number", "minimum": 0, "maximum": 100 },
          "operabilityScore": { "type": "number", "minimum": 0, "maximum": 100 },
          "memoryTierUsed": {
            "type": "string",
            "enum": ["fast", "slow", "extra-slow"]
          }
        }
      }
    },
    "selected": {
      "type": "object",
      "required": ["candidateId", "selectionReason", "implementationPlan"],
      "properties": {
        "candidateId": { "type": "string" },
        "selectionReason": { "type": "string" },
        "implementationPlan": {
          "type": "array",
          "minItems": 1,
          "items": { "type": "string" }
        }
      }
    },
    "governance": {
      "type": "object",
      "required": ["hitlRequired", "gateReasons", "rbacScope"],
      "properties": {
        "hitlRequired": { "type": "boolean" },
        "gateReasons": {
          "type": "array",
          "items": { "type": "string" }
        },
        "rbacScope": { "type": "string" },
        "policyViolations": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "scores": {
      "type": "object",
      "required": ["confidence", "uncertainty", "overallFit"],
      "properties": {
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "uncertainty": { "type": "number", "minimum": 0, "maximum": 1 },
        "overallFit": { "type": "number", "minimum": 0, "maximum": 100 }
      }
    },
    "explainability": {
      "type": "object",
      "required": ["whyThis", "whyNotOthers", "evidenceRefs"],
      "properties": {
        "whyThis": { "type": "string" },
        "whyNotOthers": {
          "type": "array",
          "items": { "type": "string" }
        },
        "evidenceRefs": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 7) Scoring Rubric (0-100)
Use weighted scoring for each candidate bundle.

### 7.1 Weighted dimensions
- Determinism and Testability: 25
- Maintainability and Evolvability: 20
- Risk and Security Fit: 20
- Reversibility and Recovery: 15
- Operational Fit (telemetry, deployability, supportability): 10
- Performance and Cost Efficiency: 10

Total: 100

### 7.2 Scoring guidance
For each dimension, score as:
- 0-39: weak fit
- 40-69: acceptable with caveats
- 70-84: strong fit
- 85-100: excellent fit

### 7.3 Penalties
Apply hard penalties before final ranking:
- Policy violation: minus 40 and force HITL gate
- Missing rollback path for medium+ risk: minus 20
- No test strategy: minus 25
- Observability missing: minus 15

### 7.4 Promotion rule
Promote a pattern bundle to Fast Thinking cache only if:
- Outcome success rate >= 80 percent over last N comparable runs
- No critical incidents in comparable scope
- Median confidence >= 0.75 and uncertainty <= 0.30

### 7.5 Retirement rule
Demote or retire bundle if any:
- 3 consecutive failures in same domain class
- drift rate exceeds threshold for 14-day window
- repeated policy gate escalations for same bundle

---

## 8) Tool-Selection Pipeline Integration Contract

### Request payload (minimum)
```json
{
  "requestId": "req-20260302-0001",
  "scenario": {
    "summary": "Need resilient agent orchestration with deterministic execution path",
    "domain": "PPA-core",
    "constraints": [
      "Windows + PowerShell environment",
      "Least privilege tools",
      "Human approval for irreversible actions"
    ],
    "objectives": [
      "Improve reliability",
      "Reduce failure recovery time"
    ],
    "riskLevel": "medium",
    "noveltyLevel": "medium",
    "irreversibilityLevel": "medium"
  }
}
```

### Decision logic summary
1. Route to memory tier by risk/novelty/irreversibility.
2. Retrieve candidate patterns and prior outcomes.
3. Compose candidate bundles.
4. Score with rubric.
5. Apply governance penalties and HITL gates.
6. Return ranked recommendations and selected plan.

---

## 9) Suggested Initial Pattern Catalog for PPA
Seed with a compact, high-value set first.

### Execution and reliability
- Command
- State Machine
- Saga
- Retry with backoff
- Circuit Breaker
- Bulkhead
- Idempotency Key

### Architecture and changeability
- Strategy
- Adapter
- Facade
- CQRS (where justified)
- Event Sourcing (selective)
- Anti-Corruption Layer

### Governance and safety
- Policy-as-Code
- Approval Gate (HITL)
- Least Privilege Executor
- Audit Log / Decision Record

### Learning loop
- Feedback Loop
- Postmortem pattern
- Pattern retirement/promote workflow

---

## 10) Open Questions
1. Should SRCGEEE be the canonical acronym in code artifacts, or expanded names only?
2. Do you want strict deterministic tie-breaking when candidate scores are equal?
3. Should policy penalties be configurable by domain (finance vs internal tooling)?

---

## 11) Next Implementation Step
Implement two files next:
1. pattern-recommender-result.schema.json (extracted from section 6)
2. pattern-scoring-rubric.yaml (weights, penalties, thresholds)

This draft intentionally keeps both in one document first for review speed.
