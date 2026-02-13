"""
git_push_autonomous_models.py

Data models for git_push_autonomous.py skill.
"""

from enum import Enum


class GitPushStatus(Enum):
    """Status of git push operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ALREADY_UP_TO_DATE = "already_up_to_date"


class PushReason(Enum):
    """Reason why push succeeded or failed."""
    SUCCESS = "success"
    NO_COMMITS = "no_commits"
    REMOTE_NOT_FOUND = "remote_not_found"
    AUTH_FAILED = "auth_failed"
    NETWORK_ERROR = "network_error"
    GIT_ERROR = "git_error"
    ALREADY_PUSHED = "already_pushed"
