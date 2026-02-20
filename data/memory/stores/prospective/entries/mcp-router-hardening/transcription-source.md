# Transcription Source — Tailscale for Security

## Source document
- [docs/Tailscale for security.md](docs/Tailscale%20for%20security.md)

## Why this is attached
This transcription expands the original MCP router thread with practical security rationale for using a private Tailscale tailnet as the transport boundary for MCP router traffic.

## Extracted focus points for this packet
- Keep router access on private overlay networking by default.
- Avoid direct public exposure of internal skills and tools.
- Use policy-based access control and observable connection decisions.
- Treat public endpoint support as opt-in and hardened, not default.

## Usage in slow-thinking stage
Use this transcription as supporting context when drafting architecture ADRs and control-plane policies for MCP router deployment.
