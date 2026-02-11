# ============================================================================
# Common Profile - Shared Unix-Style Utilities
# ============================================================================
# These utilities are always loaded regardless of workspace mode
# Available across all modes: coding, testing, content
#
# Unix Equivalents in PowerShell
# ============================================================================

# ========== head - Show first N lines (default 10) ==========
function head {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [object]$InputObject,
        
        [int]$n = 10
    )
    
    $input | Select-Object -First $n
}

# ========== tail - Show last N lines (default 10) ==========
function tail {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [object]$InputObject,
        
        [int]$n = 10
    )
    
    $input | Select-Object -Last $n
}

# ========== wc - Count lines, words, characters ==========
function wc {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [object]$InputObject,
        
        [switch]$Lines,
        [switch]$Words,
        [switch]$Chars
    )
    
    begin {
        $allInput = @()
    }
    
    process {
        $allInput += $_
    }
    
    end {
        if ($allInput) {
            $lineCount = @($allInput).Count
            $wordCount = ($allInput -join " ").Split() | Measure-Object | Select-Object -ExpandProperty Count
            $charCount = ($allInput -join " ").Length
            
            if ($Lines) {
                Write-Output $lineCount
            } elseif ($Words) {
                Write-Output $wordCount
            } elseif ($Chars) {
                Write-Output $charCount
            } else {
                Write-Output "Lines: $lineCount, Words: $wordCount, Chars: $charCount"
            }
        }
    }
}

# ========== grep - Search for patterns (Select-String wrapper) ==========
function grep {
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string]$Pattern,
        
        [Parameter(ValueFromPipeline=$true, ValueFromRemainingArguments=$true)]
        [string[]]$InputObject,
        
        [switch]$Invert,
        [switch]$IgnoreCase,
        [int]$Context
    )
    
    begin {
        $allInput = @()
        $params = @{
            Pattern = $Pattern
        }
        
        if ($IgnoreCase) { $params.Add("CaseSensitive", $false) }
        if ($Context) { $params.Add("Context", $Context) }
    }
    
    process {
        if ($InputObject) {
            $allInput += $InputObject
        }
    }
    
    end {
        if ($allInput) {
            $files = @()
            $lines = @()
            
            foreach ($item in $allInput) {
                if (Test-Path $item -PathType Leaf) {
                    $files += $item
                } else {
                    $lines += $item
                }
            }
            
            if ($files) {
                Get-Content $files | Select-String @params -NotMatch:$Invert
            } elseif ($lines) {
                $lines | Select-String @params -NotMatch:$Invert
            }
        } else {
            Write-Host "Usage: grep 'pattern' [files]" -ForegroundColor Yellow
            Write-Host "Usage: command | grep 'pattern'" -ForegroundColor Yellow
        }
    }
}

# ========== cat - Display file contents ==========
function cat {
    param([string]$Path)
    if (Test-Path $Path) {
        Get-Content $Path
    } else {
        Write-Host "File not found: $Path" -ForegroundColor Red
    }
}

# ========== less - Display with pagination ==========
function less {
    param([string]$Path)
    if (Test-Path $Path) {
        Get-Content $Path | Out-Host -Paging
    } else {
        Write-Host "File not found: $Path" -ForegroundColor Red
    }
}

# ========== pwd - Print working directory ==========
function pwd {
    Get-Location
}

# ========== ls - List directory (alias for Get-ChildItem) ==========
Set-Alias -Name ls -Value Get-ChildItem -Force -Option AllScope

# ============================================================================
# Common Helper Functions
# ============================================================================

function Show-Common-Help {
    Write-Host "🛠️  COMMON UTILITIES - Available in All Modes:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "TEXT PROCESSING:" -ForegroundColor Yellow
    Write-Host "  head [file]         # Show first 10 lines" -ForegroundColor Gray
    Write-Host "  tail [file]         # Show last 10 lines" -ForegroundColor Gray
    Write-Host "  wc [file]           # Count lines, words, chars" -ForegroundColor Gray
    Write-Host "  grep 'pattern'      # Search for pattern" -ForegroundColor Gray
    Write-Host "  cat [file]          # Display file contents" -ForegroundColor Gray
    Write-Host "  less [file]         # Display with pagination" -ForegroundColor Gray
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  dir | grep 'txt'                 # Find txt files" -ForegroundColor Gray
    Write-Host "  cat file.txt | head -5           # First 5 lines" -ForegroundColor Gray
    Write-Host "  Get-Content file.txt | wc -Lines # Count lines" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "✓ Common utilities loaded" -ForegroundColor Green
