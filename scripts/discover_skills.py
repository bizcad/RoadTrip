#!/usr/bin/env python3
"""
discover_skills.py - Discover all skills in the project

Scans src/skills/ for skill Python files and extracts metadata.
Returns list of discovered skills with entry_point and basic info.
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def extract_skill_info(skill_file: Path) -> Dict[str, Any]:
    """
    Extract skill information from a .py file.
    
    Looks for:
    - Docstring (description)
    - @dataclass with capability hints
    - Class definitions
    """
    skill_name = skill_file.stem
    
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            "name": skill_name,
        "entry_point": str(skill_file).replace("\\", "/"),
            "valid": False
        }
    
    # Extract docstring (module-level)
    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    description = ""
    if docstring_match:
        description = docstring_match.group(1).strip().split('\n')[0][:200]
    
    # Look for class definitions
    class_matches = re.findall(r'class (\w+)\(', content)
    
    # Try to find capabilities in docstring or comments
    capabilities = []
    if "capabilities" in content.lower():
        cap_matches = re.findall(r'["\']([\w_]+)["\'].*?capability', content, re.IGNORECASE)
        capabilities = list(set(cap_matches))
    
    return {
        "name": skill_name,
        "entry_point": str(skill_file).replace("\\", "/"),
        "description": description or f"Skill: {skill_name}",
        "classes": class_matches,
        "capabilities": capabilities,
        "valid": True,
        "file_size_bytes": skill_file.stat().st_size
    }


def discover_all_skills(skills_dir: str = "src/skills") -> List[Dict[str, Any]]:
    """
    Discover all skills in the skills directory.
    
    Excludes:
    - __init__.py
    - Files ending with _models.py (data structures)
    - registry and __pycache__
    
    Returns sorted list of skill info dicts
    """
    skills_path = Path(skills_dir)
    
    if not skills_path.exists():
        print(f"❌ Skills directory not found: {skills_path}")
        return []
    
    skills = []
    
    for skill_file in sorted(skills_path.glob("*.py")):
        # Skip non-skill files
        if skill_file.name == "__init__.py":
            continue
        if skill_file.name.endswith("_models.py"):
            continue
        if skill_file.name.startswith("registry"):
            continue
        
        skill_info = extract_skill_info(skill_file)
        skills.append(skill_info)
    
    return sorted(skills, key=lambda s: s["name"])


def print_discovery_report(skills: List[Dict[str, Any]]) -> None:
    """Print human-readable discovery report."""
    print("\n" + "="*70)
    print("SKILL DISCOVERY REPORT")
    print("="*70)
    print(f"\nFound {len(skills)} skills:\n")
    
    for i, skill in enumerate(skills, 1):
        status = "[OK]" if skill.get("valid") else "[WARN]"
        print(f"{i}. {status} {skill['name']}")
        print(f"   Entry Point: {skill['entry_point']}")
        print(f"   Description: {skill['description']}")
        if skill.get('classes'):
            print(f"   Classes: {', '.join(skill['classes'])}")
        if skill.get('capabilities'):
            print(f"   Capabilities: {', '.join(skill['capabilities'])}")
        print()


def main():
    """Main discovery function."""
    skills = discover_all_skills()
    print_discovery_report(skills)
    
    print(f"\n📊 Summary:")
    print(f"   Total Skills Found: {len(skills)}")
    print(f"   Valid: {len([s for s in skills if s.get('valid')])}")
    print(f"   Total Lines: {sum(s.get('file_size_bytes', 0) // 50 for s in skills)} approx\n")
    
    return skills


if __name__ == "__main__":
    main()
