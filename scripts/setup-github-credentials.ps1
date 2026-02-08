<#
.SYNOPSIS
    One-time setup: Store GitHub PAT in Windows Credential Manager.

.DESCRIPTION
    Securely stores your GitHub Personal Access Token (PAT) in Windows Credential Manager
    so that future git operations can authenticate silently without prompting.

    This script must be run once per machine before using git_push with token-based auth.

    The token is stored securely by Windows and can only be accessed by the current user.

.PARAMETER GitHubToken
    Your GitHub Personal Access Token (PAT).
    - Fine-grained tokens (recommended): Start with "ghp_"
    - Classic tokens: Start with "github_pat_"
    
    You can generate one here: https://github.com/settings/tokens
    Required scopes: repo (full control), at minimum.

.PARAMETER Interactive
    If specified, prompt for the token interactively (masked input).
    Default: Use -GitHubToken parameter.

.PARAMETER Verify
    If specified, verify that the token was stored and retrieve metadata.

.PARAMETER List
    If specified, list all stored Git-related credentials in Windows Credential Manager.

.EXAMPLE
    .\setup-github-credentials.ps1 -GitHubToken "ghp_your_token_here"
    Stores the token in Windows Credential Manager.

.EXAMPLE
    .\setup-github-credentials.ps1 -Interactive
    Prompts for the token securely (input will be masked).

.EXAMPLE
    .\setup-github-credentials.ps1 -Verify
    Verifies the token is stored and shows metadata (without exposing the token).

.NOTES
    Requires Windows Credential Manager (Windows 7 or later).
    Requires git to be installed and accessible on the system PATH.
    The token is encrypted by Windows and stored securely.
    The script never logs or displays the actual token (only metadata).

#>

[CmdletBinding(DefaultParameterSetName='Token')]
param(
    [Parameter(ParameterSetName='Token', Position=0, HelpMessage='GitHub Personal Access Token (ghp_... or github_pat_...)')]
    [string]$GitHubToken = $null
    ,
    [Parameter(ParameterSetName='Interactive', HelpMessage='Prompt for token interactively (masked)')]
    [switch]$Interactive
    ,
    [Parameter(HelpMessage='Verify token storage without exposing the token')]
    [switch]$Verify
    ,
    [Parameter(HelpMessage='List all Git-related credentials in Windows Credential Manager')]
    [switch]$List
)

# ============================================================================
# Configuration
# ============================================================================

$WCM_Entry = "github_pat"  # Windows Credential Manager entry name
$TokenPattern = '^(ghp_|github_pat_).{32,}$'  # GitHub PAT format

function Write-Banner([string]$msg) {
    Write-Host "`n=== $msg ===" -ForegroundColor Cyan
}

function Write-Success([string]$msg) {
    Write-Host "✓ $msg" -ForegroundColor Green
}

function Write-Error-Custom([string]$msg) {
    Write-Host "✗ $msg" -ForegroundColor Red
}

function Write-Info([string]$msg) {
    Write-Host "ℹ $msg" -ForegroundColor Yellow
}

function Validate-GithubPAT([string]$token) {
    <#
    .SYNOPSIS
      Validate GitHub PAT format (basic checks).
    #>
    if ([string]::IsNullOrWhiteSpace($token)) {
        return $false
    }
    
    if ($token -notmatch $TokenPattern) {
        Write-Error-Custom "Invalid GitHub PAT format"
        Write-Info "GitHub PATs must start with 'ghp_' (fine-grained) or 'github_pat_' (classic) and be at least 36 characters"
        return $false
    }
    
    return $true
}

function Store-Token-WCM([string]$token) {
    <#
    .SYNOPSIS
      Store token in Windows Credential Manager using cmdkey.
    #>
    if (-not (Validate-GithubPAT -token $token)) {
        return $false
    }
    
    try {
        # Use cmdkey to store the credential
        # Format: cmdkey /add:target /user:username /pass:password
        # Note: cmdkey /add overwrites if already exists
        $output = Write-Host "Storing in Windows Credential Manager..." -ForegroundColor Gray
        
        # For GitHub, we use the token as both username and password (GitHub auth method)
        # This is a common pattern; actual git credential helpers use the token as password
        $result = & cmdkey /add:$WCM_Entry /user:$WCM_Entry /pass:$token 2>&1
        
        # cmdkey doesn't set LASTEXITCODE reliably; check for success message
        $success = ($LASTEXITCODE -eq 0) -or ($result -like '*successfully*')
        
        if ($success) {
            Write-Success "Token stored in Windows Credential Manager"
            return $true
        } else {
            Write-Error-Custom "Failed to store token in Windows Credential Manager"
            Write-Info "You may need to run this script as Administrator"
            Write-Info "Error details: $result"
            return $false
        }
    } catch {
        Write-Error-Custom "Exception while storing token: $_"
        return $false
    }
}

function List-Git-Credentials {
    <#
    .SYNOPSIS
      List all Git-related credentials stored in Windows Credential Manager.
    #>
    Write-Banner "Git Credentials in Windows Credential Manager"
    
    try {
        $result = & cmdkey /list 2>&1 | Select-String -Pattern 'git|github' -AllMatches
        
        if ($result) {
            Write-Host $result
        } else {
            Write-Info "No Git-related credentials found"
        }
    } catch {
        Write-Error-Custom "Failed to list credentials: $_"
    }
}

function Verify-Token {
    <#
    .SYNOPSIS
      Verify that token is stored and show metadata (without exposing the token).
    #>
    Write-Banner "Verifying GitHub Token Storage"
    
    try {
        # Use cmdkey /list to check if entry exists (doesn't expose the token)
        $result = & cmdkey /list:$WCM_Entry 2>&1
        
        if ($LASTEXITCODE -eq 0 -and $result) {
            Write-Success "GitHub token is stored and available"
            Write-Info "Location: Windows Credential Manager"
            Write-Info "Entry name: $WCM_Entry"
            Write-Host "`nCredential details (token contents hidden):" -ForegroundColor Cyan
            Write-Host $result
            
            # Try to retrieve and validate token via Python skill
            Write-Info "To validate token freshness, you can test with: python src/skills/token_resolver.py --token-name github_pat --validate"
            
            return $true
        } else {
            Write-Error-Custom "GitHub token not found in Windows Credential Manager"
            Write-Info "Run this script with a token or --Interactive to set it up"
            return $false
        }
    } catch {
        Write-Error-Custom "Failed to verify token: $_"
        return $false
    }
}

function Show-Setup-Instructions {
    <#
    .SYNOPSIS
      Show instructions for GitHub PAT creation.
    #>
    Write-Banner "GitHub Personal Access Token Setup"
    Write-Host @"
To create a GitHub Personal Access Token (PAT):

1. Go to: https://github.com/settings/tokens/new
2. Select token type:
   → Fine-grained (recommended): More secure, scoped permissions
   → Classic: Broader access, simpler
3. Set required permissions:
   ✓ Repository access (read & write)
   ✓ Commit status (if needed)
4. Generate and copy the token
5. Store it using this script:
   .\setup-github-credentials.ps1 -GitHubToken "ghp_..."
   or
   .\setup-github-credentials.ps1 -Interactive

IMPORTANT:
  - Treat the token like a password
  - Never commit it to git
  - Regenerate if compromised
  - Use minimal scopes needed

"@
}


# ============================================================================
# Main Flow
# ============================================================================

# Show help if no parameters
if (-not $GitHubToken -and -not $Interactive -and -not $Verify -and -not $List) {
    Show-Setup-Instructions
    exit 0
}

# List credentials
if ($List) {
    List-Git-Credentials
    exit 0
}

# Verify storage
if ($Verify) {
    Verify-Token
    exit 0
}

# Collect token interactively
if ($Interactive) {
    Write-Banner "GitHub Personal Access Token Setup"
    Write-Info "You will be prompted for your GitHub PAT"
    Write-Info "Your input will be masked and not logged"
    
    $SecureToken = Read-Host "Enter GitHub Personal Access Token (ghp_... or github_pat_...)" -AsSecureString
    $GitHubToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($SecureToken))
    
    # Clear secure string from memory
    $SecureToken.Dispose()
}

# Validate token format
if (-not (Validate-GithubPAT -token $GitHubToken)) {
    exit 1
}

# Store token in Windows Credential Manager
Write-Banner "Storing GitHub Token"
if (Store-Token-WCM -token $GitHubToken) {
    Write-Host "`nSetup complete! You can now use:" -ForegroundColor Green
    Write-Host "  .\invoke-git-push-with-token.ps1`n" -ForegroundColor Cyan
    Write-Host "This will perform git operations without prompting for authentication." -ForegroundColor Gray
    exit 0
} else {
    exit 1
}
