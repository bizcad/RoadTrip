# Hardened MCP Router — Fast-Thinking Notes

## Elevator pitch
Bring safety to AI integrations by forcing external MCP traffic through one hardened, observable control point.

## Initial boundary model
- Route external MCP calls through a dedicated router host (candidate: isolated iMac).
- Connect router and primary workstation over private Tailscale tailnet.
- Keep internal skills private by default; expose only an explicit allowlist.
- Treat any public endpoint as optional and policy-gated.

## Combined control-plane model (network + app)
- Use Tailscale + router firewall policy for network-level separation and path control.
- Use Registry-driven capability gating for app-level routing and permission control.
- Apply this model consistently across external skills, Aspire app endpoints, VPS services, and Docker containers.
- Require both layers to pass: reachable on approved network path and authorized by Registry/app policy.

## Minimal controls (phase 1)
- Default deny for inbound tools; allowlist only required MCP servers/capabilities.
- Per-connector identity and auth policy (no anonymous trust).
- Rate limits, timeout ceilings, and retry ceilings to prevent amplification.
- Full request audit log with source, target, policy decision, and outcome.
- Kill-switch to disable an external connector without stopping internal ops.

## Evidence to collect
- Count of blocked unauthorized attempts vs approved passes.
- Number of internal capabilities externally reachable (target: near zero).
- Mean time to isolate a misbehaving MCP source.
- False-positive deny rate on approved workflows.
- Number of denied requests blocked by network layer vs app policy layer.

## Decision trigger
Promote when this pattern consistently reduces exposed paths and improves incident containment without breaking approved workflows.

## Supporting transcription
- [docs/Tailscale for security.md](docs/Tailscale%20for%20security.md)
- [data/memory/stores/prospective/entries/mcp-router-hardening/transcription-source.md](data/memory/stores/prospective/entries/mcp-router-hardening/transcription-source.md)
- [data/memory/stores/prospective/entries/mcp-router-hardening/transcript-summary.md](data/memory/stores/prospective/entries/mcp-router-hardening/transcript-summary.md)

## Implementation checklist
- [data/memory/stores/prospective/entries/mcp-router-hardening/deployment-checklist.md](data/memory/stores/prospective/entries/mcp-router-hardening/deployment-checklist.md)
