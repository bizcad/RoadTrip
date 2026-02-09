# bpublish Command - Usage Guide

**Phase 5: CLI Integration**  
**Status**: Ready to use  
**Shortcut**: `bp`

---

## Quick Start

After loading the RoadTrip profile, you have the `bpublish` command available:

```powershell
# Simple publish
bpublish -Title "My Blog Post" -Excerpt "A short summary." -Content $content

# Or use the alias
bp -Title "..." -Excerpt "..." -Content $content

# Preview without publishing
bpublish -Title "..." -Excerpt "..." -Content $content -DryRun
```

---

## Command Syntax

### Basic
```powershell
bpublish -Title "Title" -Excerpt "Summary" -Content $content
```

### With All Options
```powershell
bpublish `
  -Title "Post Title" `
  -Excerpt "SEO summary" `
  -Content $content `
  -AuthorName "Nicholas Stein" `
  -AuthorPicture "/assets/blog/authors/ns.jpg" `
  -CoverImage "/assets/blog/cover.jpg" `
  -OgImage "/assets/blog/og.jpg" `
  -Date (Get-Date) `
  -DryRun `
  -Verbose
```

### From a File
```powershell
bpublish -File "path/to/post.md"
```

---

## Parameters

| Parameter | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `Title` | string | Yes* | — | 1-100 characters |
| `Excerpt` | string | Yes* | — | 50-160 characters (SEO) |
| `Content` | string | Yes* | — | 50+ characters, Markdown |
| `File` | string | Yes** | — | Path to .md file (alternative) |
| `AuthorName` | string | No | "RoadTrip" | Post author name |
| `AuthorPicture` | string | No | default | URL path to author image |
| `CoverImage` | string | No | default | URL path to cover image |
| `OgImage` | string | No | CoverImage | Open Graph image |
| `Date` | datetime | No | Today | Publication date (UTC) |
| `DryRun` | switch | No | — | Preview without publishing |
| `Verbose` | switch | No | — | Show detailed output |

*Use either `-Title/-Excerpt/-Content` OR `-File` (not both)

---

## Examples

### Example 1: Simple Post
```powershell
$content = @"
# My First Post

This is my first blog post using the one-liner interface.

## Key Points

- Easy to publish
- Deterministic validation
- Automatic deployment

More content here...
"@

bpublish `
  -Title "My First Post" `
  -Excerpt "Publishing my first blog post with the new CLI tool." `
  -Content $content
```

**Output**:
```
Loading input...
Publishing blog post...
✅ Blog Post Published

📝 Post Details:
   Filename: 2026-02-09-my-first-post.md
   Slug: my-first-post
   URL: https://roadtrip-blog-ten.vercel.app/blog/my-first-post
   Commit: a1b2c3d4
   Confidence: 1.0
```

### Example 2: Dry-Run Preview
```powershell
bpublish `
  -Title "Test Post" `
  -Excerpt "This is just a preview, nothing will be published." `
  -Content "Content here..." `
  -DryRun
```

**Output**:
```
[DRY-RUN MODE]
✅ Blog Post Published

📝 Post Details:
   Filename: 2026-02-09-test-post.md
   URL: https://roadtrip-blog-ten.vercel.app/blog/test-post
   
DRY-RUN: Post would be published to GitHub and deployed via Vercel
```

### Example 3: From File
Create `docs/my-post.md`:
```markdown
---
title: "Post from File"
excerpt: "This post is loaded from a markdown file."
---

# Content

This approach works when your post already exists as a file.
```

Then publish:
```powershell
bpublish -File "docs/my-post.md"
```

### Example 4: Using the Alias
```powershell
bp -Title "Quick Post" -Excerpt "Using the bp alias for speed." -Content $myContent
```

### Example 5: Verbose Output
```powershell
bpublish `
  -Title "Debug Test" `
  -Excerpt "Learning how verbose mode works." `
  -Content "Content..." `
  -Verbose
```

---

## Validation Rules

The command validates your post before publishing. Common failures:

### ❌ Empty Title
```powershell
bpublish -Title "" -Excerpt "..." -Content "..."
```
**Error**: `Title is required (-Title)`

### ❌ Title Too Long (>100 chars)
```powershell
bpublish -Title ("x" * 101) -Excerpt "..." -Content "..."
```
**Error**: `title too long (101 > 100 chars)`

### ❌ Excerpt Too Short (<50 chars)
```powershell
bpublish -Title "Valid" -Excerpt "Short" -Content "Valid content..."
```
**Error**: `excerpt too short (5 < 50 chars)`

### ❌ Content Too Short (<50 chars)
```powershell
bpublish -Title "Valid" -Excerpt "Valid excerpt here." -Content "Short"
```
**Error**: `content too short (5 < 50 chars)`

### ❌ Secrets Detected
```powershell
bpublish -Title "API Guide" -Excerpt "..." -Content "API_KEY=secret123..."
```
**Error**: `secrets detected in content`

---

## Output Explained

### Success Case
```
✅ Blog Post Published

📝 Post Details:
   Filename: 2026-02-09-orchestrator-patterns.md
   Slug: orchestrator-patterns
   URL: https://roadtrip-blog-ten.vercel.app/blog/orchestrator-patterns
   Commit: 5a6b7c8d
   Confidence: 1.0
```

**What this means**:
- ✅ Post is now live on the blog
- 📝 Markdown file created in blog repo's `_posts/` folder
- URL is accessible immediately (Vercel usually deploys within 30 seconds)
- Commit hash shows the git commit that was pushed
- Confidence 1.0 = certainty (all validations passed)

### Failure Case
```
❌ Publication Failed

Reason:
  - excerpt must be 50-160 characters (got 42)

Decision: REJECT
Confidence: 1.0
```

**What this means**:
- ❌ Post was not published
- Reason clearly states what was wrong
- Decision: REJECT (hard block, post was not safe to publish)
- Confidence 1.0 = certain this is an error (not probabilistic)

---

## Workflow Examples

### Scenario 1: Quick Blog Post
```powershell
$content = @"
# Quick Thoughts on Agents

Today I learned about deterministic agents...

[Full content]
"@

bpublish `
  -Title "Quick Thoughts on Agents" `
  -Excerpt "Reflecting on deterministic agent patterns and their impact." `
  -Content $content
```

### Scenario 2: Republish with Different Author
```powershell
bpublish `
  -File "docs/post.md" `
  -AuthorName "Guest Author" `
  -AuthorPicture "/assets/blog/authors/guest.jpg"
```

### Scenario 3: Testing Before Publishing
```powershell
# Test dry-run first
bpublish -Title "..." -Excerpt "..." -Content $content -DryRun

# If preview looks good, publish without -DryRun
bpublish -Title "..." -Excerpt "..." -Content $content
```

### Scenario 4: Batch Publishing (via Loop)
```powershell
$posts = @(
    @{Title="Post 1"; Excerpt="..."; Content="..."},
    @{Title="Post 2"; Excerpt="..."; Content="..."}
)

foreach ($post in $posts) {
    bpublish -Title $post.Title -Excerpt $post.Excerpt -Content $post.Content
    Start-Sleep -Seconds 5  # Wait between posts
}
```

---

## Troubleshooting

### "py not found" or "python not found"
Use `py` instead of `python` (Windows Python launcher):
```powershell
# This works:
py --version

# If bpublish complains about python:
# Edit scripts/bpublish-function.ps1 and replace 'python' with 'py'
```

### "No module named 'src'"
Make sure you're running from the RoadTrip repo root:
```powershell
cd G:\repos\AI\RoadTrip
bpublish -Title "..." -Excerpt "..." -Content $content
```

### "Config file not found"
The `config/blog-config.yaml` file is missing. Make sure you're at the workspace root:
```powershell
Get-ChildItem config/
# Should show: blog-config.yaml
```

### PyYAML Import Error
Install PyYAML:
```powershell
py -m pip install pyyaml
```

### Git Auth Fails
The blog poet requires git credentials. Make sure git is configured:
```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## Advanced Usage

### Suppressing Output
```powershell
$result = bpublish -Title "..." -Excerpt "..." -Content $content
if ($result -eq $false) {
    Write-Host "Publication failed"
}
```

### Integration with Scripts
```powershell
function publish-daily-update {
    $content = (Get-ChildItem -Filter "daily-*.md" -Newest 1).FullName
    bpublish -File $content -Verbose
}

# Or in a scheduled task
#$trigger = New-ScheduledTaskTrigger -Daily -At 8am
#Register-ScheduledTask -TaskName "PublishDailyPost" -Action $action -Trigger $trigger
```

### One-Liner Publishing
```powershell
$c = Get-Content "docs/post.md" -Raw; bpublish -File "docs/post.md"
```

---

## How It Works (Under the Hood)

1. **Input** → Parse title, excerpt, content
2. **Validate** → Check requirements (length, secrets, format)
3. **Format** → Generate YAML frontmatter, create filename
4. **Commit** → Stage file, create git commit
5. **Push** → Push to GitHub (triggers Vercel)
6. **Return** → Both URL and status

All done in seconds. Vercel deploys live within 30 seconds.

---

## System Requirements

- PowerShell 5.0+ (or PowerShell Core 6+)
- Python 3.10+ (py launcher)
- PyYAML: `py -m pip install pyyaml`
- Git configured with credentials
- RoadTrip workspace cloned locally

---

## Related Commands

```powershell
# Publish blog post
bpublish -Title "..." -Excerpt "..." -Content $content

# Quick alias
bp -Title "..." -Excerpt "..." -Content $content

# Dry-run preview
bpublish -Title "..." -Excerpt "..." -Content $content -DryRun

# From file
bpublish -File "path/to/post.md"

# Git push (Phase 1b)
gpush "message"

# Log session activity
logt "Blog published"; logr
```

---

## Frequently Asked Questions

**Q: Can I edit a post after publishing?**  
A: Edit the .md file in the blog repo, commit, and push. Vercel redeploys automatically.

**Q: How long until posts go live?**  
A: Usually 30 seconds. Check the blog at https://roadtrip-blog-ten.vercel.app/

**Q: Can I schedule post publication?**  
A: Not yet. But you can use PowerShell scheduled tasks + `bpublish`.

**Q: What's in the frontmatter?**  
A: Title, excerpt, author, dates, cover/og images in YAML format.

**Q: Can I use HTML?**  
A: No. Markdown only for security. Use Markdown syntax for formatting.

---

**Documentation**: Phase 5 CLI Integration  
**Last Updated**: 2026-02-09  
**Status**: Ready for use
