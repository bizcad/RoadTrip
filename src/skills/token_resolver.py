#!/usr/bin/env python3
"""
token_resolver.py
------------------

Resolves a GitHub Personal Access Token (PAT) using a secure fallback chain:

1. Environment variable: GITHUB_TOKEN
2. Windows Credential Manager (preferred)
3. Optional .env file (dev-only, insecure)

OUTPUT:
    - Default mode: prints ONLY the token to stdout (for git-askpass).
    - Metadata mode (--metadata): prints JSON metadata to stderr, token to stdout.

SECURITY:
    - Never prints the token to stderr or logs.
    - Fingerprint is SHA-256(token) truncated to 16 hex chars.
    - .env fallback is explicitly marked insecure for dev-only use.

Exit codes:
    0 = Success (token found and output)
    1 = Token not found in any source
"""

import os
import sys
import json
import hashlib
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================

# The CredMan target name used by setup-github-credentials.ps1
CREDMAN_TARGET = "git:github.com:roadtrip-pat"

# Optional .env fallback (dev only)
ENV_FILE_PATH = Path(__file__).resolve().parent.parent / ".env"


# ============================================================================
# Utilities
# ============================================================================

def fingerprint(token: str) -> str:
    """Return first 16 hex chars of SHA-256(token)."""
    h = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return h[:16]


def load_from_env() -> tuple:
    """Load token from GITHUB_TOKEN environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip(), "Env:GITHUB_TOKEN"
    return None, None


def load_from_credman() -> tuple:
    """
    Load token from Windows Credential Manager using pywin32.
    If pywin32 is not available, returns (None, None).
    """
    try:
        import win32cred  # type: ignore
    except ImportError:
        return None, None

    try:
        cred = win32cred.CredRead(
            Type=win32cred.CRED_TYPE_GENERIC,
            TargetName=CREDMAN_TARGET
        )
        token = cred.get("CredentialBlob", None)
        if token:
            return token.strip(), f"Windows Credential Manager ({CREDMAN_TARGET})"
    except Exception:
        pass

    return None, None


def load_from_env_file() -> tuple:
    """
    Dev-only fallback: read .env file containing GITHUB_TOKEN=...
    """
    if not ENV_FILE_PATH.exists():
        return None, None

    try:
        for line in ENV_FILE_PATH.read_text().splitlines():
            if line.strip().startswith("GITHUB_TOKEN="):
                _, value = line.split("=", 1)
                token = value.strip()
                if token:
                    return token, ".env (INSECURE DEV FALLBACK)"
    except Exception:
        pass

    return None, None


# ============================================================================
# Main Resolver
# ============================================================================

def resolve_token() -> tuple:
    """
    Resolve token using fallback chain: env → credman → .env
    Returns (token, source) or (None, None) if not found.
    """
    # 1. Environment variable
    token, source = load_from_env()
    if token:
        return token, source

    # 2. Windows Credential Manager
    token, source = load_from_credman()
    if token:
        return token, source

    # 3. .env fallback (dev-only)
    token, source = load_from_env_file()
    if token:
        return token, source

    return None, None


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Resolve and output GitHub PAT token."""
    metadata_mode = "--metadata" in sys.argv

    token, source = resolve_token()

    if not token:
        # No token found — fail with clear error on stderr
        sys.stderr.write(
            "ERROR: No GitHub token found. "
            "Run setup-github-credentials.ps1 to configure credentials.\n"
        )
        sys.exit(1)

    # Print metadata to stderr (never include token)
    if metadata_mode:
        meta = {
            "source": source,
            "fingerprint": fingerprint(token),
        }
        sys.stderr.write(json.dumps(meta) + "\n")

    # Print ONLY the token to stdout (for git-askpass to consume)
    sys.stdout.write(token)
    sys.exit(0)


if __name__ == "__main__":
    main()
