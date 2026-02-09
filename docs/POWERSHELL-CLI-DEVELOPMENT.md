# PowerShell CLI Development Checklist

**Purpose**: Prevent common PowerShell pitfalls in CLI wrapper development  
**Reference**: See [Principles-and-Processes.md](Principles-and-Processes.md#powershell--cli-wrapper-standards)  

---

## Critical Rules (Must Follow)

### ❌ Never Declare Built-In Common Parameters

PowerShell automatically provides these parameters to every function:
- `-Verbose`
- `-Debug`
- `-ErrorAction`
- `-WarningAction`
- `-ErrorVariable`
- `-WarningVariable`
- `-OutVariable`
- `-OutBuffer`
- `-Confirm`
- `-WhatIf`

**If you declare them again**, PowerShell throws: `"A parameter with the name 'X' was defined multiple times for the command."`

**❌ WRONG:**
```powershell
param(
    [switch]$Verbose,      # ❌ DON'T DO THIS
    [switch]$DryRun
)
```

**✅ CORRECT:**
```powershell
param(
    [switch]$DryRun       # ✅ Only declare custom parameters
)

# Inside function, check verbose state:
if ($VerbosePreference -eq "Continue") {
    Write-Verbose "Detailed output..."
}
```

### ✅ How to Implement Verbose Output

Use the automatic `$VerbosePreference` variable:

```powershell
function bpublish {
    param([string]$Title, [switch]$DryRun)
    
    # User calls: bpublish -Title "..." -Verbose
    # PowerShell sets $VerbosePreference = "Continue"
    
    if ($VerbosePreference -eq "Continue") {
        Write-Verbose "Processing: $Title"
    }
}
```

### ✅ How to Implement Dry-Run (-WhatIf)

Use `$PSCmdlet.ShouldProcess()` for native `-WhatIf` support:

```powershell
function bpublish {
    param([string]$Title)
    
    if ($PSCmdlet.ShouldProcess("Publish post: $Title")) {
        # Not executed if user passes -WhatIf
        git push origin
    }
}
```

**User calls:**
```powershell
bpublish -Title "My Post"        # Actually publishes
bpublish -Title "My Post" -WhatIf # Shows what would happen
```

---

## Naming Conventions

### 1. Avoid PowerShell Automatic Variables in Loops

**❌ WRONG:**
```powershell
foreach ($error in $results.errors) {
    Write-Host "- $error"
}
# $error is PowerShell's automatic error object!
```

**✅ CORRECT:**
```powershell
foreach ($errorMsg in $results.errors) {
    Write-Host "- $errorMsg"
}
```

**Other automatic variables to avoid as loop variables:**
- `$_` (current object in pipeline)
- `$args` (function arguments array)
- `$error` (error collection)
- `$host` (host interface)
- `$input` (pipeline input)
- `$null` (null value)
- `$true`, `$false` (booleans)

---

## Function Structure Pattern

### Recommended Template

```powershell
<#
.SYNOPSIS
    Brief description of what this does.

.DESCRIPTION
    Detailed description of functionality, inputs, outputs.

.PARAMETER Title
    Description of the Title parameter.

.EXAMPLE
    bpublish -Title "My Post" -Excerpt "..."
    Description of what this example does.

.NOTES
    Phase 5: CLI Integration
    Dependencies: Python skill in src/skills/
#>

function bpublish {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Title,
        
        [Parameter(Mandatory=$true)]
        [string]$Excerpt,
        
        [switch]$DryRun
        # ✅ NO $Verbose parameter — PowerShell provides it
    )
    
    try {
        # Step 1: Validate input
        if ([string]::IsNullOrWhiteSpace($Title)) {
            throw "Title cannot be empty"
        }
        
        # Step 2: Check verbose state (not declared as param)
        if ($VerbosePreference -eq "Continue") {
            Write-Verbose "Processing Title: $Title"
        }
        
        # Step 3: Execute logic
        # ... call Python, handle results ...
        
        return $true
    }
    catch {
        Write-Error $_
        return $false
    }
}

# After function definition, create alias
Set-Alias -Name bp -Value bpublish -Scope Global -Force
```

---

## Loading Functions in Profiles

### ❌ Wrong: Using Import-Module

```powershell
# In profile
Import-Module $PSScriptRoot\scripts\bpublish-function.ps1
# Error: That's a .ps1 file, not a .psm1 module!
```

### ✅ Correct: Using Dot-Sourcing

```powershell
# In profile (RoadTrip_profile.ps1)
$bpublishPath = Join-Path $PSScriptRoot "scripts\bpublish-function.ps1"
if (Test-Path $bpublishPath) {
    . $bpublishPath  # Dot-source to load into current scope
}

# Now bpublish and bp are available
```

### ❌ Never Use Export-ModuleMember Outside Modules

```powershell
# In a .ps1 script file
Export-ModuleMember -Function bpublish -Alias bp
# Error: Only valid inside actual .psm1 module files!
```

---

## Error Handling Pattern

```powershell
function bpublish {
    param([string]$Title)
    
    try {
        # Validate parameters
        if (-not $Title) {
            throw "Title required"
        }
        
        # Call Python skill
        $result = py -c "..."
        if ($LASTEXITCODE -ne 0) {
            throw "Python execution failed"
        }
        
        Write-Host "✅ Success!"
        return $true
    }
    catch {
        Write-Error "❌ Error: $_"
        return $false
    }
}
```

---

## Colored Output Pattern

```powershell
function Write-Status {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )
    
    switch ($Type) {
        "Success" { Write-Host $Message -ForegroundColor Green }
        "Error"   { Write-Host $Message -ForegroundColor Red }
        "Warning" { Write-Host $Message -ForegroundColor Yellow }
        "Info"    { Write-Host $Message -ForegroundColor Cyan }
    }
}

# Usage
Write-Status "Operation completed" "Success"
Write-Status "Warning: value may be incorrect" "Warning"
Write-Status "❌ Publication failed" "Error"
Write-Status "Running validation..." "Info"
```

---

## Testing CLI Functions

### Test Pattern

```powershell
# Terminal 1: Load profile
. .\infra\RoadTrip_profile.ps1

# Test 1: Simple call
bpublish -Title "Test" -Excerpt "..." -Content "..."

# Test 2: Verbose output
bpublish -Title "Test" -Excerpt "..." -Content "..." -Verbose

# Test 3: Dry run
bpublish -Title "Test" -Excerpt "..." -Content "..." -DryRun

# Test 4: Error case
bpublish -Title "" -Excerpt "..." -Content "..."  # Should error

# Test 5: Alias
bp -Title "Test" -Excerpt "..." -Content $content
```

---

## Phase 5+ Reference

See [PHASE-5-COMPLETION.md](../workflows/PHASE-5-COMPLETION.md) for the actual implementation of `bpublish` using these patterns.

Key files:
- `scripts/bpublish-function.ps1` — Full CLI wrapper (~250 lines)
- `infra/RoadTrip_profile.ps1` — Profile integration
- `docs/bpublish_usage.md` — User documentation

---

## Quick Fixes for Common Errors

### Error: "A parameter with the name 'Verbose' was defined multiple times"

**Fix**: Remove `-Verbose` parameter declaration. Use `$VerbosePreference` instead.

```powershell
# BEFORE:
param([switch]$Verbose)

# AFTER:
param()  # Remove -Verbose
if ($VerbosePreference -eq "Continue") { ... }
```

### Error: "The variable 'X' is declared but never used"

**Fix**: Remove unused variable assignments.

```powershell
# BEFORE:
$repoRoot = Get-Location  # Assigned but never used

# AFTER:
# Just remove this line
```

### Error: "Set-Alias: The input object cannot be bound"

**Fix**: Make sure Set-Alias is called AFTER function definition.

```powershell
# WRONG: Alias before function
Set-Alias -Name bp -Value bpublish
function bpublish { ... }  # Function not yet defined!

# RIGHT: Alias after function
function bpublish { ... }
Set-Alias -Name bp -Value bpublish  # Function exists now
```

---

## Checklist for CLI Wrappers

Before submitting a PowerShell CLI wrapper, verify:

- [ ] No explicit `-Verbose` parameter declared
- [ ] No explicit `-Debug` or `-Confirm` parameters
- [ ] Loop variables don't shadow automatic variables (`$error`, `$_`, `$args`)
- [ ] Function uses dot-sourcing (`. .\script.ps1`), not Import-Module
- [ ] No `Export-ModuleMember` in .ps1 files
- [ ] `Set-Alias` defined AFTER function definition
- [ ] Using `$VerbosePreference` to check verbose state
- [ ] Try/catch for error handling
- [ ] Colored output with `Write-Host -ForegroundColor`
- [ ] Help documentation in `<# ... #>` block
- [ ] Tested with `-Verbose` flag
- [ ] Parameter validation before use
- [ ] Returns boolean or clear output

---

**Maintained by**: RoadTrip development team  
**Related**: [Principles-and-Processes.md](Principles-and-Processes.md)  
**Last Updated**: 2026-02-09
