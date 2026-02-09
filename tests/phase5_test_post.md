---
title: Phase 5 CLI Integration Complete
excerpt: Phase 5 demonstrates the blog publisher skill now accessible via a simple PowerShell command-line interface for easy publish.
author: Nicholas Stein
---

# Phase 5 CLI Integration Complete

This blog post demonstrates the Phase 5 implementation where the blog publisher skill is now accessible via a simple PowerShell command-line interface.

## What This Means

Instead of running Python directly, users can now publish blog posts with:

```powershell
bpublish -Title "..." -Excerpt "..." -Content "..."
```

Or using the shorter alias:

```powershell
bp -Title "..." -Excerpt "..." -Content "..."
```

## Testing the CLI

This post was published using the new `bpublish` command from the RoadTrip PowerShell profile. The workflow is:

1. Load RoadTrip profile
2. Call bpublish with post content
3. Function validates, formats, commits, and pushes
4. Vercel automatically deploys
5. Post appears live on the blog

## Key Features

- **Dry-run mode**: Preview without publishing (`-DryRun`)
- **File input**: Read posts from markdown files (`-File`)
- **Validation**: Automatic checks before publication
- **Deterministic**: Same input always produces same output
- **Confidence scoring**: Shows how certain the system is about the decision

## Next Steps

With Phase 5 complete, the blog publisher skill is now fully integrated into the RoadTrip development environment. Users can publish posts with a single command.
