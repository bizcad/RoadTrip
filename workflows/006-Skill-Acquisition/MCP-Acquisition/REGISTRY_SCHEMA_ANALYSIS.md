# Official MCP Registry Schema Analysis

**Date**: February 14, 2026  
**Source**: https://github.com/modelcontextprotocol/registry  
**Schema Version**: 2025-12-11  
**API Version**: v0.1 (API Freeze - stable, no breaking changes)

---

## Registry Overview

The Official MCP Registry is a metaregistry (not a package registry):
- **Purpose**: Metadata about MCP servers, not the code/binaries themselves
- **Hosting**: https://registry.modelcontextprotocol.io
- **API Docs**: https://registry.modelcontextprotocol.io/docs
- **GitHub**: https://github.com/modelcontextprotocol/registry
- **Status**: Preview (launched Sep 2025), API Freeze as of Oct 2025
- **Maintained by**: Anthropic, GitHub, PulseMCP, Microsoft, Stacklok

---

## Server.json Format

### Root Structure

```typescript
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.user/server-name",
  "description": "Server description",
  "version": "1.0.0",
  "repository": { /* optional */ },
  "icons": [ /* optional */ ],
  "packages": [ /* required */ ]
}
```

### Key Sections

#### 1. **Identity** (Required)
- **name**: Unique identifier in format `io.github.user/name` or similar
  - Namespace formats: `io.github.USER`, `me.DOMAIN`, `com.COMPANY`, etc.
  - Namespace ownership enforced via GitHub OAuth or DNS/HTTP verification
- **description**: Human-readable description
- **version**: SemVer version string

#### 2. **Repository** (Optional)
```typescript
{
  "url": "https://github.com/owner/repo.git",
  "source": "github"  // or other VCS
}
```

#### 3. **Icons** (Optional)
```typescript
{
  "src": "https://example.com/icon.png",
  "mimeType": "image/png",
  "sizes": ["32x32", "128x128"]
}
```

#### 4. **Packages** (Required - Array)
Each package defines how to obtain and run the MCP server:

```typescript
{
  "registryType": "npm" | "pypi" | "oci" (docker) | "nuget" | "mcpb",
  "identifier": "package-name",
  "version": "1.0.0",
  "runtimeHint": "npx" | "python" | "docker" | "dnx",
  
  "transport": {
    "type": "stdio"  // or "sse" or "http"
  },
  
  "environmentVariables": [
    {
      "name": "API_KEY",
      "description": "Description of what this is",
      "isRequired": true | false,
      "isSecret": true | false  // redacted in UI
    }
  ]
}
```

---

## Registry Ecosystem Structure

### Package Registries Referenced
- **npm**: Node.js packages
- **PyPI**: Python packages
- **OCI (Docker Hub)**: Container images
- **NuGet**: .NET packages
- **mcpb**: Binary bundles (downloadable .mcpb files with SHA256 checksums)

### Transport Types
- **stdio**: Standard in/out communication
- **sse**: Server-Sent Events
- **http**: HTTP requests

---

## Data from Seed

The seed database includes authenticated MCPs from major domains:

- `io.github.*` - GitHub user/org repositories
- `ai.company/*` - Company-owned MCPs (Anthropic, GitHub, etc.)
- `me.domain/*` - Individually-owned MCPs with DNS verification

### Example: Smithery Namespace
- 150+ community MCPs published under `ai.smithery/` namespace
- Range from test servers to production tools
- Examples: Discord integration, Reddit ads, Unreal Engine control, PDF processing

---

## API Endpoints (v0.1)

### List Servers
```bash
GET /v0.1/servers
```

Returns paginated list with filtering support.

### Get Single Server
```bash
GET /v0.1/servers/{name}
```

### Search/Filter
- By name
- By description keywords
- By recent updates
- By package type

### Authentication Endpoints
- GitHub OAuth
- GitHub OIDC token exchange
- DNS verification
- HTTP verification

### Admin Endpoints
- Validation (`/validate`) - Returns validation errors/warnings
- Health checks
- Version info

---

## Empirical Discovery Plan

To build our MCP catalog, we will:

### Phase 1: Query Registry (This Week)
1. Get list of 100+ servers from `/v0.1/servers` API
2. Extract top 20-30 by activity/downloads
3. Sample across different domains (io.github, ai.company, me.domain)

### Phase 2: Download & Introspect (Next Week)
1. Clone GitHub repositories OR download from npm/PyPI
2. Inspect `server.json` for:
   - Tools defined (count, schema, I/O types)
   - Resources (if any)
   - Prompts (if any)
   - Authentication requirements
   - Transport type preferences
   - Environment variables
3. Extract from package.json / setup.py / Dockerfile for licensing, deps

### Phase 3: Analyze Patterns
1. Categorize by capability type (tools, resources, prompts)
2. Identify common I/O patterns
3. Find authentication/security patterns
4. Map dependencies

### Phase 4: Design SQLite Schema
Based on observed patterns, create:
- `mcp_servers` table
- `mcp_tools` table
- `mcp_capabilities` table
- `mcp_auth_patterns` table

### Phase 5: Build Acquisition Tool
- `discovery/registry_client.py` - Query Official Registry API
- `discovery/mcp_inspector.py` - Clone & introspect MCPs
- `discovery/schema_extractor.py` - Parse server.json + package metadata
- `processing/catalog_builder.py` - Create SQLite database
- Output: `mcp_catalog.sqlite` + analysis reports

---

## File Organization

```
src/mcp/
├── discovery/          # Tools for finding & analyzing MCPs
│   ├── __init__.py
│   ├── registry_client.py      # Query Official Registry API
│   ├── mcp_inspector.py        # Clone & introspect repos
│   ├── schema_extractor.py     # Parse server.json, package.json
│   └── audit.py                # Generate analysis reports
│
├── processing/         # Tools for converting MCPs to RoadTrip skills
│   ├── __init__.py
│   ├── catalog_builder.py      # Create SQLite database
│   ├── mcp_to_skill.py         # Convert MCP → RoadTrip Skill
│   ├── fingerprinter.py        # Create skill fingerprints
│   └── validator.py            # Validate MCP for safety
│
└── interactions/       # Tools for calling & using MCPs
    ├── __init__.py
    ├── mcp_client_adapter.py   # Adapt MCP to RoadTrip calling convention
    ├── transport_handler.py    # stdio/sse/http wrappers
    ├── environment_injector.py # Inject auth tokens safely
    └── error_handler.py        # MCP error recovery

Tracking Documents:
workflows/006-Skill-Acquisition/MCP-Acquisition/
├── plan.md                      # Overall acquisition strategy
├── REGISTRY_SCHEMA_ANALYSIS.md  # (this file)
├── MCP_CATALOG_ANALYSIS_RESULTS.md (to be generated)
└── IMPLEMENTATION_LOG.md        (to be updated)
```

---

## Key Insights for RoadTrip

### 1. Namespace Ownership = Trust Authority
- GitHub users: Verified through OAuth
- Domains: Verified through DNS
- Companies: Direct relationship with registry maintainers
- **Implication**: We can use namespace as first-order trust signal

### 2. Multiple Packages per MCP
- Many MCPs offer npm + Docker + binary options
- Allows flexibility in deployment strategy (cli vs container vs embedded)
- **Implication**: Must support multiple execution modes

### 3. Environment Variables are Standard
- Required vs optional
- Secret vs public
- All MCPs follow same pattern
- **Implication**: IBAC (Instruction-Based Access Control) has clear hooks

### 4. Transformation is Possible
- Server.json → RoadTrip SkillMetadata (straightforward mapping)
- Tools schema → SkillCapability (already designed)
- Transport types → execution strategy (stdio default)
- **Implication**: Can bulk-convert once schema understood

---

## Next Steps

1. **Week 1**: Create registry client → query 100+ servers
2. **Week 2**: Build inspector → analyze 15-20 real MCPs
3. **Week 3**: Extract patterns → propose SQLite schema
4. **Week 4**: Implement catalog → populate with 30-50 MCPs

---

## References

- Official Registry: https://registry.modelcontextprotocol.io
- GitHub Repo: https://github.com/modelcontextprotocol/registry
- Schema: https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
- Documentation: https://github.com/modelcontextprotocol/registry/tree/main/docs
- API Docs: https://registry.modelcontextprotocol.io/docs
- Ecosystem Vision: https://github.com/modelcontextprotocol/registry/blob/main/docs/design/ecosystem-vision.md
