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
import json
import re
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass
from datetime import datetime, timezone


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
    
    def __init__(
        self,
        skills_dir: str = None,
        registry_file: str = None,
        known_solutions_file: str = None,
        metrics_log_file: str = None,
    ):
        """Initialize orchestrator with skills directory and registry"""
        if skills_dir is None:
            skills_dir = str(Path(__file__).parent / "skills")
        if registry_file is None:
            registry_file = str(Path(__file__).parent.parent / "config" / "skills-registry.yaml")
        if known_solutions_file is None:
            known_solutions_file = str(Path(__file__).parent.parent / "config" / "known-solutions.yaml")
        if metrics_log_file is None:
            metrics_log_file = str(Path(__file__).parent.parent / "logs" / "execution_metrics.jsonl")
        
        self.skills_dir = Path(skills_dir)
        self.registry_file = Path(registry_file)
        self.known_solutions_file = Path(known_solutions_file)
        self.metrics_log_file = Path(metrics_log_file)
        self.loaded_skills = {}  # {skill_name: module}
        self.skills_registry = {}  # {skill_name: SkillMetadata}
        self.known_solutions = []
        
        # Load registry first (fast lookup)
        self._load_registry()

        # Load known remediation memory
        self._load_known_solutions()
        
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
            
            for skill_name, metadata in (registry_data.get("skills", {}) or {}).items():
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
        """Load executable skills (ready/active) that expose execute()."""
        for skill_name, metadata in self.skills_registry.items():
            if metadata.status not in {"ready", "active"}:
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

    def _load_known_solutions(self):
        """Load known problem->solution entries from structured memory file."""
        if not self.known_solutions_file.exists():
            self.known_solutions = []
            return

        try:
            with open(self.known_solutions_file, "r", encoding="utf-8") as f:
                payload = yaml.safe_load(f) or {}
            entries = payload.get("solutions", [])
            self.known_solutions = entries if isinstance(entries, list) else []
        except Exception:
            self.known_solutions = []

    def _log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Append structured orchestration events for learning/diagnostics."""
        try:
            self.metrics_log_file.parent.mkdir(parents=True, exist_ok=True)
            event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "payload": payload,
            }
            with open(self.metrics_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass

    def _infer_intent(self, skill_name: str, input_data: Dict[str, Any]) -> str:
        """Infer high-level intent used for fallback and solution lookup."""
        normalized_name = (skill_name or "").lower()
        prompt = str(input_data.get("prompt", "")).lower()
        if "push" in normalized_name or "push" in prompt:
            return "git_push"
        return "generic"

    def _extract_error_message(self, output: Any, default_message: str = "Skill execution failed") -> str:
        """Extract a readable error string from structured skill output."""
        if isinstance(output, dict):
            errors = output.get("errors")
            if isinstance(errors, list) and errors:
                return "; ".join(str(item) for item in errors)
            for field_name in ("error", "reason", "message"):
                value = output.get(field_name)
                if isinstance(value, str) and value.strip():
                    return value
        return default_message

    def _is_success_output(self, output: Any) -> bool:
        """Evaluate success for skill outputs that include explicit status flags."""
        if isinstance(output, dict):
            if "success" in output:
                return bool(output.get("success"))
            if "status" in output:
                return str(output.get("status", "")).upper() in {"SUCCESS", "APPROVED", "VALID", "OK"}
        return True

    def _lookup_known_solution(self, intent: str, error_code: str, error_message: str) -> Dict[str, Any] | None:
        """Find first known solution whose patterns match this failure."""
        text = (error_message or "").lower()
        code = (error_code or "").upper()

        for solution in self.known_solutions:
            solution_intent = str(solution.get("intent", "")).lower().strip()
            if solution_intent and solution_intent != intent:
                continue

            matches = solution.get("matches", {}) if isinstance(solution.get("matches"), dict) else {}
            error_codes = [str(item).upper() for item in matches.get("error_codes", [])]
            if error_codes and code not in error_codes:
                continue

            patterns = [str(item) for item in matches.get("message_patterns", [])]
            if patterns and not any(re.search(pattern, text) for pattern in patterns):
                continue

            return {
                "id": solution.get("id"),
                "title": solution.get("title"),
                "summary": solution.get("summary"),
                "steps": solution.get("steps", []),
            }

        return None

    def _resolve_fallback_skill(self, intent: str, excluded_skills: set[str]) -> str | None:
        """Pick fallback skill for retry path, excluding already-tried skills."""
        if intent == "git_push":
            for candidate in self.loaded_skills.keys():
                if candidate in excluded_skills:
                    continue
                if "push" in candidate.lower():
                    return candidate
        return None
    
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
    
    def run_skill(
        self,
        skill_name: str,
        input_data: Dict[str, Any],
        intent: str | None = None,
        attempt: int = 1,
        max_retries: int = 1,
        excluded_skills: set[str] | None = None,
    ) -> SkillResult:
        """
        Run a single skill with given input.
        
        Args:
            skill_name: Name of the skill (without .py)
            input_data: Input dict to pass to skill
        
        Returns:
            SkillResult with status, output, and metadata
        """
        if excluded_skills is None:
            excluded_skills = set()

        if skill_name not in self.loaded_skills:
            return SkillResult(
                skill_name=skill_name,
                status="FAILED",
                error=f"Skill not found: {skill_name}. Available: {list(self.loaded_skills.keys())}"
            )

        resolved_intent = intent or self._infer_intent(skill_name, input_data)
        
        try:
            skill_module = self.loaded_skills[skill_name]
            output = skill_module.execute(input_data)

            if self._is_success_output(output):
                self._log_event(
                    "EXECUTION_SUCCESS",
                    {
                        "skill": skill_name,
                        "attempt": attempt,
                        "intent": resolved_intent,
                    },
                )
                return SkillResult(
                    skill_name=skill_name,
                    status="SUCCESS",
                    output=output,
                    metadata={"skill_version": getattr(skill_module, "__version__", "unknown"), "attempt": attempt}
                )

            error_message = self._extract_error_message(output)
            error_code = "EXECUTION_FAILED"

            fallback_skill = None
            if attempt <= max_retries:
                fallback_skill = self._resolve_fallback_skill(
                    resolved_intent,
                    excluded_skills | {skill_name},
                )

            if fallback_skill:
                self._log_event(
                    "RETRY_WITH_FALLBACK",
                    {
                        "intent": resolved_intent,
                        "from_skill": skill_name,
                        "to_skill": fallback_skill,
                        "attempt": attempt,
                    },
                )
                return self.run_skill(
                    skill_name=fallback_skill,
                    input_data=input_data,
                    intent=resolved_intent,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    excluded_skills=excluded_skills | {skill_name},
                )

            known_solution = self._lookup_known_solution(resolved_intent, error_code, error_message)
            self._log_event(
                "EXECUTION_FAILED",
                {
                    "skill": skill_name,
                    "attempt": attempt,
                    "intent": resolved_intent,
                    "error_code": error_code,
                    "error": error_message,
                    "known_solution": known_solution.get("id") if known_solution else None,
                },
            )
            return SkillResult(
                skill_name=skill_name,
                status="FAILED",
                error=error_message,
                metadata={
                    "skill_version": getattr(skill_module, "__version__", "unknown"),
                    "attempt": attempt,
                    "error_code": error_code,
                    "known_solution": known_solution,
                }
            )
        except Exception as e:
            error_message = str(e)
            error_code = type(e).__name__

            fallback_skill = None
            if attempt <= max_retries:
                fallback_skill = self._resolve_fallback_skill(
                    resolved_intent,
                    excluded_skills | {skill_name},
                )

            if fallback_skill:
                self._log_event(
                    "RETRY_AFTER_EXCEPTION",
                    {
                        "intent": resolved_intent,
                        "from_skill": skill_name,
                        "to_skill": fallback_skill,
                        "attempt": attempt,
                        "exception_type": error_code,
                    },
                )
                return self.run_skill(
                    skill_name=fallback_skill,
                    input_data=input_data,
                    intent=resolved_intent,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    excluded_skills=excluded_skills | {skill_name},
                )

            known_solution = self._lookup_known_solution(resolved_intent, error_code, error_message)
            self._log_event(
                "EXECUTION_EXCEPTION",
                {
                    "skill": skill_name,
                    "attempt": attempt,
                    "intent": resolved_intent,
                    "error_code": error_code,
                    "error": error_message,
                    "known_solution": known_solution.get("id") if known_solution else None,
                },
            )
            return SkillResult(
                skill_name=skill_name,
                status="FAILED",
                error=error_message,
                metadata={
                    "exception_type": error_code,
                    "attempt": attempt,
                    "known_solution": known_solution,
                }
            )
    
    def run_workflow(self, workflow_spec: List[tuple], max_retries_per_skill: int = 1) -> List[SkillResult]:
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
            
            intent = self._infer_intent(skill_name, merged_input)
            result = self.run_skill(
                skill_name,
                merged_input,
                intent=intent,
                max_retries=max_retries_per_skill,
            )
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
