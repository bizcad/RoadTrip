"""
Orchestrator: Dynamically load and chain skills

Core architecture: Agents don't hardcode skill calls. 
Orchestrator discovers, validates, and chains skills based on workflow definition.

Skills Registry: Instead of scanning fs every run, loads metadata from skills-registry.yaml
"Ready" skills (status=ready) can be executed immediately.
"Discovered" skills (status=discovered) exist but need execute() wrapper.
"""

import sys
import importlib
import importlib.util
import yaml
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class SkillMetadata:
    """Metadata about a skill from the registry"""
    name: str
    version: str
    description: str
    interface: str
    status: str  # "ready" or "discovered"
    file: str = None


@dataclass
class SkillResult:
    """Standardized skill output format"""
    skill_name: str
    status: str  # "SUCCESS" | "FAILED" | "SKIPPED"
    output: Any = None
    error: str = None
    metadata: Dict[str, Any] = None


class Orchestrator:
    """
    Simple orchestrator: Load skills, chain them, pass outputs through pipeline.
    
    Skills are loaded from skills-registry.yaml for fast lookup.
    Only "ready" skills (with execute() interface) can be run directly.
    
    Usage:
        orch = Orchestrator()
        result = orch.run_workflow([
            ("validator", {"files": ["file1.py"]}),
            ("committer", {"files": ["file1.py"]})
        ])
    """
    
    def __init__(self, skills_dir: str = None, registry_file: str = None):
        """Initialize orchestrator with skills directory and registry"""
        if skills_dir is None:
            skills_dir = str(Path(__file__).parent / "skills")
        if registry_file is None:
            registry_file = str(Path(__file__).parent.parent / "config" / "skills-registry.yaml")
        
        self.skills_dir = Path(skills_dir)
        self.registry_file = Path(registry_file)
        self.loaded_skills = {}  # {skill_name: module}
        self.skills_registry = {}  # {skill_name: SkillMetadata}
        
        # Load registry first (fast lookup)
        self._load_registry()
        
        # Then load ready skills
        self._load_ready_skills()
    
    def _load_registry(self):
        """Load skills-registry.yaml for metadata"""
        if not self.registry_file.exists():
            print(f"[WARN] Registry not found: {self.registry_file}")
            print(f"       Run: python src/registry_builder.py")
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                registry_data = yaml.safe_load(f)
            
            for skill_name, metadata in registry_data.get("skills", {}).items():
                self.skills_registry[skill_name] = SkillMetadata(
                    name=skill_name,
                    version=metadata.get("version", "unknown"),
                    description=metadata.get("description", ""),
                    interface=metadata.get("interface", ""),
                    status=metadata.get("status", "unknown"),
                    file=metadata.get("file", "")
                )
            
            meta = registry_data.get("metadata", {})
            print(f"[OK] Registry loaded: {len(self.skills_registry)} total skills")
            print(f"     Ready: {meta.get('ready_skills', 0)}, Discovered: {meta.get('discovered_skills', 0)}")
        except Exception as e:
            print(f"[FAIL] Failed to load registry: {e}")
    
    def _load_ready_skills(self):
        """Load only 'ready' skills (those with execute() interface)"""
        for skill_name, metadata in self.skills_registry.items():
            if metadata.status != "ready":
                continue  # Skip discovered skills
            
            skill_file = self.skills_dir / metadata.file
            if not skill_file.exists():
                print(f"[WARN] Skill file not found: {skill_file}")
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(skill_name, skill_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "execute"):
                    self.loaded_skills[skill_name] = module
                    print(f"[OK] Loaded skill: {skill_name}")
            except Exception as e:
                print(f"[FAIL] Failed to load skill {skill_name}: {e}")
    
    def get_skill_info(self, skill_name: str) -> SkillMetadata:
        """Get metadata for a skill"""
        return self.skills_registry.get(skill_name)
    
    def list_ready_skills(self) -> List[SkillMetadata]:
        """Get list of all ready skills"""
        return [m for m in self.skills_registry.values() if m.status == "ready"]
    
    def list_all_skills(self) -> List[SkillMetadata]:
        """Get list of all discovered skills (ready + discovered)"""
        return list(self.skills_registry.values())
    
    def list_skills(self) -> Dict[str, str]:
        """Get dictionary of all discovered skills and their versions"""
        skills_info = {}
        for skill_name, module in self.loaded_skills.items():
            version = getattr(module, "__version__", "unknown")
            skills_info[skill_name] = version
        return skills_info
    
    def print_skills(self) -> None:
        """Pretty-print available skills"""
        if not self.loaded_skills:
            print("\n[WARN] No skills discovered")
            return
        
        print(f"\nAvailable Skills ({len(self.loaded_skills)}):")
        print("-" * 50)
        for skill_name, module in sorted(self.loaded_skills.items()):
            version = getattr(module, "__version__", "unknown")
            docstring = (module.__doc__ or "").split('\n')[0].strip()
            print(f"  - {skill_name:<20} v{version:<6} {docstring}")
        print("-" * 50)
    
    def run_skill(self, skill_name: str, input_data: Dict[str, Any]) -> SkillResult:
        """
        Run a single skill with given input.
        
        Args:
            skill_name: Name of the skill (without .py)
            input_data: Input dict to pass to skill
        
        Returns:
            SkillResult with status, output, and metadata
        """
        if skill_name not in self.loaded_skills:
            return SkillResult(
                skill_name=skill_name,
                status="FAILED",
                error=f"Skill not found: {skill_name}. Available: {list(self.loaded_skills.keys())}"
            )
        
        try:
            skill_module = self.loaded_skills[skill_name]
            output = skill_module.execute(input_data)
            
            return SkillResult(
                skill_name=skill_name,
                status="SUCCESS",
                output=output,
                metadata={"skill_version": getattr(skill_module, "__version__", "unknown")}
            )
        except Exception as e:
            return SkillResult(
                skill_name=skill_name,
                status="FAILED",
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )
    
    def run_workflow(self, workflow_spec: List[tuple]) -> List[SkillResult]:
        """
        Execute a workflow: sequence of (skill_name, input_data) tuples.
        
        Each skill's output becomes available for next skill via context.
        
        Args:
            workflow_spec: List of (skill_name, input_dict) tuples
        
        Returns:
            List of SkillResults in execution order
        """
        results = []
        context = {}  # Shared context across skills
        
        for i, (skill_name, input_data) in enumerate(workflow_spec):
            # Merge input_data with context (input_data takes precedence)
            merged_input = {**context, **input_data}
            
            print(f"\n[{i+1}/{len(workflow_spec)}] Running skill: {skill_name}")
            print(f"  Input: {merged_input}")
            
            result = self.run_skill(skill_name, merged_input)
            results.append(result)
            
            print(f"  Result: {result.status}")
            if result.output:
                print(f"  Output: {result.output}")
            if result.error:
                print(f"  Error: {result.error}")
            
            # Stop on failure
            if result.status == "FAILED":
                print(f"\n❌ Workflow stopped at skill #{i+1}: {skill_name}")
                break
            
            # Update context with this skill's output
            if result.output:
                context.update({"previous_output": result.output})
        
        return results


def main():
    """Demo: Orchestrator loading and running skills"""
    print("=" * 60)
    print("Orchestrator Demo: Dynamic Skill Chaining")
    print("=" * 60)
    
    orch = Orchestrator()
    
    # Show available skills
    orch.print_skills()
    
    # Demo workflow: validator -> committer
    workflow = [
        ("mock_validator", {"files": ["src/main.py", "src/util.py"]}),
        ("mock_committer", {"message": "feat: add new features", "author": "agent"})
    ]
    
    print(f"\nExecuting workflow with {len(workflow)} steps...")
    results = orch.run_workflow(workflow)
    
    print("\n" + "=" * 60)
    print("Workflow Summary")
    print("=" * 60)
    for i, result in enumerate(results, 1):
        status_icon = "[OK]" if result.status == "SUCCESS" else "[FAIL]"
        print(f"{i}. {status_icon} {result.skill_name}: {result.status}")
    
    all_passed = all(r.status == "SUCCESS" for r in results)
    print(f"\nOverall: {'[OK] SUCCESS' if all_passed else '[FAIL] FAILED'}")


if __name__ == "__main__":
    main()
