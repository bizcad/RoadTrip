# MCP Module Architecture

**Purpose**: Organize Python code for MCP discovery, processing, and interaction  
**Principle**: Clear separation of concerns using filesystem hierarchy as primary classification  

---

## Directory Structure

```
src/mcp/
│
├── __init__.py                    # Module exports
│
├── discovery/                     # ACQUISITION PHASE
│   ├── __init__.py
│   ├── registry_client.py         # Query Official MCP Registry API
│   ├── mcp_inspector.py           # Clone & introspect repos
│   ├── schema_extractor.py        # Parse server.json, package.json, etc.
│   ├── audit.py                   # Generate analysis reports
│   └── models.py                  # Dataclasses for discovery results
│
├── processing/                    # CONVERSION PHASE
│   ├── __init__.py
│   ├── catalog_builder.py         # Create/manage SQLite database
│   ├── mcp_to_skill.py            # Convert MCP → RoadTrip Skill
│   ├── fingerprinter.py           # Create SkillFingerprint from MCP
│   ├── validator.py               # Security & safety validation
│   ├── schema.sql                 # SQLite DDL
│   └── models.py                  # Dataclasses for processing results
│
└── interactions/                  # EXECUTION PHASE
    ├── __init__.py
    ├── mcp_client_adapter.py      # Adapt MCP to RoadTrip calling convention
    ├── transport_handler.py       # stdio/sse/http wrappers
    ├── environment_injector.py    # Inject auth tokens safely
    ├── error_handler.py           # MCP error recovery
    └── models.py                  # Dataclasses for runtime data
```

---

## Module Responsibilities

### discovery/

**Purpose**: Find and analyze MCPs from Official Registry

#### `mcp_server_registry_client.py`
```python
class MCPServerRegistryClient:
    """Query Official MCP Registry API (registry.modelcontextprotocol.io)"""
    
    def __init__(self, cache_dir: str = None):
        # Initialize with optional caching
    
    async def get_servers(self, limit: int = 100) -> List[ServerEntry]:
        # GET /v0.1/servers with pagination
    
    async def get_server(self, name: str) -> ServerEntry:
        # GET /v0.1/servers/{name}
    
    async def search(self, query: str) -> List[ServerEntry]:
        # Search by name, description, namespace
    
    def cache_results(self, servers: List[ServerEntry]) -> None:
        # Save locally to avoid rate limits
```

#### `mcp_inspector.py`
```python
class MCPInspector:
    """Clone and introspect MCP repositories"""
    
    def __init__(self, temp_dir: str = "/tmp/mcp_introspection"):
        # Set up temporary clone directory
    
    async def introspect(self, github_url: str) -> MCPMetadata:
        # Clone repo → extract metadata
        # Locates: server.json, package.json, setup.py, go.mod, etc.
        # Returns: structured MCPMetadata object
    
    def parse_server_json(self, path: str) -> ServerJSON:
        # Parse official server.json format
    
    def parse_package_json(self, path: str) -> PackageMetadata:
        # Extract npm dependencies, name, version
    
    def extract_capabilities(self, path: str) -> List[Capability]:
        # Find tool definitions, prompts, resources
```

#### `schema_extractor.py`
```python
class SchemaExtractor:
    """Extract structured data from MCPs"""
    
    def extract_tools(self, repo_path: str) -> List[ToolSchema]:
        # Find tool definitions with:
        # - Name, description
        # - Input schema (JSON Schema)
        # - Output schema (JSON Schema)
        # - Cost estimate
    
    def extract_auth_requirements(self, repo_path: str) -> AuthPattern:
        # Identify: API keys, OAuth, certs, other secrets
    
    def extract_dependencies(self, repo_path: str) -> DependencyList:
        # Extract from package.json, setup.py, go.mod, etc.
    
    def extract_runtime_info(self, repo_path: str) -> RuntimeInfo:
        # Language, version requirements, transport type
```

#### `audit.py`
```python
class AuditGenerator:
    """Generate analysis reports"""
    
    def generate_csv(self, results: List[MCPMetadata]) -> str:
        # Output: analysis.csv (tabular data)
    
    def generate_json(self, results: List[MCPMetadata]) -> str:
        # Output: analysis.json (detailed per-MCP)
    
    def generate_pattern_report(self, results: List[MCPMetadata]) -> str:
        # Output: PATTERN_ANALYSIS.md
        # Identify patterns, variations, anomalies
```

#### `models.py`
```python
@dataclass
class ServerEntry:
    """Entry from Official Registry"""
    name: str
    version: str
    description: str
    repository_url: str
    packages: List[str]
    namespace: str

@dataclass
class MCPMetadata:
    """Complete introspection result for one MCP"""
    name: str
    version: str
    description: str
    author: str
    license: str
    repository: str
    runtime: str  # "python", "node", "go", etc.
    transport_type: str  # "stdio", "sse", "http"
    tools: List[ToolSchema]
    resources: List[ResourceSchema]
    prompts: List[PromptSchema]
    auth_requirements: AuthPattern
    dependencies: DependencyList
    complexity_score: float  # 0-1, based on tool count, auth, etc.
```

---

### processing/

**Purpose**: Convert MCPs to RoadTrip skills, create persistent catalog

#### `catalog_builder.py`
```python
class CatalogBuilder:
    """Create and manage SQLite catalog"""
    
    def __init__(self, db_path: str):
        # Initialize SQLite database
    
    def initialize_schema(self) -> None:
        # Create tables from schema.sql
    
    async def add_mcp(self, metadata: MCPMetadata) -> str:
        # Insert MCP into catalog
        # Returns: mcp_id for reference
    
    async def search_by_capability(self, capability_type: str) -> List[str]:
        # Find MCPs offering specific capability
    
    async def search_by_namespace(self, namespace: str) -> List[str]:
        # Find all MCPs from namespace
    
    def export_for_orchestrator(self) -> Dict:
        # Format catalog for RoadTrip skill system
    
    async def get_statistics(self) -> CatalogStats:
        # Total MCPs, by type, by namespace, etc.
```

#### `mcp_to_skill.py`
```python
class MCPToSkillConverter:
    """Convert MCP → RoadTrip Skill"""
    
    def convert(self, mcp_metadata: MCPMetadata) -> SkillMetadata:
        # Transform MCP → SkillMetadata
        # Mapping:
        #   name → skill_name
        #   description → skill_description
        #   tools → capabilities
        #   auth → security_profile
        #   runtime → execution_environment
    
    def extract_capabilities(self, mcp_metadata: MCPMetadata) -> List[Capability]:
        # For each tool in MCP:
        #   Create Capability(name, type, inputs, outputs, cost)
```

#### `fingerprinter.py`
```python
class SkillFingerprinter:
    """Create SkillFingerprint from MCP"""
    
    def create_fingerprint(self, mcp_metadata: MCPMetadata) -> SkillFingerprint:
        # Deterministic hash of interface:
        #   - Tool names + schemas
        #   - Capability signatures
        #   - Version
        # Returns: SHA256[0:16] hex string
    
    def extract_deterministic_components(self, mcp_metadata: MCPMetadata) -> Dict:
        # Interface definition (immutable from runtime)
        # Test vectors (if available)
        # Known outputs (for specific inputs)
```

#### `validator.py`
```python
class MCPValidator:
    """Security & safety validation"""
    
    def validate(self, mcp_metadata: MCPMetadata) -> ValidationResult:
        # Check for:
        # - Known vulnerabilities
        # - Privilege escalation risks
        # - Credential exposure risks
        # - Unusual patterns
        # Returns: list of issues + severity levels
    
    def assess_capabilities(self, capabilities: List[Capability]) -> CapabilityAssessment:
        # For each capability:
        #   - Required trust tier (0-3)
        #   - IBAC rules needed
        #   - Resource access permissions
```

#### `models.py`
```python
@dataclass
class ToolSchema:
    name: str
    description: str
    input_schema: Dict  # JSON Schema
    output_schema: Dict
    cost_estimate: Optional[float]

@dataclass
class AuthPattern:
    type: str  # "none", "api_key", "oauth", "cert", "env_var"
    required_fields: List[str]
    secret_fields: List[str]

@dataclass
class CatalogStats:
    total_mcps: int
    by_namespace: Dict[str, int]
    by_language: Dict[str, int]
    by_transport: Dict[str, int]
    total_tools: int
    avg_complexity: float
```

---

### interactions/

**Purpose**: Call and use MCPs at runtime

#### `mcp_client_adapter.py`
```python
class MCPClientAdapter:
    """Adapt MCP to RoadTrip calling convention"""
    
    def __init__(self, mcp_metadata: MCPMetadata, config: MCPConfig):
        # Initialize connection to MCP
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> ToolResult:
        # Execute tool on MCP
        # Handle transport (stdio/sse/http)
        # Return structured result
    
    async def list_tools(self) -> List[str]:
        # Get available tools from this MCP
    
    async def get_tool_schema(self, tool_name: str) -> Dict:
        # Get input/output schema for validation
```

#### `transport_handler.py`
```python
class TransportHandler:
    """Wrap stdio/sse/http transports"""
    
    @staticmethod
    def create(transport_type: str, endpoint: str) -> Transport:
        # Factory method for transport type
    
class StdioTransport(Transport):
    """Handle stdio communication"""
    async def call(self, request: Dict) -> Dict:
        # Send to MCP via stdin
        # Read response from stdout
    
class SSETransport(Transport):
    """Handle Server-Sent Events"""
    async def call(self, request: Dict) -> Dict:
        # Send HTTP request
        # Read streamed response
    
class HTTPTransport(Transport):
    """Handle HTTP requests"""
    async def call(self, request: Dict) -> Dict:
        # Simple HTTP POST
```

#### `environment_injector.py`
```python
class EnvironmentInjector:
    """Inject auth tokens safely"""
    
    def __init__(self, secret_manager: SecretManager):
        # Connect to secret storage
    
    async def prepare_environment(self, mcp_metadata: MCPMetadata) -> Dict:
        # For each environment variable required by MCP:
        #   1. Look up from secret manager
        #   2. Verify access allowed (IBAC)
        #   3. Return sanitized env dict
        # Never return secrets in logs
    
    async def validate_credentials(self, mcp_metadata: MCPMetadata) -> bool:
        # Check that required secrets are available
        # Return false if auth missing
```

#### `error_handler.py`
```python
class MCPErrorHandler:
    """Recover from MCP failures"""
    
    async def handle_error(self, error: MCPError) -> ErrorRecoveryAction:
        # Classify error type
        # Return recovery action (retry, skip, escalate)
    
    def extract_user_error(self, error: MCPError) -> str:
        # Format error for user (no internal details)
    
    async def log_error(self, error: MCPError, context: Dict) -> None:
        # Log to telemetry system (for Phase 2 learning)
```

---

## Key Design Patterns

### 1. **Asyncio Throughout**
All I/O operations are async:
- Registry API queries
- Git clones
- Database operations
- MCP calls

### 2. **Strict Type Hints**
All functions use full type annotations for clarity and IDE support.

### 3. **Dataclass Models**
Core data structures use `@dataclass` for clarity and serialization:
- Easy to convert to/from JSON
- Clear field documentation
- IDE support

### 4. **Factory Methods**
Create objects via factories to enable testing:
- `TransportHandler.create()`
- `CatalogBuilder()` with optional in-memory DB

### 5. **Error Specificity**
Create specific exception types:
- `RegistryError`, `IntrospectionError`, `ValidationError`, `RuntimeError`
- Allows caller to handle appropriately

---

## Integration Points

### With Phase 1b ExecutionMetrics
- `MCPClientAdapter.call_tool()` reports:
  - Tool name, arguments, result
  - Execution time, success/failure
  - To: `ExecutionMetrics.record()`

### With Phase 2a IBAC
- `EnvironmentInjector` checks access permissions
- `Validator` generates required IBAC rules
- MCPs stored in `catalog_builder.db` with security tier

### With Phase 2b Trust
- `SkillFingerprinter` creates immutable fingerprints
- `Validator` provides initial trust assessments
- Updates tracked in `ExecutionMetrics`

### With Phase 3 DAG
- `MCPClientAdapter` implements tool-calling protocol
- Results fit standard RoadTrip skill interface
- Can be composed in DAG workflows

---

## Testing Strategy

### Unit Tests (`tests/mcp/discovery/`)
- Mock registry API responses
- Test schema extraction on fixture MCPs
- Validate audit report generation

### Integration Tests (`tests/mcp/processing/`)
- Test catalog creation with real introspection results
- Test conversion MCP → Skill
- Test SQLite queries

### End-to-End Tests (`tests/mcp/interactions/`)
- Start real MCP server (docker)
- Call tools via adapter
- Verify results

---

## What Python Discovers

Python discovers modules as a **tree rooted at `src/`**:
- `src/mcp` is top-level package (has `__init__.py`)
- `src/mcp/discovery` is subpackage
- Each `.py` file is a module

**Import patterns**:
```python
# From RoadTrip scripts:
from src.mcp.discovery import RegistryClient
from src.mcp.processing import CatalogBuilder
from src.mcp.interactions import MCPClientAdapter

# From within mcp package:
from src.mcp.discovery.models import MCPMetadata
from src.mcp.processing.fingerprinter import SkillFingerprinter
```

**Organization benefit**:
- File system mirrors logical organization
- Clear what each module does
- Easy to find code
- Easy to add new modules (just create file)
- Easy to test (files are independent units)

---

## Next: Code Generation

This architecture is ready for Phase 1 implementation.

See `plan.md` for detailed task breakdown and timeline.
