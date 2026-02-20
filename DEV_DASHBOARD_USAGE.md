# Dev Dashboard - Usage & Extension Guide

**Quick Start**: `py scripts/dev_dashboard.py`

## What You Get

A working CLI dashboard with:
- **3 Implemented Menus**: Project State, Skills Registry, Codebase Navigation
- **5 Placeholder Menus**: Memory System (partial), Test Results (partial), Execution History, System Health, Settings
- **Quiz/Choice Support**: Numbered menus, checkboxes, yes/no dialogs, free text input

## Running the Dashboard

```bash
# Interactive mode (main menu)
py scripts/dev_dashboard.py

# Jump directly to a specific menu
py scripts/dev_dashboard.py --menu 1   # Project State
py scripts/dev_dashboard.py --menu 3   # Skills Registry
py scripts/dev_dashboard.py --menu 6   # Codebase Navigation

# Chat mode (future feature)
py scripts/dev_dashboard.py --chat
```

## Architecture Overview

```
MenuSystem (orchestrator)
├── MenuItem subclasses (views)
│   ├── ProjectStateMenu
│   ├── SkillsRegistryMenu
│   ├── CodebaseNavMenu
│   └── PlaceholderMenu
└── DataProvider subclasses (data)
    ├── ProjectStateProvider
    ├── SkillsRegistryProvider
    └── CodebaseNavProvider
```

**Design Pattern**: Menu/View + Data Provider separation
- **Menu**: Handles rendering and user input
- **Provider**: Fetches data from files/APIs
- **Benefit**: Can swap data sources without changing UI

## Adding a New Menu

### Step 1: Create Data Provider

```python
class MyNewProvider(DataProvider):
    """Fetches data from my source"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.my_data_file = workspace_root / "data" / "my_data.json"
    
    def get_data(self) -> Dict[str, Any]:
        """Load and parse my data"""
        if not self.my_data_file.exists():
            return {"error": "File not found"}
        
        with open(self.my_data_file, "r") as f:
            data = json.load(f)
        
        # Transform data as needed
        return {
            "total_items": len(data),
            "items": data,
            "status": "OK"
        }
```

### Step 2: Create Menu Class

```python
class MyNewMenu(MenuItem):
    """My new menu implementation"""
    
    def __init__(self, workspace_root: Path):
        super().__init__(
            menu_id="my_new_menu",
            title="My New Feature",
            emoji="✨",
            status=MenuStatus.IMPLEMENTED  # or PARTIAL, NOT_IMPLEMENTED
        )
        self.provider = MyNewProvider(workspace_root)
        self.data = None
    
    def render(self) -> str:
        """Show menu item in main menu"""
        return f"  9. {self.emoji} {self.title:<25} [{self.status.value}]"
    
    def render_detail(self) -> str:
        """Show detailed view when selected"""
        self.data = self.provider.get_data()
        
        output = "\n" + "=" * 80 + "\n"
        output += f"{self.emoji} {self.title.upper()}\n"
        output += "=" * 80 + "\n\n"
        
        # Display your data
        output += f"Total Items: {self.data['total_items']}\n"
        output += f"Status: {self.data['status']}\n"
        output += "\n"
        
        # Show action options
        output += "[R]efresh  [D]etails  [B]ack\n"
        
        return output
    
    def handle_input(self, user_input: str) -> MenuResponse:
        """Handle user choices"""
        choice = user_input.strip().lower()
        
        if choice == "r" or choice == "refresh":
            return MenuResponse(MenuAction.REFRESH)
        elif choice == "d" or choice == "details":
            self._show_details()
            return MenuResponse(MenuAction.CONTINUE)
        elif choice == "b" or choice == "back":
            return MenuResponse(MenuAction.BACK)
        
        return MenuResponse(MenuAction.CONTINUE)
    
    def _show_details(self):
        """Show drill-down details"""
        print("\n" + "=" * 80)
        print("DETAILED VIEW")
        print("=" * 80)
        for item in self.data["items"]:
            print(f"  • {item}")
        print("\n[Press Enter to continue]")
        input()
```

### Step 3: Register in MenuSystem

```python
def _load_menus(self) -> Dict[str, MenuItem]:
    """Initialize all menu items"""
    return {
        "main": None,
        "project_state": ProjectStateMenu(self.workspace_root),
        # ... existing menus ...
        "my_new_menu": MyNewMenu(self.workspace_root),  # Add here
    }
```

### Step 4: Update Main Menu Rendering

```python
def render_main_menu(self):
    """Render main menu"""
    print("\nMain Menu:")
    print()
    
    menu_order = [
        "project_state",
        "memory_system",
        # ... existing ...
        "my_new_menu",  # Add to display order
    ]
    
    for menu_id in menu_order:
        menu = self.menus[menu_id]
        print(menu.render())
    
    print()
    print("Type number (1-9), 'help' for info, 'quit' to exit")  # Update range
```

### Step 5: Map Number to Menu

```python
if user_input.isdigit():
    menu_num = int(user_input)
    if 1 <= menu_num <= 9:  # Update range
        menu_map = {
            1: "project_state",
            # ... existing ...
            9: "my_new_menu",  # Add mapping
        }
        self.navigate_to(menu_map[menu_num])
```

**Done!** Your menu is now accessible from the main dashboard.

## Using Quiz/Survey/Choice Helpers

The `QuizHelper` class provides reusable selection patterns:

### Pattern 1: Radio Select (Numbered Menu)

```python
from scripts.dev_dashboard import QuizHelper

# Single selection from list
choice = QuizHelper.radio_select(
    title="Select Memory Layer",
    message="Choose a layer to view:",
    options=[
        ("auto", "1. Auto Memory"),
        ("session", "2. Session Bootstrap"),
        ("working", "3. Working Memory"),
        ("episodic", "4. Episodic Memory"),
    ]
)

if choice:
    print(f"You selected: {choice}")
```

**Output** (with prompt_toolkit):
```
Select Memory Layer
Choose a layer to view:

  1. Auto Memory
  2. Session Bootstrap
  3. Working Memory
  4. Episodic Memory

Enter number: _
```

**Fallback** (without prompt_toolkit):
Plain text menu with number input.

### Pattern 2: Checkbox Select (Multiple Choice)

```python
# Multiple selection
selected = QuizHelper.checkbox_select(
    title="Select Skills to Test",
    message="Choose skills (space to toggle, enter to confirm):",
    options=[
        ("auth", "auth_validator", True),      # Pre-selected
        ("blog", "blog_publisher", False),
        ("commit", "commit_message", True),    # Pre-selected
        ("git", "git_push_autonomous", False),
    ]
)

print(f"Running tests for: {', '.join(selected)}")
```

**Output** (with prompt_toolkit):
```
Select Skills to Test
Choose skills:

  [x] auth_validator
  [ ] blog_publisher
  [x] commit_message
  [ ] git_push_autonomous
```

**Fallback** (without prompt_toolkit):
```
Enter numbers separated by commas (e.g., 1,3,5)
Enter choices: _
```

### Pattern 3: Yes/No Confirmation

```python
# Confirmation dialog
confirmed = QuizHelper.yes_no(
    title="Delete Confirmation",
    message="This will delete 3 archived items. Continue?"
)

if confirmed:
    delete_items()
else:
    print("Cancelled")
```

### Pattern 4: Free Text Input

```python
# Get text from user
query = QuizHelper.free_text(
    prompt="Enter search query",
    default="memory"
)

search_codebase(query)
```

## Customizing Existing Menus

### Example: Add Filter to Skills Registry

```python
class SkillsRegistryMenu(MenuItem):
    # ... existing code ...
    
    def render_detail(self) -> str:
        """Show skills with filter option"""
        self.data = self.provider.get_data()
        
        # Add filter UI
        output = "\n" + "=" * 80 + "\n"
        output += f"{self.emoji} SKILLS REGISTRY\n"
        output += "=" * 80 + "\n\n"
        
        # Show filtered skills
        skills = self._filter_skills()  # New method
        
        for skill in skills:
            # ... render skill ...
        
        output += "\n[F]ilter by status  [1-N] View skill  [B]ack\n"
        return output
    
    def handle_input(self, user_input: str) -> MenuResponse:
        choice = user_input.strip().lower()
        
        # Add filter handling
        if choice == "f" or choice == "filter":
            self._apply_filter()
            return MenuResponse(MenuAction.REFRESH)
        
        # ... existing handlers ...
    
    def _apply_filter(self):
        """Let user select status filter"""
        status = QuizHelper.radio_select(
            title="Filter Skills",
            message="Show skills with status:",
            options=[
                ("all", "All Skills"),
                ("active", "Active Only"),
                ("deprecated", "Deprecated Only"),
            ]
        )
        self.filter_status = status  # Store filter state
    
    def _filter_skills(self) -> List[Dict]:
        """Apply current filter"""
        skills = self.data["skills"]
        if hasattr(self, "filter_status") and self.filter_status != "all":
            skills = [s for s in skills if s["status"] == self.filter_status]
        return skills
```

## Expanding Data Providers

### Example: Add Real-Time Data

```python
class ProjectStateProvider(DataProvider):
    def __init__(self, workspace_root: Path):
        super().__init__()
        self.workspace_root = workspace_root
        self._cache = None
        self._cache_time = None
        self._cache_ttl = 60  # seconds
    
    def get_data(self) -> Dict[str, Any]:
        """Fetch data with caching"""
        now = datetime.now()
        
        # Return cached data if fresh
        if self._cache and self._cache_time:
            age = (now - self._cache_time).total_seconds()
            if age < self._cache_ttl:
                return self._cache
        
        # Fetch fresh data
        data = self._fetch_fresh_data()
        
        # Update cache
        self._cache = data
        self._cache_time = now
        
        return data
    
    def _fetch_fresh_data(self) -> Dict[str, Any]:
        """Actually load data from files"""
        # ... existing parsing logic ...
```

## Adding Natural Language Commands (Future)

When implementing chat mode, map NL commands to menu actions:

```python
class NLRouter:
    """Routes natural language to menu actions"""
    
    COMMAND_MAP = {
        "show skills": ("skills_registry", None),
        "run tests": ("test_results", "run"),
        "memory status": ("memory_system", None),
        "latest execution": ("execution_history", "latest"),
    }
    
    def parse(self, user_input: str) -> tuple:
        """Map NL to (menu_id, action)"""
        user_input = user_input.lower().strip()
        
        # Exact match first
        if user_input in self.COMMAND_MAP:
            return self.COMMAND_MAP[user_input]
        
        # Fuzzy match (future: use LLM)
        for cmd, target in self.COMMAND_MAP.items():
            if cmd in user_input:
                return target
        
        return (None, None)
```

## Testing Your Menu

Create a test file:

```python
# tests/test_my_new_menu.py

import pytest
from pathlib import Path
from scripts.dev_dashboard import MyNewMenu, MyNewProvider

def test_my_new_provider():
    """Test data provider"""
    provider = MyNewProvider(Path.cwd())
    data = provider.get_data()
    
    assert "total_items" in data
    assert "status" in data

def test_my_new_menu_render():
    """Test menu rendering"""
    menu = MyNewMenu(Path.cwd())
    
    # Test main menu item
    item = menu.render()
    assert "My New Feature" in item
    
    # Test detail view
    detail = menu.render_detail()
    assert "Total Items" in detail
```

## Dependencies

### Required
- `pyyaml` - For parsing config files
- Python 3.8+ - For type hints and pathlib

### Optional
- `prompt_toolkit` - For rich CLI (radio buttons, checkboxes)
    - Install: `py -m pip install prompt-toolkit`
  - Fallback: Plain text input if not installed

### Installing Dependencies

```bash
# Basic (required only)
py -m pip install pyyaml

# Full (with rich CLI)
py -m pip install pyyaml prompt-toolkit
```

## Troubleshooting

### Menu Not Showing
- Check `menu_order` list in `render_main_menu()`
- Verify menu ID matches in `_load_menus()` and `menu_map`

### Data Not Loading
- Verify file paths in DataProvider
- Check file permissions
- Add error handling in `get_data()`

### Quiz/Choice Not Working
- Install `prompt-toolkit` for rich UI
- Fallback to text input is automatic

### Menu Number Out of Range
- Update valid range in multiple places:
  - `render_main_menu()` prompt message
  - `menu_map` dictionary
  - Input validation (`if 1 <= menu_num <= N`)

## Next Steps

1. **Implement Placeholder Menus**: Memory System, Test Results, Execution History
2. **Add CRUD Operations**: Settings & Secrets menu with config editing
3. **Add Execution**: "Run" buttons to trigger workflows from dashboard
4. **Add Search**: Global search across all menus
5. **Add History**: Remember recent views and commands
6. **Add Chat Mode**: NL command parsing with LLM

## Reference

- **Design Doc**: See [DEV_DASHBOARD_DESIGN.md](DEV_DASHBOARD_DESIGN.md) for full architecture
- **Navigation**: See [CODEBASE_MAP.md](CODEBASE_MAP.md) for file locations
- **Data Schemas**: See `data/memory/schema/` for memory type definitions

---

**Tip**: Start by extending an existing menu (e.g., add a filter to Skills Registry) before creating a new one from scratch. This helps you understand the patterns.
