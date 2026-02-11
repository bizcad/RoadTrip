#!/usr/bin/env python3
"""Quick test of GIT_ASKPASS functionality"""
import subprocess
import os
from pathlib import Path

print("TEST: Reading PAT...")
pat_file = Path("G:/repos/AI/RoadTrip/ProjectSecrets/PAT.txt")
pat = pat_file.read_text().strip()
print(f"PAT length: {len(pat)}")

print("\nTEST: Setting up environment...")
env = os.environ.copy()
env['GIT_ASKPASS'] = str(Path("G:/repos/AI/RoadTrip/scripts/git_askpass_helper.py"))
env['GIT_ASKPASS_TOKEN'] = pat
env['SSH_ASKPASS_REQUIRE'] = 'never'

print("\nTEST: Running git push...")
result = subprocess.run(
    ["git", "push", "origin", "main"],
    cwd="G:/repos/AI/RoadTrip",
    capture_output=True,
    text=True,
    timeout=15,
    env=env
)

print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
