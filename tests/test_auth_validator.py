"""Tests for auth_validator.py skill."""

import pytest
from unittest.mock import patch, MagicMock
import os

from src.skills.auth_validator import AuthValidator
from src.skills.auth_validator_models import (
    AuthValidationResult,
    AuthStatus,
    AuthMethod,
)


@pytest.fixture
def validator():
    """Create an AuthValidator instance."""
    return AuthValidator()


class TestAuthValidatorHappyPath:
    """Happy path: valid Git configuration and SSH key."""
    
    def test_valid_auth_with_ssh_key(self, validator):
        """Valid Git config + SSH key = VALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push")
                    
                    assert result.status == AuthStatus.VALID
                    assert result.is_authorized == True
                    assert result.username == "Alice"
                    assert result.can_push == True
    
    def test_valid_auth_with_token(self, validator):
        """Valid Git config + token = VALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=False):
                with patch.object(validator, '_has_github_token', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Bob',
                        'user.email': 'bob@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push")
                    
                    assert result.status == AuthStatus.VALID
                    assert result.is_authorized == True
                    assert result.auth_method == AuthMethod.TOKEN


class TestAuthValidatorMissingConfig:
    """Missing or invalid Git configuration."""
    
    def test_missing_git_username(self, validator):
        """Missing user.name = INVALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            mock_git.side_effect = lambda key: {
                'user.name': None,  # Missing
                'user.email': 'alice@example.com',
            }.get(key)
            
            result = validator.validate(branch="main", operation="push")
            
            assert result.status == AuthStatus.INVALID
            assert result.is_authorized == False
            assert result.error_code == "MISSING_GIT_CONFIG"
    
    def test_missing_git_email(self, validator):
        """Missing user.email = INVALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            mock_git.side_effect = lambda key: {
                'user.name': 'Alice',
                'user.email': None,  # Missing
            }.get(key)
            
            result = validator.validate(branch="main", operation="push")
            
            assert result.status == AuthStatus.INVALID
            assert result.is_authorized == False


class TestAuthValidatorNoAuthMethod:
    """No SSH key and no token."""
    
    def test_no_auth_method(self, validator):
        """No SSH key + no token = INVALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=False):
                with patch.object(validator, '_has_github_token', return_value=False):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push")
                    
                    assert result.status == AuthStatus.INVALID
                    assert result.auth_method == AuthMethod.UNKNOWN
                    assert result.error_code == "NO_AUTH_METHOD"


class TestAuthValidatorSSHKeyValidation:
    """SSH key validation and readability."""
    
    def test_ssh_key_not_readable(self, validator):
        """SSH key exists but not readable = INVALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=False):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push")
                    
                    assert result.status == AuthStatus.INVALID
                    assert result.error_code == "SSH_KEY_NOT_FOUND"


class TestAuthValidatorTokenValidation:
    """Token validation."""
    
    def test_token_not_set(self, validator):
        """Token auth required but token not set = INVALID auth."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=False):
                with patch.object(validator, '_has_github_token', return_value=False):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push", require_ssh=False)
                    
                    assert result.status == AuthStatus.INVALID
                    assert result.error_code == "NO_AUTH_METHOD"


class TestAuthValidatorBranchPermissions:
    """Branch-level permissions."""
    
    def test_can_push_to_main(self, validator):
        """Valid auth for main branch."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push")
                    
                    assert result.can_push == True
                    assert result.target_branch == "main"
    
    def test_cannot_force_push_to_main(self, validator):
        """Cannot force-push to protected branch."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main", operation="push")
                    
                    assert result.can_force_push == False
    
    def test_can_push_to_feature_branch(self, validator):
        """Can push to feature branches."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="feature/new-ui", operation="push")
                    
                    assert result.can_push == True


class TestAuthValidatorDataStructure:
    """Result structure and serialization."""
    
    def test_result_has_required_fields(self, validator):
        """Result contains all required fields."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main")
                    
                    assert result.status is not None
                    assert result.auth_method is not None
                    assert result.is_authorized is not None
                    assert result.reasoning is not None
    
    def test_result_serializable(self, validator):
        """Result can be serialized to dict."""
        with patch.object(validator, '_get_git_config') as mock_git:
            with patch.object(validator, '_has_ssh_key', return_value=True):
                with patch.object(validator, '_validate_ssh_key', return_value=True):
                    mock_git.side_effect = lambda key: {
                        'user.name': 'Alice',
                        'user.email': 'alice@example.com',
                    }.get(key)
                    
                    result = validator.validate(branch="main")
                    d = result.to_dict()
                    
                    assert isinstance(d, dict)
                    assert 'status' in d
                    assert 'username' in d
