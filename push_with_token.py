#!/usr/bin/env python3
"""
Quick test: Pull token from env, generate commit message, and push.

This is a consolidation test for git_push_autonomous logic.

Usage:
    python push_with_token.py [--dry-run] [--message "custom message"]
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import quote

# Add src to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))


def get_token() -> Optional[str]:
    """Get GitHub token from environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = os.getenv("GITHUB_PAT")
    
    if not token:
        print("[ERROR] No GitHub token found in GITHUB_TOKEN or GITHUB_PAT")
        return None
    
    # Strip any whitespace (including newlines from env vars)
    token = token.strip()
    
    print(f"[OK] Token found (length: {len(token)})")
    return token


def get_staged_files() -> list:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Failed to get staged files: {result.stderr}")
        return []
    
    files = result.stdout.strip().split('\n')
    files = [f for f in files if f]  # Remove empty strings
    
    print(f"[OK] Staged files: {len(files)}")
    for f in files[:5]:
        print(f"     - {f}")
    
    return files


def generate_commit_message(files: list, custom_message: Optional[str] = None) -> str:
    """Generate commit message using commit_message skill."""
    
    if custom_message:
        print(f"[OK] Using custom message: {custom_message}")
        return custom_message
    
    # Use commit_message skill
    # For now, use simple heuristic based on files
    if not files:
        return "docs: update documentation"
    
    # Simple categorization
    py_files = [f for f in files if f.endswith('.py')]
    md_files = [f for f in files if f.endswith('.md')]
    other_files = [f for f in files if f not in py_files and f not in md_files]
    
    if py_files and not md_files and not other_files:
        return f"feat: update Python code ({len(py_files)} files)"
    elif md_files and not py_files and not other_files:
        return f"docs: update documentation ({len(md_files)} files)"
    else:
        return f"build: update multiple files ({len(files)} total)"


def git_push(token: str, message: str, dry_run: bool = False) -> bool:
    """Execute push with token."""
    
    print(f"[INFO] Generated message: {message}")
    
    if dry_run:
        print("[DRY-RUN] Would execute:")
        print(f"  1. git add .")
        print(f"  2. git commit -m '{message}'")
        print(f"  3. git push (with token)")
        return True
    
    # Step 1: git add (already done in main, but safe to re-run)
    print("[STEP 1] git add .")
    result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] git add failed: {result.stderr}")
        return False
    
    # Step 2: git commit (already done, will fail with "nothing to commit", that's OK)
    print(f"[STEP 2] git commit -m '{message}'")
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and "nothing to commit" not in result.stderr.lower():
        print(f"[ERROR] git commit failed: {result.stderr}")
        # Don't fail here; might already be committed
    elif result.returncode == 0:
        print(f"[OK] Committed: {result.stdout.strip()}")
    else:
        print(f"[OK] Already committed (nothing to commit)")
    
    # Step 3: git push with token via credential protocol
    print("[STEP 3] git push (with token)")
    
    # Method: Use git credential helper to inject token
    # This replaces the current credential helper temporarily
    env = os.environ.copy()
    
    # For Windows, try using the simplest method: embed token in URL
    # Get the current remote URL
    remote_result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
    )
    
    if remote_result.returncode == 0:
        remote_url = remote_result.stdout.strip()
        print(f"[DEBUG] Remote: {remote_url}")
        
        # If HTTPS, inject token
        if "https://" in remote_url and "@" not in remote_url:
            # Insert token: https://github.com/owner/repo.git → https://github:TOKEN@github.com/owner/repo.git
            # URL-encode the token to handle special characters
            encoded_token = quote(token, safe='')
            remote_with_token = remote_url.replace(
                "https://",
                f"https://github:{encoded_token}@"
            )
            print(f"[DEBUG] Pushing with token-auth URL")
            
            result = subprocess.run(
                ["git", "push", remote_with_token, "main"],
                capture_output=True,
                text=True,
                env=env,
            )
        else:
            # Already has token or is SSH, just push normally
            result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                env=env,
            )
    else:
        # Fallback: just try normal push
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            env=env,
        )
    
    if result.returncode != 0:
        print(f"[ERROR] git push failed: {result.stderr}")
        return False
    
    print(f"[OK] Pushed successfully")
    if result.stdout:
        print(result.stdout)
    
    return True


def main():
    """Main workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Push with token + auto-generated commit message")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually push")
    parser.add_argument("--message", help="Custom commit message")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("WORKFLOW: Get Token -> Stage -> Commit -> Push")
    print("=" * 60)
    
    # Step 1: Get token
    print("\n[STEP 1] Get GitHub token from environment")
    token = get_token()
    if not token:
        sys.exit(1)
    
    # Step 2: Get staged files
    print("\n[STEP 2] Check staged files")
    files = get_staged_files()
    
    # Step 3: Generate commit message
    print("\n[STEP 3] Generate commit message")
    message = generate_commit_message(files, args.message)
    
    # Step 4: Push
    print("\n[STEP 4] Execute push")
    success = git_push(token, message, dry_run=args.dry_run)
    
    if success:
        print("\n[SUCCESS] Push workflow complete")
        sys.exit(0)
    else:
        print("\n[FAILED] Push workflow failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
