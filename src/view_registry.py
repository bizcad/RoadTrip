#!/usr/bin/env python3
"""
Skills Registry Viewer: Inspect what skills are available

Shows all discovered skills, their status, and what needs wrappers.
"""

import sys
import yaml
from pathlib import Path


def main():
    registry_file = Path(__file__).parent.parent / "config" / "skills-registry.yaml"
    
    if not registry_file.exists():
        print(f"Registry not found: {registry_file}")
        print("Run: python src/registry_builder.py")
        sys.exit(1)
    
    with open(registry_file, 'r') as f:
        registry = yaml.safe_load(f)
    
    print("\n" + "=" * 70)
    print("SKILLS REGISTRY INVENTORY")
    print("=" * 70)
    
    meta = registry.get("metadata", {})
    print(f"\nTotal Skills: {meta.get('total_skills', 0)}")
    print(f"Ready (executable): {meta.get('ready_skills', 0)}")
    print(f"Discovered (need wrapper): {meta.get('discovered_skills', 0)}")
    print(f"Last scanned: {meta.get('last_scanned', 'unknown')}")
    
    # Show ready skills
    ready_skills = [s for s in registry.get("skills", {}).items() if s[1]["status"] == "ready"]
    if ready_skills:
        print(f"\n{'READY SKILLS (can execute now)':-<70}")
        for name, info in sorted(ready_skills):
            print(f"\n  {name:<20} v{info['version']}")
            print(f"    Description: {info['description']}")
            print(f"    Interface: {info['interface']}")
    
    # Show discovered skills
    discovered = [s for s in registry.get("skills", {}).items() if s[1]["status"] == "discovered"]
    if discovered:
        print(f"\n{'DISCOVERED SKILLS (need execute() wrapper)':-<70}")
        for name, info in sorted(discovered):
            version = info.get("version", "unknown")
            print(f"\n  {name:<20} v{version}")
            print(f"    Description: {info['description']}")
            print(f"    Current Interface: {info['interface']}")
    
    print("\n" + "=" * 70)
    print(f"To add a new skill:")
    print(f"  1. Create src/skills/my_skill.py with execute() function")
    print(f"  2. Run: python src/registry_builder.py")
    print(f"  3. Use in workflow: orchestrator.run_workflow([('my_skill', {{...}})])")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
