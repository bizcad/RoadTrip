<#
.SYNOPSIS
    Publish a blog post to the RoadTrip blog with one command.

.DESCRIPTION
    The bpublish command provides a one-liner interface to the blog-publisher skill.
    It validates your post, formats it with proper frontmatter, commits it to git,
    pushes to GitHub, and Vercel automatically deploys it live.

.PARAMETER Title
    The blog post title (1-100 characters).

.PARAMETER Excerpt
    A short summary for SEO (50-160 characters).

.PARAMETER Content
    The markdown content of the post (50+ characters).

.PARAMETER File
    Path to a markdown file to publish (alternative to -Content).

.PARAMETER AuthorName
    Name of the author (default: "RoadTrip").

.PARAMETER AuthorPicture
    URL path to author photo (default: "/assets/blog/authors/roadtrip.jpeg").

.PARAMETER CoverImage
    URL path to cover image (default: "/assets/blog/default-cover.jpg").

.PARAMETER OgImage
    URL path to Open Graph image (default: same as CoverImage).

.PARAMETER Date
    Publication date (default: today in UTC).

.PARAMETER DryRun
    Preview the post without publishing (no git operations).

.PARAMETER Verbose
    Show detailed output and logging.

.EXAMPLE
    # Simple post
    bpublish -Title "My Post" -Excerpt "About my post." -Content $content

.EXAMPLE
    # From file
    bpublish -File "docs/my-post.md"

.EXAMPLE
    # Dry-run preview
    bpublish -Title "Test" -Excerpt "..." -Content "..." -DryRun

.EXAMPLE
    # Short alias
    bp -Title "Quick Post" -Excerpt "..." -Content "..."

.NOTES
    Phase 5: CLI Integration for Blog Publisher Skill
    Uses: src/skills/blog_publisher.py (Python implementation)
    Config: config/blog-config.yaml
#>

function bpublish {
    param(
        [Parameter(ParameterSetName="Manual", Mandatory=$false)]
        [string]$Title,
        
        [Parameter(ParameterSetName="Manual", Mandatory=$false)]
        [string]$Excerpt,
        
        [Parameter(ParameterSetName="Manual", Mandatory=$false)]
        [string]$Content,
        
        [Parameter(ParameterSetName="File", Mandatory=$true)]
        [ValidateScript({Test-Path $_})]
        [string]$File,
        
        [string]$AuthorName = "RoadTrip",
        [string]$AuthorPicture = "",
        [string]$CoverImage = "",
        [string]$OgImage = "",
        
        [datetime]$Date,
        [switch]$DryRun
    )

    # Get workspace root
    $workspace = Split-Path (Get-Location) -Leaf
    if ($workspace -ne "RoadTrip") {
        $workspace = Split-Path (Split-Path $PROFILE) -Leaf
    }

    # Determine mode
    $isDryRun = $DryRun.IsPresent
    $isVerbose = $VerbosePreference -eq "Continue"

    # Helper function for output
    function Write-Status {
        param([string]$Message, [string]$Type = "Info")
        $color = switch($Type) {
            "Success" { "Green" }
            "Error" { "Red" }
            "Warning" { "Yellow" }
            "Info" { "Cyan" }
            default { "White" }
        }
        Write-Host $Message -ForegroundColor $color
    }

    try {
        # Step 1: Load input
        Write-Status "Loading input..." "Info"
        
        if ($PSCmdlet.ParameterSetName -eq "File") {
            # Parse markdown file
            $markdown = Get-Content $File -Raw
            $parts = $markdown -split '---'
            
            if ($parts.Count -lt 3) {
                throw "File must contain YAML frontmatter between --- delimiters"
            }
            
            $frontmatter = $parts[1]
            $Content = $parts[2].TrimStart()
            
            # Parse YAML-like frontmatter (simplified)
            $Title = ($frontmatter | Select-String 'title:\s*(.+)').Matches.Groups[1].Value.Trim('"')
            $Excerpt = ($frontmatter | Select-String 'excerpt:\s*(.+)').Matches.Groups[1].Value.Trim('"')
            
            if ($isVerbose) {
                Write-Status "Loaded from file: $File" "Info"
                Write-Status "  Title: $Title" "Info"
                Write-Status "  Excerpt: $Excerpt" "Info"
            }
        }

        # Validate required fields
        if (-not $Title) { throw "Title is required (-Title)" }
        if (-not $Excerpt) { throw "Excerpt is required (-Excerpt)" }
        if (-not $Content) { throw "Content is required (-Content)" }

        if ($isVerbose) {
            Write-Status "Input validation: PASS" "Success"
        }

        # Step 2: Call Python skill
        Write-Status "Publishing blog post..." "Info"

        # Escape content for Python
        $contentEscaped = $Content -replace '`', '``' -replace '"', '\"' -replace "'", "''"
        $titleEscaped = $Title -replace '"', '\"'
        $excerptEscaped = $Excerpt -replace '"', '\"'
        $authorEscaped = $AuthorName -replace '"', '\"'

        # Build Python command
        $pythonScript = @"
import json
import sys
sys.path.insert(0, '.')

from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config

try:
    config = load_config('config/blog-config.yaml')
    skill = BlogPublisherSkill(config)
    
    post = BlogPost(
        title='$titleEscaped',
        excerpt='$excerptEscaped',
        content='''$contentEscaped''',
        author_name='$authorEscaped',
        author_picture='$AuthorPicture',
        coverImage='$CoverImage',
        ogImage='$OgImage'
    )
    
    # In dry-run, validate but don't publish
    if $($isDryRun) or '$(if($isDryRun){"true"}else{"false"})' == 'true':
        result = skill._validate_input(post)
        formatted, filename = skill._format_post(post)
        url = skill._generate_live_url(filename)
        
        output = {
            'decision': result.decision,
            'success': False,
            'filename': filename,
            'url': url,
            'confidence': result.confidence,
            'errors': result.errors,
            'warnings': result.warnings,
            'dry_run': True
        }
    else:
        result = skill.publish(post)
        output = {
            'decision': result.decision,
            'success': result.success,
            'filename': result.filename,
            'url': result.url,
            'commit_hash': result.commit_hash,
            'confidence': result.confidence,
            'errors': result.errors,
            'warnings': result.warnings,
            'dry_run': False
        }
    
    print(json.dumps(output))
except Exception as e:
    print(json.dumps({'error': str(e)}))
"@

        # Run Python
        $result = py -c $pythonScript 2>&1
        
        if ($isVerbose) {
            Write-Status "Python output: $result" "Info"
        }

        # Parse result
        try {
            $resultObj = $result | ConvertFrom-Json
        }
        catch {
            throw "Failed to parse Python output: $result"
        }

        if ($resultObj.error) {
            throw $resultObj.error
        }

        # Step 3: Format and display output
        if ($isDryRun) {
            Write-Host ""
            Write-Status "[DRY-RUN MODE]" "Warning"
            Write-Host ""
        }

        if ($resultObj.decision -eq "APPROVE") {
            Write-Status "✅ Blog Post Published" "Success"
            
            Write-Host ""
            Write-Host "📝 Post Details:"
            Write-Host "   Filename: $($resultObj.filename)" -ForegroundColor Cyan
            Write-Host "   Slug: $(($resultObj.filename -replace '.*-', '') -replace '.md', '')" -ForegroundColor Cyan
            Write-Host "   URL: $($resultObj.url)" -ForegroundColor Cyan
            
            if ($resultObj.commit_hash) {
                Write-Host "   Commit: $($resultObj.commit_hash)" -ForegroundColor Green
            }
            
            Write-Host "   Confidence: $($resultObj.confidence)" -ForegroundColor Green
            Write-Host ""
            
            if ($resultObj.warnings.Count -gt 0) {
                Write-Status "⚠️  Warnings:" "Warning"
                foreach ($warning in $resultObj.warnings) {
                    Write-Host "   - $warning" -ForegroundColor Yellow
                }
                Write-Host ""
            }
            
            if ($isDryRun) {
                Write-Status "DRY-RUN: Post would be published to GitHub and deployed via Vercel" "Info"
            }
        }
        else {
            Write-Status "❌ Publication Failed" "Error"
            Write-Host ""
            Write-Host "Reason:"
            foreach ($errorMsg in $resultObj.errors) {
                Write-Host "  - $errorMsg" -ForegroundColor Red
            }
            Write-Host ""
            Write-Status "Decision: $($resultObj.decision)" "Error"
            Write-Status "Confidence: $($resultObj.confidence)" "Error"
            throw "Publication rejected"
        }

    }
    catch {
        Write-Status "❌ Error: $_" "Error"
        return $false
    }
    
    return $true
}

# Create alias for convenience
Set-Alias -Name bp -Value bpublish -Scope Global -Force
