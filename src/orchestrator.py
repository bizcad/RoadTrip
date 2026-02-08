"""
Orchestrator: Dynamically load and chain skills

Core architecture: Agents don't hardcode skill calls. 
Orchestrator discovers, validates, and chains skills based on workflow definition.
"""

import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass


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
    
    Usage:
        orch = Orchestrator()
        result = orch.run_workflow([
            ("validator", {"files": ["file1.py"]}),
            ("committer", {"files": ["file1.py"]})
        ])
    """
    
    def __init__(self, skills_dir: str = None):
        """Initialize orchestrator with skills directory"""
        if skills_dir is None:
            skills_dir = str(Path(__file__).parent / "skills")
        
        self.skills_dir = Path(skills_dir)
        self.loaded_skills = {}  # {skill_name: module}
        self._discover_skills()
    
    def _discover_skills(self):
        """Scan skills_dir and register all available skills"""
        if not self.skills_dir.exists():
            print(f"[WARN] Skills directory not found: {self.skills_dir}")
            return
        
        for py_file in self.skills_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue  # Skip __init__.py, etc.
            
            # Skip complex skills that don't have simple execute() function yet
            if py_file.name in ["commit_message.py", "config_loader.py", "token_resolver.py", "rules_engine.py", "models.py", "auth_validator_models.py", "commit_message_models.py"]:
                continue
            
            skill_name = py_file.stem
            try:
                # Dynamically import skill module
                spec = importlib.util.spec_from_file_location(skill_name, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Verify skill has required functions
                if hasattr(module, "execute"):
                    self.loaded_skills[skill_name] = module
                    print(f"✅ Loaded skill: {skill_name}")
            except Exception as e:
                print(f"❌ Failed to load skill {skill_name}: {e}")
    
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
    
    print(f"\nLoaded {len(orch.loaded_skills)} skills: {list(orch.loaded_skills.keys())}")
    
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
        status_icon = "✅" if result.status == "SUCCESS" else "❌"
        print(f"{i}. {status_icon} {result.skill_name}: {result.status}")
    
    all_passed = all(r.status == "SUCCESS" for r in results)
    print(f"\nOverall: {'✅ SUCCESS' if all_passed else '❌ FAILED'}")


if __name__ == "__main__":
    main()
