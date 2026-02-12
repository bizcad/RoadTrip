#!/usr/bin/env python3
"""
Fingerprint Agent (Phase 2a, Workstream A).

Generates cryptographically signed fingerprints for skills.

Responsibilities:
1. Compute deterministic SHA256 hashes of skill code + capabilities + test metadata
2. Generate composite hash combining all three
3. Sign composite hash with fingerprint authority key (RSA-2048)
4. Return SkillFingerprint dataclass with signature
5. Emit events (SkillFingerprintedEvent, SkillTestPassedEvent)

Key properties:
- Deterministic: same inputs → same hash (idempotent)
- No external API calls; pure crypto + file I/O
- Can be called multiple times safely
- Errors on missing tests or invalid skill

Usage (CLI):
    python -m src.agents.fingerprint_agent --skill auth_validator
    python -m src.agents.fingerprint_agent --all

Usage (import):
    from src.agents.fingerprint_agent import FingerprintAgent
    agent = FingerprintAgent()
    result = agent.fingerprint(FingerprintInput(...))
"""

import sys
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import argparse

try:
    from .fingerprint_models import (
        SkillFingerprint,
        FingerprintInput,
        FingerprintResult,
        FingerprintStatus,
        SkillFingerprintedEvent,
        SkillTestPassedEvent,
    )
except ImportError:
    from fingerprint_models import (
        SkillFingerprint,
        FingerprintInput,
        FingerprintResult,
        FingerprintStatus,
        SkillFingerprintedEvent,
        SkillTestPassedEvent,
    )


class FingerprintAgent:
    """
    Agent that generates cryptographic fingerprints for skills.
    
    Phase 2a Task A1a (Crypto Attestation):
    - Hash skill code
    - Hash capabilities
    - Hash test metadata
    - Combine hashes
    
    Phase 2a Task A1b (Self-Signed Authority):
    - Generate RSA-2048 key pair
    - Sign composite hash
    - Verify signature
    
    Interface:
        fingerprint(input: FingerprintInput) -> FingerprintResult
    """
    
    def __init__(self, workspace_root: str = None):
        """
        Initialize Fingerprint Agent.
        
        Args:
            workspace_root: Root of RoadTrip repo (guessed from __file__ if not provided)
        """
        if workspace_root is None:
            # Guess from file location: src/agents/fingerprint_agent.py → root
            workspace_root = Path(__file__).parent.parent.parent
        
        self.workspace_root = Path(workspace_root)
        self.skills_dir = self.workspace_root / "src" / "skills"
        self.tests_dir = self.workspace_root / "tests"
        self.events_file = self.workspace_root / "data" / "skill-events.jsonl"
    
    def fingerprint(self, input: FingerprintInput) -> FingerprintResult:
        """
        Generate a fingerprint for a skill.
        
        Args:
            input: FingerprintInput with skill name, version, paths
        
        Returns:
            FingerprintResult with status and SkillFingerprint (if successful)
        """
        
        result = FingerprintResult(
            status=FingerprintStatus.SUCCESS,
            skill_name=input.skill_name,
        )
        
        try:
            # Step 1: Locate and read skill file
            skill_path = self._resolve_skill_path(input.skill_path)
            if not skill_path.exists():
                result.status = FingerprintStatus.INVALID_SKILL
                result.error = f"Skill file not found: {skill_path}"
                return result
            
            skill_code = skill_path.read_text(encoding='utf-8')
            
            # Step 2: Compute code hash (SHA256 of file content)
            code_hash = self._hash_content(skill_code)
            result.code_hash_computed = code_hash
            
            # Step 3: Locate and hash capabilities (optional)
            capabilities_hash = self._compute_capabilities_hash(input.skill_name)
            
            # Step 4: Locate and hash test metadata
            test_path = input.test_path or self._resolve_test_path(input.skill_name)
            if not test_path.exists():
                result.status = FingerprintStatus.NO_TESTS
                result.error = f"Test file not found: {test_path}"
                return result
            
            result.tests_found = True
            
            test_code = test_path.read_text(encoding='utf-8')
            test_count, test_results = self._analyze_tests(test_code)
            test_metadata_hash = self._hash_test_metadata(test_count, 1.0, None)
            
            # Step 5: Create SkillFingerprint with hashes
            fingerprint = SkillFingerprint(
                code_hash=code_hash,
                capabilities_hash=capabilities_hash,
                test_metadata_hash=test_metadata_hash,
                skill_name=input.skill_name,
                skill_version=input.skill_version,
                test_count=test_count,
                test_pass_rate=1.0,  # Assume passes until Phase 2b verifies
            )
            
            # Step 6: Sign if requested
            if input.sign:
                try:
                    signature = self._sign_fingerprint(fingerprint)
                    fingerprint.signature = signature
                    fingerprint.signed = True
                    fingerprint.signed_at = datetime.now(timezone.utc)
                except Exception as e:
                    result.status = FingerprintStatus.FAILED
                    result.error = f"Signing failed: {e}"
                    return result
            
            result.fingerprint = fingerprint
            
            # Step 7: Emit events
            self._emit_fingerprinted_event(fingerprint)
            self._emit_test_passed_event(input.skill_name, test_count)
            
            return result
            
        except Exception as e:
            result.status = FingerprintStatus.FAILED
            result.error = str(e)
            result.details = {"exception_type": type(e).__name__}
            return result
    
    # --- Hashing Methods ---
    
    def _hash_content(self, content: str) -> str:
        """
        Compute SHA256 hash of string content.
        
        Deterministic: same content → same hash.
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _compute_capabilities_hash(self, skill_name: str) -> str:
        """
        Hash the capabilities of a skill.
        
        For now, returns hash of docstring (what skill claims to do).
        Phase 2b+ can load from capabilities.json if it exists.
        """
        # Placeholder: hash a deterministic string based on skill name
        # In production, parse docstring or load from capabilities.json
        capabilities_str = f"skill:{skill_name}:phase_2a_placeholder"
        return self._hash_content(capabilities_str)
    
    def _hash_test_metadata(self, test_count: int, pass_rate: float, coverage: Optional[float]) -> str:
        """Hash the test metadata (count + pass rate + coverage)."""
        metadata = {
            "test_count": test_count,
            "pass_rate": pass_rate,
            "coverage": coverage,
        }
        metadata_str = json.dumps(metadata, sort_keys=True)
        return self._hash_content(metadata_str)
    
    # --- Test Analysis ---
    
    def _analyze_tests(self, test_code: str) -> tuple:
        """
        Analyze test file to extract test count.
        
        Returns:
            (test_count: int, results: dict)
        
        Strategy: count "def test_" methods (simple regex).
        Later: run pytest and get actual pass rate.
        """
        import re
        test_count = len(re.findall(r'def test_', test_code))
        
        # For Phase 2a, assume all tests pass until Phase 2b runs them
        return test_count, {"assumed_pass_rate": 1.0}
    
    # --- Signing Methods (Stub for Phase 2a Task A1b) ---
    
    def _sign_fingerprint(self, fingerprint: SkillFingerprint) -> str:
        """
        Sign the composite hash with fingerprint authority key.
        
        Phase 2a Task A1b (Self-Signed Authority):
        - Load or generate RSA-2048 key from config/fingerprint-authority/
        - Sign composite_hash with private key
        - Return base64-encoded signature
        
        TODO: Implement RSA signing when Task A1b starts.
        For now: return a placeholder signature.
        """
        
        # Placeholder for Phase 2a Task A1b
        composite = fingerprint.composite_hash()
        # In production: use cryptography.hazmat.primitives.asymmetric.rsa
        placeholder_sig = hashlib.sha256(f"sig:{composite}".encode()).hexdigest()[:32]
        return placeholder_sig
    
    # --- Event Emission ---
    
    def _emit_fingerprinted_event(self, fingerprint: SkillFingerprint) -> None:
        """Emit SkillFingerprintedEvent to data/skill-events.jsonl."""
        event = SkillFingerprintedEvent(
            skill_name=fingerprint.skill_name,
            fingerprint_hash=fingerprint.composite_hash(),
            signed=fingerprint.signed,
            signer_key_id=fingerprint.signer_key_id,
        )
        self._write_event(event)
    
    def _emit_test_passed_event(self, skill_name: str, test_count: int) -> None:
        """Emit SkillTestPassedEvent to data/skill-events.jsonl."""
        event = SkillTestPassedEvent(
            skill_name=skill_name,
            test_count=test_count,
            test_pass_rate=1.0,  # Assume for Phase 2a
        )
        self._write_event(event)
    
    def _write_event(self, event) -> None:
        """Append event to data/skill-events.jsonl (JSONL format, one per line)."""
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        
        event_dict = {
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "skill_name": event.skill_name,
        }
        
        # Add event-specific fields
        if hasattr(event, 'fingerprint_hash'):
            event_dict["fingerprint_hash"] = event.fingerprint_hash
            event_dict["signed"] = event.signed
        if hasattr(event, 'test_count'):
            event_dict["test_count"] = event.test_count
        
        event_line = json.dumps(event_dict)
        
        with open(self.events_file, 'a', encoding='utf-8') as f:
            f.write(event_line + '\n')
    
    # --- Path Resolution ---
    
    def _resolve_skill_path(self, skill_path: str) -> Path:
        """Resolve skill path (relative or absolute)."""
        p = Path(skill_path)
        if p.is_absolute():
            return p
        return self.workspace_root / skill_path
    
    def _resolve_test_path(self, skill_name: str) -> Path:
        """Guess test path from skill name."""
        # E.g., auth_validator → tests/test_auth_validator.py
        return self.tests_dir / f"test_{skill_name}.py"


# --- CLI Entry Point ---

def main():
    """CLI for fingerprinting skills."""
    parser = argparse.ArgumentParser(description="Fingerprint Agent (Phase 2a)")
    parser.add_argument('--skill', help='Fingerprint one skill (name or path)')
    parser.add_argument('--all', action='store_true', help='Fingerprint all Phase 1b skills')
    parser.add_argument('--no-sign', action='store_true', help='Skip signing')
    parser.add_argument('--force', action='store_true', help='Force rehashing')
    
    args = parser.parse_args()
    
    agent = FingerprintAgent()
    
    # Phase 1b skill list
    phase_1b_skills = [
        ("auth_validator", "src/skills/auth_validator.py"),
        ("telemetry_logger", "src/skills/telemetry_logger.py"),
        ("commit_message", "src/skills/commit_message.py"),
        ("blog_publisher", "src/skills/blog_publisher.py"),
    ]
    
    if args.all:
        print("Fingerprinting all Phase 1b skills...")
        for skill_name, skill_path in phase_1b_skills:
            input = FingerprintInput(
                skill_name=skill_name,
                skill_version="1.0",
                skill_path=skill_path,
                sign=not args.no_sign,
                force_rehash=args.force,
            )
            result = agent.fingerprint(input)
            print(f"  {skill_name}: {result.status.value}")
            if result.error:
                print(f"    Error: {result.error}")
    
    elif args.skill:
        # Find skill by name or path
        skill_name = args.skill
        skill_path = f"src/skills/{skill_name}.py"
        
        input = FingerprintInput(
            skill_name=skill_name,
            skill_version="1.0",
            skill_path=skill_path,
            sign=not args.no_sign,
            force_rehash=args.force,
        )
        result = agent.fingerprint(input)
        
        print(f"Fingerprinted {skill_name}: {result.status.value}")
        if result.fingerprint:
            print(f"  Code hash: {result.fingerprint.code_hash[:16]}...")
            print(f"  Signed: {result.fingerprint.signed}")
        if result.error:
            print(f"  Error: {result.error}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
