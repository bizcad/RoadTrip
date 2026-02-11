# ============================================================================
# Skills Registry - Python Skills Discovery & Management
# ============================================================================
# Registers and manages Python-based skills for the RoadTrip AI agents
# Part of CODING mode
# ============================================================================

$ProjectRoot = if ($ProjectRoot) { $ProjectRoot } else { (Get-Item .).FullName }

# ============================================================================
# Python Path Configuration
# ============================================================================

# Add skills to PYTHONPATH for Python imports
$skillsPaths = @(
    "$ProjectRoot\src",
    "$ProjectRoot\src\skills",
    "$ProjectRoot"
)

foreach ($path in $skillsPaths) {
    if ($env:PYTHONPATH -notlike "*$path*") {
        $env:PYTHONPATH = "$path;$env:PYTHONPATH"
    }
}

# ============================================================================
# Skills Registry
# ============================================================================

$script:AvailableSkills = @{
    "commit-message" = @{
        Path = "$ProjectRoot\src\skills\commit_message.py"
        Class = "CommitMessageSkill"
        Description = "Generate semantic commit messages using AI"
        Status = "Implemented"
    }
    "blog-publish" = @{
        Path = "$ProjectRoot\src\skills\blog_publisher.py"
        Class = "BlogPublisherSkill"
        Description = "Publish blog posts to Vercel"
        Status = "Implemented"
    }
    "session-log" = @{
        Path = "$ProjectRoot\src\skills\session_logger.py"
        Class = "SessionLoggerSkill"
        Description = "Log development sessions and prompts"
        Status = "Implemented"
    }
}

# ============================================================================
# Skills Management Functions
# ============================================================================

function list-skills {
    <#
    .SYNOPSIS
    List all available skills
    #>
    Write-Host "📚 Available Skills:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($name in $script:AvailableSkills.Keys | Sort-Object) {
        $skill = $script:AvailableSkills[$name]
        $statusColor = if ($skill.Status -eq "Implemented") { "Green" } else { "Yellow" }
        
        Write-Host "  ◆ $name" -ForegroundColor Green
        Write-Host "    Class:       $($skill.Class)" -ForegroundColor Gray
        Write-Host "    Description: $($skill.Description)" -ForegroundColor Gray
        Write-Host "    Status:      $($skill.Status)" -ForegroundColor $statusColor
        Write-Host "    Path:        $($skill.Path)" -ForegroundColor Gray
        Write-Host ""
    }
}

function get-skill {
    <#
    .SYNOPSIS
    Get detailed information about a specific skill
    #>
    param([string]$SkillName)
    
    if (-not $SkillName) {
        Write-Host "Usage: get-skill 'skill-name'" -ForegroundColor Yellow
        list-skills
        return
    }
    
    if ($script:AvailableSkills.ContainsKey($SkillName)) {
        $skill = $script:AvailableSkills[$SkillName]
        Write-Host "Skill: $SkillName" -ForegroundColor Cyan
        Write-Host "  Class:       $($skill.Class)" -ForegroundColor Green
        Write-Host "  Description: $($skill.Description)" -ForegroundColor Green
        Write-Host "  Status:      $($skill.Status)" -ForegroundColor Green
        Write-Host "  Path:        $($skill.Path)" -ForegroundColor Green
        Write-Host ""
        
        if (Test-Path $skill.Path) {
            Write-Host "Preview:" -ForegroundColor Yellow
            Get-Content $skill.Path | Select-Object -First 20 | Out-String
        }
    } else {
        Write-Host "❌ Skill not found: $SkillName" -ForegroundColor Red
        Write-Host ""
        list-skills
    }
}

function test-skill {
    <#
    .SYNOPSIS
    Test a specific skill
    #>
    param([string]$SkillName)
    
    if (-not $SkillName) {
        Write-Host "Usage: test-skill 'skill-name'" -ForegroundColor Yellow
        return
    }
    
    if ($script:AvailableSkills.ContainsKey($SkillName)) {
        $skill = $script:AvailableSkills[$SkillName]
        
        if (Test-Path $skill.Path) {
            Write-Host "🧪 Testing skill: $SkillName" -ForegroundColor Yellow
            Write-Host "Path: $($skill.Path)" -ForegroundColor Gray
            Write-Host ""
            
            # Try to import and test
            try {
                $result = python -c "from skills.$(Split-Path $skill.Path -LeafBase) import $($skill.Class); print('✅ Import successful')" 2>&1
                Write-Host $result -ForegroundColor Green
            }
            catch {
                Write-Host "❌ Test failed: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Skill file not found: $($skill.Path)" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Skill not found: $SkillName" -ForegroundColor Red
    }
}

function skill-import-test {
    <#
    .SYNOPSIS
    Test that all skills can be imported
    #>
    Write-Host "🧪 Testing skill imports..." -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($name in $script:AvailableSkills.Keys) {
        $skill = $script:AvailableSkills[$name]
        $moduleName = Split-Path $skill.Path -LeafBase
        
        try {
            $result = python -c "from skills.$moduleName import $($skill.Class); print('✅')" 2>&1
            Write-Host "  ✅ $name" -ForegroundColor Green
        }
        catch {
            Write-Host "  ❌ $name" -ForegroundColor Red
        }
    }
}

# ============================================================================
# Helper Aliases
# ============================================================================

Set-Alias -Name skills -Value list-skills -Force
Set-Alias -Name skill-info -Value get-skill -Force

# Verify functions are available
if (Get-Command list-skills -ErrorAction SilentlyContinue) {
    Write-Host "✓ Skills registry loaded (list-skills, get-skill available)" -ForegroundColor Green
} else {
    Write-Host "❌ WARNING: Skills registry loaded but functions not available" -ForegroundColor Red
}
