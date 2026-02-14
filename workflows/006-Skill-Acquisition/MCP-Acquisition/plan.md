# MCP Acquisition Strategy & Implementation Plan

**Date Created**: February 14, 2026  
**Status**: Planning Phase  
**Owner**: RoadTrip Self-Improvement Infrastructure (Phase 2a)  
**Target Completion**: March 31, 2026  

---

## Strategic Objective

Design and build an **empirical MCP discovery and acquisition system** that:
1. Learns what MCPs actually look like (not theoretical schema)
2. Builds a persistent SQLite catalog for skill orchestration
3. Establishes patterns for safe, scalable MCP integration
4. Creates the foundation for Phase 2 (trust, fingerprinting, IBAC)

**Principle**: "Teach me to fish, not give me fish"
- We will introspect real MCPs to discover patterns
- We will not design schema theoretically
- We will observe → catalog → integrate

---

## Work Breakdown Structure

### Phase 1: Registry Discovery (Week 1, Feb 14-20)

**Objective**: Query Official Registry, identify candidates for introspection

#### Tasks
- [ ] 1.1 Create `RegistryClient` class
  - Authenticate with Official MCP Registry API
  - Query `/v0.1/servers` endpoint
  - Handle pagination
  - Cache results locally

- [ ] 1.2 Get list of 200+ MCPs
  - Filter by registry type (npm, pypi, oci)
  - Sort by recent updates + stars (proxy)
  - Identify top 20-30 candidates

- [ ] 1.3 Sample across 3 namespaces
  - `io.github.*` (community)
  - `ai.*` (company MCPs)
  - `me.*` (individual domain)

- [ ] 1.4 Generate candidate list
  - Output: `mcp_candidates.json` (30 MCPs with GitHub URLs)

**Artifacts**:
- `src/mcp/discovery/registry_client.py`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/mcp_candidates.json`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/WEEK1_REPORT.md`

---

### Phase 2: MCP Introspection (Week 2-3, Feb 21-Mar 5)

**Objective**: Clone real MCPs, extract metadata, learn patterns

#### Tasks
- [ ] 2.1 Create `MCPInspector` class
  - Clone GitHub repositories to temp directory
  - Locate `server.json` or equivalent metadata
  - Parse package.json / setup.py / go.mod
  - Extract capability definitions

- [ ] 2.2 Introspect 15-20 real MCPs
  - Document for each:
    - Name, description, author
    - Tools (count, I/O schemas, capabilities)
    - Resources (if any)
    - Prompts (if any)
    - Authentication requirements
    - Transport types
    - Dependencies
    - Language/runtime
    - Complexity (simple vs advanced)

- [ ] 2.3 Generate empirical analysis
  - Output: `analysis.csv` (structured data)
  - Output: `analysis.json` (detailed per-MCP)
  - Output: `PATTERN_ANALYSIS.md` (observations)

- [ ] 2.4 Identify variation points
  - Which fields vary across MCPs?
  - Which are always present?
  - Which are unusual?

**Artifacts**:
- `src/mcp/discovery/mcp_inspector.py`
- `src/mcp/discovery/schema_extractor.py`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/analysis.csv`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/analysis.json`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/PATTERN_ANALYSIS.md`

---

### Phase 3: Schema Design (Week 3, Mar 1-5)

**Objective**: Propose SQLite schema based on observed patterns

#### Tasks
- [ ] 3.1 Analyze empirical variations
  - Which data is relational vs document?
  - Which needs indexing?
  - Which is time-varying vs static?

- [ ] 3.2 Design SQLite tables
  - `mcp_servers`: Core metadata
  - `mcp_capabilities`: Tools, resources, prompts
  - `mcp_authentication`: Auth patterns
  - `mcp_packages`: Delivery & runtime info
  - Support tables for categorization, relationships

- [ ] 3.3 Plan RoadTrip integration points
  - How does server.json map to SkillMetadata?
  - How to compute SkillFingerprint?
  - How to extract SkillCapabilities?

- [ ] 3.4 Create schema definition document
  - SQL DDL
  - Rationale for each table/field
  - Example queries for key operations

**Artifacts**:
- `workflows/006-Skill-Acquisition/MCP-Acquisition/SCHEMA_DESIGN.md`
- `src/mcp/processing/schema.sql`

---

### Phase 4: Catalog Builder Implementation (Week 4, Mar 6-12)

**Objective**: Implement tool to create persistent SQLite catalog

#### Tasks
- [ ] 4.1 Create `CatalogBuilder` class
  - Read introspection results
  - Validate against schema
  - Create SQLite database

- [ ] 4.2 Create `MCPToSkill` converter
  - Map MCP metadata → SkillMetadata
  - Extract capabilities → SkillCapabilities
  - Compute fingerprints
  - Assign trust vectors (initial)

- [ ] 4.3 Implement query API
  - Find MCPs by capability
  - Find MCPs by namespace
  - Find MCPs by complexity level
  - Find MCPs with similar auth patterns

- [ ] 4.4 Generate initial catalog
  - Populate `mcp_catalog.sqlite` with 30-50 MCPs
  - Export `MCP_CATALOG_REPORT.md`

- [ ] 4.5 Create CLI tool
  - Can query local catalog
  - Can update from registry
  - Can export for RoadTrip skills registry

**Artifacts**:
- `src/mcp/processing/catalog_builder.py`
- `src/mcp/processing/mcp_to_skill.py`
- `src/mcp/processing/fingerprinter.py`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/mcp_catalog.sqlite`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/MCP_CATALOG_REPORT.md`

---

### Phase 5: Safety & Validation (Week 4, Mar 6-12)

**Objective**: Ensure acquired MCPs are safe for integration

#### Tasks
- [ ] 5.1 Create `MCPValidator` class
  - Check for known vulnerabilities in dependencies
  - Identify privileged operations (filesystem, network, credentials)
  - Flag unusual patterns
  - Security scoring

- [ ] 5.2 Create `CapabilityAssessor` class
  - Map capabilities to RoadTrip trust tiers
  - Identify required IBAC rules
  - Recommend isolation strategy

- [ ] 5.3 Generate security report
  - Per-MCP risk assessment
  - Recommended access policies
  - Execution environment requirements

**Artifacts**:
- `src/mcp/processing/validator.py`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/SECURITY_ASSESSMENT.md`

---

### Phase 6: Documentation & Integration Points (Week 5, Mar 13-19)

**Objective**: Document findings and prepare for Phase 2a integration

#### Tasks
- [ ] 6.1 Write integration guide
  - How to query catalog from orchestrator
  - How to initialize MCP at runtime
  - How to capture execution metrics
  - How to handle errors

- [ ] 6.2 Create adapter for Phase 2a
  - Connection between orchestrator and MCP catalog
  - Telemetry hooks for ExecutionMetrics
  - Error handling for Observation system

- [ ] 6.3 Finalize documentation
  - What we learned about MCPs
  - Schema design decisions
  - Lessons for skill acquisition
  - Recommendations for Phase 3-4

**Artifacts**:
- `workflows/006-Skill-Acquisition/MCP-Acquisition/INTEGRATION_GUIDE.md`
- `src/mcp/interactions/orchestrator_adapter.py`
- `workflows/006-Skill-Acquisition/MCP-Acquisition/LESSONS_LEARNED.md`

---

## Parallel Work Streams

### Concurrent Track: Phase 1b ExecutionMetrics (Feb 14-Mar 10)
- Start immediately, independent of MCP work
- Creates telemetry foundation for Phase 2a
- Will be ready before MCP catalog is complete
- Integration point: Mar 11+

### Concurrent Track: Batch 1 Utility Skills (Feb 21-Mar 10)
- CSV, YAML, JSON, File reader/writers
- Non-dependent on MCP work
- 8 skills, homogeneous pattern
- Integration point: Immediately after Batch 1 complete

---

## Success Criteria

### By Feb 20 (Week 1)
- [ ] Registry client works
- [ ] Can retrieve 200+ MCPs from Official Registry
- [ ] Have ranked list of 30 candidates

### By Mar 5 (Week 3)
- [ ] Introspected 15-20 MCPs successfully
- [ ] Have empirical analysis and pattern document
- [ ] Schema design complete and reviewed

### By Mar 12 (Week 4)
- [ ] SQLite catalog created with 30-50 MCPs
- [ ] Conversion from server.json → SkillMetadata working
- [ ] Can query catalog by various criteria

### By Mar 19 (Week 5)
- [ ] All documentation finalized
- [ ] Integration hooks ready for Phase 2a
- [ ] Ready to scale to 100+ MCPs

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Registry API rate limits | Start with cached seed.json, rate-limit queries |
| Missingserver.json in some repos | Flag as "metadata incomplete", exclude or create manually |
| Dependency resolution complexity | Use package manager APIs (npm, PyPI) instead of manual parsing |
| Security assessment false positives | Conservative flagging; docs explain why |
| MCPs with unusual patterns | Document as outliers, decide on case-by-case basis |

---

## Resources Required

### External APIs
- Official MCP Registry: https://registry.modelcontextprotocol.io/v0.1/servers
- GitHub API (for metadata, rate limit: 60 req/hour unauthenticated)
- npm API (for package metadata)
- PyPI API (for package metadata)

### Tools
- Python 3.11+
- SQLite 3
- git (for cloning)
- requests library (API calls)
- gitpython (repo cloning)

### Storage
- ~5 GB for cloned MCPs during introspection (temporary)
- ~50 MB for final SQLite catalog
- ~20 MB for analysis artifacts

---

## Timeline

```
Feb 14-20: Phase 1 - Registry Discovery
Feb 21-Mar 5: Phase 2-3 - Introspection & Design     [Parallel: Phase 1b]
Mar 6-12: Phase 4-5 - Implementation & Validation   [Parallel: Batch 1 skills]
Mar 13-19: Phase 6 - Documentation & Integration
Mar 20+: Ready for Phase 2a ExecutionMetrics integration
```

---

## Next Step

Begin Phase 1 immediately:
1. Create `RegistryClient` class
2. Query Official Registry API
3. Generate candidate list by Feb 20

See `REGISTRY_SCHEMA_ANALYSIS.md` for technical details.
