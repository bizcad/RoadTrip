"""
NotebookQuerySkill: Executes queries against specific NotebookLM notebooks.
Uses the 'MemoryTaggerSkill' output to route queries effectively.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List

__version__ = "0.1.0"

# Path to the notebooklm executable
NOTEBOOKLM_EXE = r"C:\Users\bizca\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe"

def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a query against one or more NotebookLM notebooks.
    
    Args:
        context: Expects 'prompt' (the question) 
                 and 'matched_notebooks' (list of {id: str, title: str}).
                 If 'matched_notebooks' is missing, it will attempt to list or use default.
    
    Returns:
        Dict containing 'answers' (list of strings or a combined string).
    """
    prompt = context.get("prompt") or context.get("query")
    notebooks = context.get("matched_notebooks", [])
    
    if not prompt:
        return {"success": False, "error": "No prompt provided to NotebookQuerySkill"}

    if not notebooks:
        return {"success": False, "error": "No notebooks targeted for query. Run MemoryTaggerSkill first."}

    answers = []
    
    for nb in notebooks:
        nb_id = nb.get("id")
        if not nb_id or "TBD" in nb_id:
            continue
            
        print(f"  → Querying NotebookLM: {nb.get('title')} ({nb_id})")
        
        try:
            # We use the 'ask' command which is the most robust for retrieval
            # Since we can't 'use' a notebook persistently in this stateless script,
            # we check if 'ask' supports a notebook flag or use the 'use' then 'ask' approach in a subshell.
            
            # Note: The notebooklm CLI might need the 'use' command first.
            # We'll try to chain them if possible, or use the direct 'ask' if supported.
            
            cmd = [NOTEBOOKLM_EXE, "use", nb_id, ";", NOTEBOOKLM_EXE, "ask", f'"{prompt}"']
            # Running via shell because of the semicolon
            result = subprocess.run(
                " ".join(cmd),
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                answers.append({
                    "notebook_title": nb.get("title"),
                    "notebook_id": nb_id,
                    "answer": result.stdout.strip()
                })
            else:
                answers.append({
                    "notebook_title": nb.get("title"),
                    "notebook_id": nb_id,
                    "error": result.stderr.strip()
                })
        except Exception as e:
            answers.append({
                "notebook_title": nb.get("title"),
                "notebook_id": nb_id,
                "error": str(e)
            })

    if not answers:
        return {"success": False, "error": "Failed to retrieve answers from any targeted notebooks."}

    return {
        "success": True,
        "answers": answers,
        "combined_answer": "\n\n".join([f"### Source: {a.get('notebook_title')}\n{a.get('answer') or a.get('error')}" for a in answers])
    }
