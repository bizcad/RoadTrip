# MCP Module Quick Reference

**For**: Understanding what each Python module does and where to find it  
**Last Updated**: February 14, 2026  

---

## Quick Navigation

### I need to... | Go to...

| Task | File |
|------|------|
| Find MCPs in Official Registry | `src/mcp/discovery/registry_client.py` |
| Clone & analyze real MCPs | `src/mcp/discovery/mcp_inspector.py` |
| Extract tool schemas from MCP | `src/mcp/discovery/schema_extractor.py` |
| Create analysis reports (CSV, JSON) | `src/mcp/discovery/audit.py` |
| Create SQLite catalog database | `src/mcp/processing/catalog_builder.py` |
| Convert MCP to RoadTrip Skill | `src/mcp/processing/mcp_to_skill.py` |
| Create SkillFingerprint from MCP | `src/mcp/processing/fingerprinter.py` |
| Validate MCP for security/safety | `src/mcp/processing/validator.py` |
| Call MCP tools at runtime | `src/mcp/interactions/mcp_client_adapter.py` |
| Handle stdio/sse/http transports | `src/mcp/interactions/transport_handler.py` |
| Inject auth credentials safely | `src/mcp/interactions/environment_injector.py` |
| Handle MCP errors gracefully | `src/mcp/interactions/error_handler.py` |

---

## Module Import Examples

### Discovery Phase
```python
# Query official registry for MCPs
from src.mcp.discovery import RegistryClient
client = RegistryClient(cache_dir="./mcp_cache")
servers = await client.get_servers(limit=100)

# Introspect a real MCP repo
from src.mcp.discovery import MCPInspector
inspector = MCPInspector()
metadata = await inspector.introspect("https://github.com/user/mcp-server")

# Extract specific information
from src.mcp.discovery import SchemaExtractor
extractor = SchemaExtractor()
tools = extractor.extract_tools(repo_path)

# Generate analysis reports
from src.mcp.discovery import AuditGenerator
auditor = AuditGenerator()
csv_output = auditor.generate_csv(results)
```

### Processing Phase
```python
# Create catalog database
from src.mcp.processing import CatalogBuilder
catalog = CatalogBuilder(db_path="./mcp_catalog.sqlite")
await catalog.initialize_schema()

# Convert MCP to Skill
from src.mcp.processing import MCPToSkillConverter
converter = MCPToSkillConverter()
skill = converter.convert(mcp_metadata)

# Create fingerprint
from src.mcp.processing import SkillFingerprinter
fingerprinter = SkillFingerprinter()
fingerprint = fingerprinter.create_fingerprint(mcp_metadata)

# Validate security
from src.mcp.processing import MCPValidator
validator = MCPValidator()
result = validator.validate(mcp_metadata)
```

### Interactions Phase
```python
# Call MCP tools
from src.mcp.interactions import MCPClientAdapter
adapter = MCPClientAdapter(mcp_metadata, config)
result = await adapter.call_tool("tool_name", {"arg": "value"})

# Handle credentials
from src.mcp.interactions import EnvironmentInjector
injector = EnvironmentInjector(secret_manager)
env = await injector.prepare_environment(mcp_metadata)

# Handle errors
from src.mcp.interactions import MCPErrorHandler
error_handler = MCPErrorHandler()
action = await error_handler.handle_error(error)
```

---

## File Organization Tree

```
src/mcp/
├── __init__.py                      # [PHASE 1: Create empty]
├── discovery/
│   ├── __init__.py                  # [PHASE 1: Export main classes]
│   ├── registry_client.py           # [PHASE 1, WEEK 1: Create]
│   ├── mcp_inspector.py             # [PHASE 2, WEEK 2: Create]
│   ├── schema_extractor.py          # [PHASE 2, WEEK 2: Create]
│   ├── audit.py                     # [PHASE 2, WEEK 3: Create]
│   └── models.py                    # [PHASE 1: Create with dataclasses]
│
├── processing/
│   ├── __init__.py                  # [PHASE 3: Export main classes]
│   ├── schema.sql                   # [PHASE 3, WEEK 3: Create DDL]
│   ├── catalog_builder.py           # [PHASE 4, WEEK 4: Create]
│   ├── mcp_to_skill.py              # [PHASE 4, WEEK 4: Create]
│   ├── fingerprinter.py             # [PHASE 4, WEEK 4: Create]
│   ├── validator.py                 # [PHASE 5, WEEK 4: Create]
│   └── models.py                    # [PHASE 3: Create with dataclasses]
│
└── interactions/
    ├── __init__.py                  # [PHASE 6: Export main classes]
    ├── mcp_client_adapter.py         # [PHASE 6, WEEK 5: Create]
    ├── transport_handler.py          # [PHASE 6, WEEK 5: Create]
    ├── environment_injector.py       # [PHASE 5, WEEK 4: Create]
    ├── error_handler.py              # [PHASE 6, WEEK 5: Create]
    └── models.py                     # [PHASE 6: Create with dataclasses]
```

---

## Data Flow Diagram

```
DISCOVERY PHASE
├─ RegistryClient
│  └─→ [Official Registry API]
│      └─→ 200+ server entries
│
├─ MCPInspector
│  └─→ [GitHub] + [Clone repos]
│      └─→ server.json, package.json
│
└─ SchemaExtractor → [Parse metadata]
   └─→ MCPMetadata objects
       └─→ AuditGenerator
           └─→ analysis.csv, analysis.json

PROCESSING PHASE
├─ CatalogBuilder
│  └─→ [Create SQLite]
│      └─→ mcp_catalog.sqlite
│
├─ MCPToSkillConverter
│  └─→ MCPMetadata → SkillMetadata
│
├─ SkillFingerprinter
│  └─→ MCPMetadata → SkillFingerprint
│
└─ MCPValidator
   └─→ MCPMetadata → SecurityAssessment

INTERACTIONS PHASE
├─ EnvironmentInjector
│  └─→ [Secret Manager] → Credentials
│
├─ MCPClientAdapter
│  └─→ TransportHandler
│      └─→ [stdio/sse/http] → MCP Server
│          └─→ Tool Results
│
└─ MCPErrorHandler
   └─→ [Collect metrics] → ExecutionMetrics
```

---

## Key Dates for Implementation

- **Feb 14-20 (Week 1)**: Phase 1 - Registry Discovery
  - Create: `registry_client.py`, `models.py`, `__init__.py` in discovery/

- **Feb 21-Mar 5 (Week 2-3)**: Phase 2-3 - Introspection & Design
  - Create: `mcp_inspector.py`, `schema_extractor.py`, `audit.py`
  - Create: `schema.sql`, `models.py` in processing/

- **Mar 6-12 (Week 4-5)**: Phase 4-5 - Implementation & Validation
  - Create: All files in processing/ and interactions/

- **Mar 13-19 (Week 6)**: Phase 6 - Documentation & Integration
  - Integration tests, final documentation

---

## Dependencies

### Required Python Libraries
```
requests                # HTTP API calls
aiohttp                # Async HTTP
GitPython              # Git cloning
sqlite3                # Built-in SQLite driver
pydantic               # Data validation (optional)
```

### To Install
```bash
pip install requests aiohttp GitPython
```

---

## For Testing: Fixture Data

Place test MCPs in `tests/fixtures/mcp_repos/`:
```
tests/fixtures/
├── mcp_repos/
│   ├── simple-mcp/
│   │   ├── server.json
│   │   └── package.json
│   ├── complex-mcp/
│   │   ├── server.json
│   │   └── requirements.txt
│   └── mcp_catalog_sample.sqlite
```

---

## Progress Tracking

See `plan.md` for detailed WBS and timeline.

Current status: Planning complete, ready for Phase 1 implementation.
