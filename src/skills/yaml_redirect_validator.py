"""Skill: validate YAML redirect chains for corruption risks.

Validates `deprecated_in_favor_of` links as a directed graph and enforces:
- DAG property (no cycles)
- max hop count
- target existence (with optional terminal targets such as `prospective`)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RedirectValidationRequest:
    """Input contract for redirect-chain validation."""

    yaml_path: str
    repo_path: str = "."
    entry_map_path: str = ""
    max_hops: int = 3
    terminal_targets: tuple[str, ...] = ("prospective",)
    suggest_prospective_on_missing: bool = True


class YamlRedirectValidatorSkill:
    """Validate `deprecated_in_favor_of` redirect graphs in YAML files."""

    def validate(self, request: RedirectValidationRequest) -> dict[str, Any]:
        yaml_file = (Path(request.repo_path).resolve() / request.yaml_path).resolve()
        if not yaml_file.exists():
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "YAML_NOT_FOUND",
                "error": f"YAML file not found: {yaml_file}",
            }

        data = self._load_yaml(yaml_file)
        entry_map = self._resolve_entry_map(data, request.entry_map_path)
        if not entry_map:
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "NO_ENTRY_MAP",
                "error": "Could not find a mapping of entries to validate",
            }

        redirect_map = self._build_redirect_map(entry_map)
        result = self._analyze_redirects(
            redirect_map=redirect_map,
            max_hops=max(1, request.max_hops),
            terminal_targets=set(request.terminal_targets),
            suggest_prospective_on_missing=request.suggest_prospective_on_missing,
        )

        blocked = len(result["cycles"]) > 0 or len(result["max_hop_violations"]) > 0
        decision = "BLOCK" if blocked else "APPROVE"

        return {
            "success": True,
            "decision": decision,
            "yaml_path": request.yaml_path,
            "entry_count": len(entry_map),
            "redirect_count": len(redirect_map),
            "is_dag": len(result["cycles"]) == 0,
            "max_hops": max(1, request.max_hops),
            "cycles": result["cycles"],
            "max_hop_violations": result["max_hop_violations"],
            "missing_targets": result["missing_targets"],
            "suggested_prospective_redirects": result["suggested_prospective_redirects"],
        }

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        with open(path, "r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle) or {}
        if isinstance(value, dict):
            return value
        return {}

    def _resolve_entry_map(self, data: dict[str, Any], entry_map_path: str) -> dict[str, dict[str, Any]]:
        if entry_map_path:
            pointer: Any = data
            for part in entry_map_path.split("."):
                if not isinstance(pointer, dict):
                    return {}
                pointer = pointer.get(part)
            if isinstance(pointer, dict):
                return {
                    str(key): value
                    for key, value in pointer.items()
                    if isinstance(value, dict)
                }
            return {}

        for candidate_key in ("skills", "entries", "registry", "items"):
            candidate = data.get(candidate_key)
            if isinstance(candidate, dict):
                mapped = {
                    str(key): value
                    for key, value in candidate.items()
                    if isinstance(value, dict)
                }
                if mapped:
                    return mapped

        mapped = {str(key): value for key, value in data.items() if isinstance(value, dict)}
        return mapped

    def _build_redirect_map(self, entry_map: dict[str, dict[str, Any]]) -> dict[str, str]:
        redirects: dict[str, str] = {}
        for entry_id, payload in entry_map.items():
            target = payload.get("deprecated_in_favor_of")
            if isinstance(target, str) and target.strip():
                redirects[entry_id] = target.strip()
        return redirects

    def _analyze_redirects(
        self,
        redirect_map: dict[str, str],
        max_hops: int,
        terminal_targets: set[str],
        suggest_prospective_on_missing: bool,
    ) -> dict[str, Any]:
        cycles: list[list[str]] = []
        max_hop_violations: list[dict[str, Any]] = []
        missing_targets: list[dict[str, str]] = []
        suggestions: list[dict[str, str]] = []

        visiting: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            if node in visiting:
                if node in stack:
                    idx = stack.index(node)
                    cycles.append(stack[idx:] + [node])
                return

            visiting.add(node)
            stack.append(node)

            nxt = redirect_map.get(node)
            if nxt:
                if nxt in redirect_map:
                    dfs(nxt)
                elif nxt not in terminal_targets:
                    missing_targets.append({"source": node, "target": nxt})
                    if suggest_prospective_on_missing:
                        suggestions.append({"source": node, "suggested_target": "prospective"})

            stack.pop()
            visiting.remove(node)
            visited.add(node)

        for node in redirect_map:
            dfs(node)

        for source in redirect_map:
            hops = 0
            current = source
            seen: set[str] = set()
            while current in redirect_map:
                if current in seen:
                    break
                seen.add(current)
                nxt = redirect_map[current]
                hops += 1
                if hops > max_hops:
                    max_hop_violations.append(
                        {
                            "source": source,
                            "hops": hops,
                            "max_hops": max_hops,
                        }
                    )
                    break
                if nxt in terminal_targets or nxt not in redirect_map:
                    break
                current = nxt

        return {
            "cycles": cycles,
            "max_hop_violations": max_hop_violations,
            "missing_targets": missing_targets,
            "suggested_prospective_redirects": suggestions,
        }


def execute(input_data: dict[str, Any]) -> dict[str, Any]:
    """Skill entrypoint for validating redirect chains in YAML."""

    yaml_path = str(input_data.get("yaml_path", "")).strip()
    if not yaml_path:
        return {
            "success": False,
            "decision": "REJECT",
            "error_code": "INVALID_INPUT",
            "error": "yaml_path is required",
        }

    terminal_targets_raw = input_data.get("terminal_targets", ["prospective"])
    if isinstance(terminal_targets_raw, list):
        terminal_targets = tuple(str(value).strip() for value in terminal_targets_raw if str(value).strip())
    else:
        terminal_targets = ("prospective",)

    request = RedirectValidationRequest(
        yaml_path=yaml_path,
        repo_path=str(input_data.get("repo_path", ".")),
        entry_map_path=str(input_data.get("entry_map_path", "")).strip(),
        max_hops=int(input_data.get("max_hops", 3)),
        terminal_targets=terminal_targets or ("prospective",),
        suggest_prospective_on_missing=bool(input_data.get("suggest_prospective_on_missing", True)),
    )

    skill = YamlRedirectValidatorSkill()
    return skill.validate(request)
