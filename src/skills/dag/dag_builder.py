"""
dag_builder.py (Phase 3) - Fluent builder for Skill DAGs

Provides fluent API for constructing DAGs with support for dev/prod modes,
configuration, and input mapping.
"""

from typing import Any, Dict, List, Optional

from .skill_base import SkillBase
from .skill_dag import SkillDAG, SkillNode
from .execution_models import ExecutionMode, RetryConfig, RetryStrategy


class DAGBuilder:
    """
    Fluent builder for Skill DAGs.
    
    Usage:
        builder = DAGBuilder(ExecutionMode.PROD)
        builder.add_skill(skill1) \\
               .add_skill(skill2) \\
               .add_dependency(skill1.name, skill2.name) \\
               .configure_skill(skill1.name, {"timeout": 30}) \\
               .map_input(skill2.name, {"output": "input"}) \\
               .set_retry_config(RetryConfig(max_retries=3))
        
        dag = builder.build()
    """
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.PROD):
        """
        Initialize builder.
        
        Args:
            mode: Execution mode (dev/prod)
        """
        self.dag = SkillDAG()
        self.mode = mode
        self.retry_config = RetryConfig()
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._input_mappings: Dict[str, Dict[str, str]] = {}
    
    def add_skill(self, skill: SkillBase) -> "DAGBuilder":
        """
        Add skill to DAG.
        
        Args:
            skill: SkillBase instance
        
        Returns:
            Self for chaining
        """
        self.dag.add_node(skill)
        return self
    
    def add_skills(self, *skills: SkillBase) -> "DAGBuilder":
        """
        Add multiple skills.
        
        Args:
            *skills: Variable argument list of skills
        
        Returns:
            Self for chaining
        """
        for skill in skills:
            self.add_skill(skill)
        return self
    
    def add_dependency(self, source_skill: str, target_skill: str) -> "DAGBuilder":
        """
        Add dependency: target depends on source.
        
        Args:
            source_skill: Source skill name
            target_skill: Target skill name
        
        Returns:
            Self for chaining
        """
        self.dag.add_edge(source_skill, target_skill)
        return self
    
    def add_dependencies(self, dependencies: List[tuple[str, str]]) -> "DAGBuilder":
        """
        Add multiple dependencies.
        
        Args:
            dependencies: List of (source, target) tuples
        
        Returns:
            Self for chaining
        """
        for source, target in dependencies:
            self.add_dependency(source, target)
        return self
    
    def configure_skill(
        self,
        skill_name: str,
        config: Dict[str, Any]
    ) -> "DAGBuilder":
        """
        Set skill configuration overrides.
        
        Args:
            skill_name: Skill name
            config: Configuration dictionary
        
        Returns:
            Self for chaining
        """
        if skill_name not in self._configs:
            self._configs[skill_name] = {}
        self._configs[skill_name].update(config)
        return self
    
    def map_input(
        self,
        skill_name: str,
        mapping: Dict[str, str]
    ) -> "DAGBuilder":
        """
        Map output from upstream skills to input for this skill.
        
        Example: skill2 needs github_token, which skill1 produces as gh_token
                 map_input("skill2", {"gh_token": "github_token"})
        
        Args:
            skill_name: Target skill name
            mapping: {upstream_output_key: downstream_input_key}
        
        Returns:
            Self for chaining
        """
        if skill_name not in self._input_mappings:
            self._input_mappings[skill_name] = {}
        self._input_mappings[skill_name].update(mapping)
        return self
    
    def set_execution_mode(self, mode: ExecutionMode) -> "DAGBuilder":
        """
        Set execution mode (dev/prod).
        
        Args:
            mode: ExecutionMode.DEV or ExecutionMode.PROD
        
        Returns:
            Self for chaining
        """
        self.mode = mode
        return self
    
    def dev(self) -> "DAGBuilder":
        """
        Switch to dev mode (debug output visible).
        
        Returns:
            Self for chaining
        """
        self.mode = ExecutionMode.DEV
        return self
    
    def prod(self) -> "DAGBuilder":
        """
        Switch to prod mode (fluid piping).
        
        Returns:
            Self for chaining
        """
        self.mode = ExecutionMode.PROD
        return self
    
    def set_retry_config(self, config: RetryConfig) -> "DAGBuilder":
        """
        Set retry configuration for all skills.
        
        Args:
            config: RetryConfig instance
        
        Returns:
            Self for chaining
        """
        self.retry_config = config
        return self
    
    def set_retry_strategy(self, strategy: RetryStrategy) -> "DAGBuilder":
        """
        Set retry strategy.
        
        Args:
            strategy: RetryStrategy enum value
        
        Returns:
            Self for chaining
        """
        self.retry_config.strategy = strategy
        return self
    
    def set_max_retries(self, max_retries: int) -> "DAGBuilder":
        """
        Set maximum retry attempts.
        
        Args:
            max_retries: Number of retries (default 3)
        
        Returns:
            Self for chaining
        """
        self.retry_config.max_retries = max_retries
        return self
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate DAG before building.
        
        Returns:
            (is_valid, error_list)
        """
        # Validate DAG structure
        is_valid, errors = self.dag.validate()
        
        if not is_valid:
            return False, errors
        
        # Validate config references valid skills
        for skill_name in self._configs:
            if skill_name not in self.dag.nodes:
                errors.append(f"Config for non-existent skill: {skill_name}")
        
        # Validate input mapping references valid skills
        for skill_name in self._input_mappings:
            if skill_name not in self.dag.nodes:
                errors.append(f"Input mapping for non-existent skill: {skill_name}")
        
        return len(errors) == 0, errors
    
    def build(self) -> SkillDAG:
        """
        Build and return DAG.
        
        Applies all configuration and input mappings to DAG nodes.
        
        Returns:
            SkillDAG ready for execution
        
        Raises:
            ValueError: If validation fails
        """
        is_valid, errors = self.validate()
        if not is_valid:
            raise ValueError(f"DAG validation failed: {errors}")
        
        # Apply configurations to nodes
        for skill_name, config in self._configs.items():
            node = self.dag.get_node(skill_name)
            node.config_overrides.update(config)
        
        # Apply input mappings to nodes
        for skill_name, mapping in self._input_mappings.items():
            node = self.dag.get_node(skill_name)
            node.input_mapping.update(mapping)
        
        if self.mode == ExecutionMode.DEV:
            print("[DAG] Built in DEV mode (debug output enabled)")
        
        return self.dag
    
    def build_and_validate(self) -> tuple[Optional[SkillDAG], List[str]]:
        """
        Build DAG and validate, or return validation errors.
        
        Returns:
            (dag, warnings) - dag may be invalid if validation fails, warnings list
        """
        is_valid, errors = self.validate()
        
        if is_valid:
            return self.build(), []
        else:
            return None, errors
    
    def get_execution_order(self) -> List[str]:
        """
        Get topological execution order without building.
        
        Returns:
            List of skill names in order
        """
        return self.dag.topological_sort()
    
    def get_execution_layers(self) -> Dict[int, List[str]]:
        """
        Get skills grouped by execution layer (parallelizable groups).
        
        Returns:
            {layer: [skill_names]}
        """
        return self.dag.get_layers()
    
    def debug_info(self) -> Dict[str, Any]:
        """
        Get debug information about DAG being built.
        
        Returns:
            Debug dictionary
        """
        layers = self.dag.get_layers()
        
        return {
            "mode": self.mode.value,
            "skills_count": len(self.dag.nodes),
            "edges_count": len(self.dag.edges),
            "layers_count": len(layers),
            "execution_order": self.dag.topological_sort(),
            "layers": layers,
            "retry_config": {
                "max_retries": self.retry_config.max_retries,
                "strategy": self.retry_config.strategy.value,
                "base_delay": self.retry_config.base_delay
            },
            "configured_skills": list(self._configs.keys()),
            "mapped_skills": list(self._input_mappings.keys())
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"<DAGBuilder mode={self.mode.value} skills={len(self.dag.nodes)} "
                f"edges={len(self.dag.edges)}>"
        )
