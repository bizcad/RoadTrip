from pathlib import Path

from src.skills.registry_list import execute


def test_registry_list_returns_sorted_skill_names(tmp_path):
    registry = tmp_path / "config" / "skills-registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        """
metadata:
  registry_version: "1.0"
skills:
  rules_engine:
    version: 1.0.0
  auth_validator:
    version: 1.0.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = execute({"repo_path": str(tmp_path), "registry_path": "config/skills-registry.yaml"})

    assert result["success"] is True
    assert result["decision"] == "APPROVE"
    assert result["skills"] == ["auth_validator", "rules_engine"]
    assert result["total_skills"] == 2


def test_registry_list_rejects_missing_registry(tmp_path):
    result = execute({"repo_path": str(tmp_path), "registry_path": "config/skills-registry.yaml"})
    assert result["success"] is False
    assert result["error_code"] == "REGISTRY_NOT_FOUND"
