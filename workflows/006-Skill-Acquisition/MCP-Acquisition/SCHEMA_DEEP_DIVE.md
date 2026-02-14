# Official MCP Registry Schema - Technical Deep Dive

**Source**: https://registry.modelcontextprotocol.io  
**Schema Version**: 2025-12-11  
**Last Researched**: February 14, 2026  

---

## Server.json Format (Official Specification)

### Root Level
```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.user/server-name",
  "description": "Human-readable description",
  "version": "1.0.0",
  "repository": { "url": "...", "source": "github" },
  "icons": [ { "src": "...", "mimeType": "image/png", "sizes": [...] } ],
  "packages": [ /* see below */ ]
}
```

### Identity Section

**name** (required)
- Format: `namespace/identifier`
- Namespaces: `io.github.USER`, `ai.COMPANY`, `me.DOMAIN`, etc.
- Verified ownership:
  - GitHub: OAuth login
  - Domain: DNS or HTTP challenge
  - Corporate: Pre-verified by maintainers

**version** (required)
- SemVer format: `MAJOR.MINOR.PATCH`
- Examples: `1.0.0`, `1.7.3`, `0.0.1`

**repository** (optional)
```json
{
  "url": "https://github.com/owner/repo.git",
  "source": "github" | "gitlab" | "bitbucket" | ...
}
```

### Packages Section (Required Array)

Each package represents one way to obtain/run the MCP:

```json
{
  "registryType": "npm|pypi|oci|nuget|mcpb",
  "identifier": "package-name-in-registry",
  "version": "1.0.0",
  "runtimeHint": "npx|python|docker|dnx",
  "transport": { "type": "stdio|sse|http" },
  "environmentVariables": [ /* see below */ ]
}
```

#### Registry Types & Where to Find Code

| Type | Where | Example | Access |
|------|-------|---------|--------|
| npm | npmjs.com | `airtable-mcp-server` | `npx airtable-mcp-server` |
| pypi | pypi.org | `time-mcp-pypi` | `python -m time_mcp_pypi` |
| oci (Docker) | docker.io | `docker.io/domdomegg/airtable-mcp-server:1.7.2` | `docker pull ...` |
| nuget | nuget.org | `TimeMcpServer` | `.NET package` |
| mcpb | Direct URL | `https://github.com/.../releases/download/v1.7.2/airtable-mcp-server.mcpb` | SHA256 checksum |

#### Transport Types

| Type | Protocol | Use Case | Performance |
|------|----------|----------|-------------|
| stdio | stdin/stdout | Default, simplest | Low latency, local |
| sse | HTTP EventStream | Server-hosted MCPs | Higher latency, remote |
| http | HTTP POST | For REST APIs | Variable latency |

#### Environment Variables

```json
{
  "name": "AIRTABLE_API_KEY",
  "description": "Personal access token from https://airtable.com/create/tokens/new",
  "isRequired": true,
  "isSecret": true
}
```

Properties:
- **name**: Exact environment variable name
- **description**: What this is and where to get it
- **isRequired**: Boolean - if false, MCP has sensible default
- **isSecret**: Boolean - if true, never log this value

---

## Real Examples From Registry

### Example 1: Airtable MCP (npm + Docker)
```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.domdomegg/airtable-mcp-server",
  "description": "Read and write access to Airtable database schemas, tables, and records.",
  "repository": {
    "url": "https://github.com/domdomegg/airtable-mcp-server.git",
    "source": "github"
  },
  "version": "1.7.2",
  "icons": [
    {
      "src": "https://airtable.com/images/favicon/favicon-32x32.png",
      "mimeType": "image/png",
      "sizes": ["32x32"]
    }
  ],
  "packages": [
    {
      "registryType": "npm",
      "identifier": "airtable-mcp-server",
      "version": "1.7.2",
      "runtimeHint": "npx",
      "transport": { "type": "stdio" },
      "environmentVariables": [
        {
          "description": "Airtable personal access token...",
          "isRequired": true,
          "isSecret": true,
          "name": "AIRTABLE_API_KEY"
        }
      ]
    },
    {
      "registryType": "oci",
      "identifier": "docker.io/domdomegg/airtable-mcp-server:1.7.2",
      "runtimeHint": "docker",
      "transport": { "type": "stdio" },
      "environmentVariables": [...]
    },
    {
      "registryType": "mcpb",
      "identifier": "https://github.com/domdomegg/airtable-mcp-server/releases/download/v1.7.2/airtable-mcp-server.mcpb",
      "fileSha256": "8220de07a08ebe908f04da139ea03dbfe29758141347e945da60535fb7bcca20",
      "transport": { "type": "stdio" }
    }
  ]
}
```

**Observations**:
- Single MCP available via 3 distributions (npm, Docker, binary)
- All use stdio transport
- Auth token is required + secret
- Icon included for UI

### Example 2: Time MCP (3 different versions)
```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.domdomegg/time-mcp-nuget",
  "description": "Get the current UTC time in RFC 3339 format.",
  "version": "1.0.8",
  "packages": [
    {
      "registryType": "nuget",
      "identifier": "TimeMcpServer",
      "version": "1.0.8",
      "runtimeHint": "dnx",
      "transport": { "type": "stdio" }
    }
  ]
}
```

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.domdomegg/time-mcp-pypi",
  "description": "Get the current UTC time in RFC 3339 format.",
  "version": "1.0.6",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "time-mcp-pypi",
      "version": "1.0.6",
      "runtimeHint": "python",
      "transport": { "type": "stdio" }
    }
  ]
}
```

**Observations**:
- Same "time" MCP, different implementations for different languages
- Simple (no auth), minimal metadata
- Each is registered separately in registry

---

## API Endpoints (v0.1)

### List Servers
```
GET /v0.1/servers?limit=100&offset=0
```

Response:
```json
{
  "servers": [
    {
      "name": "io.github.domdomegg/airtable-mcp-server",
      "versions": ["1.7.3", "1.7.2"],
      "updatedAt": "2025-02-14T12:00:00Z",
      "stars": 500,
      "downloads": 10000
    }
  ]
}
```

### Get Specific Server
```
GET /v0.1/servers/{name}
```

Returns full `server.json` for all versions.

### Search
```
GET /v0.1/servers?search=airtable
```

Searches by name, description, keywords.

### Validate
```
POST /v0.1/validate
Content-Type: application/json

{server.json as JSON}
```

Returns validation errors/warnings.

---

## Namespace Patterns

### Community (io.github.*)
- Published by individual GitHub users
- Verified through OAuth
- Examples:
  - `io.github.domdomegg/airtable-mcp-server` (30+ stars, production)
  - `io.github.smithery/222wcnm-bilistalkermcp` (test server)

### Corporate (ai.*)
- Published by companies/organizations
- Pre-verified by maintainers
- Examples:
  - `ai.anthropic/*` - Anthropic official servers
  - `ai.github/*` - GitHub official servers
  - `ai.com.mcp/registry` - Registry browsing MCP
  - `ai.exa/exa` - Commercial services

### Domain (me.*)
- Published by individuals with verified domain
- Verified through DNS/HTTP challenge
- Examples:
  - `me.adamjones/custom-mcp` (requires adamjones.me verification)

### Company (com.*)
- Published by companies with verified domain
- Examples:
  - Various commercial vendors

### Project-Specific
- Various experimental patterns
- Examples:
  - `ai.auteng/mcp`, `ai.aliengiraffe/spotdb`

---

## What We'll Extract

During introspection (Phase 2-3), for each MCP we'll identify:

| Attribute | From | Example |
|-----------|------|---------|
| Namespace | server.json name | `io.github.domdomegg` |
| Identity | server.json name | `airtable-mcp-server` |
| Current Version | server.json version | `1.7.3` |
| Description | server.json description | "Read and write access to..." |
| Repository | server.json repository.url | `https://github.com/...` |
| Author | GitHub repo metadata | `@domdomegg` |
| License | GitHub LICENSE file | Apache 2.0, MIT, etc. |
| # Packages | server.json packages.length | 3 (npm, docker, mcpb) |
| Package Types | server.json packages[].registryType | npm, oci, mcpb |
| Transport | server.json packages[].transport.type | stdio (all usually) |
| Auth Required | server.json packages[].environmentVariables | 1 required API key |
| Runtime | Detected from package.json/setup.py | Node.js 18+ |
| Complexity | Tool count + resource access | 15+ tools = complex |
| Last Updated | GitHub commit date | 2025-02-14 |

---

## Empirical Discovery Strategy

### Step 1: Query Registry
```bash
GET https://registry.modelcontextprotocol.io/v0.1/servers?limit=200
```
outputs → `mcp_candidates.json` (200+ entries)

### Step 2: Sort by Relevance
- Recent updates (last 30 days preferred)
- Appear in multiple sources
- From trusted namespaces (io.github with activity, ai.*)
- GitHub star count (if available)

### Step 3: Select 15-20 for Deep Dive
- Sample across namespaces
- Mix of simple (0-5 tools) and complex (+10 tools)
- Different registry types (npm, pypi, oci)
- Different auth patterns

### Step 4: Clone Repos, Extract
For each selected MCP:
1. Clone from GitHub
2. Find server.json + package.json/setup.py/go.mod
3. Extract capabilities (tool definitions)
4. Identify auth requirements
5. Calculate complexity score

### Step 5: Aggregate Results
- `analysis.csv` (tabular)
- `analysis.json` (detailed)
- `PATTERN_ANALYSIS.md` (observations)

### Step 6: Design Schema
Based on patterns observed:
- Which fields are always present?
- Which are optional?
- Which need special handling (auth, large arrays)?
- What queries do we need to support?

---

## What RoadTrip Needs From MCPs

### Phase 2a Integration
- **Identity**: Unique server.json name
- **Tools**: List of callable functions with input/output schemas
- **Auth**: What credentials required (API keys, OAuth, etc.)
- **Transport**: How to communicate (stdio default)

### Phase 2b Trust
- **Namespace**: Who publisher is → first-order trust
- **History**: Recent activity, stability
- **Complexity**: How many tools, resource access patterns
- **Permissions**: IBAC rules needed

### Phase 3 Orchestration  
- **Capabilities**: What can it do (file access? network?)
- **Interface**: Standard tool-calling protocol
- **Error Handling**: What can go wrong

### Phase 4 Self-Improvement
- **Telemetry**: Execution metrics, reliability
- **Observations**: Error patterns, latency trends
- **Optimization**: Which tools most/least reliable

---

## Key Takeaway for RoadTrip

The Official MCP Registry is well-structured for discovery:
- Standardized `server.json` format across 500+ MCPs
- Clear distribution channels (npm, PyPI, Docker)
- Ownership verified and traceable
- Rich metadata (description, icons, auth requirements)
- Stable API (v0.1 freeze)

**This makes scaling from 10 → 100+ MCPs straightforward.**

Our job: 
1. Query registry → get candidates
2. Introspect real MCPs → learn patterns
3. Build persistent catalog → integrate with RoadTrip
4. Execute safely → via orchestrator

---

## References

- Official Registry: https://registry.modelcontextprotocol.io
- Registry Repo: https://github.com/modelcontextprotocol/registry
- API Docs: https://registry.modelcontextprotocol.io/docs
- Schema URL: https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json
- Ecosystem Vision: https://github.com/modelcontextprotocol/registry/blob/main/docs/design/ecosystem-vision.md
- Publishing Guide: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx
