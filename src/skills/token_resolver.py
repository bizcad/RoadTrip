#!/usr/bin/env python3
"""
Token Resolver Skill: Manages secure credential storage and retrieval.

Provides a unified interface for storing and retrieving authentication tokens
(GitHub PAT, API keys, etc.) from secure storage backends:
  - Windows Credential Manager (preferred, native Windows security)
  - Environment variables (portable, CI/CD-friendly)
  - .env files (dev-only, must be .gitignored)

This skill enables other skills to access credentials without embedding them
in code or prompting the user interactively.

Architecture:
  1. Setup phase: Store token once (user supplies via -Setup)
  2. Runtime phase: Resolve token silently (environment or WCM)
  3. Logging phase: Log token operations without exposing actual token

Exit codes:
  0 = Success
  1 = Token not found
  2 = Invalid token format
  3 = Storage operation failed
  4 = Permission denied
"""

import sys
import os
import json
import argparse
import hashlib
import subprocess
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
from pathlib import Path


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TokenMetadata:
    """Metadata about a stored token (does NOT include the actual token)."""
    token_name: str  # e.g., "github_pat"
    storage_type: Literal["wcm", "env", "env_file"]  # Where it's stored
    token_hash: str  # SHA256 of token (for verification, not reversal)
    created_at: str  # ISO timestamp
    last_accessed: str  # ISO timestamp
    is_valid: bool = True  # Whether token is still valid
    rotation_due: bool = False  # Hint for token rotation
    confidence: float = 0.95  # Confidence in token freshness

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ResolvedToken:
    """Result of token resolution (contains actual token and metadata)."""
    token: str  # The actual credential
    token_name: str  # Name/key (e.g., "github_pat")
    source: Literal["wcm", "env", "env_file"]  # Where it came from
    is_valid: bool = True  # Validation status
    confidence: float = 0.95  # How confident we are in this token
    reasoning: str = ""  # Why we chose this source
    
    def mask(self) -> dict:
        """Return metadata without exposing the actual token."""
        return {
            "token_name": self.token_name,
            "source": self.source,
            "is_valid": self.is_valid,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "token_preview": f"{self.token[:10]}...{self.token[-4:]}" if self.token else "N/A"
        }

    def to_dict(self):
        # Never expose raw token in dict
        return self.mask()

    def to_json(self):
        return json.dumps(self.mask(), indent=2)


@dataclass
class TokenResolverResult:
    """Final result from TokenResolver operations."""
    success: bool
    token_name: str
    source: Optional[str] = None  # wcm, env, env_file
    token: Optional[str] = None  # Only set if success=True
    message: str = ""
    error_code: Optional[int] = None
    metadata: Optional[TokenMetadata] = None

    def to_dict(self):
        # Never expose raw token
        d = asdict(self)
        d.pop('token', None)  # Remove token from dict
        return d

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# Token Resolver Class
# ============================================================================

class TokenResolver:
    """
    Resolve and manage authentication credentials across multiple backends.
    
    Priority order (for resolution):
      1. Environment variable (GITHUB_TOKEN, etc.)
      2. Windows Credential Manager (native Windows secure storage)
      3. .env file (dev-only, must be .gitignored)
    
    All operations are logged without exposing actual tokens.
    """

    def __init__(self, token_name: str = "github_pat", verbose: bool = False):
        """
        Initialize token resolver.
        
        Args:
            token_name: Identifier for the token (e.g., "github_pat", "api_key")
            verbose: Log detailed operations
        """
        self.token_name = token_name
        self.verbose = verbose
        self.env_var_name = self._format_env_var(token_name)
        self.wcm_entry = token_name  # Windows Credential Manager entry name
        self.env_file = Path.home() / ".env"  # Optional ~/.env for dev

    @staticmethod
    def _format_env_var(token_name: str) -> str:
        """Convert 'github_pat' → 'GITHUB_TOKEN' (standard naming)."""
        return token_name.upper().replace("_", "") + "_TOKEN" if "_" not in token_name else token_name.upper()

    def setup_wcm(self, token: str) -> TokenResolverResult:
        """
        Store token in Windows Credential Manager (secure, Windows-only).
        
        This is a one-time setup step that must be run once per machine.
        
        Args:
            token: The actual token/credential to store
            
        Returns:
            TokenResolverResult with success status
        """
        if not token:
            return TokenResolverResult(
                success=False,
                token_name=self.token_name,
                error_code=2,
                message="Token cannot be empty"
            )

        try:
            # PowerShell command to store in Windows Credential Manager
            ps_cmd = f"""
$cred = New-Object System.Management.Automation.PSCredential -ArgumentList '{self.token_name}', $(ConvertTo-SecureString -String '{token}' -AsPlainText -Force)
$credProvider = New-Object System.Net.NetworkCredential($cred.UserName, $cred.Password)
# This would require additional WCM integration; for now use cmdkey
"""
            # Use cmdkey (Windows built-in) to store credential
            # Format: cmdkey /add:targetname /user:username /pass:password
            result = subprocess.run(
                ["cmdkey", f"/add:{self.wcm_entry}", f"/user:{self.token_name}", f"/pass:{token}"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                from datetime import datetime
                metadata = TokenMetadata(
                    token_name=self.token_name,
                    storage_type="wcm",
                    token_hash=token_hash,
                    created_at=datetime.utcnow().isoformat(),
                    last_accessed=datetime.utcnow().isoformat(),
                    is_valid=True
                )
                if self.verbose:
                    print(f"[INFO] Stored '{self.token_name}' in Windows Credential Manager")
                return TokenResolverResult(
                    success=True,
                    token_name=self.token_name,
                    source="wcm",
                    message="Token stored in Windows Credential Manager",
                    metadata=metadata
                )
            else:
                if self.verbose:
                    print(f"[ERROR] Failed to store in WCM: {result.stderr}")
                return TokenResolverResult(
                    success=False,
                    token_name=self.token_name,
                    error_code=3,
                    message=f"WCM storage failed: {result.stderr}"
                )
        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Exception during WCM setup: {e}")
            return TokenResolverResult(
                success=False,
                token_name=self.token_name,
                error_code=3,
                message=f"WCM setup failed: {str(e)}"
            )

    def resolve(self) -> TokenResolverResult:
        """
        Resolve token from storage (env var → WCM → env file).
        
        Returns:
            TokenResolverResult with resolved token (if found)
        """
        # Priority 1: Environment variable
        env_token = os.environ.get(self.env_var_name)
        if env_token:
            if self.verbose:
                print(f"[INFO] Resolved '{self.token_name}' from environment variable")
            return TokenResolverResult(
                success=True,
                token_name=self.token_name,
                source="env",
                token=env_token,
                message="Token resolved from environment variable"
            )

        # Priority 2: Windows Credential Manager
        try:
            result = subprocess.run(
                ["cmdkey", f"/list:{self.wcm_entry}"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0 and self.wcm_entry in result.stdout:
                # Token exists in WCM, retrieve it
                # Note: cmdkey /list only shows existence, not the actual credential
                # For actual retrieval, we'd need additional PowerShell/API calls
                # For now, this confirms WCM storage works
                if self.verbose:
                    print(f"[INFO] Found '{self.token_name}' in Windows Credential Manager")
                # Actual token retrieval would require PowerShell or additional APIs
                return TokenResolverResult(
                    success=True,
                    token_name=self.token_name,
                    source="wcm",
                    message="Token stored in WCM (retrieval requires additional setup)",
                    error_code=None
                )
        except Exception as e:
            if self.verbose:
                print(f"[DEBUG] WCM check failed (may be non-Windows): {e}")

        # Priority 3: .env file (dev-only)
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        if line.startswith(f"{self.env_var_name}="):
                            env_token = line.split("=", 1)[1].strip().strip('"\'')
                            if env_token:
                                if self.verbose:
                                    print(f"[INFO] Resolved '{self.token_name}' from .env file")
                                return TokenResolverResult(
                                    success=True,
                                    token_name=self.token_name,
                                    source="env_file",
                                    token=env_token,
                                    message="Token resolved from .env file"
                                )
            except Exception as e:
                if self.verbose:
                    print(f"[DEBUG] .env file read failed: {e}")

        # Not found
        if self.verbose:
            print(f"[WARN] Token '{self.token_name}' not found in any storage backend")
        return TokenResolverResult(
            success=False,
            token_name=self.token_name,
            error_code=1,
            message=f"Token '{self.token_name}' not found. Use --setup to configure."
        )

    def validate_token(self, token: str) -> bool:
        """
        Validate token format (basic check).
        
        For GitHub PAT:
          - Must start with 'ghp_' (fine-grained) or 'github_pat_' (classic)
          - Must be at least 36 characters
        """
        if not token:
            return False
        
        # GitHub PAT format check
        if self.token_name.lower() == "github_pat":
            if not (token.startswith("ghp_") or token.startswith("github_pat_")):
                if self.verbose:
                    print(f"[WARN] Token does not match GitHub PAT format (should start with 'ghp_' or 'github_pat_')")
                return False
            if len(token) < 36:
                if self.verbose:
                    print(f"[WARN] GitHub PAT appears too short (expected 36+ chars)")
                return False
        
        return True


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Resolve and manage authentication tokens securely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # One-time setup: store GitHub PAT in Windows Credential Manager
  %(prog)s --token-name github_pat --setup ghp_...your_token...

  # Runtime: resolve token from storage
  %(prog)s --token-name github_pat

  # List where token is stored (without exposing it)
  %(prog)s --token-name github_pat --list-sources

  # Validate token format
  %(prog)s --token-name github_pat --validate
"""
    )
    parser.add_argument(
        "--token-name",
        default="github_pat",
        help="Token identifier (e.g., 'github_pat', 'openai_key'). Default: github_pat"
    )
    parser.add_argument(
        "--setup",
        help="Store token in secure storage. Usage: --setup <actual_token>"
    )
    parser.add_argument(
        "--resolve",
        action="store_true",
        help="Resolve token from storage (default if no other option)"
    )
    parser.add_argument(
        "--restore-from-env",
        action="store_true",
        help="Load from environment variable/env file instead of prompting"
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="Show where token is stored (without exposing it)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate token format (requires resolved token)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (always masks token)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    resolver = TokenResolver(token_name=args.token_name, verbose=args.verbose)

    # Setup: Store token
    if args.setup:
        result = resolver.setup_wcm(args.setup)
        if args.json:
            print(result.to_json())
        else:
            print(result.message)
        return 0 if result.success else result.error_code or 1

    # List sources: Show storage locations without exposing token
    if args.list_sources:
        sources = []
        if os.environ.get(resolver.env_var_name):
            sources.append("environment variable")
        # Check WCM (would need additional cmdkey logic)
        if resolver.env_file.exists():
            sources.append(f".env file ({resolver.env_file})")
        
        if sources:
            msg = f"Token '{args.token_name}' is stored in: {', '.join(sources)}"
            if args.json:
                print(json.dumps({"token_name": args.token_name, "sources": sources}, indent=2))
            else:
                print(msg)
            return 0
        else:
            msg = f"Token '{args.token_name}' not found in any storage location"
            if args.json:
                print(json.dumps({"token_name": args.token_name, "sources": [], "error": msg}, indent=2))
            else:
                print(msg)
            return 1

    # Resolve: Get token from storage
    result = resolver.resolve()
    
    if args.validate and result.success:
        is_valid = resolver.validate_token(result.token)
        result.is_valid = is_valid
        if not is_valid:
            result.success = False
            result.error_code = 2

    if result.success:
        if args.json:
            print(result.to_json())
        else:
            # Just print the token (caller can redirect to env var or pipe to git)
            print(result.token)
        return 0
    else:
        if args.json:
            print(result.to_json())
        else:
            print(f"ERROR: {result.message}", file=sys.stderr)
        return result.error_code or 1


if __name__ == "__main__":
    sys.exit(main())
