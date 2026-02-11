<#
.SYNOPSIS
    One-time setup: Store GitHub PAT securely in Windows Credential Manager.

.DESCRIPTION
    This script prompts for a GitHub Personal Access Token (PAT) and stores it
    securely in Windows Credential Manager using native Windows APIs.
    
    The token is stored as a generic credential under the target name:
      git:github.com:roadtrip-pat
    
    This target name is shared with token_resolver.py, so the silent git push
    workflow can retrieve the token automatically without user interaction.

    Security:
    - Token is never echoed to console or logs.
    - Token is cleared from memory after storage.
    - Only the fingerprint (SHA-256 hash, first 16 hex chars) is logged.
    - Storage is encrypted by Windows Credential Manager (DPAPI).

.PARAMETER TargetName
    Credential Manager target name (default: git:github.com:roadtrip-pat).
    Change this if you need separate tokens for different repos/orgs.

.EXAMPLE
    .\setup-github-credentials.ps1
    Prompts for PAT and stores it in Windows Credential Manager.

.EXAMPLE
    .\setup-github-credentials.ps1 -TargetName "git:github.com:my-org-pat"
    Uses a custom target name for org-specific automation.

.NOTES
    Requirements:
      - Windows 10 or later
      - PowerShell 5.1+
      - Administrator privileges (recommended, for DPAPI encryption)

    The GitHub PAT should have at minimum:
      - Contents: Read & Write (if pushing to repos)
      - Metadata: Read (always needed)
      
    For fine-grained PATs, we recommend:
      - Scope: Single repository (if possible)
      - Permissions: Contents only (read+write)
      - Expiration: 90 days (rotate regularly)
#>

param(
    [string]$TargetName = "git:github.com:roadtrip-pat"
)

$ErrorActionPreference = 'Stop'

# ============================================================================
# Helpers
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = 'INFO'
    )
    $ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
    Write-Host "[$ts][$Level] $Message"
}

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

function Get-TokenFingerprint {
    param([string]$Token)

    $bytes = [Text.Encoding]::UTF8.GetBytes($Token)
    $hash  = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    $hex   = [Convert]::ToHexString($hash)
    return $hex.Substring(0, 16)
}

# ============================================================================
# Credential Manager Native Interop
# ============================================================================

$CRED_TYPE_GENERIC = 1
$CRED_PERSIST_LOCAL_MACHINE = 2

# Define the CREDENTIAL struct for P/Invoke
$CredentialDefinition = @"
using System;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct CREDENTIAL
{
    public int Flags;
    public int Type;
    public string TargetName;
    public string Comment;
    public long LastWritten;
    public int CredentialBlobSize;
    public IntPtr CredentialBlob;
    public int Persist;
    public int AttributeCount;
    public IntPtr Attributes;
    public string TargetAlias;
    public string UserName;
}

public class CredentialManager
{
    [DllImport("advapi32", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool CredWrite(ref CREDENTIAL userCredential, uint flags);
}
"@

Add-Type -TypeDefinition $CredentialDefinition -Language CSharp -ErrorAction Stop

function Set-GenericCredential {
    param(
        [string]$TargetName,
        [string]$Secret,
        [string]$UserName = "git"
    )

    $bytes = [Text.Encoding]::Unicode.GetBytes($Secret)
    $size  = $bytes.Length

    $ptr = [Runtime.InteropServices.Marshal]::AllocHGlobal($size)
    try {
        [Runtime.InteropServices.Marshal]::Copy($bytes, 0, $ptr, $size)

        $cred = New-Object CREDENTIAL
        $cred.Flags = 0
        $cred.Type  = $script:CRED_TYPE_GENERIC
        $cred.TargetName = $TargetName
        $cred.Comment    = "GitHub PAT for RoadTrip silent Git push"
        $cred.CredentialBlobSize = $size
        $cred.CredentialBlob     = $ptr
        $cred.Persist            = $script:CRED_PERSIST_LOCAL_MACHINE
        $cred.AttributeCount     = 0
        $cred.Attributes         = [IntPtr]::Zero
        $cred.TargetAlias        = $null
        $cred.UserName           = $UserName

        $ok = [CredentialManager]::CredWrite([ref]$cred, 0)
        if (-not $ok) {
            $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
            throw "CredWrite failed with Win32 error $err"
        }
    }
    finally {
        if ($ptr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeHGlobal($ptr)
        }
    }
}


# ============================================================================
# Main
# ============================================================================

Write-Host ""
Write-Log "GitHub PAT Setup for Windows Credential Manager"
Write-Host ""

Write-Log "Target: $TargetName"
Write-Host ""

Write-Host "This script will:"
Write-Host "  1. Prompt you for your GitHub PAT (securely, input hidden)"
Write-Host "  2. Store it in Windows Credential Manager (encrypted)"
Write-Host "  3. Log only the fingerprint (SHA-256 hash, never the token)"
Write-Host ""
Write-Host "PAT should have appropriate scopes:"
Write-Host "  - For private repos: 'repo' scope"
Write-Host "  - For fine-grained PATs: Minimum 'Contents: Read & Write'"
Write-Host ""

# Prompt for PAT (hidden input)
$secure1 = Read-Host "Enter GitHub PAT (input hidden)" -AsSecureString
$secure2 = Read-Host "Confirm GitHub PAT (input hidden)" -AsSecureString

$plain1 = Get-PlainTextFromSecureString -SecureString $secure1
$plain2 = Get-PlainTextFromSecureString -SecureString $secure2

# Validation
if ([string]::IsNullOrWhiteSpace($plain1) -or [string]::IsNullOrWhiteSpace($plain2)) {
    Write-Log "PAT cannot be empty." 'ERROR'
    exit 1
}

if ($plain1 -ne $plain2) {
    Write-Log "PAT entries do not match." 'ERROR'
    exit 1
}

if ($plain1.Length -lt 20) {
    Write-Log "PAT looks suspiciously short. Please verify you pasted the full token." 'WARN'
    $confirm = Read-Host "Continue anyway? (y/n)"
    if ($confirm -ine 'y') {
        Write-Log "Aborted." 'INFO'
        exit 0
    }
}

$fingerprint = Get-TokenFingerprint -Token $plain1

try {
    Set-GenericCredential -TargetName $TargetName -Secret $plain1
    Write-Log "✓ Stored GitHub PAT in Windows Credential Manager."
    Write-Log "  Token fingerprint (SHA-256, first 16 hex chars): $fingerprint"
    Write-Host ""
    Write-Log "✓ Setup complete. Silent Git pushes can now use token_resolver.py."
    Write-Log "  Run: .\invoke-git-push-with-token.ps1 -DryRun"
    Write-Host ""
}
catch {
    Write-Log "Failed to store credential: $_" 'ERROR'
    exit 1
}
finally {
    # Clear plaintext from memory as much as we reasonably can
    $plain1 = $null
    $plain2 = $null
    $secure1.Dispose()
    $secure2.Dispose()
}
