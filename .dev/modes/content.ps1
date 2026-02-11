# ============================================================================
# CONTENT MODE - Writing & Publishing
# ============================================================================
# Optimized for writing blog posts, documentation, and creative content
# - Model: Claude 3 Opus (better for long-form, nuanced writing)
# - Skills: Blog publishing, documentation generation
# - Focus: Writing quality, publishing workflows

$script:ProjectDefaultModel = "claude-3-opus"
$script:ImageModel = "dall-e-3"

# Load content-focused profiles
. (Join-Path $ProjectRoot "infra\blog-publishing-profile.ps1")

# ============================================================================
# Content Mode Aliases
# ============================================================================

function draft-blog {
    param([string]$Title)
    
    if (-not $Title) {
        Write-Host "Usage: draft-blog 'Your Blog Title'" -ForegroundColor Yellow
        return
    }
    
    # Convert title to filename (kebab-case)
    $filename = $Title -replace '[^a-zA-Z0-9]', '-' -replace '-+', '-' | 
                ForEach-Object { $_.Trim('-').ToLower() }
    
    $blogPath = Join-Path $ProjectRoot "docs\blog_$filename.md"
    
    # Create draft template
    $template = @"
# $Title

**Date:** $(Get-Date -Format 'MMMM dd, yyyy')
**Status:** Draft

## Overview

<!-- Add your overview here -->

## Key Points

<!-- Add key sections here -->

## Conclusion

<!-- Add conclusion here -->

---

*Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*
"@

    $template | Set-Content $blogPath -Encoding UTF8
    Write-Host "✅ Created draft: $blogPath" -ForegroundColor Green
    Get-Item $blogPath | Select-Object FullName
}

function list-drafts {
    Write-Host "📝 Blog Drafts:" -ForegroundColor Cyan
    Get-ChildItem (Join-Path $ProjectRoot "docs\blog_*.md") -ErrorAction SilentlyContinue | 
    ForEach-Object { Write-Host "  • $($_.Name)" -ForegroundColor Green }
}

function show-content-help {
    Write-Host "📝 CONTENT MODE - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "BLOG MANAGEMENT:" -ForegroundColor Yellow
    Write-Host "  draft-blog 'Title'    # Create new blog draft" -ForegroundColor Gray
    Write-Host "  list-drafts           # List all drafts" -ForegroundColor Gray
    Write-Host "  bpublish (bp)         # Publish blog post" -ForegroundColor Gray
    Write-Host "  publish-blog          # Wrapper for bpublish" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NAVIGATION:" -ForegroundColor Yellow
    Write-Host "  cdp                   # Go to project root" -ForegroundColor Gray
    Write-Host "  cd-prompts            # Go to PromptTracking" -ForegroundColor Gray
    Write-Host ""
    Write-Host "AI CONTEXT:" -ForegroundColor Yellow
    Write-Host "  Model: $script:ProjectDefaultModel (optimized for long-form)" -ForegroundColor Green
    Write-Host "  Image: $script:ImageModel (for illustrations)" -ForegroundColor Green
    Write-Host ""
    Write-Host "SWITCHING:" -ForegroundColor Yellow
    Write-Host "  use-mode coding       # Switch to coding mode" -ForegroundColor Gray
    Write-Host "  use-mode testing      # Switch to testing mode" -ForegroundColor Gray
    Write-Host ""
}

function publish-blog {
    Write-Host "📤 Publishing blog..." -ForegroundColor Yellow
    # This will call the existing bpublish function
    if (Get-Command bp -ErrorAction SilentlyContinue) {
        bp
    } elseif (Get-Command bpublish -ErrorAction SilentlyContinue) {
        bpublish
    } else {
        Write-Host "❌ Blog publishing function not found" -ForegroundColor Red
    }
}

# ============================================================================
# Mode Startup
# ============================================================================

Write-Host ""
Write-Host "📝 CONTENT MODE ACTIVATED" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  Model:    $script:ProjectDefaultModel (long-form optimized)" -ForegroundColor Green
Write-Host "  Image:    $script:ImageModel" -ForegroundColor Green
Write-Host "  Focus:    Blog posts, documentation, creative writing" -ForegroundColor Green
Write-Host "  Commands: draft-blog, list-drafts, bpublish" -ForegroundColor Green
Write-Host "  Help:     show-content-help" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
