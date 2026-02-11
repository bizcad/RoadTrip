# ============================================================================
# Load Secrets - Secure Credential Management
# ============================================================================
# Loads credentials from Windows Credential Manager (secure storage)
# NEVER hardcode secrets in profiles or commit to Git!
#
# Setup Instructions:
# 1. Store credentials one time:
#    cmdkey /add:github_pat /user:github /pass:"your_personal_access_token"
#    cmdkey /add:openai_key /user:openai /pass:"your_api_key"
#    cmdkey /add:vercel_token /user:vercel /pass:"your_vercel_token"
#
# 2. List stored credentials:
#    cmdkey /list
#
# 3. Delete a credential:
#    cmdkey /delete:github_pat
#
# ============================================================================

function Get-StoredCredential {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CredentialName,
        
        [switch]$AsPlainText
    )
    
    try {
        $cred = [Windows.Security.Credentials.PasswordVault]::new()
        $vault = $cred.RetrieveAll() | Where-Object { $_.Resource -eq $CredentialName }
        
        if ($vault) {
            $vault = $vault[0]
            $vault.RetrievePassword()
            return $vault.Password
        } else {
            Write-Host "⚠️  Credential not found: $CredentialName" -ForegroundColor Yellow
            return $null
        }
    }
    catch {
        Write-Host "⚠️  Could not retrieve credential '$CredentialName': $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

# ============================================================================
# Load Environment Variables from Secure Storage
# ============================================================================

# GitHub PAT
$githubPat = Get-StoredCredential "github_pat"
if ($githubPat) {
    $env:GITHUB_PAT = $githubPat
    $env:GIT_ASKPASS = "c:\Program Files\git\core.fnmatch.mingw64.dll"  # For git operations
}

# OpenAI API Key
$openaiKey = Get-StoredCredential "openai_key"
if ($openaiKey) {
    $env:OPENAI_API_KEY = $openaiKey
}

# Vercel Token
$vercelToken = Get-StoredCredential "vercel_token"
if ($vercelToken) {
    $env:VERCEL_TOKEN = $vercelToken
}

# Add more as needed:
# $env:ANTHROPIC_API_KEY = Get-StoredCredential "anthropic_key"
# $env:AZURE_SUBSCRIPTION_ID = Get-StoredCredential "azure_sub_id"

Write-Host "✓ Secrets loaded from Windows Credential Manager" -ForegroundColor Green
