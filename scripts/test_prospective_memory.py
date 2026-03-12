import sys
import os
from pathlib import Path

# Fix path to include src/
sys.path.append(str(Path(__file__).parent.parent / "src"))

from skills.sensation_capture import execute as capture_sensation

def test_capture():
    print("--- Testing Sensation Capture ---")
    
    input_data = {
        "title": "Prospective Memory Research Bridge",
        "description": "We need to automate the 'Retrieve' (Research) phase of the CIRC-gee loop for prospective entries. This involves wiring NotebookLM queries to new sensations automatically.",
        "provenance": [
            "Session Log 20260305",
            "7 levels of memory.md",
            "Search results for YoungMoneyInvestments/claude-cortex"
        ],
        "tags": ["memory-and-context", "research", "automation"],
        "repo_path": str(Path(__file__).parent.parent)
    }
    
    result = capture_sensation(input_data)
    
    if result["success"]:
        print(f"[SUCCESS] {result['message']}")
        print(f"Entry ID: {result['entry_id']}")
        print(f"Path: {result['path']}")
        
        # Verify directory exists
        entry_path = Path(__file__).parent.parent / result["path"]
        if entry_path.exists():
            print(f"[VERIFIED] Directory exists at {entry_path}")
            files = list(entry_path.glob("*"))
            print(f"Files created: {[f.name for f in files]}")
    else:
        print(f"[FAILED] {result.get('error')}")

if __name__ == "__main__":
    test_capture()
