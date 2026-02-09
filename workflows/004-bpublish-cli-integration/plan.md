# Phase 5: CLI Integration - `bpublish` Command

**Phase**: 5 of 6  
**Status**: Planning  
**Goal**: Create PowerShell `bpublish` command for one-button blog publishing

---

## Overview

Transform the blog-publisher skill from Python functions to a PowerShell one-liner command.

**Before Phase 5**:
```powershell
# Have to write Python code to publish
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(title='...', excerpt='...', content='...')
result = skill.publish(post)
"
```

**After Phase 5**:
```powershell
# One-liner to publish
bpublish -Title "My Post" -Excerpt "Summary" -Content $content

# Or with file
bpublish -File "path/to/post.md"

# Dry-run preview
bpublish -Title "..." -Excerpt "..." -Content $content -DryRun
```

---

## Deliverables

### 1. PowerShell Wrapper Function

**File**: `scripts/bpublish-function.ps1` (150+ lines)

Function signature:
```powershell
function bpublish {
    param(
        [string]$Title,
        [string]$Excerpt,
        [string]$Content,
        [string]$File,
        [string]$AuthorName = "RoadTrip",
        [string]$AuthorPicture = "",
        [string]$CoverImage = "",
        [string]$OgImage = "",
        [datetime]$Date,
        [switch]$DryRun,
        [switch]$Verbose
    )
    
    # Implementation:
    # 1. Validate parameters
    # 2. Read file if -File provided
    # 3. Call Python skill
    # 4. Return result with formatting
}
```

### 2. PowerShell Profile Integration

**File**: `RoadTrip_profile.ps1` (updated)

Addition:
```powershell
# Load blog publisher command
. "$PSScriptRoot\scripts\bpublish-function.ps1"

# Alias for convenience
Set-Alias -Name bp -Value bpublish -Scope Global
```

### 3. Dry-Run Mode

Preview what would happen without actually pushing to git:
```powershell
bpublish -Title "My Post" -Excerpt "..." -Content $content -DryRun
```

Output:
```
[DRY-RUN] Decision: APPROVE
[DRY-RUN] Filename: 2026-02-09-my-post.md
[DRY-RUN] URL: https://roadtrip-blog-ten.vercel.app/blog/my-post
[DRY-RUN] Would commit: blog: publish My Post (2026-02-09)
[DRY-RUN] Would push to: origin/main
```

### 4. Error Handling & Output

Success output:
```
✅ Blog Post Published
   Filename: 2026-02-09-my-post.md
   URL: https://roadtrip-blog-ten.vercel.app/blog/my-post
   Commit: a1b2c3d4
   Confidence: 0.99
```

Failure output:
```
❌ Publication Failed
   Reason: content too short (45 < 50 chars)
   Decision: REJECT
   Confidence: 1.0
```

### 5. Documentation

**File**: `docs/bpublish_usage.md` (150+ lines)

Contents:
- Quick start guide
- Command syntax reference
- All parameter options
- Example workflows
- Troubleshooting

---

## Implementation Plan

### Step 1: Create PowerShell Wrapper (30 min)
- [ ] Parse parameters (title, excerpt, content, file)
- [ ] Validate required fields
- [ ] Call Python blog_publisher.py
- [ ] Format output (success/failure)
- [ ] Handle errors gracefully

### Step 2: Dry-Run Mode (15 min)
- [ ] Add `-DryRun` parameter
- [ ] Suppress git operations in dry-run
- [ ] Show what would happen
- [ ] Return preview output

### Step 3: Profile Integration (10 min)
- [ ] Load function on profile startup
- [ ] Create `bp` alias
- [ ] Test from fresh terminal

### Step 4: Documentation (20 min)
- [ ] Write usage guide
- [ ] Add examples
- [ ] Document parameters
- [ ] Provide troubleshooting

### Step 5: End-to-End Demo (15 min)
- [ ] Publish test post via `bpublish`
- [ ] Verify it appears on live blog
- [ ] Capture screenshots/logs
- [ ] Document workflow

---

## Test Cases for Phase 5

### Test 5.1: Simple Command
```powershell
bpublish -Title "CLI Test" -Excerpt "Testing the CLI." -Content "This is test content..." 
```
Expected: Post published, URL shown

### Test 5.2: Dry-Run Preview
```powershell
bpublish -Title "Dry Run Test" -Excerpt "..." -Content "..." -DryRun
```
Expected: Preview shown, nothing pushed

### Test 5.3: From File
```powershell
bpublish -File "docs/my-post.md"
```
Expected: Post content read, published

### Test 5.4: Error Handling
```powershell
bpublish -Title "" -Excerpt "..." -Content "..."
```
Expected: Error message, no publication

### Test 5.5: Alias Works
```powershell
bp -Title "Alias Test" -Excerpt "..." -Content "..."
```
Expected: `bp` alias works same as `bpublish`

---

## Technical Details

### Parameter Validation
- Title: required, 1-100 chars
- Excerpt: required, 50-160 chars
- Content: required, >50 chars (from SKILL.md)
- File: reads markdown, validates extracted fields

### Calling Python Skill
```powershell
$result = py -c @"
import json, sys
sys.path.insert(0, '$PSScriptRoot')
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config

config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(title='$Title', excerpt='$Excerpt', content='''$Content''')
result = skill.publish(post)

# Output as JSON for PowerShell to parse
print(json.dumps({
    'decision': result.decision,
    'success': result.success,
    'url': result.url,
    'filename': result.filename,
    'confidence': result.confidence,
    'errors': result.errors
}))
"@
```

### Output Formatting
```powershell
if ($result.decision -eq "APPROVE") {
    Write-Host "✅ Blog Post Published" -ForegroundColor Green
    Write-Host "   URL: $($result.url)" -ForegroundColor Green
} else {
    Write-Host "❌ Publication Failed" -ForegroundColor Red
    foreach ($error in $result.errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
}
```

---

## Integration Points

### With Orchestrator
Once Phase 5 complete, orchestrator can call:
```powershell
bpublish -Title $post.title -Excerpt $post.excerpt -Content $post.content -Verbose
```

### With Git Pushes
Blog publisher already uses git internally (Phase 3), so `bpublish` integrates with RoadTrip's git infrastructure seamlessly.

### With Session Logging
Optional: Log all `bpublish` calls to session log:
```powershell
logt "Blog Publisher"
bpublish -Title "..." -Excerpt "..." -Content "..."
logr
```

---

## Success Criteria

- ✅ `bpublish` command available after profile loads
- ✅ `bp` alias works
- ✅ DryRun mode shows preview without side effects
- ✅ File input works (reads markdown)
- ✅ Error messages clear and actionable
- ✅ Live test: post published via `bpublish` appears on blog
- ✅ All edge cases handled (missing params, invalid content, etc.)

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| 5a | 1 hour | PowerShell wrapper + tests |
| 5b | 30 min | Profile integration + documentation |
| 5c | 30 min | End-to-end demo + cleanup |
| **Total** | **2 hours** | Complete CLI interface |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Python subprocess complexity | Use json output format, parse carefully |
| Parameter escaping issues | Test with special characters early |
| Profile conflicts | Load after user functions, clear namespace |
| File encoding issues | Ensure UTF-8 throughout |

---

## Related Files

- **Prototype**: workflow/001-gpush-skill-set/Phase_1b_Execution_Log.md (similar CLI pattern)
- **Skill**: src/skills/blog_publisher.py (underlying implementation)
- **Config**: config/blog-config.yaml (blog settings)
- **Profile**: RoadTrip_profile.ps1 (integration point)

---

## Phase 6 Preview

After Phase 5 complete:
- Write comprehensive end-to-end workflow test
- Test full orchestrator → blog publisher → published post flow
- Capture metrics (latency, success rate, etc.)
- Document the complete journey
- Clean up for release

---

**Phase 5 Status**: Ready to implement  
**Created**: 2026-02-09  
**Next**: Start with PowerShell wrapper function
