"""
skill_dag.py (Phase 3) - Skill DAG (Directed Acyclic Graph)

Represents skill dependencies and execution order.
Supports cascade-stop semantics: if a skill fails, dependents are skipped.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .skill_base import SkillBase


class DAGValidationError(Exception):
    """DAG validation error."""
    pass


class TopologyOrder(str, Enum):
    """Topological order for DAG execution."""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"


@dataclass
class SkillNode:
    """
    Node in skill DAG.
    
    Represents a skill with optional configuration overrides.
    """
    skill: SkillBase
    skill_name: str
    config_overrides: Dict[str, any] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)  # output_key -> input_key
    
    def __hash__(self):
        """Hash for use in sets."""
        return hash(self.skill_name)
    
    def __eq__(self, other):
        """Equality check."""
        if not isinstance(other, SkillNode):
            return False
        return self.skill_name == other.skill_name
    
    def __repr__(self):
        """String representation."""
        return f"<SkillNode {self.skill_name}>"


@dataclass
class DAGEdge:
    """
    Edge in skill DAG.
    
    Represents a dependency: source_skill -> target_skill
    target depends on source completing successfully.
    """
    source_skill: str  # skill_name
    target_skill: str  # skill_name
    
    def __hash__(self):
        """Hash for use in sets."""
        return hash((self.source_skill, self.target_skill))
    
    def __eq__(self, other):
        """Equality check."""
        if not isinstance(other, DAGEdge):
            return False
        return (self.source_skill == other.source_skill and 
                self.target_skill == other.target_skill)
    
    def __repr__(self):
        """String representation."""
        return f"<DAGEdge {self.source_skill} -> {self.target_skill}>"


class SkillDAG:
    """
    Directed Acyclic Graph for skill execution.
    
    Enforces:
    - No cycles (validated on add_edge)
    - Cascade-stop semantics (if dependency fails, dependents are skipped)
    - Proper dependency resolution (all dependencies must be added)
    
    Usage:
        dag = SkillDAG()
        dag.add_node(skill1)
        dag.add_node(skill2)
        dag.add_edge(skill1.name, skill2.name)  # skill2 depends on skill1
        order = dag.topological_sort()  # Returns [skill1, skill2]
    """
    
    def __init__(self):
        """Initialize empty DAG."""
        self.nodes: Dict[str, SkillNode] = {}
        self.edges: Set[DAGEdge] = set()
        self._adjacency: Dict[str, Set[str]] = {}  # skill_name -> {dependent_names}
        self._dependencies: Dict[str, Set[str]] = {}  # skill_name -> {dependency_names}
    
    def add_node(
        self,
        skill: SkillBase,
        config_overrides: Optional[Dict[str, any]] = None,
        input_mapping: Optional[Dict[str, str]] = None
    ) -> SkillNode:
        """
        Add skill node to DAG.
        
        Args:
            skill: SkillBase instance
            config_overrides: Config overrides for this execution
            input_mapping: Map output keys -> input keys for piping
        
        Returns:
            SkillNode
        
        Raises:
            ValueError: If skill already added
        """
        if skill.name in self.nodes:
            raise ValueError(f"Skill {skill.name} already in DAG")
        
        node = SkillNode(
            skill=skill,
            skill_name=skill.name,
            config_overrides=config_overrides or {},
            input_mapping=input_mapping or {}
        )
        
        self.nodes[skill.name] = node
        self._adjacency[skill.name] = set()
        self._dependencies[skill.name] = set()
        
        return node
    
    def add_edge(self, source_skill: str, target_skill: str) -> None:
        """
        Add dependency edge: target depends on source.
        
        Args:
            source_skill: Skill name (must be in DAG)
            target_skill: Skill name (must be in DAG)
        
        Raises:
            ValueError: If skill not in DAG
            DAGValidationError: If would create cycle
        """
        # Validate both skills exist
        if source_skill not in self.nodes:
            raise ValueError(f"Source skill '{source_skill}' not in DAG")
        if target_skill not in self.nodes:
            raise ValueError(f"Target skill '{target_skill}' not in DAG")
        
        # Check for cycles (would target -> source create a cycle?)
        if self._would_create_cycle(target_skill, source_skill):
            raise DAGValidationError(
                f"Would create cycle: {target_skill} -> {source_skill}"
            )
        
        # Add edge
        edge = DAGEdge(source_skill, target_skill)
        if edge not in self.edges:
            self.edges.add(edge)
            self._adjacency[source_skill].add(target_skill)
            self._dependencies[target_skill].add(source_skill)
    
    def _would_create_cycle(self, from_skill: str, to_skill: str) -> bool:
        """Check if adding edge would create cycle (DFS)."""
        visited = set()
        
        def has_path(current: str, target: str) -> bool:
            if current == target:
                return True
            if current in visited:
                return False
            
            visited.add(current)
            for dependent in self._adjacency[current]:
                if has_path(dependent, target):
                    return True
            
            return False
        
        return has_path(from_skill, to_skill)
    
    def get_dependencies(self, skill_name: str) -> Set[str]:
        """Get all dependencies for a skill."""
        if skill_name not in self.nodes:
            raise ValueError(f"Skill '{skill_name}' not in DAG")
        return self._dependencies[skill_name].copy()
    
    def get_dependents(self, skill_name: str) -> Set[str]:
        """Get all skills that depend on this skill."""
        if skill_name not in self.nodes:
            raise ValueError(f"Skill '{skill_name}' not in DAG")
        return self._adjacency[skill_name].copy()
    
    def get_all_dependents(self, skill_name: str) -> Set[str]:
        """
        Get all transitive dependents (cascade-stop semantics).
        
        If skill fails, all of these should be skipped.
        """
        visited = set()
        
        def traverse(skill: str):
            for dependent in self._adjacency[skill]:
                if dependent not in visited:
                    visited.add(dependent)
                    traverse(dependent)
        
        traverse(skill_name)
        return visited
    
    def topological_sort(self) -> List[str]:
        """
        Topological sort of skills (execution order).
        
        Uses Kahn's algorithm (BFS-based).
        
        Returns:
            List of skill names in execution order
        
        Raises:
            DAGValidationError: If cycle detected (shouldn't happen if add_edge validates)
        """
        # Copy in-degree count
        in_degree = {skill: len(self._dependencies[skill]) for skill in self.nodes}
        
        # Queue of skills with no dependencies
        queue = [skill for skill in self.nodes if in_degree[skill] == 0]
        
        result = []
        
        while queue:
            # Remove skill with no dependencies
            current = queue.pop(0)
            result.append(current)
            
            # Process dependents
            for dependent in self._adjacency[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check if all skills were processed (would indicate cycle)
        if len(result) != len(self.nodes):
            raise DAGValidationError("Cycle detected in DAG")
        
        return result
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate DAG integrity.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check all dependencies are in DAG
        for skill_name, deps in self._dependencies.items():
            for dep in deps:
                if dep not in self.nodes:
                    errors.append(f"Skill '{skill_name}' depends on missing skill '{dep}'")
        
        # Check no cycles
        try:
            self.topological_sort()
        except DAGValidationError as e:
            errors.append(str(e))
        
        return len(errors) == 0, errors
    
    def get_execution_layer(self, skill_name: str) -> int:
        """
        Get execution layer of skill (0 = no dependencies, 1 = depends on layer 0, etc.).
        """
        if skill_name not in self.nodes:
            raise ValueError(f"Skill '{skill_name}' not in DAG")
        
        max_dependency_layer = -1
        for dep in self._dependencies[skill_name]:
            max_dependency_layer = max(max_dependency_layer, self.get_execution_layer(dep))
        
        return max_dependency_layer + 1
    
    def get_layers(self) -> Dict[int, List[str]]:
        """
        Get skills grouped by execution layer.
        
        Skills in same layer can execute in parallel.
        
        Returns:
            {layer_number: [skill_names]}
        """
        layers: Dict[int, List[str]] = {}
        
        for skill_name in self.nodes:
            layer = self.get_execution_layer(skill_name)
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(skill_name)
        
        return layers
    
    def get_node(self, skill_name: str) -> SkillNode:
        """Get skill node."""
        if skill_name not in self.nodes:
            raise ValueError(f"Skill '{skill_name}' not in DAG")
        return self.nodes[skill_name]
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"<SkillDAG nodes={len(self.nodes)} edges={len(self.edges)} "
                f"layers={len(self.get_layers())}>"
        )
