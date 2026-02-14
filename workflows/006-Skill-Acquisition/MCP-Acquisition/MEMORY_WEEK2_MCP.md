# Agent Memory System - Week 2+ MCP Acquisition (MCPInspector)

**Agent Role**: Week 2-3 MCP Acquisition (Introspection Phase)  
**Task**: Build MCPInspector and SchemaExtractor, analyze 15-20 real MCPs  
**Timeline**: Feb 21 - Mar 5, 2026  
**Status**: Waiting for Week 1 completion  

---

## Task Definition (From plan.md Phase 2-3)

### Objective
Clone real MCPs from GitHub, extract detailed metadata, identify patterns in 15-20 servers.

### Success Criteria
- [ ] MCPInspector class fully implemented
- [ ] Can clone GitHub repositories, find and parse server.json
- [ ] SchemaExtractor class extracts tools, packages, dependencies
- [ ] Introspects 15-20 MCPs from mcp_candidates.json
- [ ] Generates empirical analysis (CSV, JSON)
- [ ] Identifies patterns, variations, anomalies
- [ ] Proposes SQLite schema based on observations
- [ ] All code documented with docstrings
- [ ] Unit tests with fixture data (don't need real GitHub repos)

### Deliverables
1. `src/mcp/discovery/mcp_inspector.py` - Clone & analyze repos
2. `src/mcp/discovery/schema_extractor.py` - Parse metadata
3. `src/mcp/discovery/audit.py` - Generate reports
4. `workflows/006-Skill-Acquisition/MCP-Acquisition/analysis.csv` - Tabular results
5. `workflows/006-Skill-Acquisition/MCP-Acquisition/analysis.json` - Detailed results
6. `workflows/006-Skill-Acquisition/MCP-Acquisition/PATTERN_ANALYSIS.md` - Findings
7. `workflows/006-Skill-Acquisition/MCP-Acquisition/SCHEMA_DESIGN.md` - Proposed schema
8. `workflows/006-Skill-Acquisition/MCP-Acquisition/WEEK2_WEEK3_PROGRESS.md` - Weekly updates

---

## 🔍 Clone Prototype Validation Results (Feb 14, Evening)

**Prototype Finding**: Ran `prototype_mcp_clone_loop.py` to validate cloning strategy BEFORE Week 2.

### Key Discoveries

#### 1. ✅ GitHub Token Authentication Works
- **Method**: `GITHUB_TOKEN` from environment variable
- **Pattern**: `https://{token}@github.com/owner/repo`
- **Critical**: Must `.strip()` token to remove newlines/whitespace from Credential Manager
- **Result**: 3/3 clones successful with proper auth
- **No more prompts**: Script can run non-interactively

#### 2. ✅ Correct Repository URL Identified
- **Wrong**: `https://github.com/anthropics/mcp-servers` ❌ (doesn't exist)
- **Correct**: `https://github.com/modelcontextprotocol/servers` ✅
- **Fixed**: Updated all 8 MCPs in mcp_candidates.json with correct URL

#### 3. 🏗️ Monorepo Structure Discovered
This is **NOT a 1:1 repo-to-MCP mapping**. The servers repo is organized as:
```
modelcontextprotocol/servers/
├── src/
│   ├── filesystem/    ← Individual MCP implementation
│   ├── postgresql/
│   ├── sqlite/
│   ├── fetch/
│   ├── git/
│   ├── github/
│   ├── time/
│   ├── memory/
│   └── ... (8+ MCPs)
├── .mcp.json          (NOT server.json - monorepo config)
├── package.json       (monorepo dependencies)
└── README.md
```

**Implication for Week 2**: 
- Clone ONCE: `git clone modelcontextprotocol/servers data/ClonedRepos/mcp-servers/`
- Process MULTIPLE MCPs from subdirectories
- Look for `.mcp.json` at root AND per-server configs
- Extract tools from each `src/{server_name}/` directory

#### 4. 🔧 Configuration File: `.mcp.json` (Not server.json)
- **Root config**: `data/ClonedRepos/mcp-servers/.mcp.json` (monorepo settings)
- **Expected**: Each MCP in `src/{name}/` may have own config or inherit root config
- **Note**: Some MCPs are written in TypeScript (Node), others in Python
- **Important**: Tools/capabilities come from code analysis, not just JSON

#### 5. 📦 File Inventory from 3 Successful Clones
Filesystem MCP clone contains:
- `.git/` - Full git history
- `.github/` - CI/CD workflows
- `src/` - 8 language-specific server implementations
- `scripts/` - Build & test scripts
- `.mcp.json` - Monorepo config
- `package.json` - Dependencies
- Multiple `README.md`, Dockerfiles, TypeScript/Python configs

**Health Check Status**: ✅ Can access code, ❓ Haven't tested server startup yet

### Impact on Week 2 Implementation

#### Architecture Change
Instead of cloning 15-20 separate repos:
1. Clone `modelcontextprotocol/servers` ONCE → `data/ClonedRepos/mcp-servers/`
2. Iterate through `src/{server_name}/` for each MCP in candidates
3. Parse both `.mcp.json` and code to extract metadata
4. Much more efficient (1 large clone vs. many small clones)

#### Authentication Pattern Validated
```python
import os
token = os.getenv("GITHUB_TOKEN").strip()  # Remove newlines!
url = f"https://{token}@github.com/modelcontextprotocol/servers"
subprocess.run(["git", "clone", url, target_dir])
```

#### Testing Strategy
- Clone prototype worked with real token → Use same pattern in tests
- Mock filepath instead of mocking git (easier to test with real artifacts)
- Already have copies of 3 servers in `data/ClonedRepos/` for reference

### Prototype Code Artifact
- **File**: `scripts/prototype_mcp_clone_loop.py` (330 LOC)
- **Reusable**: The clone + health_check pattern is production-ready
- **Location**: Can refactor into MCPInspector.clone_and_introspect()
- **Status**: Committed to feature/mcp-acquisition branch (local, push auth pending)

---

## What Week 1 Delivered

### Input: mcp_candidates.json
You will receive a JSON file with ~30 MCPs:
```json
{
  "total_fetched": 200,
  "top_candidates": [
    {
      "rank": 1,
      "name": "io.github.domdomegg/airtable-mcp-server",
      "repository_url": "https://github.com/domdomegg/airtable-mcp-server",
      "description": "Read and write Airtable records",
      "last_updated": "2025-02-14T12:00:00Z",
      "versions": ["1.7.3", "1.7.2"],
      "namespace": "io.github.domdomegg",
      "reason": "High activity, recent updates, clear use case"
    }
  ]
}
```

### Week 1 Code Available
- `src/mcp/discovery/mcp_server_registry_client.py` - Query registry
- `src/mcp/discovery/models.py` - ServerEntry dataclass
- `src/mcp/discovery/__init__.py` - Module exports

### Documentation
- REGISTRY_SCHEMA_ANALYSIS.md - What registry looks like
- SCHEMA_DEEP_DIVE.md - Real examples (Airtable, Time MCPs)
- MODULE_ARCHITECTURE.md - Your class designs

---

## What You Need to Implement

### 1. MCPInspector Class
```python
class MCPInspector:
    """Clone and introspect MCP repositories"""
    
    async def clone_monorepo(repo_url: str) -> Path:
        # Clone modelcontextprotocol/servers to data/ClonedRepos/mcp-servers/
        # Uses GITHUB_TOKEN from environment for auth
        # Returns path to cloned repo
        
    async def introspect_mcp(mcp_name: str, monorepo_path: Path) -> MCPMetadata:
        # Given an MCP name (e.g., "filesystem")
        # Find src/{mcp_name}/ in monorepo
        # Extract metadata from code + .mcp.json
        
    def parse_mcp_config(config_path: str) -> MCPConfig:
        # Read .mcp.json (root or per-MCP)
        # Extract tools, protocols, capabilities
        
    def extract_tools(repo_path: str) -> List[ToolSchema]:
        # Analyze Python or TypeScript code
        # Extract function signatures, docstrings, type hints
        # Build ToolSchema for each tool
```

**Key Points** (Validated by Prototype):
- Monorepo clone location: `data/ClonedRepos/mcp-servers/`
- Per-MCP code location: `{monorepo}/src/{mcp_name}/`
- Config file: `.mcp.json` (not server.json - was incorrect assumption!)
- Each MCP may be in Python (mcp_server_*/) or TypeScript (src/*/index.ts)
- Run health_check() after clone (verify .git and key files exist)

### 2. SchemaExtractor Class
```python
class SchemaExtractor:
    """Extract structured data from MCPs in monorepo"""
    
    def extract_from_mcp(mcp_path: str, language: str) -> MCPAnalysis:
        # Detect language (Python or TypeScript)
        # Extract tools, dependencies, auth patterns
        
    def extract_tools_python(module_path: str) -> List[ToolSchema]:
        # Read Python files, find function definitions
        # Extract docstrings, type hints
        
    def extract_tools_typescript(src_path: str) -> List[ToolSchema]:
        # Read TypeScript, find tool registrations
        # Extract from tool definitions
        
    def extract_dependencies(mcp_path: str) -> DependencyList:
        # package.json (TS), setup.py/pyproject.toml (Python)
        
    def extract_auth_requirements(mcp_path: str) -> AuthPattern:
        # API keys, environment variables from code & config
```

### 3. AuditGenerator Class
```python
class AuditGenerator:
    """Generate analysis reports"""
    
    def generate_csv(results: List[MCPMetadata]) -> str:
        # Output: analysis.csv
        
    def generate_json(results: List[MCPMetadata]) -> str:
        # Output: analysis.json
        
    def generate_pattern_report(results: List[MCPMetadata]) -> str:
        # Output: PATTERN_ANALYSIS.md
```

---

## Testing Strategy (Important!)

**DO NOT rely on real GitHub clones for unit tests.**

Create fixtures:

```
tests/fixtures/mcp_repos/
├── airtable-mcp/
│   ├── server.json      (example from research)
│   ├── package.json     (example)
│   └── README.md
├── time-mcp/
│   ├── server.json
│   ├── setup.py
│   └── README.md
└── mcp_metadata_sample.json
```

Then mock GitPython:
```python
@patch('git.Repo.clone_from')
def test_introspect(mock_clone):
    mock_clone.return_value = Repo('tests/fixtures/mcp_repos/airtable-mcp')
    # Test parsing
```

---

## Key Decisions to Make

1. **What counts as a "Tool"?**
   - Only `tools` section in server.json?
   - Also custom tool definitions in code (Go, Python, Node.js)?
   - Recommendation: Start with server.json tools, extend if patterns emerge

2. **Complexity Scoring**
   - Tool count (count)
   - Resource access (filesystem, network, credentials)
   - Authentication requirements (none, api_key, oauth, cert)
   - Recommendation: Simple scoring formula in PATTERN_ANALYSIS.md

3. **Anomaly Handling**
   - MCPs without server.json?
   - MCPs with unusual patterns?
   - Recommendation: Flag clearly, document separately

---

## What to Output

### analysis.csv (Tabular Summary)
```csv
name,namespace,tool_count,has_auth,transport,complexity,license,language
io.github.domdomegg/airtable,io.github.domdomegg,8,true,stdio,0.7,Apache2,Node.js
com.company/custom-mcp,com.company,12,true,stdio,0.9,MIT,Python
```

### analysis.json (Detailed Per-MCP)
```json
{
  "total_introspected": 20,
  "mcps": [
    {
      "name": "...",
      "metadata": { ... },
      "tools": [ ... ],
      "auth": { ... },
      "dependencies": [ ... ]
    }
  ]
}
```

### PATTERN_ANALYSIS.md
Document what you learned:
- Common patterns (what do 80%+ of MCPs have?)
- Variations (what's outliers?)
- Complexity distribution
- Auth patterns
- Transport preferences
- Recommendations for schema

### SCHEMA_DESIGN.md
Propose SQLite design:
```
CREATE TABLE mcp_servers (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  namespace TEXT,
  version TEXT,
  ...
);

CREATE TABLE mcp_tools (
  id INTEGER PRIMARY KEY,
  server_id INTEGER,
  name TEXT,
  description TEXT,
  ...
);
```

---

## Testing Strategy (Informed by Prototype)

**Key Learning**: The monorepo has both TypeScript and Python MCPs, so unit tests must handle both.

### Create Fixture Directory
```
tests/fixtures/mcp_monorepo/
├── .mcp.json              (example root config)
├── src/
│   ├── filesystem/        (TypeScript MCP)
│   │   ├── index.ts
│   │   ├── package.json
│   │   └── README.md
│   └── mcp_server_time/   (Python MCP)
│       ├── __main__.py
│       ├── server.py
│       ├── pyproject.toml
│       └── README.md
├── package.json           (monorepo dependencies)
└── mcp_metadata_sample.json
```

### Mock Clone Pattern
```python
@patch('git.Repo.clone_from')
def test_clone_monorepo(mock_clone):
    # Don't call real git - use test fixture
    mock_clone.return_value = Path("tests/fixtures/mcp_monorepo")
    
@patch('subprocess.run')  # For GITHUB_TOKEN insertion
def test_token_auth(mock_run):
    # Verify token is stripped and inserted correctly
    pass
```

### Learned from Prototype
- ✅ Real token auth works (no mocking needed for integration tests)
- ✅ Clone pattern is reusable (can lift from prototype script)
- ✅ Monorepo structure is consistent (one clone, many MCPs)
- ✅ `.mcp.json` exists at root (look there for config)

---

## Blockers & Risks

### Known Risks
- **GitHub API Rate Limits**: 60 req/hour unauthenticated, need token
- **Missing Metadata**: Some MCPs may not have server.json
- **Dependency Resolution**: setup.py with complex conditionals
- **Language Diversity**: Different package formats (npm, pip, go, etc.)

### Mitigation
- Use OAuth token if available (check environment)
- Flag incomplete MCPs separately, don't exclude
- Use simple parsing (don't execute code)
- Support multiple formats, document patterns

---

## Next Agent Should Know (For Phase 4-5)

### Input from Phase 3
- `SCHEMA_DESIGN.md` with proposed tables
- `analysis.json` with all introspected MCPs
- `PATTERN_ANALYSIS.md` with findings

### What to Build (Phase 4-5)
1. Implement SQLite schema based on design
2. Create `CatalogBuilder` to insert data
3. Create `MCPToSkillConverter` to transform MCP → Skill
4. Create `MCPValidator` for security assessment
5. Create `SkillFingerprinter` for identity

### You Will Need
- Proposed schema from Phase 3
- All analysis data (JSON format)
- Understanding of RoadTrip SkillMetadata structure

---

## References & Links

### Week 1 Output (Will Be Available)
- `mcp_candidates.json` - Top 30 MCPs to introspect
- `src/mcp/discovery/mcp_server_registry_client.py` - Registry client code
- `src/mcp/discovery/models.py` - ServerEntry dataclass

### Planning Documents
- Master Plan: `plan.md` (Phase 2-3 section)
- Registry Analysis: `REGISTRY_SCHEMA_ANALYSIS.md`
- Schema Deep Dive: `SCHEMA_DEEP_DIVE.md` (real examples)
- Module Architecture: `MODULE_ARCHITECTURE.md`

### External References
- Server.json spec: https://github.com/modelcontextprotocol/registry/docs/reference/server-json
- Real examples in seed.json: https://github.com/modelcontextprotocol/registry/blob/main/data/seed.json

---

## Memory Update Schedule

Maintain this file as you work:
- After each MCP introspected: Add to "What I Discovered"
- After each class implemented: Update "What I Implemented"  
- When blockers hit: Add to "Blockers & Issues"
- After analysis complete: Update outputs list

---

## Quick Checklist

Before starting:
- [ ] Read latest MEMORY_WEEK1_MCP.md (what Week 1 delivered)
- [ ] Read plan.md Phase 2-3
- [ ] Read MODULE_ARCHITECTURE.md for class designs
- [ ] Have mcp_candidates.json available
- [ ] Create test fixtures directory

During work:
- [ ] Update this MEMORY.md regularly
- [ ] Document blockers immediately
- [ ] Create weekly progress updates
- [ ] Test against fixtures (not real repos initially)

Before handoff:
- [ ] analysis.csv, analysis.json generated
- [ ] PATTERN_ANALYSIS.md complete
- [ ] SCHEMA_DESIGN.md ready
- [ ] All code documented
- [ ] Update "Next Agent Should Know"
- [ ] Keep this MEMORY.md for Phase 4 agent

---

**Session Will Start**: Feb 21, 2026  
**Expected Completion**: Mar 5, 2026  
**Branch**: feature/mcp-acquisition  
**Depends On**: MEMORY_WEEK1_MCP.md and its deliverables

---

## For Implementation

Start with:
1. Create `MCPInspector` skeleton
2. Create test fixtures in `tests/fixtures/mcp_repos/`
3. Implement `parse_server_json()` first (test with fixtures)
4. Implement `extract_tools()` next
5. Iterate through fixtures to verify parsing

Good luck!
