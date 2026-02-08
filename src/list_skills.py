#!/usr/bin/env python3
"""
Simple CLI to list available orchestrator skills
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from orchestrator import Orchestrator


def main():
    orch = Orchestrator()
    orch.print_skills()
    
    # Also show the dict for programmatic access
    skills_dict = orch.list_skills()
    print(f"\nSkills as dictionary: {skills_dict}")


if __name__ == "__main__":
    main()
