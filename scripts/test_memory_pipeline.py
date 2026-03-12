"""
Test script for the Memory Retrieval Pipeline.
Demonstrates: Sense -> Tagger -> Router -> Match
"""

import sys
from pathlib import Path
import json

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.orchestrator import Orchestrator
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def main():
    try:
        orch = Orchestrator()
    except Exception as e:
        print(f"Failed to init Orchestrator: {e}")
        return
    
    # 1. Sample Query
    test_query = "What are the 27 thoughts on agentic safety and the 7 levels of memory?"
    
    print(f"User Query: {test_query}\n")
    
    # 2. Run Tagger
    print("[1/2] Running MemoryTaggerSkill...")
    tag_result = orch.run_skill("memory_tagger", {"query": test_query})
    
    if tag_result.status == "SUCCESS":
        tags = tag_result.output.get("tags")
        notebooks = tag_result.output.get("matched_notebooks")
        print(f"  OK: Tags extracted: {tags}")
        print("  OK: Notebooks matched:")
        print(json.dumps(notebooks, indent=4))
    else:
        print(f"  ERR: Tagger failed: {tag_result.error}")
        return

    # 3. Explain how NotebookQuerySkill would take it from here
    print("\n[2/2] Routing to NotebookQuerySkill...")
    if notebooks:
        print(f"  INFO: Prepared to query {len(notebooks)} notebooks selectively.")
        for nb in notebooks:
            print(f"  TARGET: {nb.get('title')} (ID: {nb.get('id')})")
    else:
        print("  INFO: No relevant notebooks found in catalog.")

if __name__ == "__main__":
    main()
