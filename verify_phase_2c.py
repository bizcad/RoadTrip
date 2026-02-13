#!/usr/bin/env python3
"""Verify Phase 2c registry completeness."""

import yaml
from pathlib import Path

def verify_registry():
    """Check registry schema compliance."""
    registry_path = Path("config/skills-registry.yaml")
    
    with open(registry_path) as f:
        data = yaml.safe_load(f)
    
    skills = data.get("skills", {})
    print(f"Total skills in registry: {len(skills)}")
    print(f"Registry version: {data['metadata']['registry_version']}")
    print()
    
    # Check schema compliance
    required_fields = {"fingerprint", "updated", "entry_point"}
    all_valid = True
    
    for name, skill in sorted(skills.items()):
        has_all = all(field in skill for field in required_fields)
        status = "[OK]" if has_all else "[MISSING]"
        print(f"{status} {name:25} | fp: {bool(skill.get('fingerprint')):5} | updated: {bool(skill.get('updated')):5} | entry_point: {bool(skill.get('entry_point')):5}")
        if not has_all:
            missing = [f for f in required_fields if f not in skill]
            print(f"     Missing: {missing}")
            all_valid = False
    
    print()
    if all_valid:
        print("[OK] All skills have required schema fields!")
    else:
        print("[WARN] Some skills missing required fields")
    
    return all_valid

if __name__ == "__main__":
    verify_registry()
