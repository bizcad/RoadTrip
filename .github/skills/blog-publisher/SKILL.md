---
name: blog-publisher
version: specs-v1.0
description: Publishes blog posts to the RoadTrip blog with validation and git integration. Use when you need to create and deploy blog content with automatic formatting, excerpt validation (50-160 chars), and push to roadtrip-blog repository.
license: Internal use. RoadTrip project.
---

# Blog Publisher Skill

## Overview

Enables autonomous publishing of blog posts to the RoadTrip blog. Handles the complete pipeline: validation, formatting, git commit, and push to the blog repository.

**One-Liner**: "Given a blog post (title, excerpt, content), publish it and deploy live to https://roadtrip-blog-ten.vercel.app/"

## Input Requirements

```python
@dataclass
class BlogPost:
    title: str          # Required: 1-100 chars
    excerpt: str        # Required: 50-160 chars (SEO)
    content: str        # Required Markdown (50+ chars)
    author_name: str    # Optional, defaults to "RoadTrip"
    coverImage: str     # Optional path
    date: str           # Optional ISO format
```

## Output

```python
@dataclass
class BlogPublishResult:
    decision: str       # "APPROVE" | "REJECT"
    success: bool       # True if posted
    filename: str       # Generated filename
    url: str            # Live URL
    commit_hash: str    # Git commit hash
    confidence: float   # 0.0-1.0
    errors: list[str]   # Blocking errors
```

## Processing Pipeline

1. **Validate Input** - Check title (<100), excerpt (50-160), content (>50)
2. **Check for Secrets** - Use rules-engine validation
3. **Format Post** - Generate slug and frontmatter
4. **Prepare Commit** - Stage file and auto-generate message
5. **Push to Blog Repo** - Git push to roadtrip-blog
6. **Return Result** - Include live URL and status

## Error Handling

| Scenario | Decision | Confidence |
|----------|----------|-----------|
| Valid post, all checks pass | APPROVE | 1.0 |
| Title too long (>100) | REJECT | 1.0 |
| Excerpt too short (<50) | REJECT | 1.0 |
| Excerpt too long (>160) | REJECT | 1.0 |
| Content has secrets | REJECT | 1.0 |
| Git push fails | REJECT | 0.0 |

---

**Status**: Phase 1b Specification Complete
