# Skills Index & Semantic Discovery

**Purpose**: Enable LLM agents to discover and invoke skills based on semantic context without explicit calling.

## Quick Reference

| Skill | Primary Use | Input | Output | Cost |
|-------|------------|-------|--------|------|
| **auth-validator** | Verify authorization before operations | User identity, skill, resource | APPROVED \| FORBIDDEN_LAYER_* | $0 |
| **git-push-autonomous** | Autonomous git push with safety | Working tree changes | SUCCESS \| BLOCKED \| ERROR | $0 |
| **commit-message** | Generate semantic commit msgs | Staged files, diff | Message + confidence | $0-0.01 |
| **blog-publisher** | Publish blog posts | BlogPost object | BlogPublishResult | $0 |
| **rules-engine** | Validate files vs safety rules | File list, context | APPROVE \| BLOCK_ALL \| BLOCK_SOME | $0 |
| **telemetry-logger** | Log autonomous decisions | Decision log object | RECORDED + log_id | $0 |

## Skill Dependencies

```
git-push-autonomous
├── Calls: auth-validator (permission check)
├── Calls: rules-engine (file validation)
├── Calls: commit-message (message generation)
└── Calls: telemetry-logger (audit trail)

blog-publisher
├── Calls: rules-engine (content validation)
├── Calls: auth-validator (git push permission)
└── Calls: telemetry-logger (audit trail)
```

## How to Use Semantically

### Scenario 1: Push Changes
**You say**: "commit and push these changes"
**Claude discovers**: git-push-autonomous skill
**Claude invokes**: 
```
git-push-autonomous(
  auth_check = true,
  rules_check = true,
  auto_commit_message = true
)
```
**Result**: Changes pushed with auto-generated message, fully logged

### Scenario 2: Publish Blog Post
**You say**: "publish a blog post about RoadTrip architecture"
**Claude discovers**: blog-publisher skill
**Claude invokes**:
```
blog-publisher(
  title = "RoadTrip Architecture",
  excerpt = "...",
  content = "...",
  validate_secrets = true,
  auto_publish = true
)
```
**Result**: Post published to https://roadtrip-blog-ten.vercel.app/

### Scenario 3: Assess Authorization
**You say**: "can I deploy to production?"
**Claude discovers**: auth-validator skill
**Claude invokes**:
```
auth-validator(
  user_identity = current_user,
  skill_name = "deploy-production",
  resource = "production-cluster"
)
```
**Result**: FORBIDDEN_LAYER_2 → "Insufficient role, need Staff-Engineer or above"

## Discovery Mechanism

Skills are discoverable via:

1. **Semantic Matching**: Agent reads skill descriptions in SKILL.md
2. **Dependency Graph**: Agent understands which skills call which
3. **Configuration Keywords**: Agent matches keywords (git, push, publish, deploy, etc.)
4. **Context**: Agent tracks what tool is needed based on user request

## Phase Evolution

### Phase 1b (Now) - File Structure
- ✅ Skills in `./skills/` (canonical)
- ✅ Skills in `.github/skills/` (GitHub Actions discovery)
- ✅ Skills in `.claude/skills/` (IDE discovery)
- ✅ README + INDEX for navigation

### Phase 1c (Next) - Semantic Indexing
- Index file with descriptions + keywords
- Agent can query "find skill that does X"
- Automatic matching of requests to skills

### Phase 2a (Later) - Config-Driven
- Skills can be enabled/disabled per environment
- Confidence thresholds per skill
- Cost budgets per skill

### Phase 2b+ - Dynamic
- New skills discovered from catalog
- Skill proposals ranked by usefulness
- Auto-recommendation based on patterns

## File Locations

| Context | Location | Usage |
|---------|----------|-------|
| Canonical | `./skills/{skill-name}/` | Source of truth |
| GitHub Actions | `.github/skills/` | CI/CD workflows |
| Claude IDE | `.claude/skills/` | Chat + development |

## Example: Searching for Skills

**Agent query**: "I need to safely push changes"
**Discovery process**:
1. Parse query keywords: "push", "safely"
2. Search skill descriptions for "push"
3. Find: git-push-autonomous matches perfectly
4. Check dependencies: requires auth-validator, rules-engine
5. Verify all dependencies available
6. Use git-push-autonomous

**Agent query**: "How do I authorize this operation?"
**Discovery process**:
1. Parse query keywords: "authorize", "operation", "permission"
2. Search skill descriptions for "authorization"
3. Find: auth-validator matches
4. Load auth-validator-CLAUDE.md for decision logic
5. Use auth-validator with appropriate parameters

## Adding New Skills

1. Create skill in `./skills/{new-skill}/`
2. Write SKILL.md with interface spec
3. Write CLAUDE.md with decision logic (optional)
4. Write examples.md with usage (optional)
5. Copy to `.github/skills/{new-skill}-SKILL.md` (etc.)
6. Copy to `.claude/skills/{new-skill}-SKILL.md` (etc.)
7. Update this INDEX.md
8. Agent will auto-discover on next context refresh

## Cost Tracking Across Skills

When multiple skills are chained, total cost is tracked:

```json
{
  "workflow": "git-push-autonomous",
  "steps": [
    { "skill": "auth-validator", "cost": 0.0 },
    { "skill": "rules-engine", "cost": 0.0 },
    { "skill": "commit-message", "cost": 0.004, "approach": "tier2_llm" },
    { "skill": "telemetry-logger", "cost": 0.0 }
  ],
  "total_cost": "$0.004",
  "execution_time_sec": 3.2
}
```

## Testing Skill Discovery

**For GitHub Actions**:
```bash
find .github/skills -name "*.md" | sort
```

**For Claude in IDE**:
Agent can search `.claude/skills/` context automatically.

---

**Last Updated**: 2026-02-15  
**Status**: Phase 1b Skills Discovery Complete
