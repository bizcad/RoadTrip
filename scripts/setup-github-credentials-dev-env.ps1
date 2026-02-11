<#
.SYNOPSIS
    DEV-ONLY: Create a .env file with GitHub PAT for local development.

.DESCRIPTION
    This script is for LOCAL DEVELOPMENT ONLY to create a .env file with
    your GitHub PAT in plaintext. This is INSECURE and should NEVER be used
    in production or committed to git.

    For production, use `setup-github-credentials.ps1` to store the PAT in
    Windows Credential Manager instead.

.PARAMETER EnvFilePath
    Path to the .env file to create (default: repo root/.env).

.EXAMPLE
    .\setup-github-credentials-dev-env.ps1
    Creates .env in the repository root.

.NOTES
    SECURITY WARNING:
    - This stores your GitHub PAT in PLAINTEXT on disk
    - The .env file must be in .gitignore (never commit!)
    - Anyone with filesystem access can read your PAT
    - This is dev-only; use Windows Credential Manager in production

    Requirements:
    - .env must be listed in .gitignore
    - Only run this on your personal development machine
#>

param(
    [string]$EnvFilePath = (Join-Path (Split-Path -Parent $PSScriptRoot) ".env")
)

$ErrorActionPreference = 'Stop'

function Get-PlainTextFromSecureString {
    param([Security.SecureString]$SecureString)

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringUni($bstr)
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

Write-Host ""
Write-Host "WARNING: DEV-ONLY .env FILE CREATION" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red
Write-Host ""
Write-Host "This will store your GitHub PAT in PLAINTEXT at:"
Write-Host "  $EnvFilePath"
Write-Host ""
Write-Host "CRITICAL REQUIREMENTS:"
Write-Host "  1. .env MUST be in .gitignore (verify it's there NOW)"
Write-Host "  2. This is DEV-ONLY on your personal machine"
Write-Host "  3. NEVER commit .env to git"
Write-Host "  4. NEVER share the .env file"
Write-Host "  5. For production, use Windows Credential Manager"
Write-Host ""

# Verify .gitignore
$gitignorePath = Join-Path (Split-Path -Parent $PSScriptRoot) ".gitignore"
if (Test-Path $gitignorePath) {
    $gitignore = Get-Content $gitignorePath
    if ($gitignore -match '\.env') {
        Write-Host "✓ .gitignore contains .env (safe)" -ForegroundColor Green
    } else {
        Write-Host "✗ WARNING: .gitignore does NOT contain .env" -ForegroundColor Yellow
        Write-Host "  Please add '.env' to .gitignore before proceeding" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "? .gitignore not found; assuming .env is properly ignored" -ForegroundColor Yellow
}

Write-Host ""
$confirm = Read-Host "Type 'DEVONLY' to continue (case-sensitive)"
if ($confirm -ne 'DEVONLY') {
    Write-Host "Aborted." -ForegroundColor Gray
    exit 0
}

Write-Host ""
$secure = Read-Host "Enter GitHub PAT (input hidden)" -AsSecureString
$plain  = Get-PlainTextFromSecureString -SecureString $secure

if ([string]::IsNullOrWhiteSpace($plain)) {
    Write-Host "PAT cannot be empty." -ForegroundColor Red
    exit 1
}

try {
    # Create .env file with header warning
    $content = @(
        "## DEV-ONLY, DO NOT COMMIT",
        "## This file contains your GitHub PAT in PLAINTEXT",
        "## Ensure .env is in .gitignore",
        "GITHUB_TOKEN=$plain"
    ) -join "`n"

    $content | Out-File -FilePath $EnvFilePath -Encoding UTF8 -Force
    Write-Host ".env written to $EnvFilePath (DEV-ONLY, INSECURE)" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ REMINDER: Do NOT commit .env" -ForegroundColor Yellow
}
finally {
    # Clear plaintext from memory
    $plain = $null
    $secure.Dispose()
}
