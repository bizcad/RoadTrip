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
        print("Safer first step: python src/registry_builder.py --verify")
        print("If registry file is truly missing, restore from git before full rebuild.")
        sys.exit(1)
    
    with open(registry_file, 'r') as f:
        registry = yaml.safe_load(f)
    
    print("\n" + "=" * 70)
    print("SKILLS REGISTRY INVENTORY")
    print("=" * 70)
    
    meta = registry.get("metadata", {})
    skills = registry.get("skills", {})

    total_skills = len(skills)
    ready_statuses = {"ready", "active"}
    ready_skills = [
        item for item in skills.items()
        if item[1].get("status", "").lower() in ready_statuses
    ]
    discovered = [
        item for item in skills.items()
        if item[1].get("status", "").lower() == "discovered"
    ]

    print(f"\nTotal Skills: {total_skills}")
    print(f"Ready (executable): {len(ready_skills)}")
    print(f"Discovered (need wrapper): {len(discovered)}")
    print(f"Last scanned: {meta.get('last_scanned', 'unknown')}")
    
    # Show ready/active skills
    if ready_skills:
        print(f"\n{'READY/ACTIVE SKILLS (can execute now)':-<70}")
        for name, info in sorted(ready_skills):
            print(f"\n  {name:<20} v{info['version']}")
            print(f"    Description: {info['description']}")
            interface = info.get("interface") or info.get("entry_point", "unknown")
            print(f"    Interface: {interface}")
    
    # Show discovered skills
    if discovered:
        print(f"\n{'DISCOVERED SKILLS (need execute() wrapper)':-<70}")
        for name, info in sorted(discovered):
            version = info.get("version", "unknown")
            print(f"\n  {name:<20} v{version}")
            print(f"    Description: {info['description']}")
            print(f"    Current Interface: {info.get('interface', 'unknown')}")
    
    print("\n" + "=" * 70)
    print("Safe exploration tips:")
    print("  1. View registry (read-only): python src/view_registry.py")
    print("  2. Check drift (read-only): python src/registry_builder.py --verify")
    print("  3. For any registry mutation, use reviewed scripts/docs only")
    print("  4. Avoid direct workflow execution from terminal while exploring")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
