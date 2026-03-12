# RoadTrip vs ZeroPoint Feature Matrix

Date: 2026-03-06
Status: Discussion draft (not a decision memo)

## Summary

This matrix compares ZeroPoint's protocol-first trust model with RoadTrip/PPA's policy-and-supply-chain trust model.

High-level view:
- ZeroPoint: cryptographic protocol primitives (receipts, capability chains, constitutional rules, transport-agnostic proofs).
- RoadTrip/PPA: unified principal model (human/agent/code), deterministic PDP/PEP gating, and enterprise-grade attested code supply chain.

## Feature Matrix

| Area | ZeroPoint | RoadTrip/PPA | Relative Position |
| --- | --- | --- | --- |
| Core trust model | Portable cryptographic trust substrate with signed receipts and chained evidence | Unified auth equation: `ALLOW <= Relationship AND Policy AND Context AND Evidence` | Different focus: substrate vs control plane |
| Principal model | Participant-agnostic keypairs and capability holders | Explicit human/agent/code principal envelope with trust levels and roles | RoadTrip stronger for enterprise IAM modeling |
| Authorization primitives | Cryptographic capability grants + delegation-chain invariants | RBAC/ReBAC/ABAC + PDP/PEP + scoped delegation + risk gates | RoadTrip stronger in business-policy expressiveness |
| Human governance | Human-rooted delegation and sovereignty constraints in protocol tenets | HITL policy gates + non-recoverable-resource rule + risk scoring | Similar intent; RoadTrip stronger operationally |
| Tamper resistance | Signed hash-chained receipts and peer challenge attestations | Rich audit logs and decision traces, but mostly policy/runtime artifacts today | ZeroPoint stronger cryptographic non-repudiation |
| Supply chain trust | Emphasis on action receipts and capability accountability | Explicit SLSA + Sigstore + SBOM + provenance-gated authorization | RoadTrip stronger here |
| Policy constraints | Non-removable constitutional rules in evaluation order | Layered auth model with roadmap toward stricter controls | ZeroPoint ahead on hard immutability |
| Runtime policy | WASM policy modules and restrictive precedence | OPA/Cedar policy plane with normalized decision API | Rough parity with different implementation style |
| Transport posture | Mesh-first + transport-agnostic governance proofs | Boundary-first enforcement (API/queue/workflow/DB) | ZeroPoint stronger in sovereign/offline networking |
| Explainability and evolution | Receipts, chains, and reputation signals | SRCGEEE cycle + scoring rubric + telemetry-driven evolution | RoadTrip stronger lifecycle tooling |

## Deep-Dive: Cryptographic Substrate vs Fingerprinting

### ZeroPoint cryptographic substrate (what it is)
- Native protocol objects are signed and chained at action time.
- Authorization is represented as cryptographic capability grants and delegation chains.
- Evidence portability is first-class: third parties can verify chain integrity independent of a central platform.

### RoadTrip fingerprinting/provenance model (what it is)
- Fingerprinting and provenance are used to establish trust in code/artifacts (who built it, how, under what controls).
- SLSA + Sigstore + SBOM provide supply-chain evidence quality.
- PDP uses provenance as decision input to allow/deny sensitive actions.

### Key difference (important)
- ZeroPoint substrate secures action accountability at protocol/runtime event level.
- RoadTrip fingerprinting secures artifact origin and integrity at build/supply-chain level.

These are complementary, not mutually exclusive:
- Fingerprinting tells you whether the code is trustworthy.
- Cryptographic receipts tell you what the trustworthy code actually did.

## Deep-Dive: SPIFFE/SPIRE vs API Keys

### API keys (legacy baseline)
- Usually static/shared secrets.
- Hard to rotate and easy to leak.
- Weak binding to runtime identity and poor attribution for agent actions.

### SPIFFE/SPIRE workload identity
- Short-lived, cryptographically verifiable workload identity (SVIDs).
- Better zero-trust posture with mTLS and proof-of-possession patterns.
- Stronger principal attribution for agent/service calls.

### Practical RoadTrip implication
- "Goodbye API keys" should be a phased migration, not a flag day.
- Keep API keys only for temporary compatibility edges.
- Move internal agent/service trust to SPIFFE/SPIRE-issued identities and enforce via PDP + policy.

## Discussion Questions Before Decision

1. Do we want to remain control-plane-first and add portable cryptographic receipts later, or prioritize receipts now?
2. Should provenance-gated authorization (`deny unless attested`) become constitutional/non-overridable in our policy hierarchy?
3. Which domains need full SPIFFE/SPIRE first: CI runners, orchestrator agents, or service mesh traffic?
4. What is our minimum viable receipt format if we choose to add event-level cryptographic accountability?
5. How much of ZeroPoint's model do we adopt directly vs map into RoadTrip-native constructs?

## Suggested Near-Term Hybrid Path

1. Keep RoadTrip's principal/RBAC/ReBAC/PDP architecture as the base.
2. Formalize SPIFFE/SPIRE migration plan to reduce API-key dependence.
3. Add a signed decision-receipt artifact for high-risk actions (spend, deploy, policy change).
4. Make provenance gates (`SLSA + Sigstore`) mandatory for critical action classes.
5. Revisit constitutional/non-removable policy layer after first receipt pilot.
