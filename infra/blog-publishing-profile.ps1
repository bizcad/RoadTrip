# ============================================================================
# Blog Publishing Profile - Blog Management
# ============================================================================
# Blog publishing functions and aliases
# Part of CODING and CONTENT modes
# ============================================================================

$ProjectRoot = if ($ProjectRoot) { $ProjectRoot } else { (Get-Item .).FullName }

# ============================================================================
# Load bpublish Function
# ============================================================================

$bpublishPath = Join-Path $ProjectRoot "scripts\bpublish-function.ps1"
if (Test-Path $bpublishPath) {
    . $bpublishPath
    Set-Alias -Name bp -Value bpublish -Force
    Write-Host "✓ Blog publishing loaded (bpublish, bp)" -ForegroundColor Green
} else {
    # Fallback: Create a placeholder function
    function bpublish {
        Write-Host "📝 Blog publish function" -ForegroundColor Cyan
        Write-Host "Script location expected: $bpublishPath" -ForegroundColor Gray
        Write-Host ""
        Write-Host "To implement blog publishing:" -ForegroundColor Yellow
        Write-Host "1. Create: scripts\bpublish-function.ps1" -ForegroundColor Gray
        Write-Host "2. Define: function bpublish { ... }" -ForegroundColor Gray
        Write-Host "3. Sync drafted posts to Vercel" -ForegroundColor Gray
    }
    
    Set-Alias -Name bp -Value bpublish -Force
    Write-Host "⚠️  Blog publishing placeholder loaded (bpublish not fully configured)" -ForegroundColor Yellow
}

# ============================================================================
# Blog Management Functions
# ============================================================================

function blog-list {
    <#
    .SYNOPSIS
    List all blog posts (published and drafts)
    #>
    $blogDir = Join-Path $ProjectRoot "docs"
    
    if (Test-Path $blogDir) {
        Write-Host "📚 Blog Posts:" -ForegroundColor Cyan
        Get-ChildItem $blogDir -Filter "*.md" -Recurse | 
        ForEach-Object {
            Write-Host "  • $($_.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "Blog directory not found: $blogDir" -ForegroundColor Yellow
    }
}

function blog-draft-list {
    <#
    .SYNOPSIS
    List draft blog posts
    #>
    Write-Host "📝 Blog Drafts:" -ForegroundColor Cyan
    Get-ChildItem (Join-Path $ProjectRoot "docs\blog_*.md") -ErrorAction SilentlyContinue | 
    ForEach-Object { Write-Host "  • $($_.Name)" -ForegroundColor Yellow }
}

function blog-published-list {
    <#
    .SYNOPSIS
    List published blog posts
    #>
    Write-Host "📤 Published Posts:" -ForegroundColor Cyan
    Get-ChildItem (Join-Path $ProjectRoot "docs") -Filter "*.md" -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -notmatch "^blog_" } |
    ForEach-Object { Write-Host "  • $($_.Name)" -ForegroundColor Green }
}

function blog-stats {
    <#
    .SYNOPSIS
    Show blog statistics
    #>
    $blogDir = Join-Path $ProjectRoot "docs"
    
    if (Test-Path $blogDir) {
        $allPosts = Get-ChildItem $blogDir -Filter "*.md" -Recurse
        $draftCount = ($allPosts | Where-Object { $_.Name -match "^blog_" }).Count
        $publishedCount = $allPosts.Count - $draftCount
        
        Write-Host "📊 Blog Statistics:" -ForegroundColor Cyan
        Write-Host "  Total Posts:    $($allPosts.Count)" -ForegroundColor Green
        Write-Host "  Published:      $publishedCount" -ForegroundColor Green
        Write-Host "  Drafts:         $draftCount" -ForegroundColor Yellow
    }
}

Set-Alias -Name blog-list -Value blog-list -Force
Set-Alias -Name bl -Value blog-list -Force

Write-Host "✓ Blog publishing profile loaded" -ForegroundColor Green
