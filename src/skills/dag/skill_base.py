"""
skill_base.py (Phase 3) - Base class for skill interfaces

Defines the skill base class that all skills must inherit from.
Enforces SOLID principles via abstract methods.
Includes selector pattern for swappable external API implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum

from .execution_models import ExecutionContext, SkillResult, ExecutionStatus


class SkillInterfaceVersion(str, Enum):
    """Version of skill interface."""
    V1 = "1.0"  # Initial interface


class SkillCapability(str, Enum):
    """Standard skill capabilities."""
    READ = "read"
    WRITE = "write"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    ROUTE = "route"
    AUDIT = "audit"
    EXTERNAL_API = "external_api"


class ExternalAPIType(str, Enum):
    """Type of external API a skill uses."""
    GITHUB = "github"
    VERCEL = "vercel"
    EMAIL = "email"
    WEATHER = "weather"
    MAPS = "maps"
    DATABASE = "database"
    LLM = "llm"
    OTHER = "other"


class APISelector:
    """
    Selector pattern for swappable external API implementations.
    
    Allows skills to define multiple providers and choose at runtime.
    Example: GitHubAPI can use real GitHub, mock GitHub, or test doubles.
    """
    
    def __init__(self, api_type: ExternalAPIType):
        """Initialize selector for API type."""
        self.api_type = api_type
        self.providers: Dict[str, Any] = {}
        self.active_provider: Optional[str] = None
    
    def register_provider(self, name: str, provider: Any) -> None:
        """Register a provider implementation."""
        self.providers[name] = provider
    
    def select_provider(self, name: str) -> Any:
        """Select active provider by name."""
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not registered for {self.api_type}")
        self.active_provider = name
        return self.providers[name]
    
    def get_active_provider(self) -> Any:
        """Get currently active provider."""
        if not self.active_provider:
            raise RuntimeError(f"No active provider selected for {self.api_type}")
        return self.providers[self.active_provider]
    
    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self.providers.keys())


class SkillBase(ABC):
    """
    Base class for all skills.
    
    Enforces SOLID principles:
    - Single Responsibility: Each skill does one thing
    - Open/Closed: Extensible via inheritance, closed for modification
    - Liskov Substitution: All skills implement same interface
    - Interface Segregation: Minimal required methods
    - Dependency Inversion: Depend on abstractions (APIs), not concretes
    
    Subclasses MUST implement:
    - name() -> str
    - version() -> str
    - description() -> str
    - capabilities() -> List[str]
    - validate_inputs(inputs) -> bool
    - execute(context) -> SkillResult
    """
    
    # Class-level interface version
    interface_version = SkillInterfaceVersion.V1
    
    def __init__(
        self,
        skill_name: str,
        skill_version: str,
        capabilities: Optional[List[SkillCapability]] = None,
        external_apis: Optional[List[ExternalAPIType]] = None
    ):
        """
        Initialize skill base.
        
        Args:
            skill_name: Skill name (must match registered name)
            skill_version: Semantic version (e.g., "1.0.0")
            capabilities: Skill capabilities
            external_apis: External APIs used by this skill
        """
        self._skill_name = skill_name
        self._skill_version = skill_version
        self._capabilities = capabilities or []
        self._external_apis = external_apis or []
        self._api_selectors: Dict[ExternalAPIType, APISelector] = {}
        self._initialized = False
    
    @property
    def name(self) -> str:
        """Skill name."""
        return self._skill_name
    
    @property
    def version(self) -> str:
        """Skill version."""
        return self._skill_version
    
    @property
    def capabilities(self) -> List[SkillCapability]:
        """Skill capabilities."""
        return self._capabilities
    
    @property
    def external_apis(self) -> List[ExternalAPIType]:
        """External APIs used by skill."""
        return self._external_apis
    
    @abstractmethod
    def description(self) -> str:
        """
        Get skill description.
        
        Returns:
            Human-readable description of skill functionality
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Args:
            inputs: Input parameters
        
        Returns:
            (is_valid, error_message or None)
        """
        pass
    
    @abstractmethod
    def execute(self, context: ExecutionContext) -> SkillResult:
        """
        Execute skill.
        
        Args:
            context: Execution context with inputs, audit trail, mode
        
        Returns:
            SkillResult with status, output, and audit trail
        """
        pass
    
    def initialize(self) -> None:
        """
        Initialize skill (called before first execution).
        
        Override in subclasses for setup logic (e.g., loading configs, 
        connecting to external APIs).
        """
        self._initialized = True
    
    def shutdown(self) -> None:
        """
        Shutdown skill (called after execution complete).
        
        Override in subclasses for cleanup logic (e.g., closing connections).
        """
        pass
    
    def register_api_provider(
        self,
        api_type: ExternalAPIType,
        provider_name: str,
        provider: Any
    ) -> None:
        """
        Register external API provider.
        
        Example:
            skill.register_api_provider(
                ExternalAPIType.GITHUB,
                "real",
                GitHubRealClient()
            )
            skill.register_api_provider(
                ExternalAPIType.GITHUB,
                "mock",
                GitHubMockClient()
            )
        """
        if api_type not in self._api_selectors:
            self._api_selectors[api_type] = APISelector(api_type)
        
        self._api_selectors[api_type].register_provider(provider_name, provider)
    
    def select_api_provider(self, api_type: ExternalAPIType, name: str) -> Any:
        """Select external API provider for runtime use."""
        if api_type not in self._api_selectors:
            raise ValueError(f"No API selector for {api_type}")
        return self._api_selectors[api_type].select_provider(name)
    
    def get_api_provider(self, api_type: ExternalAPIType) -> Any:
        """Get active external API provider."""
        if api_type not in self._api_selectors:
            raise ValueError(f"No API selector for {api_type}")
        return self._api_selectors[api_type].get_active_provider()
    
    def list_api_providers(self, api_type: ExternalAPIType) -> List[str]:
        """List registered providers for API type."""
        if api_type not in self._api_selectors:
            return []
        return self._api_selectors[api_type].list_providers()
    
    def is_initialized(self) -> bool:
        """Check if skill is initialized."""
        return self._initialized
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} name={self.name} version={self.version}>"


class ExecutableSkill(SkillBase):
    """
    Abstract base class for executable skills (non-chainable).
    
    This is a convenience class for skills that don't chain to other skills.
    """
    
    def execute(self, context: ExecutionContext) -> SkillResult:
        """Execute skill with standard error handling."""
        start_time = context.audit_trail.start_time
        
        try:
            context.log_info(f"Executing {self.name}:{self.version}")
            
            # Validate inputs
            is_valid, error_msg = self.validate_inputs(context.inputs)
            if not is_valid:
                context.log_error(f"Input validation failed: {error_msg}")
                return SkillResult(
                    skill_name=self.name,
                    skill_version=self.version,
                    status=ExecutionStatus.FAILED,
                    error=error_msg
                )
            
            # Execute
            result = self.run(context)
            
            context.log_info(f"Executed {self.name}:{self.version} successfully")
            context.audit_trail.set_complete()
            
            return SkillResult(
                skill_name=self.name,
                skill_version=self.version,
                status=ExecutionStatus.COMPLETED,
                output=result
            )
        
        except Exception as e:
            error_msg = str(e)
            context.log_error(error_msg)
            context.audit_trail.set_failed()
            
            return SkillResult(
                skill_name=self.name,
                skill_version=self.version,
                status=ExecutionStatus.FAILED,
                error=error_msg
            )
    
    @abstractmethod
    def run(self, context: ExecutionContext) -> Any:
        """
        Run skill logic.
        
        This is called by execute() after input validation.
        
        Args:
            context: Execution context
        
        Returns:
            Output of skill execution (any type)
        """
        pass
