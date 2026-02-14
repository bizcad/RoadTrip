# Skill Acquisition Strategy: Building a Diverse Portfolio

**Version**: 1.0  
**Date**: 2026-02-14  
**Purpose**: Identify 15-20 initial skills to acquire so we have meaningful orchestration scenarios  

---

## Why Skill Acquisition NOW?

You said: *"It's hard to reason about DAG and orchestration/assembly/composition of workflows with only half a dozen skills."*

**Exactly right.** With only git-push and blog-publish, we can't test:
- Routing decisions (routing skill A vs. skills B & C in parallel)
- Graceful degradation (if skill X fails, try alternative Y)
- Composition patterns (request → auth → validate → transform → store → notify)
- Anomaly detection (most of the time nothing is unusual; hard to detect real anomalies)
- Bidirectional learning (hard to discover patterns with 2 data points)
- Risk management (hard to reason about cost/quota with just one pipeline)

**With 20 skills**, we can design realistic workflows:
- Parse user request → Classify intent → Route to specialized handler → Format output
- Validate credentials → Check permissions → Execute → Log → Notify
- Read config → Transform data → Validate → Store → Publish

**With 50+ skills**, the system starts learning:
- "This composition works better than documented pipeline"
- "Skill A is consistently faster than Skill B for this task"
- "When we route through handler C, success rate is 3% higher"

---

## Skill Acquisition Criteria

For PHASE 1 (initial batch), prioritize:

### ✅ Good Fit
1. **Deterministic** (not probabilistic)
   - Example: parse CSV into dict ✅
   - Example: LLM classify intent ❌ (too much variance in reasoning)
2. **Pure functions** (no side effects, or well-understood side effects)
   - Example: SHA256(data) → hash ✅
   - Example: store_in_database(data) ✅ (side effect, but deterministic)
3. **Fast** (< 5 seconds typical execution)
   - Example: YAML parse ✅ (ms)
   - Example: train_deep_learning_model ❌ (hours)
4. **Low cost** (especially on free tiers)
   - Example: cryptographic hash ✅ (free)
   - Example: OpenAI API call ⚠️ (costs tokens)
5. **Well-understood** (existing, proven implementations)
   - Example: use proven cryptography library ✅
   - Example: invent our own encryption ❌

### ❌ Defer to Phase 2
- Complex ML models (hard to fingerprint, expensive to evaluate)
- Proprietary vendor APIs with unpredictable pricing
- Stateful skills that require careful isolation

---

## Proposed First Batch: 15-20 Skills

Organized by **category** → useful compositions become obvious

### Category 1: Data Input & Parsing (4 skills)
These **read data from sources**.

1. **CSV Parser**
   - Input: `path: str, encoding: str = "utf-8"`
   - Output: `rows: List[Dict[str, str]]`
   - Example use: Read road trip itinerary from CSV
   - Cost: Free
   - Time: ~100ms

2. **YAML Parser**
   - Input: `path: str`
   - Output: `config: Dict[str, Any]`
   - Example use: Load skill configuration
   - Cost: Free
   - Time: ~50ms

3. **JSON Parser**
   - Input: `data: str`
   - Output: `parsed: Dict[str, Any]`
   - Example use: Parse API response
   - Cost: Free
   - Time: ~50ms

4. **File Reader**
   - Input: `path: str, encoding: str = "utf-8"`
   - Output: `content: str`
   - Example use: Read commit template, read docs
   - Cost: Free
   - Time: ~100ms

### Category 2: Data Validation (4 skills)
These **verify data meets requirements**.

5. **Schema Validator (JSON Schema)**
   - Input: `data: Dict, schema: Dict`
   - Output: `valid: bool, errors: List[str]`
   - Example use: Validate API input before processing
   - Cost: Free
   - Time: ~100ms

6. **Email Validator**
   - Input: `email: str`
   - Output: `valid: bool, reason: str`
   - Example use: Validate user email in API requests
   - Cost: Free
   - Time: ~50ms

7. **URL Validator**
   - Input: `url: str`
   - Output: `valid: bool, parsed_url: ParseResult`
   - Example use: Check GitHub links in commit messages
   - Cost: Free
   - Time: ~50ms

8. **Credit Card Validator (Luhn Algorithm)**
   - Input: `card_number: str`
   - Output: `valid: bool, card_type: str`
   - Example use: Validate payment info (future procurement workflow)
   - Cost: Free
   - Time: ~10ms

### Category 3: Data Transformation (4 skills)
These **change data format or structure**.

9. **CSV → JSON Converter**
   - Input: `csv_path: str, delimiter: str = ","`
   - Output: `json_data: List[Dict]`
   - Example use: Convert itinerary CSV to JSON for API
   - Cost: Free
   - Time: ~200ms

10. **Text Formatter (uppercase, title case, sentence case)**
    - Input: `text: str, style: Literal['upper', 'lower', 'title', 'sentence']`
    - Output: `formatted: str`
    - Example use: Normalize commit message format
    - Cost: Free
    - Time: ~50ms

11. **Markdown → HTML Converter**
    - Input: `markdown: str`
    - Output: `html: str`
    - Example use: Convert blog post Markdown to HTML
    - Cost: Free (python-markdown library)
    - Time: ~500ms

12. **Template Renderer (Jinja2)**
    - Input: `template: str, context: Dict[str, str]`
    - Output: `rendered: str`
    - Example use: Generate email from template, generate report
    - Cost: Free
    - Time: ~100ms

### Category 4: Data Filtering & Aggregation (3 skills)
These **select or summarize data**.

13. **Text Search & Filter**
    - Input: `items: List[str], pattern: str, match_type: Literal['exact', 'regex', 'substring']`
    - Output: `matches: List[str]`
    - Example use: Find all commits related to "bug" in description
    - Cost: Free
    - Time: ~100ms

14. **Sort & Order**
    - Input: `items: List[Dict], sort_by: str, ascending: bool = True`
    - Output: `sorted_items: List[Dict]`
    - Example use: Order tasks by priority, date, cost
    - Cost: Free
    - Time: ~100ms

15. **Deduplicate**
    - Input: `items: List[Dict], key: str`
    - Output: `unique_items: List[Dict]`
    - Example use: Remove duplicate file paths, deduplicate warnings
    - Cost: Free
    - Time: ~100ms

### Category 5: Crypto & Hash (2 skills)
These **compute cryptographic signatures or hashes**.

16. **SHA256 Hash**
    - Input: `data: str | bytes`
    - Output: `hash: str`
    - Example use: Fingerprint skills, hash content
    - Cost: Free
    - Time: ~1-10ms

17. **HMAC Generator (for auth)**
    - Input: `data: str, secret: str, algorithm: str = "sha256"`
    - Output: `signature: str`
    - Example use: Sign API requests, verify webhook authenticity
    - Cost: Free
    - Time: ~10ms

### Category 6: Notification & Reporting (2 skills)
These **send information out**.

18. **Email Sender**
    - Input: `to: str, subject: str, body: str, html: bool = False`
    - Output: `sent: bool, message_id: str`
    - Example use: Notify operator of anomalies, send digest
    - Cost: Free via mailing server (or SMTP)
    - Time: ~1000-5000ms (network dependent)

19. **Logging & Storage (append to JSONL)**
    - Input: `log_file: str, data: Dict`
    - Output: `logged: bool`
    - Example use: Store execution metrics, audit trail
    - Cost: Free (filesystem)
    - Time: ~100ms

---

## Useful Skill Compositions (DAGs)

With these 15-20 skills, here are workflows you could build:

### Workflow 1: Process Road Trip Itinerary
```
1. CSV Parser         (read itinerary.csv)
   ↓
2. Schema Validator   (ensure required fields)
   ↓
3. CSV→JSON Converter (convert to JSON)
   ↓
4. Template Renderer  (generate itinerary report)
   ↓
5. Email Sender       (send to user)
```

### Workflow 2: Validate & Process Blog Metadata
```
1. JSON Parser        (read blog metadata)
   ↓
2. Schema Validator   (check required fields)
   ↓
3. Email Validator    (check author email)
   ↓
4. URL Validator      (check links)
   ↓
5. Logging            (record results)
```

### Workflow 3: Detect Anomalies in Execution Metrics
```
1. File Reader        (read metrics JSONL)
   ↓
2. JSON Parser        (each line -> dict)
   ↓
3. Deduplicate        (remove duplicates)
   ↓
4. Sort               (sort by timestamp)
   ↓
5. Text Search        (find errors matching pattern)
   ↓
6. Logging            (store anomaly report)
   ↓
7. Email Sender       (notify operator if critical)
```

### Workflow 4: Secure Webhook Verification
```
1. JSON Parser        (parse webhook payload)
   ↓
2. HMAC Generator     (compute expected signature)
   ↓
3. Text Search        (find actual signature in headers)
   ↓
4. Schema Validator   (ensure payload minimal requirements)
   ↓
5. Forward to handler (if valid)
```

### Workflow 5: Skill Fingerprinting
```
1. File Reader        (read skill source code)
   ↓
2. SHA256 Hash        (compute content hash)
   ↓
3. File Reader        (read test file)
   ↓
4. SHA256 Hash        (compute test hash)
   ↓
5. Template Renderer  (generate fingerprint metadata)
   ↓
6. Text Formatter     (format for YAML header)
```

---

## Timeline: How to Acquire These 20 Skills

**Phase**: Workflow 006 (Skill Acquisition)  
**Timeline**: Feb 14 - Apr 30, 2026 (parallel with Phases 1b-2)  

### Batch 1: Baseline (Feb 14 - Feb 28)
**Skills**: Categories 1 & 2 (8 skills)  
Activities:
- [ ] Search for existing implementations (Python stdlib, PyPI)
- [ ] Assess code quality, license compatibility
- [ ] Write wrappers (standardize interface, add error handling)
- [ ] Add YAML headers with fingerprints
- [ ] Write tests (100% coverage target)
- [ ] Get approval from operator
- [ ] Add to REGISTRY.yaml

**Output**: 8 skills in production registry

### Batch 2: Transformation (Mar 1 - Mar 15)
**Skills**: Category 3 (4 skills) + Category 5 (2 skills)  
Activities: Same as Batch 1  
**Output**: 6 more skills (14 total)

### Batch 3: Filtering & Aggregation (Mar 16 - Mar 31)
**Skills**: Category 4 (3 skills)  
Activities: Same as Batch 1  
**Output**: 3 more skills (17 total)

### Batch 4: Integration & Polish (Apr 1 - Apr 30)
**Skills**: Category 6 (2 skills) + review & refinement  
Activities:
- [ ] Implement Category 6 skills
- [ ] Run end-to-end composition test (Workflow 1-5 above actually work)
- [ ] Performance profiling (identify bottlenecks)
- [ ] Security audit (each skill for credential leaks, injection vulnerabilities)
- [ ] Documentation (each skill with examples)

**Output**: 19 skills in production, fully composed and tested

---

## Skill Acquisition Process (From Workflow 006)

For each skill in the batches above:

1. **Discovery** (10 minutes)
   - Search GitHub, PyPI, crates.io, etc.
   - Find existing implementation or decide to write

2. **Evaluation** (1 hour)
   - Code quality: Is it well-written? Follows conventions?
   - Security: Could it leak credentials? Inject attacks?
   - Performance: How fast? How much memory?
   - Licensing: MIT/Apache/GPL? Compatible?

3. **Vetting** (20 minutes)
   - Create `SkillMetadata` dataclass with interfaces
   - Write unit tests (~20 test cases per skill)
   - Compute fingerprint (SHA256 of interface + tests)
   - Create `SkillSecurityProfile` (what can it access?)

4. **Onboarding** (30 minutes)
   - Create YAML header in skill file
   - Add to REGISTRY.yaml
   - Create skill entry in fingerprint.py data structures
   - Operator review & approval

5. **Integration** (20 minutes)
   - Verify skill shows up in capability queries
   - Run end-to-end test (orchestrator finds skill, invokes it)
   - Document in SKILLS.md

**Total per skill**: ~2 hours (with parallelization, batch of 4 skills = ~4-5 hours)  
**Total for 20 skills**: ~40 hours = 1 week full-time or 2-3 weeks part-time

---

## Why This Matters for Your Learning System

With these 20 skills:

### You can test **anomaly detection**
- Baseline: CSV parser succeeds > 99.9% of time
- Anomaly: If it drops to 95%, system flags it
- With 2 skills, this is trivial. With 20, you spot real patterns.

### You can test **bidirectional learning**
- Operator approves: "Use Workflow 3 (anomaly detection)" 50 times
- System learns: "Operator prefers this workflow for these inputs"
- Next similar request, system proposes Workflow 3 proactively

### You can test **routing decisions**
- DAG executor chooses between Email or Logging skill
- System learns: "Email is 40% slower; use Logging unless operator specifically asks for email"
- With 2 skills, no interesting routing decisions. With 20, routing + resource allocation becomes important.

### You can test **graceful degradation**
- Email skill occasionally fails (network timeout)
- DAG executor falls back to Logging skill automatically
- System learns: "Email is unreliable at 10pm; use Logging during that window"

---

## Detailed First Skill: CSV Parser

To show how we'd actually do this, here's the first skill:

**Skill**: CSVParser  
**Author**: RoadTrip (internal)  
**Version**: 1.0.0  

**Metadata**:
```python
@dataclass
class CSVParserMetadata(SkillMetadata):
    skill_name = "csv_parser"
    skill_id = "csv_parser::1.0.0"
    author = "RoadTrip"
    version = "1.0.0"
    description = "Parse CSV files into list of dictionaries"
    capabilities = [
        Capability(
            name="parse_csv",
            description="Parse CSV file into list of dicts with headers",
            capability_type=CapabilityType.DATA_PRODUCER,
            inputs={"csv_path": ["str"], "encoding": ["str"]},
            outputs={"rows": ["List[Dict[str, str]]"]},
            cost_tokens_min=1,
            cost_tokens_max=10,
            cost_tokens_typical=5,
            confidence_level=ConfidenceLevel.HIGH,
            success_rate_approximate=0.9999,
            tags={"parsing", "file-io", "deterministic"},
        )
    ]
```

**Fingerprint**:
```
fingerprint_hash: "a7f2e3d1c6b4a9e8"
hash_components:
  interface_signature: sha256("parse_csv(csv_path: str, encoding: str) -> List[Dict[str, str]]")
  test_spec: sha256(test file with 50 test cases)
  source_code: sha256(source code)
```

**Security Profile**:
```python
security_profile = SkillSecurityProfile(
    security_tier=0,  # No special access
    can_read_filesystem=True,  # Needs to read CSV files
    free_tier_safe=True,
    requires_approval=False,
)
```

**Implementation**:
```python
# src/skills/csv_parser.py

import csv
from typing import List, Dict

def execute(csv_path: str, encoding: str = "utf-8") -> Dict:
    """Parse CSV file into list of dicts with headers as keys."""
    try:
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            rows = [dict(row) for row in reader]
        return {
            "success": True,
            "rows": rows,
            "row_count": len(rows),
            "headers": list(rows[0].keys()) if rows else [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "rows": [],
            "row_count": 0,
        }
```

**Tests** (20+ test cases):
```python
def test_parse_simple_csv():
    result = execute("test_data/simple.csv")
    assert result["success"]
    assert len(result["rows"]) == 3
    assert result["rows"][0]["name"] == "Alice"

def test_parse_empty_csv():
    result = execute("test_data/empty.csv")
    assert result["success"]
    assert len(result["rows"]) == 0

def test_parse_with_unicode():
    result = execute("test_data/unicode.csv", encoding="utf-8")
    assert result["success"]
    assert "café" in str(result["rows"])

def test_missing_file():
    result = execute("test_data/nonexistent.csv")
    assert not result["success"]
    assert "not found" in result["error"].lower()

# ... (15 more test cases)
```

---

## Next Steps

1. **Approve the batch approach** (Batch 1 Feb 14-28, Batch 2 Mar 1-15, etc.)
2. **Review the 20 skill list** (does it match your needs? Should we add/remove?)
3. **Start Batch 1** (I can write CSV parser + YAML parser + JSON parser + File reader this week)
4. **Parallel**: Start Phase 1b coding (ExecutionMetrics) at same time

By end of April, you'll have **19 production-grade skills** + **Phase 1b metrics foundation**.  
By end of June, Phase 3 DAG is complete.  
By end of Sept, Phase 4 (self-improvement) is ready, and you have 20-30 skills learning from each other.

Shall we start with Batch 1?
