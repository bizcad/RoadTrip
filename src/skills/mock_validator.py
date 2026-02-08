"""
Mock Validator Skill

Simulates file validation before commit.
Output: List of validated files.
"""

__version__ = "0.1.0"


def execute(input_data: dict) -> dict:
    """
    Validate files for safety.
    
    Input:
        {
            "files": ["file1.py", "file2.py"],
            ...other context
        }
    
    Output:
        {
            "validated_files": [...],
            "blocked_files": [...],
            "validation_passed": bool
        }
    """
    files = input_data.get("files", [])
    
    # Simple mock: block files with ".env" or ".key" in name
    blocked_patterns = [".env", ".key", ".secret"]
    
    validated = []
    blocked = []
    
    for f in files:
        if any(pattern in f.lower() for pattern in blocked_patterns):
            blocked.append(f)
        else:
            validated.append(f)
    
    result = {
        "validated_files": validated,
        "blocked_files": blocked,
        "validation_passed": len(blocked) == 0,
        "file_count": len(files),
        "validated_count": len(validated)
    }
    
    return result
