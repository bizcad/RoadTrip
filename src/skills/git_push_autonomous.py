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
import re
import uuid
import os

from src.skills.auth_validator import AuthValidator
from src.skills.commit_message import CommitMessageSkill
from src.skills.rules_engine import evaluate as evaluate_rules
from src.skills.telemetry_logger import TelemetryLogger
from src.skills.telemetry_logger_models import TelemetryEntry


def _git_env() -> dict[str, str]:
    """Build environment for headless git subprocess calls.

    When git runs inside a subprocess with capture_output=True it has no
    attached terminal.  Without the fixes below GCM tries to pick an account
    interactively and fails with 'Cannot prompt because user interactivity has
    been disabled'.

    Three changes are required together:
    1. GCM_INTERACTIVE=never  — tells GCM to skip any interactive flow.
    2. GIT_TERMINAL_PROMPT=0  — tells git itself not to prompt on the terminal.
    3. Remove GIT_ASKPASS / SSH_ASKPASS — these point to a GUI helper
       (git-askpass.exe) that cannot run headlessly; removing them lets GCM
       reach the Windows Credential Store directly.

    Pre-requisites (one-time git config, already set on this machine):
      git config --global credential.helper manager
      git config --global credential.credentialStore wincredman
      git config --global credential.https://github.com.username <username>
    Without the username entry GCM cannot select the stored PAT silently.
    """
    env = dict(os.environ)
    env["GCM_INTERACTIVE"] = "never"
    env["GIT_TERMINAL_PROMPT"] = "0"
    env.pop("GIT_ASKPASS", None)
    env.pop("SSH_ASKPASS", None)
    return env


@dataclass
class GitPushRequest:
    """Request to push commits to remote."""
    branch: str = "main"                      # Target branch (default: main)
    remote: str = "origin"                    # Remote name (default: origin)
    repo_path: Optional[str] = None           # Repo path (default: cwd)
    force: bool = False                       # Force push (dangerous)
    dry_run: bool = False                     # Simulate without pushing
    check_auth: bool = True                   # Validate auth first
    push_timeout_seconds: int = 60            # Timeout for git push


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
                timeout=5,
                env=_git_env(),
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
                timeout=5,
                env=_git_env(),
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
                timeout=5,
                env=_git_env(),
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
                timeout=5,
                env=_git_env(),
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
            cmd = ["git", "-c", "credential.interactive=never", "push"]
            
            if request.force:
                cmd.append("--force-with-lease")  # Safer than --force
                result.warnings.append("Using --force-with-lease")
            
            cmd.extend([request.remote, request.branch])
            
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=request.push_timeout_seconds,
                env=_git_env(),
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
            result.errors.append(
                f"Git push command timed out (>{request.push_timeout_seconds}s). "
                "Set push_timeout_seconds higher if network is slow."
            )
            return False
        except Exception as e:
            result.errors.append(f"Git push execution failed: {str(e)}")
            return False


__version__ = "1.2.0"


def _run_git(repo_path: Path, args: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a git command in the repository path."""
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_git_env(),
    )


def _parse_status_paths(status_output: str) -> list[str]:
    """Parse file paths from `git status --porcelain` output."""
    files: list[str] = []
    for raw_line in status_output.splitlines():
        if not raw_line:
            continue

        line = raw_line.rstrip("\n")
        if len(line) < 4:
            continue

        path_part = line[3:].strip()
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1].strip()

        if path_part:
            files.append(path_part)

    seen: set[str] = set()
    ordered_unique: list[str] = []
    for file_path in files:
        if file_path not in seen:
            seen.add(file_path)
            ordered_unique.append(file_path)
    return ordered_unique


def _match_push_prompt(prompt: str) -> bool:
    """Return True when prompt is a push intent for latest/local changes."""
    normalized = (prompt or "").strip().lower()
    if not normalized:
        return False

    patterns = (
        r"\bpush\s+my\s+changes\b",
        r"\bpush\s+changes\b",
        r"\bpush\s+the\s+latest\s+changes\b",
        r"\bplease\s+push\s+the\s+latest\s+changes\b",
        r"\bgit\s+push\b",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)


def _stage_and_commit(
    repo_path: Path,
    commit_message: str,
) -> Dict[str, Any]:
    """Stage all changes and commit when there is staged content."""
    add_proc = _run_git(repo_path, ["add", "-A"], timeout=20)
    if add_proc.returncode != 0:
        return {
            "success": False,
            "committed": False,
            "error": f"git add failed: {add_proc.stderr.strip()}",
        }

    staged_proc = _run_git(repo_path, ["diff", "--cached", "--name-only"], timeout=10)
    if staged_proc.returncode != 0:
        return {
            "success": False,
            "committed": False,
            "error": f"git diff --cached failed: {staged_proc.stderr.strip()}",
        }

    staged_files = [line.strip() for line in staged_proc.stdout.splitlines() if line.strip()]
    if not staged_files:
        return {
            "success": True,
            "committed": False,
            "commit_hash": "",
            "staged_files": [],
        }

    commit_proc = _run_git(repo_path, ["commit", "-m", commit_message], timeout=20)
    if commit_proc.returncode != 0:
        return {
            "success": False,
            "committed": False,
            "error": f"git commit failed: {commit_proc.stderr.strip()}",
            "staged_files": staged_files,
        }

    hash_proc = _run_git(repo_path, ["rev-parse", "--short", "HEAD"], timeout=10)
    commit_hash = hash_proc.stdout.strip() if hash_proc.returncode == 0 else ""

    return {
        "success": True,
        "committed": True,
        "commit_hash": commit_hash,
        "staged_files": staged_files,
        "git_output": (commit_proc.stdout + commit_proc.stderr).strip(),
    }


def execute(input_data: dict) -> dict:
    """Execute full git-push-autonomous chain with deterministic safety gates."""
    prompt = input_data.get("prompt", "")
    if prompt and not _match_push_prompt(prompt):
        return {
            "decision": "SKIPPED",
            "success": False,
            "reason": "Prompt does not match git-push-autonomous intent.",
            "prompt": prompt,
        }

    repo_path = Path(input_data.get("repo_path", ".")).resolve()
    branch = input_data.get("branch", "main")
    remote = input_data.get("remote", "origin")
    dry_run = bool(input_data.get("dry_run", False))
    force = bool(input_data.get("force", False))
    push_timeout_seconds = int(input_data.get("push_timeout_seconds", 60))
    log_file = input_data.get("log_file", "data/telemetry.jsonl")
    commit_strategy_path = input_data.get(
        "commit_strategy_path",
        str(repo_path / "config" / "commit-strategy.yaml"),
    )
    workflow_id = f"git-push-{uuid.uuid4().hex[:8]}"

    result: Dict[str, Any] = {
        "workflow_id": workflow_id,
        "decision": "REJECT",
        "success": False,
        "prompt": prompt,
        "prompt_matched": True,
        "repo_path": str(repo_path),
        "branch": branch,
        "remote": remote,
        "dry_run": dry_run,
        "push_timeout_seconds": push_timeout_seconds,
        "changed_files": [],
        "errors": [],
        "warnings": [],
    }

    def _log(decision: str, reasoning: str, artifacts: Optional[dict] = None) -> None:
        try:
            logger = TelemetryLogger()
            entry = TelemetryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                workflow_id=workflow_id,
                decision_id=f"git-push-autonomous-{uuid.uuid4().hex[:8]}",
                skill="git_push_autonomous",
                operation="execute",
                input_summary={
                    "branch": branch,
                    "remote": remote,
                    "dry_run": dry_run,
                    "push_timeout_seconds": push_timeout_seconds,
                    "prompt": prompt,
                },
                decision=decision,
                confidence=1.0,
                reasoning=reasoning,
                artifacts=artifacts or {},
            )
            logger_result = logger.log_entry(entry, log_file)
            result["telemetry"] = {
                "success": logger_result.success,
                "log_file": logger_result.log_file,
                "total_entries": logger_result.total_entries,
            }
        except Exception as telemetry_error:
            result["warnings"].append(f"Telemetry logging failed: {telemetry_error}")

    try:
        status_proc = _run_git(repo_path, ["status", "--porcelain"], timeout=10)
        if status_proc.returncode != 0:
            error = f"git status failed: {status_proc.stderr.strip()}"
            result["errors"].append(error)
            _log("ERROR", error)
            return result

        changed_files = _parse_status_paths(status_proc.stdout)
        result["changed_files"] = changed_files

        auth_result = AuthValidator().validate(branch=branch, operation="push")
        result["auth"] = auth_result.to_dict()
        if not auth_result.is_valid_and_authorized():
            result["errors"].append(auth_result.reasoning)
            _log("DENIED", auth_result.reasoning, {"auth": auth_result.to_dict()})
            return result

        rules_result = evaluate_rules(files=changed_files, repo_root=str(repo_path))
        result["rules"] = {
            "decision": rules_result.decision,
            "approved_files": rules_result.approved_files,
            "blocked_files": [
                {
                    "path": blocked.path,
                    "reason": blocked.reason,
                    "matched_rule": blocked.matched_rule,
                }
                for blocked in rules_result.blocked_files
            ],
            "confidence": rules_result.confidence,
            "warnings": rules_result.warnings,
        }
        result["warnings"].extend(rules_result.warnings)

        if rules_result.decision != "APPROVE":
            blocked_reason = "Files blocked by safety rules"
            result["errors"].append(blocked_reason)
            _log("DENIED", blocked_reason, {"rules": result["rules"]})
            return result

        commit_result = {
            "success": True,
            "committed": False,
            "commit_hash": "",
            "message": input_data.get("message", ""),
            "staged_files": [],
        }

        if changed_files:
            message = input_data.get("message")
            if not message:
                commit_skill = CommitMessageSkill(config_path=commit_strategy_path)
                generated = commit_skill.generate(staged_files=changed_files)
                message = generated.message
                commit_result["generator"] = {
                    "approach": str(generated.approach_used.value),
                    "confidence": generated.confidence,
                }

            commit_result["message"] = message
            commit_result = {
                **commit_result,
                **_stage_and_commit(repo_path=repo_path, commit_message=message),
            }

            if not commit_result.get("success", False):
                result["errors"].append(commit_result.get("error", "Commit failed"))
                result["commit"] = commit_result
                _log("ERROR", "Commit step failed", {"commit": commit_result})
                return result

        result["commit"] = commit_result

        push_skill = GitPushSkill(repo_path=str(repo_path))
        push_request = GitPushRequest(
            branch=branch,
            remote=remote,
            force=force,
            dry_run=dry_run,
            push_timeout_seconds=push_timeout_seconds,
        )
        push_result = push_skill.push(push_request)
        result["push"] = push_result.to_dict()
        result["decision"] = push_result.decision
        result["success"] = push_result.success
        result["warnings"].extend(push_result.warnings)
        result["errors"].extend(push_result.errors)

        log_decision = "APPROVED" if push_result.success else "DENIED"
        _log(log_decision, f"Push decision: {push_result.decision}", {"push": result["push"]})
        return result

    except Exception as exc:
        result["errors"].append(str(exc))
        _log("ERROR", f"Unhandled exception: {exc}")
        return result


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
    parser.add_argument("--push-timeout-seconds", type=int, default=60, help="Timeout for git push (default: 60)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Create skill and execute push
    skill = GitPushSkill(repo_path=args.repo)
    request = GitPushRequest(
        branch=args.branch,
        remote=args.remote,
        force=args.force,
        dry_run=args.dry_run,
        push_timeout_seconds=args.push_timeout_seconds,
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
