# Transcript Summary — Tailscale for MCP Router Security

## Scope
Source transcript: [docs/Tailscale for security.md](docs/Tailscale%20for%20security.md)

This summary captures architecture-relevant conclusions for the `mcp-router-hardening` prospective packet.

## Core takeaway
Use a dedicated MCP router host (iMac candidate) on a private Tailscale tailnet as the network boundary, then enforce Registry/policy controls at the application layer.

## Key points distilled
- The MCP aggregator/router should be the single ingress control point for external MCP traffic.
- Internal skills (file operations, secrets, local tooling) should remain private-by-default and never directly exposed.
- Tailscale is positioned as a zero-trust private overlay with identity-based ACL segmentation.
- Policy intent is deny-by-default with explicit allowlist paths between nodes and ports.
- Public endpoint support can exist, but only as opt-in and hardened on the router boundary.

## Topology implied by the transcript
- Windows workstation (RoadTrip runtime)
- iMac router host (MCP aggregator / policy firewall boundary)
- Optional cloud VPS node (joined to same tailnet)
- Optional containerized services (Docker) behind explicit policy paths

## Separation model
- **Network-level separation:** Tailscale identity + ACL segmentation controls who can reach which host/port.
- **App-level separation:** Registry and connector policy controls what capabilities/routes are allowed once connected.
- Both layers must allow a path; either layer can deny.

## Directional access intent (example)
- Windows → iMac router (approved ports only)
- Windows → VPS (approved ports only)
- iMac/VPS → Windows denied by default unless explicitly granted
- External MCP endpoints terminate at router boundary, not directly on workstation

## Security outcomes to validate
- Reduced externally reachable internal capabilities
- Increased blocked unauthorized attempts at router/network boundary
- Stable approved workflows with low false-positive deny rate
- Faster isolation of misbehaving external connectors

## Notes
This is a planning summary of transcript content for prospective-memory use; implementation details should be validated with concrete ACL/policy configuration during slow-thinking design and testing.
