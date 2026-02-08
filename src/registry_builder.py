#!/usr/bin/env python3
"""
Registry Builder: Scan skills directory and build skills-registry.yaml

Usage:
    python src/registry_builder.py              # Scan and update registry
    python src/registry_builder.py --verify     # Verify registry is current
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
import inspect


def scan_skills_directory(skills_dir: Path) -> dict:
    """
    Scan skills directory and extract metadata from each skill module.
    
    Returns:
        dict: {skill_name: {version, description, interface, status}}
    """
    skills = {}
    
    for py_file in sorted(skills_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        
        skill_name = py_file.stem
        
        try:
            # Read file to extract metadata
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract version
            version = "unknown"
            if '__version__' in content:
                for line in content.split('\n'):
                    if '__version__' in line and '=' in line:
                        version = line.split('=')[1].strip().strip('"\'')
                        break
            
            # Extract docstring (description)
            docstring = ""
            if '"""' in content:
                parts = content.split('"""')
                if len(parts) >= 2:
                    docstring = parts[1].strip().split('\n')[0]
            
            # Determine status based on what functions exist
            has_execute = "def execute(" in content
            has_evaluate = "def evaluate(" in content
            has_resolve = "def resolve_" in content
            
            if has_execute:
                status = "ready"
                interface = "execute(input_data: dict) -> dict"
            elif has_evaluate:
                status = "discovered"
                interface = "(needs wrapper)"
            elif has_resolve or has_evaluate:
                status = "discovered"
                interface = "(needs wrapper)"
            else:
                status = "discovered"
                interface = "(utility function)"
            
            skills[skill_name] = {
                "version": version,
                "description": docstring or f"Skill: {skill_name}",
                "interface": interface,
                "status": status,
                "file": py_file.name,
            }
            
            print(f"[OK] Scanned {skill_name:<25} v{version:<8} status={status}")
            
        except Exception as e:
            print(f"[WARN] Failed to scan {skill_name}: {e}")
    
    return skills


def build_registry(skills_dir: Path = None, output_file: Path = None) -> dict:
    """
    Build complete skills registry and write to file.
    
    Returns:
        dict: Complete registry structure
    """
    if skills_dir is None:
        skills_dir = Path(__file__).parent / "skills"
    if output_file is None:
        output_file = Path(__file__).parent.parent / "config" / "skills-registry.yaml"
    
    print(f"\n[INFO] Scanning skills directory: {skills_dir}")
    skills = scan_skills_directory(skills_dir)
    
    # Build registry
    registry = {
        "skills": skills,
        "metadata": {
            "last_scanned": datetime.utcnow().isoformat() + "Z",
            "total_skills": len(skills),
            "ready_skills": sum(1 for s in skills.values() if s["status"] == "ready"),
            "discovered_skills": sum(1 for s in skills.values() if s["status"] == "discovered"),
            "registry_version": "1.0",
        }
    }
    
    # Write registry
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n[OK] Registry written to: {output_file}")
    print(f"     Total skills: {registry['metadata']['total_skills']}")
    print(f"     Ready: {registry['metadata']['ready_skills']}")
    print(f"     Discovered: {registry['metadata']['discovered_skills']}")
    
    return registry


def verify_registry(registry_file: Path) -> bool:
    """Check if registry is up-to-date with actual skills"""
    print(f"[INFO] Verifying registry: {registry_file}")
    
    with open(registry_file, 'r') as f:
        registry = yaml.safe_load(f)
    
    skills_dir = registry_file.parent.parent / "src" / "skills"
    actual_skills = set(p.stem for p in skills_dir.glob("*.py") if not p.name.startswith("_"))
    registered_skills = set(registry["skills"].keys())
    
    missing = actual_skills - registered_skills
    extra = registered_skills - actual_skills
    
    if missing:
        print(f"[WARN] Missing from registry: {missing}")
    if extra:
        print(f"[WARN] Extra in registry: {extra}")
    
    if not missing and not extra:
        print(f"[OK] Registry is current ({len(registered_skills)} skills)")
        return True
    else:
        print(f"[WARN] Registry is out of date. Run: python src/registry_builder.py")
        return False


if __name__ == "__main__":
    if "--verify" in sys.argv:
        registry_file = Path(__file__).parent.parent / "config" / "skills-registry.yaml"
        verify_registry(registry_file)
    else:
        build_registry()
