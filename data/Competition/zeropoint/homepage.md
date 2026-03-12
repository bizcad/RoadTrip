# ZeroPoint - Portable Trust for the Post-Platform Internet

## Navigation

- Home
- Trust Triangle
- Tenets
- Architecture
- Footprint
- Playground
- Governing Agents
- Constraints
- Whitepaper
- Setup Letter
- GitHub

## Portable Trust Infrastructure

Cryptographic governance primitives that make actions provable, authority traceable, and exit real - for any participant, over any transport, without any central authority.

Watch the Trust Triangle. Try the Playground. Read the Whitepaper.

Three autonomous agents. Three independent trust domains. No shared database. No central authority.

## What Portable Trust Means

Any third party can verify what happened using receipts alone - without trusting your servers, your platform, or your claims. The evidence travels with the work, not with a vendor.

## How It Works

### One Flow, Portable Proof

An agent delegates a task. A receipt is produced. A third party verifies the chain. The network can disappear - the evidence remains.

1. **Action Requested**
	 A human or agent requests an action. The request hits the Guard, the local sovereignty boundary.
2. **Policy Evaluated**
	 Constitutional rules (non-removable) and operational rules evaluate the request. The most restrictive decision wins.
3. **Receipt Produced**
	 If allowed, the action executes. A signed, hash-chained receipt records what happened, who authorized it, and what constraints applied.
4. **Chain Verified**
	 Any peer can verify the receipt chain independently. No platform access is needed. The proof is the product.

## Constitutional Commitments

### The Four Tenets

Embedded in the protocol. Enforced in the code. No capability grant, no policy rule, and no consensus vote can override them.

1. **Tenet I: Do No Harm**
	 ZeroPoint shall not operate in systems designed to harm humans. The `HarmPrincipleRule` is a non-removable policy rule evaluated before every action. It cannot be bypassed, overridden, or removed at runtime.
2. **Tenet II: Sovereignty Is Sacred**
	 Every participant has the right to refuse any action. Every human has the right to disconnect any agent. No participant may acquire capabilities it was not granted. Coercion is architecturally impossible.
3. **Tenet III: Action Without Evidence Is No Action**
	 Every action produces a receipt. Every receipt joins a chain. No participant may act without leaving a cryptographic trace. If it is not in the chain, it did not happen.
4. **Tenet IV: The Human Is The Root**
	 Every delegation chain terminates at a human-held key. No agent may self-authorize. The genesis key is always held by flesh, blood, and soul. A human root can be a quorum (multisig) or an org-held key under policy - still human-accountable, never a single point of failure.

## Architecture

### Three Pillars of Governance

- **"May I?" - Guard**
	The participant's sovereign boundary. Runs locally, before any action, without consulting external authority. A peer can request. A peer cannot compel.
	Keywords: `local-first`, `actor-aware`, `pre-action`.
- **"Should I?" - Policy**
	Composable rules evaluated during every decision. Constitutional rules are loaded first and cannot be overridden. The most restrictive decision wins.
	Keywords: `rule-composed`, `graduated`, `WASM-extensible`.
- **"Did I?" - Audit**
	Hash-chained, receipt-native, immutable. Every outcome joins the chain. Peers can challenge each other's chains and produce signed attestations.
	Keywords: `hash-chained`, `receipt-native`, `collective`.

Flow:

`Request -> Guard (pre-action) -> Policy (decision) -> Execute -> Audit (post-action) -> Receipt`

Nothing executes without passing through the gate. Nothing passes through the gate without joining the audit chain.

## What ZeroPoint Provides

- **Signed Capability Grants**
	Portable cryptographic authorization tokens. Scoped by action type, constrained by cost ceilings, rate limits, time windows, and scope restrictions. Delegatable with depth controls.
- **Delegation Chains**
	Tier 2 participants delegate sub-capabilities to others - human to agent, agent to agent, or human to human. Eight invariants are enforced: parent-child linkage, scope narrowing, depth limits, expiration inheritance, and signature verification.
- **Multi-Dimensional Reputation**
	Four signal categories - audit attestation, delegation chain, policy compliance, and receipt exchange - are weighted and time-decayed into a composite score. Reputation gates policy decisions.
- **WASM Policy Modules**
	Sandboxed, fuel-limited policy rules exchanged between peers over the mesh. Compiled with wasmtime, hash-verified on receipt, and evaluated alongside native rules.
- **Distributed Consensus**
	Receipt-based multi-peer voting with configurable thresholds: Unanimous, Majority, or K-of-N. No central coordinator. Only signed receipts flowing through the mesh.
- **Collective Audit Verification**
	Peers challenge each other's audit chains, verify integrity, and produce signed attestations. Broken chains generate negative reputation signals.
- **Persistent Mesh State**
	SQLite-backed storage for peers, reputation signals, delegation chains, audit attestations, and policy agreements. Save and restore across node restarts.
- **CLI Tooling**
	Interactive chat, command security evaluation (Guard), mesh status and peer management, audit chain challenge, capability delegation, and state persistence - all from the terminal.

## Transport

### Sovereign Mesh Networking

ZeroPoint participants communicate over a Reticulum-compatible encrypted mesh - or HTTP, TCP, UDP, or any combination. No DNS, no certificate authorities, and no cloud infrastructure are required. Identity is a keypair. Authentication is a signature. The same protocol runs over LoRa at 300 baud or fiber at 1 Gbps. Agents, humans, and services are all first-class peers.

| Metric | Value |
| --- | --- |
| Destination hash | 128-bit |
| Default MTU | 500-byte |
| Cryptography | Ed25519 signing + X25519 ECDH |
| Framing | HDLC wire-compatible |

```rust
// Create a sovereign identity (agent, human, or service)
let identity = MeshIdentity::generate();
let node = MeshNode::new(identity);

// Attach any physical medium
let tcp = TcpClientInterface::connect("127.0.0.1:4242").await?;
node.attach_interface(Arc::new(tcp)).await;

// Start the mesh runtime
let runtime = MeshRuntime::start_default(Arc::new(node));

// Every action produces a receipt. Every receipt joins the chain.
```

## Foundation

### Built on Reticulum

ZeroPoint is built as a citizen of the Reticulum Network Stack, created by Mark Qvist. Reticulum proved that encrypted, uncentralizable networking requires no central authority - only cryptographic proof, personal sovereignty, and a refusal to build tools of harm.

The ZeroPoint Tenets draw directly from Reticulum's Harm Principle, its concept of cryptographic sovereignty, and its insistence that architecture embodies values. ZeroPoint builds on Reticulum's wire protocol as citizens of its mesh and carries forward its philosophical commitments into the domain of accountable digital action for agents, humans, and every system in between.

The Zen of Reticulum is required reading.

## Try It Now

ZeroPoint is open source, technically complete, and ready for early adopters.

```bash
# Clone the repository
git clone https://github.com/zeropoint-foundation/zeropoint.git
cd zeropoint

# Run all 699 tests across 13 crates
cargo test --workspace

# Start the governance server
cargo run -p zp-server

# Open the playground
open http://localhost:3000
```

### Interactive Demos

- Governance Playground: type an action and watch ZeroPoint evaluate it live.
- Chain Visualizer: see receipt chains form and verify integrity.

### Read the Docs

- Whitepaper: the full technical overview and portable trust thesis.
- Governance Framework: protocol constraints and tenets.

### Contribute

- GitHub: 13 crates, 699 tests, MIT/Apache-2.0.
- Contributing Guide: how to get involved.

> Trust is infrastructure.

## Footer Links

- Trust Triangle
- Playground
- Whitepaper
- Footprint
- Governing Agents
- GitHub

Maintained by ThinkStream Labs · MIT / Apache-2.0
