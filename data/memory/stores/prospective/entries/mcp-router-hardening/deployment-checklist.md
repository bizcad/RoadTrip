# Deployment Checklist — MCP Router Hardening

Use this checklist to move from prospective design to controlled implementation.

## 1) Topology and scope
- [ ] Confirm nodes in scope: Windows workstation, iMac router host, optional VPS, optional Docker services.
- [ ] Confirm external MCP traffic terminates at router boundary, not directly on workstation.
- [ ] Confirm public endpoint usage is optional and explicitly approved.

## 2) Network layer gates (Tailscale + ACL)
- [ ] All participating nodes are joined to the intended tailnet.
- [ ] ACL posture is deny-by-default.
- [ ] Allowlist only required source→destination port paths.
- [ ] Verify no implicit iMac/VPS/container path to Windows unless explicitly required.
- [ ] Validate management/admin path is separate from runtime data paths.

## 3) Application layer gates (Registry + policy)
- [ ] Registry capability allowlist is defined per connector/route.
- [ ] Connector identity/auth policy is required for every external source.
- [ ] Routing decision is policy-evaluated and auditable for every request.
- [ ] Kill-switch exists to disable a connector without full system shutdown.

## 4) Runtime safety controls
- [ ] Request timeout ceilings are configured.
- [ ] Retry ceilings are configured to prevent amplification.
- [ ] Basic rate limits are configured per external connector.
- [ ] High-risk capabilities (file/secrets/local tooling) are blocked from external routes by default.

## 5) Validation tests
- [ ] Positive test: approved MCP workflow succeeds end-to-end.
- [ ] Negative test: unauthorized source or path is denied at network layer.
- [ ] Negative test: unauthorized capability is denied at app policy layer.
- [ ] Lateral movement test: iMac/VPS/container cannot reach blocked Windows targets.
- [ ] Incident test: kill-switch containment time is measured and acceptable.

## 6) Evidence capture
- [ ] Record blocked unauthorized attempts.
- [ ] Record allowed approved attempts.
- [ ] Record denied-by-network vs denied-by-app-policy counts.
- [ ] Record false-positive deny rate for approved workflows.
- [ ] Record mean time to isolate a misbehaving external connector.

## 7) Promote/hold criteria
- [ ] Promote when exposure is reduced and approved workflows remain stable.
- [ ] Hold if false-positive denies are high or policy drift is unresolved.
- [ ] Quarantine if kill-switch containment or isolation tests fail.

## References
- [data/memory/stores/prospective/entries/mcp-router-hardening/transcript-summary.md](data/memory/stores/prospective/entries/mcp-router-hardening/transcript-summary.md)
- [data/memory/stores/prospective/entries/mcp-router-hardening/hardening-notes.md](data/memory/stores/prospective/entries/mcp-router-hardening/hardening-notes.md)
- [docs/Tailscale for security.md](docs/Tailscale%20for%20security.md)
