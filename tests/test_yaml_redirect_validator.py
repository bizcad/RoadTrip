from pathlib import Path

from src.skills.yaml_redirect_validator import execute


def _write_yaml(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def test_redirect_validator_approves_valid_dag(tmp_path):
    _write_yaml(
        tmp_path / "config" / "registry.yaml",
        """
skills:
  a:
    deprecated_in_favor_of: b
  b:
    deprecated_in_favor_of: c
  c:
    status: active
""",
    )

    result = execute(
        {
            "repo_path": str(tmp_path),
            "yaml_path": "config/registry.yaml",
            "entry_map_path": "skills",
            "max_hops": 3,
        }
    )

    assert result["success"] is True
    assert result["decision"] == "APPROVE"
    assert result["is_dag"] is True
    assert result["cycles"] == []
    assert result["max_hop_violations"] == []


def test_redirect_validator_blocks_cycle(tmp_path):
    _write_yaml(
        tmp_path / "config" / "registry.yaml",
        """
skills:
  a:
    deprecated_in_favor_of: b
  b:
    deprecated_in_favor_of: a
""",
    )

    result = execute(
        {
            "repo_path": str(tmp_path),
            "yaml_path": "config/registry.yaml",
            "entry_map_path": "skills",
            "max_hops": 5,
        }
    )

    assert result["success"] is True
    assert result["decision"] == "BLOCK"
    assert result["is_dag"] is False
    assert len(result["cycles"]) >= 1


def test_redirect_validator_blocks_max_hop_overflow(tmp_path):
    _write_yaml(
        tmp_path / "config" / "registry.yaml",
        """
skills:
  a:
    deprecated_in_favor_of: b
  b:
    deprecated_in_favor_of: c
  c:
    deprecated_in_favor_of: d
  d:
    status: active
""",
    )

    result = execute(
        {
            "repo_path": str(tmp_path),
            "yaml_path": "config/registry.yaml",
            "entry_map_path": "skills",
            "max_hops": 2,
        }
    )

    assert result["success"] is True
    assert result["decision"] == "BLOCK"
    assert len(result["max_hop_violations"]) >= 1


def test_redirect_validator_suggests_prospective_for_missing_target(tmp_path):
    _write_yaml(
        tmp_path / "config" / "registry.yaml",
        """
skills:
  old:
    deprecated_in_favor_of: removed-skill
""",
    )

    result = execute(
        {
            "repo_path": str(tmp_path),
            "yaml_path": "config/registry.yaml",
            "entry_map_path": "skills",
            "max_hops": 3,
            "suggest_prospective_on_missing": True,
        }
    )

    assert result["success"] is True
    assert result["decision"] == "APPROVE"
    assert result["missing_targets"] == [{"source": "old", "target": "removed-skill"}]
    assert result["suggested_prospective_redirects"] == [
        {"source": "old", "suggested_target": "prospective"}
    ]
