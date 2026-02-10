#!/usr/bin/env python3
"""
auth_validator.py

Validates Git authentication credentials and user permissions.
Ensures only authorized users can execute git operations.

Deterministic skill: same input → same auth result (valid/invalid).
No external API calls; checks local config and environment.

Usage:
    python auth_validator.py --branch main --operation push
    from src.skills.auth_validator import AuthValidator
    result = AuthValidator().validate(branch="main", operation="push")
"""

import sys
import json
import subprocess
from pathlib import Path
from dataclasses import asdict, dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone

try:
    from .auth_validator_models import (
        AuthStatus,
        AuthMethod,
    )
except ImportError:
    from auth_validator_models import (
        AuthStatus,
        AuthMethod,
    )


@dataclass
class AuthValidationResult:
    """Output of auth_validator skill (Phase 1b simple version)."""
    status: AuthStatus
    auth_method: AuthMethod
    is_authorized: bool
    
    username: Optional[str] = None
    user_email: Optional[str] = None
    can_push: bool = False
    can_force_push: bool = False
    target_branch: str = "main"
    reasoning: str = ""
    error_code: Optional[str] = None
    validated_at: str = None
    expires_at: Optional[str] = None
    
    def __post_init__(self):
        if self.validated_at is None:
            self.validated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }
    
    def is_valid_and_authorized(self) -> bool:
        """Is auth valid AND authorized?"""
        return self.status == AuthStatus.VALID and self.is_authorized


class AuthValidator:
    """Validates Git credentials and permissions."""

    def validate(
        self,
        branch: str = "main",
        operation: str = "push",
        require_ssh: bool = False,
    ) -> AuthValidationResult:
        """
        Validate Git authentication.
        
        Args:
            branch: Target branch (e.g., "main")
            operation: Operation being performed (e.g., "push", "create_pr")
            require_ssh: If True, must use SSH (not token)
        
        Returns:
            AuthValidationResult with status, username, permissions
        """
        
        # Try to get Git user config
        username = self._get_git_config("user.name")
        user_email = self._get_git_config("user.email")
        
        if not username or not user_email:
            return AuthValidationResult(
                status=AuthStatus.INVALID,
                auth_method=AuthMethod.UNKNOWN,
                is_authorized=False,
                reasoning="Git user.name or user.email not configured. Run: git config user.name 'Your Name'",
                error_code="MISSING_GIT_CONFIG",
            )
        
        # Detect auth method
        auth_method = self._detect_auth_method(require_ssh)
        
        if auth_method == AuthMethod.UNKNOWN:
            return AuthValidationResult(
                status=AuthStatus.INVALID,
                auth_method=AuthMethod.UNKNOWN,
                is_authorized=False,
                reasoning="No authentication method detected. Configure SSH key or GitHub token.",
                error_code="NO_AUTH_METHOD",
            )
        
        # Check credentials validity
        if auth_method == AuthMethod.SSH_KEY:
            if not self._validate_ssh_key():
                return AuthValidationResult(
                    status=AuthStatus.INVALID,
                    auth_method=AuthMethod.SSH_KEY,
                    is_authorized=False,
                    username=username,
                    user_email=user_email,
                    reasoning="SSH key not found or not readable.",
                    error_code="SSH_KEY_NOT_FOUND",
                )
        
        elif auth_method == AuthMethod.TOKEN:
            # Check if token env var exists
            if not self._has_github_token():
                return AuthValidationResult(
                    status=AuthStatus.INVALID,
                    auth_method=AuthMethod.TOKEN,
                    is_authorized=False,
                    username=username,
                    user_email=user_email,
                    reasoning="GitHub token not set. Set GITHUB_TOKEN environment variable.",
                    error_code="GITHUB_TOKEN_NOT_SET",
                )
        
        # Determine permissions based on branch
        can_push = self._can_push_to_branch(branch)
        can_force_push = self._can_force_push_to_branch(branch)
        
        if not can_push:
            return AuthValidationResult(
                status=AuthStatus.PERMISSION_DENIED,
                auth_method=auth_method,
                is_authorized=False,
                username=username,
                user_email=user_email,
                target_branch=branch,
                reasoning=f"Permission denied: cannot push to '{branch}'.",
                error_code="PERMISSION_DENIED",
            )
        
        # All checks passed
        return AuthValidationResult(
            status=AuthStatus.VALID,
            auth_method=auth_method,
            is_authorized=True,
            username=username,
            user_email=user_email,
            can_push=True,
            can_force_push=can_force_push,
            target_branch=branch,
            reasoning=f"Auth valid. {username} can push to {branch}.",
        )
    
    def _get_git_config(self, key: str) -> Optional[str]:
        """Get Git configuration value."""
        try:
            result = subprocess.run(
                ["git", "config", key],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def _detect_auth_method(self, require_ssh: bool) -> AuthMethod:
        """Detect which authentication method is available."""
        if require_ssh:
            if self._has_ssh_key():
                return AuthMethod.SSH_KEY
            return AuthMethod.UNKNOWN
        
        # Try SSH first
        if self._has_ssh_key():
            return AuthMethod.SSH_KEY
        
        # Fall back to token
        if self._has_github_token():
            return AuthMethod.TOKEN
        
        return AuthMethod.UNKNOWN
    
    def _has_ssh_key(self) -> bool:
        """Check if SSH key exists."""
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        return ssh_key_path.exists()
    
    def _validate_ssh_key(self) -> bool:
        """Validate that SSH key is readable."""
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        try:
            with open(ssh_key_path, 'r') as f:
                f.read(1)  # Just check if readable
            return True
        except Exception:
            return False
    
    def _has_github_token(self) -> bool:
        """Check if GitHub token is set in environment."""
        import os
        return bool(os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN"))
    
    def _can_push_to_branch(self, branch: str) -> bool:
        """Determine if user can push to this branch."""
        # Phase 1b: Simple rules
        # - main: only with valid auth
        # - feature/*: anyone with valid auth
        # - dev: anyone with valid auth
        # Expand this in Phase 2 with role-based rules
        
        protected_branches = ["main", "master"]
        if branch in protected_branches:
            # In Phase 1b, just validate auth; Phase 2 adds role checks
            return True
        
        return True
    
    def _can_force_push_to_branch(self, branch: str) -> bool:
        """Determine if user can force-push to this branch."""
        # Phase 1b: Never allow force-push to main/master
        protected_branches = ["main", "master"]
        return branch not in protected_branches



class AuthValidator:
    """Validates Git credentials and permissions."""

    def validate(
        self,
        branch: str = "main",
        operation: str = "push",
        require_ssh: bool = False,
    ) -> AuthValidationResult:
        """
        Validate Git authentication.
        
        Args:
            branch: Target branch (e.g., "main")
            operation: Operation being performed (e.g., "push", "create_pr")
            require_ssh: If True, must use SSH (not token)
        
        Returns:
            AuthValidationResult with status, username, permissions
        """
        
        # Try to get Git user config
        username = self._get_git_config("user.name")
        user_email = self._get_git_config("user.email")
        
        if not username or not user_email:
            return AuthValidationResult(
                status=AuthStatus.INVALID,
                auth_method=AuthMethod.UNKNOWN,
                is_authorized=False,
                reasoning="Git user.name or user.email not configured. Run: git config user.name 'Your Name'",
                error_code="MISSING_GIT_CONFIG",
            )
        
        # Detect auth method
        auth_method = self._detect_auth_method(require_ssh)
        
        if auth_method == AuthMethod.UNKNOWN:
            return AuthValidationResult(
                status=AuthStatus.INVALID,
                auth_method=AuthMethod.UNKNOWN,
                is_authorized=False,
                reasoning="No authentication method detected. Configure SSH key or GitHub token.",
                error_code="NO_AUTH_METHOD",
            )
        
        # Check credentials validity
        if auth_method == AuthMethod.SSH_KEY:
            if not self._validate_ssh_key():
                return AuthValidationResult(
                    status=AuthStatus.INVALID,
                    auth_method=AuthMethod.SSH_KEY,
                    is_authorized=False,
                    username=username,
                    user_email=user_email,
                    reasoning="SSH key not found or not readable.",
                    error_code="SSH_KEY_NOT_FOUND",
                )
        
        elif auth_method == AuthMethod.TOKEN:
            # Check if token env var exists
            if not self._has_github_token():
                return AuthValidationResult(
                    status=AuthStatus.INVALID,
                    auth_method=AuthMethod.TOKEN,
                    is_authorized=False,
                    username=username,
                    user_email=user_email,
                    reasoning="GitHub token not set. Set GITHUB_TOKEN environment variable.",
                    error_code="GITHUB_TOKEN_NOT_SET",
                )
        
        # Determine permissions based on branch
        can_push = self._can_push_to_branch(branch)
        can_force_push = self._can_force_push_to_branch(branch)
        
        if not can_push:
            return AuthValidationResult(
                status=AuthStatus.PERMISSION_DENIED,
                auth_method=auth_method,
                is_authorized=False,
                username=username,
                user_email=user_email,
                target_branch=branch,
                reasoning=f"Permission denied: cannot push to '{branch}'.",
                error_code="PERMISSION_DENIED",
            )
        
        # All checks passed
        return AuthValidationResult(
            status=AuthStatus.VALID,
            auth_method=auth_method,
            is_authorized=True,
            username=username,
            user_email=user_email,
            can_push=True,
            can_force_push=can_force_push,
            target_branch=branch,
            reasoning=f"Auth valid. {username} can push to {branch}.",
        )
    
    def _get_git_config(self, key: str) -> Optional[str]:
        """Get Git configuration value."""
        try:
            result = subprocess.run(
                ["git", "config", key],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def _detect_auth_method(self, require_ssh: bool) -> AuthMethod:
        """Detect which authentication method is available."""
        if require_ssh:
            if self._has_ssh_key():
                return AuthMethod.SSH_KEY
            return AuthMethod.UNKNOWN
        
        # Try SSH first
        if self._has_ssh_key():
            return AuthMethod.SSH_KEY
        
        # Fall back to token
        if self._has_github_token():
            return AuthMethod.TOKEN
        
        return AuthMethod.UNKNOWN
    
    def _has_ssh_key(self) -> bool:
        """Check if SSH key exists."""
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        return ssh_key_path.exists()
    
    def _validate_ssh_key(self) -> bool:
        """Validate that SSH key is readable."""
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        try:
            with open(ssh_key_path, 'r') as f:
                f.read(1)  # Just check if readable
            return True
        except Exception:
            return False
    
    def _has_github_token(self) -> bool:
        """Check if GitHub token is set in environment."""
        import os
        return bool(os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN"))
    
    def _can_push_to_branch(self, branch: str) -> bool:
        """Determine if user can push to this branch."""
        # Phase 1b: Simple rules
        # - main: only with valid auth
        # - feature/*: anyone with valid auth
        # - dev: anyone with valid auth
        # Expand this in Phase 2 with role-based rules
        
        protected_branches = ["main", "master"]
        if branch in protected_branches:
            # In Phase 1b, just validate auth; Phase 2 adds role checks
            return True
        
        return True
    
    def _can_force_push_to_branch(self, branch: str) -> bool:
        """Determine if user can force-push to this branch."""
        # Phase 1b: Never allow force-push to main/master
        protected_branches = ["main", "master"]
        return branch not in protected_branches
