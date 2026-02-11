#!/usr/bin/env python3
"""
GIT_ASKPASS helper script - returns the GitHub PAT when git asks for password
"""
import sys
import os
from pathlib import Path

# Get the PAT from environment or file
pat = os.environ.get('GIT_ASKPASS_TOKEN')
if not pat:
    pat_file = Path(__file__).parent.parent / "ProjectSecrets" / "PAT.txt"
    pat = pat_file.read_text().strip()

# Return the token (git will use this for the password when asked)
print(pat)
