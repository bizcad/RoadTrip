"""
registration.py (WS3) - Skill Registration

Registers skills in the registry.
- Computes fingerprint via WS1
- Checks WS0 for duplicates
- Writes to registry
"""

from datetime import datetime
from typing import List, Optional

from .base_agent import BaseAgent
from .fingerprint_generator import FingerprintGenerator
from .registry_reader import RegistryReader
from .registry_models import SkillMetadata, RegistrationResult, AgentState, SkillStatus


class Registration(BaseAgent):
    """WS3: Registration - Register skills in registry."""
    
    def __init__(
        self,
        fingerprint_generator: FingerprintGenerator,
        registry_reader: RegistryReader,
        use_mock: bool = True
    ):
        """
        Initialize registration agent.
        
        Args:
            fingerprint_generator: Reference to WS1
            registry_reader: Reference to WS0
            use_mock: Use mock or real fingerprints
        """
        super().__init__("WS3", use_mock)
        self.generator = fingerprint_generator
        self.registry_reader = registry_reader
    
    def handle_query(self, query: str) -> RegistrationResult:
        """
        Handle registration requests.
        
        Query format: "register:{skill_name}:{version}:{capabilities_csv}:{author}:{tests}:{coverage}"
        Response: RegistrationResult
        """
        self.transition_state(AgentState.COMPUTING, f"Registering: {query[:50]}")
        
        try:
            parts = query.replace("register:", "").split(":")
            if len(parts) < 4:
                raise ValueError(f"Invalid query format. Expected at least 4 parts")
            
            skill_name = parts[0]
            version = parts[1]
            capabilities = parts[2].split(",") if parts[2] else []
            author = parts[3]
            tests = int(parts[4]) if len(parts) > 4 else 0
            coverage = float(parts[5]) if len(parts) > 5 else 0.0
            
            result = self.register_skill(
                skill_name, version, capabilities, author, tests, coverage
            )
            
            self.transition_state(AgentState.VERIFIED, f"Registered: {skill_name}")
            return result
        
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Registration failed: {e}")
            raise
    
    def register_skill(
        self,
        skill_name: str,
        version: str,
        capabilities: List[str],
        author: str,
        test_count: int = 0,
        test_coverage: float = 0.0,
        description: str = "",
        source_files: Optional[List[str]] = None
    ) -> RegistrationResult:
        """
        Register a skill in the registry.
        
        Args:
            skill_name: Skill name
            version: Semver (e.g., "1.0.0")
            capabilities: List of capability names
            author: Author name
            test_count: Number of tests
            test_coverage: Test coverage percentage
            description: Skill description
            source_files: List of source file paths
        """
        # Step 1: Ask WS0 if already registered
        self.transition_state(AgentState.QUERYING, f"Checking if {skill_name} already registered")
        existing_skill = self.registry_reader.handle_query(f"get_skill:{skill_name}")
        
        if existing_skill and existing_skill.version == version:
            raise ValueError(f"Skill {skill_name}:{version} already registered!")
        
        # Step 2: Get fingerprint from WS1
        self.transition_state(AgentState.COMPUTING, f"Computing fingerprint via WS1")
        fingerprint_result = self.generator.handle_query(f"compute:{skill_name}:{version}")
        fingerprint = fingerprint_result.fingerprint
        
        # Step 3: Create metadata
        if not source_files:
            source_files = [
                f"src/skills/{skill_name}.py",
                f"src/skills/{skill_name}_models.py",
                f"tests/test_{skill_name}.py"
            ]
        
        metadata = SkillMetadata(
            name=skill_name,
            version=version,
            fingerprint=fingerprint,
            author=author,
            capabilities=capabilities,
            tests=test_count,
            test_coverage=test_coverage,
            status=SkillStatus.ACTIVE,
            created=datetime.now().isoformat(),
            description=description,
            source_files=source_files
        )
        
        # Step 4: Write to registry
        self.transition_state(AgentState.WRITING, f"Writing {skill_name} to registry")
        registry = self.registry_reader.read_registry()
        registry.skills[skill_name] = metadata
        self.registry_reader.write_registry(registry)
        
        self.logger.info(f"✅ Registered {skill_name}:{version} with fingerprint {fingerprint}")
        
        return RegistrationResult(
            skill_name=skill_name,
            version=version,
            fingerprint=fingerprint,
            status="registered",
            message=f"Successfully registered {skill_name}:{version}"
        )
