"""
config_resolver.py (Phase 3) - Configuration resolution

Implements config source priority: hard-code -> .env -> Secrets
Allows DAG to make runtime decisions about config sources.
"""

import os
from typing import Any, Dict, Optional
from pathlib import Path
from enum import Enum
import json


class ConfigSource(str, Enum):
    """Configuration source priority."""
    HARDCODED = "hardcoded"  # Compiled into code
    ENV = "env"              # Environment variables
    SECRETS = "secrets"      # Secret management (Vault, etc.)
    DEFAULT = "default"      # Default values


class ConfigResolver:
    """
    Resolves configuration with priority chain.
    
    Resolution order:
    1. Hard-coded values (highest priority)
    2. Environment variables
    3. Secret management system
    4. Default values (lowest priority)
    
    Used by DAGExecutor to decide where to get config values.
    """
    
    def __init__(self):
        """Initialize resolver."""
        self.hardcoded_config: Dict[str, Any] = {}
        self.env_config: Dict[str, Any] = {}
        self.secrets_config: Dict[str, Any] = {}
        self.default_config: Dict[str, Any] = {}
        self._secrets_file: Optional[Path] = None
        self._env_file: Optional[Path] = None
    
    def set_secrets_file(self, path: str) -> None:
        """Set path to secrets file (JSON)."""
        self._secrets_file = Path(path)
        self._load_secrets()
    
    def set_env_file(self, path: str) -> None:
        """Set path to .env file."""
        self._env_file = Path(path)
        self._load_env_file()
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file."""
        if not self._env_file or not self._env_file.exists():
            return
        
        try:
            with open(self._env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.env_config[key.strip()] = value.strip()
        except Exception as e:
            print(f"[WARN] Failed to load .env file: {e}")
    
    def _load_secrets(self) -> None:
        """Load secrets from JSON file."""
        if not self._secrets_file or not self._secrets_file.exists():
            return
        
        try:
            with open(self._secrets_file) as f:
                self.secrets_config = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load secrets file: {e}")
    
    def register_hardcoded(self, key: str, value: Any) -> None:
        """Register hard-coded configuration value."""
        self.hardcoded_config[key] = value
    
    def register_hardcoded_batch(self, config: Dict[str, Any]) -> None:
        """Register batch of hard-coded values."""
        self.hardcoded_config.update(config)
    
    def register_default(self, key: str, value: Any) -> None:
        """Register default configuration value."""
        self.default_config[key] = value
    
    def register_defaults_batch(self, config: Dict[str, Any]) -> None:
        """Register batch of default values."""
        self.default_config.update(config)
    
    def get(
        self,
        key: str,
        default: Optional[Any] = None,
        required: bool = False
    ) -> Any:
        """
        Get configuration value with priority resolution.
        
        Args:
            key: Configuration key
            default: Default value if not found
            required: Raise error if not found
        
        Returns:
            Configuration value
        
        Raises:
            KeyError: If required=True and key not found
        """
        # Check priorities in order
        if key in self.hardcoded_config:
            return self.hardcoded_config[key]
        
        # Check environment (both .env and os.environ)
        if key in self.env_config:
            return self.env_config[key]
        
        if key in os.environ:
            return os.environ[key]
        
        # Check secrets
        if key in self.secrets_config:
            return self.secrets_config[key]
        
        # Check defaults
        if key in self.default_config:
            return self.default_config[key]
        
        # Not found
        if required:
            raise KeyError(f"Required config key not found: {key}")
        
        return default
    
    def get_source(self, key: str) -> Optional[ConfigSource]:
        """
        Get the source of a configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            ConfigSource enum indicating where value came from, or None if not found
        """
        if key in self.hardcoded_config:
            return ConfigSource.HARDCODED
        if key in self.env_config or key in os.environ:
            return ConfigSource.ENV
        if key in self.secrets_config:
            return ConfigSource.SECRETS
        if key in self.default_config:
            return ConfigSource.DEFAULT
        return None
    
    def get_with_source(self, key: str, default: Optional[Any] = None) -> tuple[Any, Optional[ConfigSource]]:
        """
        Get configuration value and its source.
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            (value, source) tuple
        """
        value = self.get(key, default)
        source = self.get_source(key)
        return value, source
    
    def get_all_keys(self) -> list[str]:
        """Get all registered configuration keys."""
        keys = set()
        keys.update(self.hardcoded_config.keys())
        keys.update(self.env_config.keys())
        keys.update(os.environ.keys())
        keys.update(self.secrets_config.keys())
        keys.update(self.default_config.keys())
        return sorted(list(keys))
    
    def debug_config(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get debug info about configuration.
        
        Args:
            key: Specific key to debug (None = all)
        
        Returns:
            Debug information
        """
        if key:
            return {
                "key": key,
                "value": self.get(key),
                "source": self.get_source(key),
                "sources_checked": self._get_sources_for_key(key)
            }
        
        return {
            "hardcoded_keys": list(self.hardcoded_config.keys()),
            "env_keys": list(self.env_config.keys()),
            "secrets_keys": list(self.secrets_config.keys()),
            "default_keys": list(self.default_config.keys()),
            "total_keys": len(self.get_all_keys())
        }
    
    def _get_sources_for_key(self, key: str) -> Dict[str, bool]:
        """Check all sources for a key."""
        return {
            "hardcoded": key in self.hardcoded_config,
            "env_file": key in self.env_config,
            "os_environ": key in os.environ,
            "secrets": key in self.secrets_config,
            "default": key in self.default_config
        }


class SkillConfigResolver(ConfigResolver):
    """
    Specialized config resolver for skills.
    
    Provides convenience methods for common skill configuration patterns.
    """
    
    def get_skill_config(self, skill_name: str, key: str, default: Optional[Any] = None) -> Any:
        """
        Get skill-specific configuration.
        
        Follows naming convention: {SKILL_NAME}_{KEY}
        
        Example: get_skill_config("github_api", "token")
                 looks for: GITHUB_API_TOKEN
        """
        full_key = f"{skill_name.upper()}_{key.upper()}"
        return self.get(full_key, default)
    
    def get_skill_config_required(self, skill_name: str, key: str) -> Any:
        """Get required skill configuration."""
        full_key = f"{skill_name.upper()}_{key.upper()}"
        return self.get(full_key, required=True)
    
    def get_api_url(self, api_name: str) -> str:
        """Get API URL configuration."""
        return self.get_skill_config(api_name, "url", "")
    
    def get_api_token(self, api_name: str) -> str:
        """Get API token configuration."""
        return self.get_skill_config(api_name, "token", "")
    
    def get_api_key(self, api_name: str) -> str:
        """Get API key configuration."""
        return self.get_skill_config(api_name, "key", "")
    
    def register_skill_hardcoded(self, skill_name: str, key: str, value: Any) -> None:
        """Register skill-specific hard-coded configuration."""
        full_key = f"{skill_name.upper()}_{key.upper()}"
        self.register_hardcoded(full_key, value)
    
    def register_skill_defaults(self, skill_name: str, config: Dict[str, Any]) -> None:
        """Register skill-specific default configuration."""
        defaults = {}
        for key, value in config.items():
            full_key = f"{skill_name.upper()}_{key.upper()}"
            defaults[full_key] = value
        self.register_defaults_batch(defaults)
