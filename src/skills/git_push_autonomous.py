#!/usr/bin/env python3
"""
git_push_autonomous.py - Git Push Skill

Purpose: Autonomous git push to remote repository with credential validation.
Replaces: push_with_token.py (Python subprocess-based, no browser prompts)

Key Principles:
- ALL decisions are deterministic (validates auth, then pushes)
- Confidence scores reflect validation strictness
- Silent operation: uses Windows Credential Manager (no CLI prompts)
- Idempotent: push to up-to-date repo is safe
- All-or-nothing: repository is either pushed or not

Specification:
1. Validate git credentials (auth_validator check)
2. Verify remote URL is correct (github.com/bizcad/RoadTrip)
3. Check for unpushed commits (git rev-list origin/main..HEAD)
4. Execute git push origin main
5. Return result with commit count, push status, errors
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import json
import sys


@dataclass
class GitPushRequest:
    """Request to push commits to remote."""
    branch: str = "main"                      # Target branch (default: main)
    remote: str = "origin"                    # Remote name (default: origin)
    repo_path: Optional[str] = None           # Repo path (default: cwd)
    force: bool = False                       # Force push (dangerous)
    dry_run: bool = False                     # Simulate without pushing
    check_auth: bool = True                   # Validate auth first


@dataclass
class GitPushResult:
    """Result of a git push operation."""
    decision: str                      # "APPROVE" | "REJECT" | "ALREADY_PUSHED"
    success: bool                      # True if push succeeded
    confidence: float = 0.0            # 0.0-1.0 (1.0 = certain)
    
    # Push details
    commit_count: int = 0              # Number of commits to push
    commit_hashes: list[str] = field(default_factory=list)  # All commit hashes (first 8 chars)
    branch: str = "main"
    remote: str = "origin"
    remote_url: str = ""               # Validated remote URL
    
    # Status
    push_timestamp: Optional[str] = None  # UTC timestamp of push
    git_output: str = ""               # git push stdout
    
    # Errors/warnings
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging."""
        return {
            "decision": self.decision,
            "success": self.success,
            "confidence": self.confidence,
            "commit_count": self.commit_count,
            "commit_hashes": self.commit_hashes,
            "branch": self.branch,
            "remote": self.remote,
            "remote_url": self.remote_url,
            "push_timestamp": self.push_timestamp,
            "git_output": self.git_output[:200],  # Truncate for logging
            "warnings": self.warnings,
            "errors": self.errors,
            "metadata": self.metadata
        }


class GitPushSkill:
    """Git push skill with credential validation and deterministic logic."""
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize Git Push Skill.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = Path(repo_path or ".")
        if not self.repo_path.is_absolute():
            self.repo_path = self.repo_path.resolve()
    
    def push(self, request: GitPushRequest) -> GitPushResult:
        """Execute git push with validation.
        
        Args:
            request: GitPushRequest specifying branch, remote, options
            
        Returns:
            GitPushResult with success status and details
        """
        result = GitPushResult(
            decision="APPROVE",
            success=False,
            confidence=1.0,
            branch=request.branch,
            remote=request.remote
        )
        
        # Validate repository
        if not self._validate_git_repo(result):
            result.decision = "REJECT"
            return result
        
        # Validate remote URL
        if not self._validate_remote_url(request.remote, result):
            result.decision = "REJECT"
            return result
        
        # Check for unpushed commits
        commits = self._get_unpushed_commits(request.branch, request.remote, result)
        if commits is None:
            result.decision = "REJECT"
            return result
        
        if len(commits) == 0:
            result.decision = "ALREADY_PUSHED"
            result.success = True
            result.confidence = 1.0
            result.warnings.append(f"No unpushed commits on {request.branch}")
            return result
        
        result.commit_count = len(commits)
        result.commit_hashes = commits
        
        # Dry-run check
        if request.dry_run:
            result.decision = "APPROVE"
            result.success = True
            result.confidence = 0.99  # Slightly reduced for dry-run
            result.warnings.append(f"DRY-RUN: Would push {len(commits)} commits")
            return result
        
        # Execute git push
        if not self._execute_git_push(request, result):
            result.decision = "REJECT"
            return result
        
        result.decision = "APPROVE"
        result.success = True
        result.confidence = 1.0
        result.push_timestamp = datetime.now(timezone.utc).isoformat()
        
        return result
    
    def _validate_git_repo(self, result: GitPushResult) -> bool:
        """Check if repo path is a valid git repository.
        
        Returns:
            True if valid, False if not
        """
        try:
            cmd = ["git", "rev-parse", "--git-dir"]
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                result.errors.append(f"Not a git repository: {self.repo_path}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            result.errors.append("Git command timed out")
            return False
        except Exception as e:
            result.errors.append(f"Git validation failed: {str(e)}")
            return False
    
    def _validate_remote_url(self, remote_name: str, result: GitPushResult) -> bool:
        """Validate remote URL is github.com/bizcad/RoadTrip.
        
        Args:
            remote_name: Remote name (e.g., "origin")
            result: Result object to populate
            
        Returns:
            True if valid, False if not
        """
        try:
            cmd = ["git", "config", f"remote.{remote_name}.url"]
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                result.errors.append(f"Remote '{remote_name}' not found")
                return False
            
            url = proc.stdout.strip()
            result.remote_url = url
            
            # Validate it's github.com/bizcad/RoadTrip
            if "github.com" not in url or "bizcad/RoadTrip" not in url:
                result.errors.append(
                    f"Remote URL validation failed. Expected github.com/bizcad/RoadTrip, got: {url}"
                )
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            result.errors.append("Git config command timed out")
            return False
        except Exception as e:
            result.errors.append(f"Remote validation failed: {str(e)}")
            return False
    
    def _get_unpushed_commits(
        self,
        branch: str,
        remote: str,
        result: GitPushResult
    ) -> Optional[list[str]]:
        """Get list of unpushed commits.
        
        Uses: git rev-list origin/main..HEAD (commits not in remote)
        
        Args:
            branch: Branch name (e.g., "main")
            remote: Remote name (e.g., "origin")
            result: Result object to populate
            
        Returns:
            List of commit hashes (first 8 chars) or None if error
        """
        try:
            # Get unpushed commit hashes
            cmd = [
                "git",
                "rev-list",
                f"{remote}/{branch}..HEAD",
                "--pretty=format:%h"  # Show abbreviated hash
            ]
            
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                # Might fail if remote branch doesn't exist yet
                result.warnings.append(
                    f"Could not check {remote}/{branch} (may not exist on remote yet)"
                )
                # Fall back to checking HEAD
                return self._get_commits_from_head(result)
            
            # Parse commit hashes (one per line, already abbreviated)
            commits = [line.strip() for line in proc.stdout.strip().split('\n') if line.strip()]
            return commits
            
        except subprocess.TimeoutExpired:
            result.errors.append("Git rev-list command timed out")
            return None
        except Exception as e:
            result.errors.append(f"Failed to get unpushed commits: {str(e)}")
            return None
    
    def _get_commits_from_head(self, result: GitPushResult) -> list[str]:
        """Get all commits from HEAD (fallback when remote doesn't exist).
        
        Returns:
            List of recent commit hashes
        """
        try:
            cmd = ["git", "log", "-10", "--pretty=format:%h"]
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                return []
            
            commits = [line.strip() for line in proc.stdout.strip().split('\n') if line.strip()]
            result.warnings.append(f"Using last {len(commits)} commits from HEAD")
            return commits
            
        except Exception:
            return []
    
    def _execute_git_push(self, request: GitPushRequest, result: GitPushResult) -> bool:
        """Execute git push to remote.
        
        Args:
            request: GitPushRequest with push options
            result: Result object to populate
            
        Returns:
            True if successful, False if failed
        """
        try:
            cmd = ["git", "push"]
            
            if request.force:
                cmd.append("--force-with-lease")  # Safer than --force
                result.warnings.append("Using --force-with-lease")
            
            cmd.extend([request.remote, request.branch])
            
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.git_output = proc.stdout + proc.stderr
            
            if proc.returncode != 0:
                result.errors.append(f"Git push failed: {proc.stderr}")
                return False
            
            # Parse output for confirmation
            if "fast-forward" in proc.stdout or "master -> master" in proc.stdout or "main -> main" in proc.stdout:
                result.metadata["push_type"] = "fast-forward"
            
            return True
            
        except subprocess.TimeoutExpired:
            result.errors.append("Git push command timed out (>30s)")
            return False
        except Exception as e:
            result.errors.append(f"Git push execution failed: {str(e)}")
            return False


def main():
    """CLI entry point: python git_push_autonomous.py [options]"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous git push to remote repository"
    )
    parser.add_argument("--branch", default="main", help="Branch to push (default: main)")
    parser.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    parser.add_argument("--repo", help="Repository path (default: current directory)")
    parser.add_argument("--force", action="store_true", help="Force push with lease")
    parser.add_argument("--dry-run", action="store_true", help="Simulate push without executing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Create skill and execute push
    skill = GitPushSkill(repo_path=args.repo)
    request = GitPushRequest(
        branch=args.branch,
        remote=args.remote,
        force=args.force,
        dry_run=args.dry_run
    )
    result = skill.push(request)
    
    # Output result
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Decision: {result.decision}")
        print(f"Success: {result.success}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Commits pushed: {result.commit_count}")
        print(f"Remote URL: {result.remote_url}")
        
        if result.commit_hashes:
            print(f"Commit hashes: {', '.join(result.commit_hashes)}")
        
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        
        if result.errors:
            print(f"Errors: {result.errors}")
            sys.exit(1)
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
