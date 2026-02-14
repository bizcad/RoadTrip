"""
Quick prototype: Clone 3 MCPs and validate structure

This is a proof-of-concept for Week 2's MCPInspector.clone_and_introspect() workflow.
Tests:
- Can we clone from GitHub?
- Do clones land in the right place?
- Can we find server.json?
- What does a minimal health check look like?

Run: py scripts/prototype_mcp_clone_loop.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional
import subprocess
import sys
import os

# Configure paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
CLONED_REPOS_DIR = DATA_DIR / "ClonedRepos"
CANDIDATES_FILE = DATA_DIR / "mcp_candidates.json"


def load_candidates(limit: int = 3) -> List[dict]:
    """Load top N candidates from mcp_candidates.json"""
    if not CANDIDATES_FILE.exists():
        print(f"❌ ERROR: {CANDIDATES_FILE} not found")
        return []
    
    with open(CANDIDATES_FILE) as f:
        data = json.load(f)
    
    servers = data.get("servers", [])
    return servers[:limit]


def clone_mcp(name: str, repo_url: str, target_dir: Path) -> bool:
    """Clone an MCP repo using git with GITHUB_TOKEN auth"""
    if target_dir.exists():
        print(f"  ⚠️  Already cloned, skipping: {target_dir.name}")
        return True
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Use GITHUB_TOKEN if available for authentication
    token = os.getenv("GITHUB_TOKEN", "").strip()  # Strip whitespace/newlines
    if token and "github.com" in repo_url:
        # Insert token into URL: https://token@github.com/...
        repo_url = repo_url.replace("https://github.com/", f"https://{token}@github.com/")
    
    try:
        print(f"  🔄 Cloning {repo_url[:50]}..." if token else f"  🔄 Cloning {repo_url}...")
        result = subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if result.returncode != 0:
            print(f"  ❌ Clone failed: {result.stderr[:200]}")
            return False
        
        print(f"  ✅ Cloned successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Clone timed out (>60s)")
        return False
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:200]}")
        return False


def health_check(clone_dir: Path) -> dict:
    """Check if clone has expected MCP structure"""
    checks = {
        "has_server_json": False,
        "has_package_json": False,
        "has_git": False,
        "files": [],
    }
    
    if not clone_dir.exists():
        return checks
    
    # List files
    try:
        files = list(clone_dir.glob("*"))[:10]  # First 10 files
        checks["files"] = [f.name for f in files]
    except Exception as e:
        checks["error"] = str(e)
    
    # Check for key files
    checks["has_server_json"] = (clone_dir / "server.json").exists()
    checks["has_package_json"] = (clone_dir / "package.json").exists()
    checks["has_git"] = (clone_dir / ".git").is_dir()
    
    return checks


def main():
    """Run the prototype clone loop"""
    print("\n" + "=" * 80)
    print("MCP CLONE PROTOTYPE - Testing Week 2 Introspection Strategy")
    print("=" * 80)
    
    # Load candidates
    print("\n📋 Loading MCP candidates...")
    candidates = load_candidates(limit=3)
    
    if not candidates:
        print("❌ No candidates found")
        return False
    
    print(f"✅ Loaded {len(candidates)} candidates")
    
    # Ensure clone directory exists
    CLONED_REPOS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Using clone directory: {CLONED_REPOS_DIR}")
    
    # Clone each candidate
    results = []
    for i, mcp in enumerate(candidates, 1):
        name = mcp.get("name", f"unknown-{i}")
        repo_url = mcp.get("repository", "")
        
        print(f"\n[{i}/{len(candidates)}] {name}")
        print(f"  Repository: {repo_url}")
        
        if not repo_url:
            print(f"  ❌ No repository URL")
            results.append({
                "name": name,
                "status": "failed",
                "reason": "no_url",
            })
            continue
        
        # Clone
        clone_dir = CLONED_REPOS_DIR / name
        clone_success = clone_mcp(name, repo_url, clone_dir)
        
        if not clone_success:
            results.append({
                "name": name,
                "status": "failed",
                "reason": "clone_failed",
            })
            continue
        
        # Health check
        print(f"  🔍 Running health check...")
        checks = health_check(clone_dir)
        
        result = {
            "name": name,
            "status": "success",
            "clone_path": str(clone_dir),
            "health_check": checks,
        }
        
        # Summary
        if checks["has_server_json"]:
            print(f"  ✅ Has server.json")
        else:
            print(f"  ⚠️  Missing server.json")
        
        if checks["has_git"]:
            print(f"  ✅ Has .git (can track history)")
        
        print(f"  📦 Files found: {len(checks['files'])} (showing first 10)")
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("PROTOTYPE RESULTS")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n✅ Successful clones: {success_count}/{len(candidates)}")
    
    # Show server.json findings
    server_json_found = sum(
        1 for r in results 
        if r.get("health_check", {}).get("has_server_json")
    )
    print(f"🔍 MCPs with server.json: {server_json_found}/{success_count}")
    
    # Detailed results
    print("\nDetailed Results:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"\n{status_icon} {result['name']}")
        if result["status"] == "success":
            checks = result.get("health_check", {})
            print(f"   - server.json: {checks.get('has_server_json')}")
            print(f"   - package.json: {checks.get('has_package_json')}")
            print(f"   - .git: {checks.get('has_git')}")
            print(f"   - Path: {result['clone_path']}")
        else:
            print(f"   Reason: {result.get('reason')}")
    
    # What we learned
    print("\n" + "=" * 80)
    print("LESSONS FOR WEEK 2")
    print("=" * 80)
    
    if success_count > 0:
        print("\n✅ GitHub cloning works")
        if server_json_found > 0:
            print("✅ Real MCPs have server.json in expected location")
        else:
            print("⚠️  Some MCPs missing server.json - need fallback strategy")
        print("✅ data/ClonedRepos/ is the right location")
    else:
        print("\n❌ GitHub cloning failed - may need authentication token")
        print("   Check: GITHUB_TOKEN environment variable")
    
    # Next steps
    print("\n📋 Next Steps for Week 2:")
    print("  1. Use cloning approach from this prototype")
    print("  2. Build MCPInspector with parse_server_json()")
    print("  3. Extract tools and capabilities")
    print("  4. Store results in analysis.json")
    
    print("\n" + "=" * 80 + "\n")
    
    return success_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
