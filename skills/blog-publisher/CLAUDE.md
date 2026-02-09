# Blog Publisher Skill - Decision Logic

**Version**: 1.0  
**Status**: Active  
**Related Docs**: `SKILL.md` (interface spec), `workflows/003-roadtrip-blog-post/plan.md` (context)

---

## Why Blog Publisher Exists

The orchestrator needs a **deterministic, reusable skill** that handles the full lifecycle of publishing a blog post from concept to live deployment. This skill bridges RoadTrip's internal workflow (where we document processes) to a public blog (where we share knowledge).

**Design Principle**: All decisions are deterministic; no LLM calls. The skill's confidence scores reflect input quality and input validation strictness, not probabilistic reasoning.

---

## Decision Tree

```
Input: BlogPost
  │
  ├─> Null Check
  │   ├─> Missing fields? → REJECT (confidence 1.0)
  │   └─> All present? → Continue
  │
  ├─> Validation Phase
  │   ├─> Title check (non-empty, <100 chars)
  │   │   ├─> FAIL → REJECT, confidence 1.0
  │   │   └─> PASS → Continue
  │   ├─> Content check (non-empty, >50 chars)
  │   │   ├─> FAIL → REJECT, confidence 1.0
  │   │   └─> PASS → Continue
  │   ├─> Secrets check (delegate to rules-engine)
  │   │   ├─> BLOCK_ALL → REJECT, confidence 1.0
  │   │   ├─> BLOCK_SOME → REJECT, confidence 1.0
  │   │   └─> APPROVE → Continue
  │   └─> File size check (<1MB)
  │       ├─> FAIL → REJECT, confidence 1.0
  │       └─> PASS → Continue
  │
  ├─> Formatting Phase
  │   ├─> Generate slug from title
  │   ├─> Parse date (ISO format or today)
  │   ├─> Fill defaults (author, tags, description)
  │   └─> Build frontmatter YAML
  │       └─> Continue
  │
  ├─> Git Prep Phase
  │   ├─> Stage file in blog repo
  │   ├─> Generate commit message
  │   ├─> Verify git status is clean (only our file)
  │   │   ├─> Dirty → REJECT, confidence 0.95
  │   │   └─> Clean → Continue
  │   └─> Continue
  │
  └─> Execution Phase
      ├─> Git push to origin/main
      │   ├─> Success → APPROVE, confidence 1.0
      │   ├─> Auth failed → REJECT, confidence 1.0
      │   ├─> Network timeout → REJECT (after retry), confidence 0.99
      │   └─> Continue
      └─> Return BlogPublishResult
```

---

## Confidence Scoring Rationale

### Deterministic Confidence Model

Unlike LLM-based skills (which guess probabilistically), **Blog Publisher's confidence reflects input validation strictness and operational certainty**.

| Scenario | Score | Rationale |
|----------|-------|-----------|
| **All checks pass, push succeeds** | 1.0 | Certain; post is live |
| **All checks pass, git succeeds, Vercel build unknown** | 0.99 | Very confident; Vercel builds usually succeed, but we don't wait |
| **Valid input, but optional fields auto-filled** | 0.99 | High confidence; auto-fill is conservative |
| **Valid input, warnings present (missing description)** | 0.95 | Confident but not perfect; warnings are logged |
| **Git working tree dirty** | 0.95 | Probably our fault (dirty state), not input fault |
| **Deployment awaiting confirmation** | 0.85 | Post committed; build status unknown |
| **Input missing optional fields** | 0.99 | No problem; we fill them |
| **Input too short** | 1.0 | Certain rejection |
| **Secrets detected** | 1.0 | Certain rejection (safety-first) |
| **Auth failure on git push** | 0.99 | Certain rejection (permission issue) |
| **Network timeout** | 0.0 | Failure; not confident in state |

### Why No 0.5-0.7 Scores?

This skill is **binary**:
- Either we validate tight and block (confidence 1.0)
- Or we validate passes and approve (confidence 0.95+)

We don't do probabilistic guessing like an LLM would. Confidence ≥ 0.95 means: "Go ahead, we're very sure." Confidence < 0.95 means: "Block, investigate."

---

## Decision Logic Details

### 1. Validation Phase

**Why strict?** A blog post is a **public artifact**. We should err on the side of caution.

**Title Validation**
- Empty → Block (confidence 1.0, "title required")
- >100 chars → Block (confidence 1.0, "title too long")
- Contains only whitespace → Block (confidence 1.0)
- Valid → Continue (confidence maintained)

**Content Validation**
- Empty → Block (confidence 1.0, "content required")
- <50 chars → Block (confidence 1.0, "blog post too short")
- Contains HTML tags → Block (confidence 1.0, "HTML not allowed, markdown only")
- File size >1MB → Block (confidence 1.0, "file too large")
- Valid → Continue

**Secrets Check** (Delegate to rules-engine)
- Input: file content
- Output: APPROVE, BLOCK_SOME, BLOCK_ALL
- If not APPROVE → Block (confidence 1.0, reason from rules-engine)

**Why delegate to rules-engine?** The rules-engine already has patterns for `.env`, `credentials`, `API_KEY`, etc. We reuse that deterministic logic instead of duplicating it.

### 2. Formatting Phase

**Slug Generation** - Deterministic algorithm

```
Title: "My Cool Blog Post!"
  ↓ lowercase
"my cool blog post!"
  ↓ remove punctuation
"my cool blog post"
  ↓ replace spaces with dashes
"my-cool-blog-post"
  ↓ remove consecutive dashes
"my-cool-blog-post"  (no change)
```

**Why slug matters**: URLs are part of the blog's permanent identity. Clean slugs reduce future maintenance.

**Filename Generation**

```
Date: 2026-02-09 (today or input)
Slug: my-cool-blog-post
Filename: 2026-02-09-my-cool-blog-post.md
```

**Why this format?** Standard in blogging. Helps:
- Sort posts by date in file system
- Avoid slug collisions (same title, different dates)
- Parse dates easily

**Frontmatter YAML**

```yaml
---
title: "My Cool Blog Post!"
date: 2026-02-09
author: "RoadTrip" (default if not provided)
tags: ["blog"] (default if not provided)
description: "My cool blog post!..." (first 160 chars if not provided)
---
```

**Why YAML?** Standard in static blog generators (Next.js blog template uses this). Parsed reliably.

### 3. Git Prepare Phase

**Why check if working tree is clean?** We want to push *only our new post*, not other uncommitted changes. If the repo is dirty, we block to avoid accidents.

**Git Status Check**
- Working tree has other uncommitted changes → Block (confidence 0.95, "repo not clean")
- Only our new post staged → Continue

**Commit Message Generation**

```
blog: publish {title} ({date})

Examples:
- "blog: publish Orchestrator Architecture Proven (2026-02-09)"
- "blog: publish Skill Development Process (2026-02-09)"
```

**Why this format?**
- Follows Conventional Commits (feat, fix, docs, etc.)
- `blog` scope identifies this as a blog operation
- Title + date in message for context
- Enables future automated changelogs

### 4. Execution Phase

**Git Push**

1. Attempt: `git push origin main`
2. On success: Return commit hash, set success=True
3. On failure:
   - Auth error → Block (confidence 1.0, "permission denied")
   - Network timeout → Retry up to 3 times, then Block (confidence 0.99)
   - Branch conflict → Block (confidence 0.99, "main branch conflict")

**Why retry on timeout?** Network glitches are transient. One retry handles most cases; three is overkill and reduces reliability.

---

## All-or-Nothing Publishing

**Principle**: A blog post is either fully published or not published at all.

**What this means**:
- If validation fails → Don't commit, don't push
- If git fails → Don't leave partial commits
- If Vercel fails → Not our problem (but we log it)

**Why?** Users expect atomicity: "I published a post" or "I didn't." A half-published post is confusing.

---

## Determinism & Idempotency

### Idempotent = Same Input → Same Output

If you call the skill twice with identical input:
- First call: ✅ Post published, commit hash ABC123
- Second call: ❌ File already exists, git status clean (no changes to push)

**Is that a problem?** No. We return:
```python
BlogPublishResult(
    decision="APPROVE",
    success=False,
    errors=["file already exists, nothing pushed"]
)
```

**Why allow this?** It's deterministic and safe. The orchestrator can log "republish attempted" and move on. No data loss, no corruption.

### Determinism = No Randomness

Every decision flows from input + config:
- No timestamps in logic (only in output metadata)
- No random slug suffixes
- No probabilistic reasoning
- Date always from input or today's date (deterministic)

**Test**: Run with same input 10 times → 10 identical outputs (or 10 "file exists" messages).

---

## Error Recovery Strategy

### Hard Failures (Don't Retry)
- Title or content empty → Reject immediately
- Secrets detected → Reject immediately
- Auth failed → Reject (permissions are not transient)

### Soft Failures (Retry Strategy)
- Network timeout → Retry 3x with exponential backoff
- Vercel build failure → Log but don't block (we don't control it)

### Conservative Defaults
- Missing author? Use "RoadTrip"
- Missing tags? Use ["blog"]
- Missing description? Auto-generate from content
- Missing date? Use today's date

---

## Interaction with Other Skills

### Uses: Rules-Engine (Secrets Validation)
Request:
```python
evaluate(content, "blog-content")
```

Response:
```python
RulesResult(
    decision="APPROVE",  # or "BLOCK_ALL"
    confidence=1.0
)
```

Decision: If rules-engine says BLOCK, we block. Otherwise continue.

### Uses: Git-Push-Autonomous (Reference)
We follow the same git patterns:
- Conservative defaults (block on dirty repo)
- Idempotent operations (re-running is safe)
- Clear error messages
- Retry strategy for transient failures

### Future: Auth-Validator (Phase 1b)
Once available, check git permissions before push:
```python
auth_result = validate_git_auth(repo_url, branch)
if not auth_result.can_push:
    REJECT with auth_result.error
```

### Future: Telemetry-Logger (Phase 1b)
Log every decision:
```python
log_entry = {
    "skill": "blog_publisher",
    "timestamp": now(),
    "decision": "APPROVE",
    "success": True,
    "confidence": 1.0,
    "url": "https://..."
}
telemetry_logger(log_entry)
```

---

## FAQ: Decision Logic

**Q: Why block on secrets?**  
A: Blog posts are public. Accidentally publishing credentials would be catastrophic. Conservative.

**Q: Why require >50 chars?**  
A: Anything shorter isn't really a blog post; it's a tweet. This prevents spam.

**Q: Why auto-fill author?**  
A: Convenience. The orchestrator is publishing on behalf of RoadTrip. If a human wrote it, they'll add their name.

**Q: Why slug generation (not use full title)?**  
A: URLs should be short, readable, and SEO-friendly. A full title with punctuation is messy.

**Q: What if Vercel fails?**  
A: Not our problem. We pushed; Vercel builds. If the build fails, it's a Vercel configuration issue, not a skill issue. We log it and move on.

**Q: Can I publish twice?**  
A: Yes, but the second attempt will be idempotent (file already exists). The orchestrator can detect this and handle appropriately.

**Q: What about drafts?**  
A: Out of scope for Phase 1. A blog post is public. Future enhancement: add "published=false" to frontmatter for draft mode.

---

## Confidence Calibration Process

**How we validate scoring**:
1. Collect 20 real blog publish attempts (Phase 4 testing)
2. Compare confidence scores to actual outcomes
3. Calibrate:
   - If confidence 1.0 had failures → Lower score
   - If confidence 0.95 had failures → Tighten validation
   - If confidence <0.5 never failed → Raise score

**Example calibration**:
```
Initial: Confidence 1.0 on git push
Results: 2/100 failures (network timeout)
New: Confidence 0.99 on git push success
Rationale: 1% chance of transient network issues
```

---

## Success = Certainty, Not Perfection

**Accept 99% confidence on push success because**:
- Network is genuinely 99% reliable
- WAN timeouts are rare but possible
- We retry, which further reduces failure rate

**Accept 1.0 confidence on validation blocks because**:
- These are logical checks (non-empty, valid YAML)
- No external factors matter
- We control the check completely

---

## Design Decisions Log

| Decision | Rationale | Alternative Considered |
|----------|-----------|------------------------|
| Block on empty title | Safety-first; post needs a name | Allow auto-generated titles (rejected: less user control) |
| Slug generation algorithm | Deterministic, no randomness | UUID suffixes (rejected: ugly URLs) |
| All-or-nothing publishing | Atomicity ensures consistency | Partial commits (rejected: confusing state) |
| Git push strategy | Use standard git commands | Call Vercel API directly (rejected: unnecessary dependency) |
| 3-retry-timeout logic | Balances reliability + performance | No retry (rejected: fragile), retry forever (rejected: hangs) |
| Delegate secrets to rules-engine | Reuse existing safety logic | Duplicate patterns (rejected: maintenance burden) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-09 | Initial decision logic |

---

**Decision Logic Status**: ✅ Ready for Code Implementation (Phase 3)
