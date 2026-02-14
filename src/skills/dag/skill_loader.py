"""
skill_loader.py (Phase 3) - Skill loader with interface validation

Loads skills dynamically from entry_point paths and validates they
implement the SkillBase interface correctly.
"""

import importlib.util
import inspect
from pathlib import Path
from typing import Any, Dict, Optional, Type

from .skill_base import SkillBase, SkillInterfaceVersion
from ..registry.registry_models import SkillMetadata


class SkillLoaderError(Exception):
    """Skill loading error."""
    pass


class InterfaceValidationError(Exception):
    """Skill interface validation error."""
    pass


class SkillLoader:
    """
    Loads skills from entry_point files and validates interface.
    
    Usage:
        loader = SkillLoader()
        skill = loader.load(metadata, root_dir="/path/to/project")
        
        # Validate before using
        errors = loader.validate(skill)
        if errors:
            print(f"Validation errors: {errors}")
    """
    
    # List of required abstract methods that must be implemented
    REQUIRED_METHODS = [
        'description',
        'validate_inputs',
        'execute'
    ]
    
    def __init__(self):
        """Initialize skill loader."""
        self._loaded_skills: Dict[str, SkillBase] = {}
        self._validation_cache: Dict[str, list[str]] = {}
    
    def load(
        self,
        metadata: SkillMetadata,
        root_dir: str = ""
    ) -> SkillBase:
        """
        Load skill from entry_point path.
        
        Args:
            metadata: SkillMetadata with entry_point
            root_dir: Root directory for relative paths
        
        Returns:
            Instantiated SkillBase subclass
        
        Raises:
            SkillLoaderError: If loading fails
            InterfaceValidationError: If interface is invalid
        """
        # Check cache
        cache_key = f"{metadata.name}:{metadata.version}"
        if cache_key in self._loaded_skills:
            return self._loaded_skills[cache_key]
        
        if not metadata.entry_point:
            raise SkillLoaderError(f"No entry_point for {metadata.name}")
        
        try:
            # Resolve path
            path = Path(metadata.entry_point)
            if root_dir and not path.is_absolute():
                path = Path(root_dir) / path
            
            if not path.exists():
                raise SkillLoaderError(f"Entry point file not found: {path}")
            
            # Load module
            module = self._load_module(path)
            
            # Find SkillBase subclass
            skill_class = self._find_skill_class(module)
            
            if not skill_class:
                raise SkillLoaderError(
                    f"No SkillBase subclass found in {path}"
                )
            
            # Validate interface
            errors = self._validate_interface(skill_class)
            if errors:
                self._validation_cache[cache_key] = errors
                error_msg = "\n".join(f"  - {e}" for e in errors)
                raise InterfaceValidationError(
                    f"Interface validation failed for {metadata.name}:\n{error_msg}"
                )
            
            # Instantiate
            instance = skill_class()
            
            # Cache
            self._loaded_skills[cache_key] = instance
            
            return instance
        
        except (SkillLoaderError, InterfaceValidationError):
            raise
        
        except Exception as e:
            raise SkillLoaderError(
                f"Failed to load skill {metadata.name}: {e}"
            ) from e
    
    def _load_module(self, path: Path) -> Any:
        """Load Python module from path."""
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec or not spec.loader:
            raise SkillLoaderError(f"Could not load spec from {path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
    
    def _find_skill_class(self, module: Any) -> Optional[Type[SkillBase]]:
        """Find SkillBase subclass in module."""
        for name, obj in inspect.getmembers(module):
            # Skip built-ins and imports
            if name.startswith('_'):
                continue
            
            # Check if it's a class and subclass of SkillBase
            if (inspect.isclass(obj) and 
                issubclass(obj, SkillBase) and 
                obj is not SkillBase):
                return obj
        
        return None
    
    def _validate_interface(self, skill_class: Type[SkillBase]) -> list[str]:
        """
        Validate skill class implements required methods.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check it's a proper subclass
        if not issubclass(skill_class, SkillBase):
            errors.append("Not a SkillBase subclass")
            return errors
        
        # Check required methods are implemented
        for method_name in self.REQUIRED_METHODS:
            if not hasattr(skill_class, method_name):
                errors.append(f"Missing required method: {method_name}")
            else:
                method = getattr(skill_class, method_name)
                
                # Check it's not abstract
                if getattr(method, '__isabstractmethod__', False):
                    errors.append(f"Method not implemented: {method_name}")
                
                # Check signature for execute()
                if method_name == 'execute':
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    if 'context' not in params:
                        errors.append("execute() missing 'context' parameter")
        
        # Check __init__ accepts skill_name and skill_version
        init_sig = inspect.signature(skill_class.__init__)
        init_params = list(init_sig.parameters.keys())
        
        # Allow *args and **kwargs
        has_flexibility = (
            any(p.startswith('*') for p in init_sig.parameters)
            or '__init__' in skill_class.__dict__  # Custom init
        )
        
        if not has_flexibility:
            if 'skill_name' not in init_params and 'skill_version' not in init_params:
                errors.append("__init__ should accept skill_name and skill_version parameters")
        
        return errors
    
    def validate(self, skill: SkillBase) -> list[str]:
        """
        Validate loaded skill instance.
        
        Args:
            skill: SkillBase instance
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check basic properties
        if not skill.name:
            errors.append("Skill has no name")
        
        if not skill.version:
            errors.append("Skill has no version")
        
        # Check methods are callable
        try:
            desc = skill.description()
            if not isinstance(desc, str) or not desc:
                errors.append("description() should return non-empty string")
        except Exception as e:
            errors.append(f"description() failed: {e}")
        
        try:
            is_valid, msg = skill.validate_inputs({})
            if not isinstance(is_valid, bool):
                errors.append("validate_inputs() should return (bool, str)")
        except Exception as e:
            errors.append(f"validate_inputs() failed: {e}")
        
        return errors
    
    def validate_batch(self, skills: list[SkillBase]) -> Dict[str, list[str]]:
        """
        Validate multiple skills.
        
        Args:
            skills: List of SkillBase instances
        
        Returns:
            {skill_name: [errors]} for all skills with errors
        """
        results = {}
        for skill in skills:
            errors = self.validate(skill)
            if errors:
                results[skill.name] = errors
        return results
    
    def load_from_metadata_batch(
        self,
        metadata_list: list[SkillMetadata],
        root_dir: str = ""
    ) -> Dict[str, SkillBase]:
        """
        Load multiple skills from metadata.
        
        Args:
            metadata_list: List of SkillMetadata
            root_dir: Root directory for relative paths
        
        Returns:
            {skill_name: SkillBase} for all successfully loaded skills
        """
        results = {}
        
        for metadata in metadata_list:
            try:
                skill = self.load(metadata, root_dir)
                results[metadata.name] = skill
            except (SkillLoaderError, InterfaceValidationError) as e:
                print(f"[WARN] Failed to load {metadata.name}: {e}")
        
        return results
    
    def clear_cache(self) -> None:
        """Clear loaded skills cache."""
        self._loaded_skills.clear()
        self._validation_cache.clear()
    
    def get_loaded_skills(self) -> Dict[str, SkillBase]:
        """Get all loaded skills."""
        return self._loaded_skills.copy()
    
    def get_validation_errors(self, skill_name: str) -> Optional[list[str]]:
        """Get cached validation errors for skill."""
        return self._validation_cache.get(skill_name)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<SkillLoader loaded={len(self._loaded_skills)}>"
