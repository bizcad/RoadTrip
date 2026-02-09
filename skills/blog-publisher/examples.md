# Blog Publisher Skill - Usage Examples

**Version**: 1.0  
**Status**: Reference (for Phase 3+ implementation)

---

## Overview

This document shows how to use the blog publisher skill in different scenarios. These examples serve as requirements for the code implementation.

---

## Example 1: Simple Blog Post (Happy Path)

**Scenario**: Publish a well-formatted blog post about orchestrator architecture.

### Input

```python
from src.skills.blog_publisher import BlogPost, publish_blog_post

post = BlogPost(
    title="Orchestrator Architecture Proven",
    content="""# Orchestrator Architecture Proven

We've successfully demonstrated that the RoadTrip orchestrator can handle multi-step workflows.

## Key Components

1. **Specialist Skills** - Each handles one task deterministically
2. **Orchestrator** - Composes specialists into workflows
3. **Safety Checks** - Conservative defaults block risky operations

## Proof of Concept

This blog post itself was published by an agent, proving the orchestrator works end-to-end.
""",
    author="Nicholas Stein",
    tags=["orchestrator", "agents", "automation"]
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="APPROVE",
    success=True,
    filename="2026-02-09-orchestrator-architecture-proven.md",
    url="https://roadtrip-blog-ten.vercel.app/blog/orchestrator-architecture-proven",
    commit_hash="a1b2c3d4",
    git_push_confirmed=True,
    confidence=1.0,
    warnings=[],
    errors=[]
)
```

### What Happened

1. ✅ Title validated (non-empty, < 100 chars)
2. ✅ Content validated (> 50 chars, no secrets)
3. ✅ Slug generated: "orchestrator-architecture-proven"
4. ✅ Frontmatter built with all fields
5. ✅ File created: `2026-02-09-orchestrator-architecture-proven.md`
6. ✅ Git commit: "blog: publish Orchestrator Architecture Proven (2026-02-09)"
7. ✅ Git push succeeded
8. ✅ Result returned with live URL

### Post Now Live At

https://roadtrip-blog-ten.vercel.app/blog/orchestrator-architecture-proven

---

## Example 2: Minimal Input (Defaults Applied)

**Scenario**: Publish a post with only title and content; let the skill fill in the rest.

### Input

```python
post = BlogPost(
    title="Skill Development Process",
    content="# Skill Development\n\nWe build skills using spec-driven development..."
)
# author, tags, description left empty (will use defaults)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="APPROVE",
    success=True,
    filename="2026-02-09-skill-development-process.md",
    url="https://roadtrip-blog-ten.vercel.app/blog/skill-development-process",
    commit_hash="b2c3d4e5",
    git_push_confirmed=True,
    confidence=0.99,
    warnings=[
        "author field empty, using default: 'RoadTrip'",
        "tags field empty, using default: ['blog']",
        "description field empty, auto-generated from content"
    ],
    errors=[]
)
```

### What the Skill Did

1. ✅ Author: Filled with "RoadTrip"
2. ✅ Tags: Filled with ["blog"]
3. ✅ Description: Auto-generated from first 160 chars
4. ℹ️ Warnings logged (non-blocking)
5. ✅ Everything else same as Example 1

### Frontmatter Built

```yaml
---
title: "Skill Development Process"
date: 2026-02-09
author: "RoadTrip"
tags: ["blog"]
description: "Skill Development We build skills using spec-driven development..."
---
```

---

## Example 3: Invalid Title (Hard Block)

**Scenario**: Try to publish a post with an empty title.

### Input

```python
post = BlogPost(
    title="",  # ❌ Empty!
    content="This is my blog post content about something cool."
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="REJECT",
    success=False,
    filename="",
    url="",
    commit_hash="",
    git_push_confirmed=False,
    confidence=1.0,  # Certain rejection
    warnings=[],
    errors=["title cannot be empty"]
)
```

### What the Skill Did

1. ✅ Title validation: FAIL (empty)
2. ❌ Hard block, don't continue
3. ❌ Return REJECT with confidence 1.0

### No Git Operations

- ❌ No file created
- ❌ No git commit
- ❌ No push
- ✅ Clean exit with error message

---

## Example 4: Content Too Short (Hard Block)

**Scenario**: Try to publish a post with insufficient content.

### Input

```python
post = BlogPost(
    title="Too Short",
    content="Not long"  # ❌ Only 8 chars (need >50)
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="REJECT",
    success=False,
    filename="",
    url="",
    commit_hash="",
    git_push_confirmed=False,
    confidence=1.0,
    warnings=[],
    errors=["content must be at least 50 characters (got 8)"]
)
```

---

## Example 5: Content Contains Secrets (Hard Block)

**Scenario**: Try to publish a post that accidentally includes an API key.

### Input

```python
post = BlogPost(
    title="Integration Guide",
    content="""# Integration Guide

Use the Vercel API:

```
VERCEL_TOKEN=abc_xyz_secret_key_12345
API_URL=https://api.vercel.com
```

Here's how to integrate...
"""
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="REJECT",
    success=False,
    filename="",
    url="",
    commit_hash="",
    git_push_confirmed=False,
    confidence=1.0,
    warnings=[],
    errors=[
        "secrets detected in content",
        "matched pattern: .*_TOKEN=.*",
        "content blocked by rules-engine"
    ]
)
```

### Why It Blocked

- The rules-engine detected `VERCEL_TOKEN=...` pattern
- Matches the blocked pattern `^\s*[A-Z_]+_TOKEN=`
- Decision escalated to REJECT with confidence 1.0
- Conservative approach: never publish secrets

---

## Example 6: Republish Same Post (Idempotent)

**Scenario**: Publish a post, then run the same command again with same input.

### First Call

```python
post = BlogPost(
    title="Idempotency Test",
    content="This demonstrates idempotent publishing..."
)

result = publish_blog_post(post)
# Result: success=True, confidence=1.0, commit_hash="c3d4e5f6"
```

### Second Call (Identical Input)

```python
post = BlogPost(
    title="Idempotency Test",
    content="This demonstrates idempotent publishing..."
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="APPROVE",
    success=False,
    filename="2026-02-09-idempotency-test.md",
    url="https://roadtrip-blog-ten.vercel.app/blog/idempotency-test",
    commit_hash="",
    git_push_confirmed=False,
    confidence=0.99,
    warnings=[],
    errors=["file already exists at 2026-02-09-idempotency-test.md, nothing to push"]
)
```

### What Happened

1. ✅ Validation: PASS (same input as before)
2. ✅ Formatting: File already exists on disk
3. ⚠️ Git status: No changes to commit (working tree clean)
4. ❌ Git push: Nothing to push (no changes)
5. ✅ Return APPROVE (no harm done, idempotent)

### Why It's Safe

- Post is already live (no data loss)
- No partial commits
- Orchestrator can log "republish attempted, no changes"
- Deterministic behavior (same input → same outcome)

---

## Example 7: Very Long Title (Hard Block)

**Scenario**: Try to publish with a title exceeding 100 characters.

### Input

```python
post = BlogPost(
    title="This is an extraordinarily long and unnecessarily verbose title that goes on and on and on well past the hundred character limit",
    content="Some content here..."
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="REJECT",
    success=False,
    filename="",
    url="",
    commit_hash="",
    git_push_confirmed=False,
    confidence=1.0,
    warnings=[],
    errors=["title too long (got 141 chars, max 100)"]
)
```

---

## Example 8: Multiple Tags

**Scenario**: Publish a post with specific tags for categorization.

### Input

```python
post = BlogPost(
    title="SOLID Principles in Agent Design",
    content="# SOLID Principles\n\nHow we apply SOLID to agent development...",
    author="Design Team",
    tags=["agents", "architecture", "solid", "best-practices"]
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="APPROVE",
    success=True,
    filename="2026-02-09-solid-principles-in-agent-design.md",
    url="https://roadtrip-blog-ten.vercel.app/blog/solid-principles-in-agent-design",
    commit_hash="d4e5f6g7",
    git_push_confirmed=True,
    confidence=1.0,
    warnings=[],
    errors=[]
)
```

### Frontmatter Built

```yaml
---
title: "SOLID Principles in Agent Design"
date: 2026-02-09
author: "Design Team"
tags: ["agents", "architecture", "solid", "best-practices"]
description: "SOLID Principles How we apply SOLID to agent development..."
---
```

---

## Example 9: Custom Date

**Scenario**: Publish a post with a specific date (not today).

### Input

```python
post = BlogPost(
    title="Historical Post",
    content="# Looking Back\n\nThis post is about an event from last month...",
    date="2026-01-09"  # Specific date
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="APPROVE",
    success=True,
    filename="2026-01-09-historical-post.md",  # ← Note the date
    url="https://roadtrip-blog-ten.vercel.app/blog/historical-post",
    commit_hash="e5f6g7h8",
    git_push_confirmed=True,
    confidence=1.0,
    warnings=[],
    errors=[]
)
```

### Filename Reflects Custom Date

The filename uses the date you provided, not today's date. This enables backdating posts if needed.

---

## Example 10: Special Characters in Title (Slugification)

**Scenario**: Publish with special characters and punctuation in title.

### Input

```python
post = BlogPost(
    title="REST API Best Practices! Q&A Edition (2026)",
    content="# REST & Q&A\n\nHere's how to build APIs correctly..."
)

result = publish_blog_post(post)
```

### Expected Output

```python
BlogPublishResult(
    decision="APPROVE",
    success=True,
    filename="2026-02-09-rest-api-best-practices-q-a-edition-2026.md",
    url="https://roadtrip-blog-ten.vercel.app/blog/rest-api-best-practices-q-a-edition-2026",
    commit_hash="f6g7h8i9",
    git_push_confirmed=True,
    confidence=1.0,
    warnings=[],
    errors=[]
)
```

### Slug Transformation

```
"REST API Best Practices! Q&A Edition (2026)"
↓ lowercase
"rest api best practices! q&a edition (2026)"
↓ remove punctuation (keep dashes and ampersand → replace &)
"rest api best practices q a edition 2026"
↓ replace spaces with dashes
"rest-api-best-practices-q-a-edition-2026"
```

---

## Integration with Orchestrator

### Example: Using in a Workflow

```python
from src.skills.blog_publisher import BlogPost, publish_blog_post
from src.skills.rules_engine import evaluate

# Step 1: Get content (from docs or user input)
blog_content = """# My Post Title\n\nContent here..."""

# Step 2: Validate content for secrets
rules_result = evaluate(files=["blog.md"], repo_root=".")
if rules_result.decision != "APPROVE":
    print("Blog content blocked by rules")
    exit(1)

# Step 3: Create BlogPost
post = BlogPost(
    title="My Post Title",
    content=blog_content,
    tags=["orchestration"]
)

# Step 4: Publish
result = publish_blog_post(post)

if result.success:
    print(f"✅ Posted live: {result.url}")
else:
    print(f"❌ Failed: {result.errors}")
```

---

## Testing These Examples

When we get to Phase 4 (Testing), each of these examples will become a pytest test case:

```python
def test_happy_path_simple_post():
    """Example 1: Simple blog post"""
    # ... (test code)

def test_minimal_input_defaults_applied():
    """Example 2: Minimal input"""
    # ... (test code)

def test_invalid_title_hard_block():
    """Example 3: Invalid title"""
    # ... (test code)

# ... (and so on)
```

---

## Related Documentation

- **SKILL.md**: Formal specification these examples implement
- **CLAUDE.md**: Decision logic behind these outcomes
- **tests/test_blog_publisher.py**: Pytest implementations of these examples (Phase 4)

---

**Examples Version**: 1.0  
**Status**: ✅ Ready for Implementation (Phase 3)
