#!/usr/bin/env python3
"""
Use the commit_message skill to generate a proper commit message, 
then commit and push changes using GitHub CLI with PAT token.
"""

import sys
import subprocess
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skills.commit_message import CommitMessageSkill

def main():
    print("=" * 70)
    print("Using Python Skills to Commit and Push Updates")
    print("=" * 70)
    
    # Load PAT token from ProjectSecrets
    pat_file = Path(__file__).parent.parent / "ProjectSecrets" / "PAT.txt"
    if not pat_file.exists():
        print(f"❌ PAT file not found: {pat_file}")
        return 1
    
    pat_token = pat_file.read_text().strip()
    print(f"\n✅ Loaded PAT token from {pat_file}")
    
    # Initialize the skill
    skill = CommitMessageSkill()
    
    # Step 1: Get list of changed files
    print("\n[Step 1/3] Detecting changed files...")
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to get git status: {result.stderr}")
        return 1
    
    # Parse changed files
    changed_files = []
    for line in result.stdout.strip().split('\n'):
        if line and not line.startswith('??'):  # Ignore untracked files
            filepath = line[3:].strip()
            changed_files.append(filepath)
    
    msg = None
    
    if not changed_files:
        print("✅ No uncommitted changes to stage")
        print("  → Proceeding directly to push any unpushed commits...")
        msg = "chore: push unpushed commits"
    else:
        print(f"✅ Found {len(changed_files)} changed file(s): {', '.join(changed_files[:3])}")
        
        # Step 2: Generate commit message using the skill
        print("\n[Step 2/3] Generating commit message with commit_message skill...")
        
        commit_message = skill.generate(
            staged_files=changed_files,
            diff="",
            user_message=None,
            dry_run=False
        )
        msg = commit_message.message if hasattr(commit_message, 'message') else str(commit_message)
        print(f"✅ Generated commit message:\n   {msg}")
    
    # Step 3: Make the actual git commit and push
    print("\n[Step 3/3] Committing and pushing...")
    
    try:
        commit_hash = None
        
        # Only commit if there are staged changes
        if changed_files:
            # Stage all changed files
            print(f"  → Staging {len(changed_files)} file(s)...")
            subprocess.run(
                ["git", "add"] + changed_files,
                cwd=Path(__file__).parent.parent,
                check=True,
                capture_output=True
            )
            
            # Commit with the generated message
            print(f"  → Creating commit with message: {msg[:50]}...")
            result = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Commit failed: {result.stderr}")
                return 1
            
            # Extract commit hash
            commit_output = result.stdout.strip()
            commit_hash = commit_output.split()[2] if ' ' in commit_output else "unknown"
            print(f"✅ Commit created: {commit_hash}")
        else:
            print("  → Skipping commit (no staged changes)")
        
        # Configure silent authentication and push
        print("  → Configuring silent authentication with GIT_ASKPASS...")
        
        # Set up environment with GIT_ASKPASS pointing to our helper script
        push_env = os.environ.copy()
        push_env['GIT_ASKPASS'] = str(Path(__file__).parent / "git_askpass_helper.py")
        push_env['GIT_ASKPASS_TOKEN'] = pat_token
        push_env['SSH_ASKPASS_REQUIRE'] = 'never'
        push_env['DISPLAY'] = ':0'  # Indicate to use stdio, not X11
        
        # Push using normal origin URL (git will use GIT_ASKPASS for password)
        print("  → Pushing to origin/main...")
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
            env=push_env
        )
        
        if result.returncode != 0:
            print(f"❌ Push failed: {result.stderr if result.stderr else result.stdout}")
            return 1
        
        print(f"✅ Push successful")
        
        # Show final status
        print("\n" + "=" * 70)
        print("SUCCESS: Changes committed and pushed using Python skills")
        print("=" * 70)
        
        # Show recent commits
        result = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print("\nRecent commits:")
        print(result.stdout)
        
        return 0
        
    except subprocess.TimeoutExpired:
        print("❌ Push timed out")
        return 1
    except Exception as e:
        print(f"❌ Error during commit/push: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
