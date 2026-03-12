"""
MemoryTaggerSkill: Classifies and tags queries for targeted memory retrieval.
Extends the CIRC-gee loop by providing a fast lens for slow thinking layers.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List

__version__ = "0.1.0"

def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the 'prompt' or 'query' from context and returns relevant memory tags.
    
    Args:
        context: Expects 'prompt' or 'query'. 
                 Can also take 'catalog_path' (optional).
    
    Returns:
        Dict containing 'tags', 'notebook_ids', and 'confidence'.
    """
    prompt = context.get("prompt") or context.get("query")
    if not prompt:
        return {"success": False, "error": "No prompt or query provided to MemoryTaggerSkill"}

    # 1. Load the Memory Catalog
    catalog_path = context.get("catalog_path")
    if not catalog_path:
        catalog_path = Path(__file__).parent.parent.parent / "config" / "memory-catalog.yaml"
    else:
        catalog_path = Path(catalog_path)
    
    if not catalog_path.exists():
        return {"success": False, "error": f"Memory catalog not found at {catalog_path}"}

    try:
        with open(catalog_path, 'r') as f:
            catalog = yaml.safe_load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to parse memory catalog: {e}"}

    # 2. Simple Keyword / Semantic Tagger (V1: Keyword-based)
    # V2 would use an LLM to classify.
    found_tags = []
    matched_notebooks = []
    
    prompt_lower = prompt.lower()
    
    for notebook in catalog.get("notebooks", []):
        nb_id = notebook.get("id")
        nb_tags = notebook.get("tags", [])
        nb_desc = notebook.get("description", "").lower()
        nb_title = notebook.get("title", "").lower()
        
        # Match against tags directly (e.g., if user mentions #SAFETY)
        for tag in nb_tags:
            if tag.lower() in prompt_lower:
                found_tags.append(tag)
        
        # Match against description or title keywords
        # Split description into keywords (simple approach)
        keywords = nb_desc.split() + nb_title.split()
        for kw in keywords:
            if len(kw) > 3 and kw in prompt_lower:
                for tag in nb_tags:
                    if tag not in found_tags:
                        found_tags.append(tag)
                if nb_id not in [n.get("id") for n in matched_notebooks]:
                    matched_notebooks.append({"id": nb_id, "title": notebook.get("title")})
                break

    # If no notebooks matched, return a default "PHILOSOPHY" one or generic
    if not matched_notebooks:
        # Fallback to general philosophy if nothing else matches
        for notebook in catalog.get("notebooks", []):
            if "#PHILOSOPHY" in notebook.get("tags", []):
                matched_notebooks.append({"id": notebook.get("id"), "title": notebook.get("title")})
                found_tags.append("#PHILOSOPHY")

    # 3. Format result
    return {
        "success": True,
        "tags": list(set(found_tags)),
        "matched_notebooks": matched_notebooks,
        "confidence": 0.8 if matched_notebooks else 0.4
    }
