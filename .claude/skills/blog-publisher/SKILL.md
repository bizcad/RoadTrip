---
name: blog-publisher
version: specs-v1.0
description: Publishes blog posts to the RoadTrip blog with validation and git integration. Use when you need to create and deploy blog content with automatic formatting, excerpt validation (50-160 chars), and push to roadtrip-blog repository.
license: Internal use. RoadTrip project.
---

# Blog Publisher Skill Specification

**Version**: 1.1 (Updated after Phase 2 Prototype)  
**Status**: Specification Corrected Based on Actual Blog Template  

---

## Overview

The **Blog Publisher Skill** enables autonomous publishing of blog posts to the RoadTrip blog. It handles the complete pipeline: validation, formatting, git commit, and push to the blog repository.

**One-Liner**: "Given a blog post (title, excerpt, content, author, coverImage), publish it to roadtrip-blog repo and deploy live to https://roadtrip-blog-ten.vercel.app/"

---

## Input Specification

### BlogPost Dataclass

**Phase 2 Discovery**: Actual blog template requires coverImage and excerpt. Specification updated to match.

```python
@dataclass
class BlogPost:
    """A blog post ready for publishing."""
    
    title: str                          # Required: 1-100 chars
    excerpt: str                        # Required: 50-160 chars (SEO description)
    content: str                        # Required Markdown content (50+ chars)
    author_name: str = "RoadTrip"      # Optional, defaults to "RoadTrip"
    author_picture: str = ""           # Optional, path to author image
    coverImage: str = ""               # Optional, path to cover image
    date: str = ""                     # Optional ISO format, defaults to today
    ogImage: str = ""                  # Optional, Open Graph image path
```

### Input Validation Rules

**Hard Requirements** (Must Pass):
- [ ] `title`: Non-empty, < 100 characters
- [ ] `excerpt`: Non-empty, > 50 characters, < 160 characters
- [ ] `content`: Non-empty, > 50 characters
- [ ] `date`: Valid ISO format (YYYY-MM-DDTHH:mm:ss.000Z) or empty (will use today)
- [ ] Content: No secrets/credentials (uses existing rules-engine validation)
- [ ] Content: Markdown syntax only, no HTML

**Soft Requirements** (Warnings but continues):
- [ ] `author_name`: Defaults to "RoadTrip" if empty
- [ ] `author_picture`: Defaults to placeholder if empty
- [ ] `coverImage`: Defaults to placeholder if empty
- [ ] `ogImage`: Defaults to coverImage if empty

---

## Output Specification

### BlogPublishResult Dataclass

```python
@dataclass
class BlogPublishResult:
    """Result of a blog publish operation."""
    
    decision: str                       # "APPROVE" | "REJECT"
    success: bool                       # True if post went live
    filename: str                       # Generated filename (e.g., "2026-02-09-my-post.md")
    url: str                            # Live URL on blog (e.g., ".../blog/my-post")
    commit_hash: str                    # Git commit hash (first 8 chars)
    git_push_confirmed: bool            # True if push succeeded
    confidence: float                   # 0.0-1.0 (1.0 = certain, 0.95+ = very confident)
    warnings: list[str]                 # Non-blocking issues (empty description, etc.)
    errors: list[str]                   # Blocking errors
    metadata: dict                      # Additional info (build_status, vercel_domain, etc.)
```

---

## Processing Pipeline

### Step 1: Validate Input
- Check title (non-empty, <100 chars)
- Check excerpt (non-empty, 50-160 chars)
- Check content (non-empty, >50 chars)
- Validate date format (ISO or empty)
- Validate no secrets using rules-engine
- Check file size (< 1MB)
- **Decision**: APPROVE or REJECT

### Step 2: Format Post
- Generate slug from title (lowercase, dashes)
- Create filename: `YYYY-MM-DD-{slug}.md`
- Parse date to ISO format with milliseconds (if missing, use today)
- Build frontmatter (YAML block) with actual template format
- Combine frontmatter + content

### Step 3: Prepare Git Commit
- Stage new/modified file in blog repo
- Generate commit message: `blog: publish {title} ({date})`
- Verify git working tree is clean

### Step 4: Push to Blog Repo
- Git push to `bizcad/roadtrip-blog` main branch
- Wait for acknowledgment (git push succeeds)
- Return commit hash

### Step 5: Return Result
- Include live URL (extrapolated from blog domain)
- Set success = True/False based on push result
- Set confidence score
- Include warnings and errors
- Include metadata (build time estimate, etc.)

---

## Configuration (config/blog-config.yaml)

```yaml
blog:
  repo:
    url: "https://github.com/bizcad/roadtrip-blog.git"
    branch: "main"
    local_path: null  # Will be auto-detected vs. fetched if needed
    posts_folder: "_posts"  # Relative path to posts directory
  
  vercel:
    domain: "roadtrip-blog-ten.vercel.app"
    build_check_enabled: false  # Phase 2: enable Vercel API checks
    estimated_build_time_sec: 30  # From Phase 2 observation
  
  git:
    author_name: "RoadTrip Orchestrator"
    author_email: "workflow@roadtrip.local"
    commit_prefix: "blog"
  
  validation:
    min_content_length: 50
    min_excerpt_length: 50
    max_excerpt_length: 160
    max_file_size_mb: 1
    check_for_secrets: true  # Use rules-engine
  
  defaults:
    author_name: "RoadTrip"
    author_picture: "/assets/blog/authors/roadtrip.jpeg"
    coverImage: "/assets/blog/default-cover.jpg"
    timezone: "UTC"
```

---

## Frontmatter Format (Actual Template)

```yaml
---
title: "Post Title Here"
excerpt: "Short description for SEO (50-160 chars)"
coverImage: "/assets/blog/post-slug/cover.jpg"
date: 2026-02-09T13:45:23.456Z
author:
  name: "Author Name"
  picture: "/assets/blog/authors/author.jpeg"
ogImage:
  url: "/assets/blog/post-slug/cover.jpg"
---

# Post Title Here

Markdown content starts here...
```

**Note**: Date must be in ISO 8601 format with milliseconds (YYYY-MM-DDTHH:mm:ss.000Z)

---

## Slug Generation Algorithm

Given title: **"My Cool Blog Post!"**

1. Lowercase: `"my cool blog post!"`
2. Remove punctuation: `"my cool blog post"`
3. Replace spaces with dashes: `"my-cool-blog-post"`
4. Remove consecutive dashes: (no change)
5. Result: `"my-cool-blog-post"`

**Filename**: `2026-02-09-my-cool-blog-post.md`

**Edge Cases**:
- Title with multiple spaces: spaces collapse to single dash
- Title with special chars: `"API/REST!??"` → `"api-rest"`
- Very long title: truncate to 50 chars, trim trailing dashes

---

## Error Handling & Confidence Levels

| Scenario | Decision | Confidence | Notes |
|----------|----------|-----------|-------|
| Valid post, all checks pass | APPROVE | 1.0 | Certain to succeed |
| Valid post, missing cover/author image | APPROVE | 0.99 | Auto-fills with defaults |
| Title too long (>100 chars) | REJECT | 1.0 | Hard block |
| Excerpt too short (<50 chars) | REJECT | 1.0 | Hard block |
| Content too short (<50 chars) | REJECT | 1.0 | Hard block |
| Content has secrets | REJECT | 1.0 | Hard block (rules-engine) |
| Git push fails | REJECT | 0.0 | Failure confirmed |
| Vercel build status unknown | APPROVE | 0.85 | Post committed; build TBD |
| Missing config | REJECT | 1.0 | Conservative default |

---

## Integration Points

### Dependency: Rules-Engine Skill
- Input: file content
- Output: APPROVE/BLOCK decision with confidence
- Usage: `evaluate_content(content)` checks for secrets

### Dependency: Auth-Validator Skill (Phase 1b)
- Input: git repo, target branch
- Output: Permission check result
- Usage: Verify we can push before attempting

### Dependency: Telemetry-Logger Skill (Phase 1b)
- Input: BlogPublishResult
- Output: JSONL log entry
- Usage: Record all publishing decisions for auditing

---

## Success Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Publish time | < 10 seconds | (excluding Vercel build) |
| Validation accuracy | 100% of Phase 1 rules | No false approvals of secrets |
| Confidence scores | Calibrated per scenario | See error handling table above |
| Git operations | 100% idempotent | Re-running with same input = no-op |
| Test coverage | 100% | All decision paths covered |

---

**Status**: Phase 1b Specification Complete ✅
