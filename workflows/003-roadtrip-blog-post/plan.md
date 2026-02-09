# Workflow 003: RoadTrip Blog Post Publisher

**Created**: 2026-02-09  
**Status**: Planning Phase (Spec Development)  
**Plan Version**: 1.0  
**Priority**: High — Demonstrates skill orchestration on real, visible outcome

---

## Overview

Build an **blog post publisher skill** that enables autonomous publishing of blog posts to the RoadTrip blog. This workflow proves that the RoadTrip skill framework can:

1. ✅ Integrate with external services (Vercel-hosted blog)
2. ✅ Publish real content to a live endpoint
3. ✅ Orchestrate multi-step workflows (validate → format → commit → push → deploy)
4. ✅ Use a one-button interface similar to `gpush`

**Success Metric**: A single command publishes a blog post from the RoadTrip workspace to https://roadtrip-blog-ten.vercel.app/ and the post appears live.

---

## Project Context

### Blog Infrastructure (In Place)
- **Repo**: `bizcad/roadtrip-blog` (private on GitHub)
- **Hosted at**: https://roadtrip-blog-ten.vercel.app/
- **Tech Stack**: Next.js + Markdown (blog-starter-kit template)
- **Post Format**: Markdown files in `/posts` folder with frontmatter
- **Auto-Deploy**: Vercel watches GitHub repo; every push triggers rebuild

### Existing RoadTrip Skill Architecture (Phase 1a Complete)
- **Location**: `src/skills/` (Python modules)
- **Framework**: Deterministic code + config-driven rules
- **Phase 1a**: `rules_engine.py` (file validation) ✅ Complete
- **Phase 1b**: `auth_validator.py`, `telemetry_logger.py`, `commit_message.py` (status: planned)
- **Patterns**: Models → Config → Implementation → Tests

### Related Workflows
- **001-gpush-skill-set**: Git push automation (reference for orchestrator pattern)
- **002-principles-review**: Framework principles (reference for SOLID compliance)

---

## Strategic Goals

1. **Proof of Concept**: Demonstrate skills can publish to external systems
2. **One-Button Publishing**: `bpublish` command (like `gpush`) that handles full pipeline
3. **Process Documentation**: This workflow document becomes a learning artifact for future skill development
4. **Reusable Pattern**: Blog publisher pattern becomes template for other external integrations (social media, docs portals, etc.)

---

## Workflow: Prototype → Code

### Phase 1: Specification & Planning (This Document)

**Deliverables**:
- [ ] Blog post specification (SKILL.md)
- [ ] Decision logic documentation (CLAUDE.md)
- [ ] CLI interface specification
- [ ] Configuration schema
- [ ] Example posts and test cases

**Key Questions**:
- Should the skill read from RoadTrip docs or accept content as input?
- What frontmatter fields are required? (title, date, author, tags, etc.)
- Should the skill handle slug generation?
- What git commit message format should be used?

### Phase 2: Prototype & Dry-Run

**No production code yet.** Instead:
- Write example blog posts in plain Markdown
- Run manual `git add` → `git commit` → `git push` to the blog repo
- Verify Vercel picks up the change and deploys
- Document the manual steps so they can be automated

**Deliverables**:
- [ ] 2-3 example posts pushed to blog repo
- [ ] Vercel builds complete and posts go live
- [ ] Manual process documented step-by-step
- [ ] Output: test plan for the skill

### Phase 3: Code Orchestrator & Skills

Using the manual prototype, build:
- `blog_post_models.py` - Dataclasses for blog posts, validation results
- `blog_publisher.py` - Main skill that orchestrates the pipeline
- Configuration: `config/blog-config.yaml`

**Skill Pipeline**:
```
Input: BlogPost(title, content, tags, author)
  ↓
Step 1: Validate - Check frontmatter, title, content
  ↓
Step 2: Format - Generate slug, create filename with date, add frontmatter
  ↓
Step 3: Commit - Git add, commit with message "blog: publish {title}"
  ↓
Step 4: Push - Git push to blog repo
  ↓
Output: BlogPublishResult(success, url, commit_hash, vercel_status)
```

**Deliverables**:
- [ ] src/skills/blog_publisher.py (main skill)
- [ ] ConfigBlog parsed from config/blog-config.yaml
- [ ] Full type hints, docstrings, error handling
- [ ] All SOLID principles verified

### Phase 4: Testing & Validation

**Unit Tests** (before integration):
- Validate BlogPost dataclass creation
- Test slug generation
- Test frontmatter formatting
- Test commit message generation

**Integration Tests**:
- Create temporary git repo
- Run full pipeline (format → commit → push)
- Verify files created correctly
- Verify git history looks good

**End-to-End Tests**:
- Actually push to blog repo
- Wait for Vercel build
- Verify post appears on live site
- Clean up test post

**Deliverables**:
- [ ] tests/test_blog_publisher.py (minimum 20 tests)
- [ ] Test fixtures (sample posts, temp repos, mock Vercel)
- [ ] All tests passing
- [ ] 100% coverage of Phase 1 logic

### Phase 5: CLI & One-Button Interface

Create PowerShell command `bpublish` (like `gpush`):
```powershell
bpublish "My Blog Post Title"       # Read from ./posts/My_Blog_Post_Title.md
bpublish -DryRun                    # Show what would be posted
bpublish -File "custom_path.md"     # Use specific file
```

**Deliverables**:
- [ ] PowerShell function in infra/RoadTrip_profile.ps1
- [ ] Help text and examples
- [ ] Integration with blog_publisher skill
- [ ] Error handling and logging

### Phase 6: End-to-End Demonstration

**Proof of Concept Task**:
1. Write blog post: "Orchestrator Architecture Proven" (or similar)
2. Run `bpublish "Orchestrator Architecture Proven"`
3. Monitor as it:
   - Formats and validates the post
   - Commits to blog repo
   - Vercel sees the push
   - Build completes
   - Post appears live at roadtrip-blog-ten.vercel.app/blog/orchestrator-architecture-proven

**Deliverables**:
- [ ] Session log documenting the complete flow
- [ ] Screenshots of blog post going live
- [ ] Confirmation that orchestration works end-to-end

---

## Technical Specification

### Blog Post Format

**Directory**: `blog-repo/posts/` (on the roadtrip-blog repo)  
**Filename**: `YYYY-MM-DD-{slug}.md`  
**Example**: `2026-02-09-orchestrator-architecture-proven.md`

**Frontmatter** (YAML):
```yaml
---
title: "Orchestrator Architecture Proven"
date: 2026-02-09
author: "Nicholas Stein"
tags: ["orchestrator", "agents", "automation"]
description: "How the RoadTrip orchestrator proved that autonomous agents can handle multi-step workflows."
---

# Orchestrator Architecture Proven

Blog post content here...
```

### Slug Generation Rules

- Title: "My Cool Blog Post!"
- Slug: `my-cool-blog-post` (lowercase, no special chars, dashes for spaces)
- Filename: `2026-02-09-my-cool-blog-post.md`

### Validation Rules

**Required fields**:
- [ ] Title (non-empty, < 100 chars)
- [ ] Content (non-empty, > 50 chars)
- [ ] Date (defaults to today if not provided)

**Optional fields**:
- [ ] Author (defaults to "RoadTrip Workflow")
- [ ] Tags (defaults to ["blog"])
- [ ] Description (defaults to first 160 chars)

**Content checks**:
- [ ] No secrets (.env, API keys, credentials)
- [ ] No HTML (Markdown only)
- [ ] No excessive file size (< 1MB)

### Git Commit Strategy

**Commit pattern**: `blog: publish {title} (date)`

**Example**:
```
blog: publish Orchestrator Architecture Proven (2026-02-09)
```

**Why**: Follows Conventional Commits pattern; enables automated changelogs.

### Error Handling

**Hard blocks** (operations fail):
- [ ] Title is empty
- [ ] Content has secrets
- [ ] Git push fails

**Warnings** (operations continue):
- [ ] Description field empty (auto-generated)
- [ ] Tags field empty (defaults to ["blog"])

**Recoverable errors** (retry):
- [ ] Network timeout on `git push`
- [ ] Vercel build failure (not skill's responsibility, but log it)

---

## File Structure (Deliverables)

```
RoadTrip/
├── workflows/003-roadtrip-blog-post/
│   ├── plan.md                          # This document (living artifact)
│   ├── prototype-log.md                 # Manual steps + observations (Phase 2)
│   ├── code-review-checklist.md         # Quality review before merge (Phase 3)
│   └── test-report.md                   # Test results & coverage (Phase 4)
│
├── skills/blog-publisher/
│   ├── SKILL.md                         # Interface spec
│   ├── CLAUDE.md                        # Decision logic
│   └── examples.md                      # Usage examples
│
├── src/skills/
│   └── blog_publisher.py                # Main implementation (Phase 3)
│
├── tests/
│   └── test_blog_publisher.py           # Test suite (Phase 4)
│
├── config/
│   └── blog-config.yaml                 # Configuration (Phase 3)
│
├── infra/                               # (Update existing)
│   └── RoadTrip_profile.ps1             # Add bpublish command (Phase 5)
│
└── PromptTracking/
    └── Session Log 20260209.md          # Update with blog publisher work
```

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| **Specification** | SKILL.md + CLAUDE.md complete | ⏳ Phase 1 |
| **Prototype** | 2 posts live on blog | ⏳ Phase 2 |
| **Code** | blog_publisher.py + tests passing | ⏳ Phase 3-4 |
| **CLI** | `bpublish` command working | ⏳ Phase 5 |
| **E2E Test** | Full flow demonstrated | ⏳ Phase 6 |
| **Documentation** | This plan + all phases logged | ⏳ Ongoing |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Blog repo is private; permissions needed | Can't push | Use existing PAT token from ProjectSecrets/ |
| Vercel build fails | Post doesn't appear live | Monitor build status; add explicit wait in skill |
| Slug collision (same title, different date) | Overwrites post | Add version suffix logic if needed |
| Large posts (> 1MB) | Upload fails | Add file size validation in Phase 1 |
| Date parsing issues | Incorrect filename | Use ISO format (YYYY-MM-DD) throughout |

---

## Dependencies & Prerequisites

- ✅ Git & GitHub access (existing via PAT token in ProjectSecrets/)
- ✅ Python 3.10+ (already in use for rules_engine)
- ✅ PyYAML for config parsing (already a dependency)
- ✅ Vercel deployment (blog repo already live)
- ✅ Blog starter kit template (already deployed)

---

## Recommendations for This Session

**Start with Phase 1 & 2** (Specification + Prototype):

1. Create `skills/blog-publisher/SKILL.md` - interface spec
2. Create `skills/blog-publisher/CLAUDE.md` - decision logic
3. Manually create 2-3 test posts, push to blog repo
4. Verify posts appear live at roadtrip-blog-ten.vercel.app/
5. Document the manual process in prototype-log.md

**Defer to next session**: Phases 3-6 (code, tests, CLI, end-to-end)

**Why**:
- Validates the concept works before building code
- Catches any git/Vercel issues early
- Gives us real examples to code against
- Keeps this session focused on process documentation

---

## Version Alignment

**This Workflow Version**: 1.0 (Planning complete)  
**RoadTrip Skills Framework**: v1.1 (Principles-and-Processes.md)  
**Phase Target**: Phase 1 (Proof of Concept)  
**Next Review**: After Phase 2 prototype (recommend: same session)

---

## Notes

This plan will evolve as we move through phases. After each phase completion, update this document with:
- [ ] What was actually built
- [ ] What we learned
- [ ] Adjustments to future phases
- [ ] Time spent for planning accuracy on future projects

---

**Created by**: Claude (Copilot)  
**Last Updated**: 2026-02-09 12:11:58  
**Status**: ✅ Ready for Phase 1 (Spec Development)
