#!/usr/bin/env python3
"""
Dev Dashboard CLI - Interactive state tracking for RoadTrip developers

Usage:
    py scripts/dev_dashboard.py               # Interactive mode
    py scripts/dev_dashboard.py --menu 1      # Jump to specific menu
    py scripts/dev_dashboard.py --chat        # Chat mode (future)

Requirements:
    py -m pip install pyyaml prompt-toolkit
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Optional: prompt_toolkit for rich CLI (checkboxes, autocomplete)
try:
    from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog, yes_no_dialog
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================


class MenuStatus(Enum):
    """Status of menu implementation"""
    IMPLEMENTED = "IMPLEMENTED"
    PARTIAL = "PARTIAL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class MenuAction(Enum):
    """Actions that can be returned from menu interactions"""
    CONTINUE = "continue"
    NAVIGATE = "navigate"
    BACK = "back"
    QUIT = "quit"
    REFRESH = "refresh"


@dataclass
class MenuResponse:
    """Response from menu interaction"""
    action: MenuAction
    target_menu: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# ============================================================================
# BASE CLASSES
# ============================================================================


class MenuItem(ABC):
    """Abstract base class for menu items"""
    
    def __init__(self, menu_id: str, title: str, emoji: str, status: MenuStatus):
        self.menu_id = menu_id
        self.title = title
        self.emoji = emoji
        self.status = status
    
    @abstractmethod
    def render(self) -> str:
        """Return menu display text"""
        pass
    
    @abstractmethod
    def render_detail(self) -> str:
        """Return detailed view when menu is selected"""
        pass
    
    @abstractmethod
    def handle_input(self, user_input: str) -> MenuResponse:
        """Process user input, return action"""
        pass
    
    def can_execute(self) -> bool:
        """Check if menu item is available"""
        return self.status == MenuStatus.IMPLEMENTED
    
    def status_badge(self) -> str:
        """Return colored status badge"""
        badges = {
            MenuStatus.IMPLEMENTED: "✅",
            MenuStatus.PARTIAL: "⚠️ ",
            MenuStatus.NOT_IMPLEMENTED: "❌"
        }
        return badges[self.status]


class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Fetch data from source"""
        pass


# ============================================================================
# QUIZ/SURVEY/CHOICE HELPERS
# ============================================================================


class QuizHelper:
    """Helper functions for quiz/survey/choice interactions"""
    
    @staticmethod
    def radio_select(title: str, message: str, options: List[tuple]) -> Optional[str]:
        """
        Present a numbered menu (radio buttons) for single selection
        
        Args:
            title: Dialog title
            message: Prompt message
            options: List of (value, label) tuples
        
        Returns:
            Selected value or None if cancelled
        """
        if PROMPT_TOOLKIT_AVAILABLE:
            result = radiolist_dialog(
                title=title,
                text=message,
                values=options
            ).run()
            return result
        else:
            # Fallback: text-based menu
            print(f"\n{title}")
            print(message)
            print()
            for i, (value, label) in enumerate(options, 1):
                print(f"  {i}. {label}")
            print()
            
            while True:
                choice = input("Enter number: ").strip()
                if choice.isdigit():
                    num = int(choice) - 1
                    if 0 <= num < len(options):
                        return options[num][0]
                print(f"Invalid choice. Enter 1-{len(options)}")
    
    @staticmethod
    def checkbox_select(title: str, message: str, options: List[tuple]) -> List[str]:
        """
        Present checkboxes for multiple selection
        
        Args:
            title: Dialog title
            message: Prompt message
            options: List of (value, label, default_checked) tuples
        
        Returns:
            List of selected values (empty if cancelled)
        """
        if PROMPT_TOOLKIT_AVAILABLE:
            result = checkboxlist_dialog(
                title=title,
                text=message,
                values=options
            ).run()
            return result if result else []
        else:
            # Fallback: text-based selection
            print(f"\n{title}")
            print(message)
            print("Enter numbers separated by commas (e.g., 1,3,5)")
            print()
            for i, (value, label, _) in enumerate(options, 1):
                print(f"  {i}. {label}")
            print()
            
            choice = input("Enter choices: ").strip()
            if not choice:
                return []
            
            selected = []
            for part in choice.split(","):
                part = part.strip()
                if part.isdigit():
                    num = int(part) - 1
                    if 0 <= num < len(options):
                        selected.append(options[num][0])
            
            return selected
    
    @staticmethod
    def yes_no(title: str, message: str) -> bool:
        """
        Present yes/no confirmation dialog
        
        Args:
            title: Dialog title
            message: Question text
        
        Returns:
            True for yes, False for no
        """
        if PROMPT_TOOLKIT_AVAILABLE:
            result = yes_no_dialog(
                title=title,
                text=message
            ).run()
            return result if result is not None else False
        else:
            # Fallback: text-based y/n
            print(f"\n{title}")
            print(message)
            choice = input("[y/N]: ").strip().lower()
            return choice in ["y", "yes"]
    
    @staticmethod
    def free_text(prompt: str, default: str = "") -> str:
        """
        Get free text input from user
        
        Args:
            prompt: Prompt message
            default: Default value
        
        Returns:
            User input string
        """
        if default:
            prompt = f"{prompt} [{default}]"
        result = input(f"{prompt}: ").strip()
        return result if result else default


# ============================================================================
# DATA PROVIDERS
# ============================================================================


class ProjectStateProvider(DataProvider):
    """Provides project state data from MEMORY.md and other sources"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.memory_path = workspace_root / "MEMORY.md"
        self.registry_path = workspace_root / "config" / "skills-registry.yaml"
        self.test_results_path = workspace_root / "test_results.txt"
    
    def get_data(self) -> Dict[str, Any]:
        """Parse project state from multiple sources"""
        data = {
            "current_phase": "Unknown",
            "next_milestone": "Unknown",
            "active_skills": 0,
            "ready_skills": 0,
            "recent_activity": "No data",
            "blockers": "Unknown",
            "tests_passing": "N/A",
            "test_coverage": "N/A",
            "registry_status": "Unknown",
            "telemetry_events": "N/A"
        }
        
        # Parse MEMORY.md for phase info
        if self.memory_path.exists():
            memory_content = self.memory_path.read_text(encoding="utf-8")
            
            # Look for phase markers
            if "Phase 3 Complete" in memory_content or "Phase 3 COMPLETE" in memory_content:
                data["current_phase"] = "Phase 3 Complete ✅"
                data["next_milestone"] = "Phase 4A - Desktop UI"
            
            # Look for recent activity (last updated timestamp)
            for line in memory_content.split("\n"):
                if "Last Updated" in line:
                    data["recent_activity"] = line.split(":", 1)[1].strip()
                    break
            
            # Check for blockers
            if "blockers" in memory_content.lower():
                if "no blockers" in memory_content.lower() or "0 blockers" in memory_content.lower():
                    data["blockers"] = "None"
        
        # Parse skills-registry.yaml
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                registry = yaml.safe_load(f)
                if registry and "metadata" in registry:
                    data["active_skills"] = registry["metadata"].get("total_skills", 0)
                    data["ready_skills"] = registry["metadata"].get("ready_skills", 0)
                    data["registry_status"] = "Valid"
        
        # Parse test results
        if self.test_results_path.exists():
            test_content = self.test_results_path.read_text(encoding="utf-8")
            # Look for pytest summary line (e.g., "42 passed in 8.3s")
            for line in test_content.split("\n"):
                if "passed" in line.lower():
                    data["tests_passing"] = line.strip()
                    break
        
        # Count telemetry events (if exists)
        telemetry_path = self.workspace_root / "data" / "telemetry.jsonl"
        if telemetry_path.exists():
            try:
                with open(telemetry_path, "r", encoding="utf-8") as f:
                    count = sum(1 for _ in f)
                data["telemetry_events"] = f"{count:,} total"
            except Exception:
                pass
        
        return data


class SkillsRegistryProvider(DataProvider):
    """Provides skills registry data"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.registry_path = workspace_root / "config" / "skills-registry.yaml"
    
    def get_data(self) -> Dict[str, Any]:
        """Parse skills registry YAML"""
        if not self.registry_path.exists():
            return {"skills": [], "total": 0}
        
        with open(self.registry_path, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f)
        
        skills_list = []
        if registry and "skills" in registry:
            for skill_name, skill_data in registry["skills"].items():
                skills_list.append({
                    "name": skill_name,
                    "version": skill_data.get("version", "N/A"),
                    "status": skill_data.get("status", "unknown"),
                    "fingerprint": skill_data.get("fingerprint", "N/A")[:8],
                    "coverage": f"{skill_data.get('test_coverage', 0):.0%}",
                    "entry_point": skill_data.get("entry_point", "N/A"),
                    "description": skill_data.get("description", "No description"),
                    "source_files": skill_data.get("source_files", []),
                    "tests": skill_data.get("tests", 0)
                })
        
        return {
            "skills": skills_list,
            "total": len(skills_list),
            "active": sum(1 for s in skills_list if s["status"] == "active")
        }


class CodebaseNavProvider(DataProvider):
    """Provides codebase navigation data"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.index_path = workspace_root / "CODEBASE_INDEX_ENHANCED.json"
    
    def get_data(self) -> Dict[str, Any]:
        """Load codebase index"""
        if not self.index_path.exists():
            return {"error": "Index not found"}
        
        with open(self.index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
        
        return {
            "total_files": len(index.get("file_classifications", {}).get("by_functional_path", {}).get("ALL_FILES", [])),
            "entry_points": len(index.get("entry_points", [])),
            "skills": len(index.get("skills", [])),
            "tasks": list(index.get("common_tasks", {}).keys()),
            "index": index
        }


# ============================================================================
# MENU IMPLEMENTATIONS
# ============================================================================


class ProjectStateMenu(MenuItem):
    """Menu 1: Project State Overview"""
    
    def __init__(self, workspace_root: Path):
        super().__init__("project_state", "Project State", "📊", MenuStatus.IMPLEMENTED)
        self.provider = ProjectStateProvider(workspace_root)
        self.data = None
    
    def render(self) -> str:
        return f"  1. {self.emoji} {self.title:<25} [{self.status.value}]"
    
    def render_detail(self) -> str:
        """Show detailed project state"""
        self.data = self.provider.get_data()
        
        output = "\n" + "=" * 60 + "\n"
        output += f"{self.emoji} PROJECT STATE\n"
        output += "=" * 60 + "\n\n"
        
        output += f"Current Phase:     {self.data['current_phase']}\n"
        output += f"Next Milestone:    {self.data['next_milestone']}\n"
        output += f"Active Skills:     {self.data['active_skills']} registered, {self.data['ready_skills']} ready\n"
        output += f"Recent Activity:   {self.data['recent_activity']}\n"
        output += f"Blockers:          {self.data['blockers']}\n"
        output += "\n"
        output += "Quick Stats:\n"
        output += f"  ├─ Tests Passing:        {self.data['tests_passing']}\n"
        output += f"  ├─ Code Coverage:        {self.data['test_coverage']}\n"
        output += f"  ├─ Registry Status:      {self.data['registry_status']}\n"
        output += f"  └─ Telemetry Events:     {self.data['telemetry_events']}\n"
        output += "\n"
        output += "[R]efresh  [B]ack to main menu\n"
        
        return output
    
    def handle_input(self, user_input: str) -> MenuResponse:
        choice = user_input.strip().lower()
        
        if choice == "r" or choice == "refresh":
            return MenuResponse(MenuAction.REFRESH)
        elif choice == "b" or choice == "back":
            return MenuResponse(MenuAction.BACK)
        else:
            return MenuResponse(MenuAction.CONTINUE)


class SkillsRegistryMenu(MenuItem):
    """Menu 3: Skills Registry"""
    
    def __init__(self, workspace_root: Path):
        super().__init__("skills_registry", "Skills Registry", "⚙️", MenuStatus.IMPLEMENTED)
        self.provider = SkillsRegistryProvider(workspace_root)
        self.data = None
    
    def render(self) -> str:
        return f"  3. {self.emoji} {self.title:<25} [{self.status.value}]"
    
    def render_detail(self) -> str:
        """Show skills registry table"""
        self.data = self.provider.get_data()
        
        output = "\n" + "=" * 80 + "\n"
        output += f"{self.emoji} SKILLS REGISTRY\n"
        output += "=" * 80 + "\n\n"
        
        if not self.data["skills"]:
            output += "No skills found in registry.\n"
        else:
            # Table header
            output += f"{'Skill Name':<25} {'Status':<10} {'Fingerprint':<12} {'Coverage':<10}\n"
            output += "─" * 80 + "\n"
            
            # Table rows
            for skill in self.data["skills"]:
                status_icon = "✅" if skill["status"] == "active" else "⚠️"
                output += f"{skill['name']:<25} {status_icon} {skill['status']:<7} {skill['fingerprint']:<12} {skill['coverage']:<10}\n"
            
            output += "\n"
            output += f"Total: {self.data['total']} skills registered, {self.data['active']} active\n"
        
        output += "\n"
        output += "[1-{}] View skill details  [B]ack to main menu\n".format(self.data['total'])
        
        return output
    
    def handle_input(self, user_input: str) -> MenuResponse:
        choice = user_input.strip().lower()
        
        if choice == "b" or choice == "back":
            return MenuResponse(MenuAction.BACK)
        elif choice.isdigit():
            skill_num = int(choice) - 1
            if 0 <= skill_num < len(self.data["skills"]):
                self._show_skill_detail(skill_num)
                return MenuResponse(MenuAction.CONTINUE)
        
        return MenuResponse(MenuAction.CONTINUE)
    
    def _show_skill_detail(self, skill_index: int):
        """Show detailed view of a specific skill"""
        skill = self.data["skills"][skill_index]
        
        print("\n" + "=" * 80)
        print(f"SKILL: {skill['name']}")
        print("=" * 80)
        print(f"Version:      {skill['version']}")
        print(f"Status:       {skill['status']} {'✅' if skill['status'] == 'active' else '⚠️'}")
        print(f"Fingerprint:  {skill['fingerprint']} (truncated)")
        print(f"Entry Point:  {skill['entry_point']}")
        print()
        print(f"Description:")
        print(f"  {skill['description']}")
        print()
        print(f"Source Files: {len(skill['source_files'])} files")
        for source_file in skill['source_files']:
            print(f"  ├─ {source_file}")
        print()
        print(f"Test Coverage: {skill['coverage']}")
        print()
        print("[Press Enter to continue]")
        input()


class CodebaseNavMenu(MenuItem):
    """Menu 6: Codebase Navigation"""
    
    def __init__(self, workspace_root: Path):
        super().__init__("codebase_nav", "Codebase Navigation", "🗺️", MenuStatus.IMPLEMENTED)
        self.provider = CodebaseNavProvider(workspace_root)
        self.workspace_root = workspace_root
        self.data = None
    
    def render(self) -> str:
        return f"  6. {self.emoji} {self.title:<25} [{self.status.value}]"
    
    def render_detail(self) -> str:
        """Show codebase navigation options"""
        self.data = self.provider.get_data()
        
        if "error" in self.data:
            return f"\nError: {self.data['error']}\n[B]ack to main menu\n"
        
        output = "\n" + "=" * 80 + "\n"
        output += f"{self.emoji} CODEBASE NAVIGATION\n"
        output += "=" * 80 + "\n\n"
        
        output += "View By:\n"
        output += "  1. Common Tasks (push_to_github, run_tests, etc.)\n"
        output += "  2. Skills (7 registered skills)\n"
        output += "  3. Entry Points (15 executables)\n"
        output += "  4. Use navigate_codebase.py (full interactive tool)\n"
        output += "\n"
        output += "Quick Stats:\n"
        output += f"  ├─ Total Files:      {self.data['total_files']} Python files\n"
        output += f"  ├─ Entry Points:     {self.data['entry_points']}\n"
        output += f"  ├─ Skills:           {self.data['skills']}\n"
        output += f"  └─ Common Tasks:     {len(self.data['tasks'])}\n"
        output += "\n"
        output += "[1-4] Select view  [B]ack to main menu\n"
        
        return output
    
    def handle_input(self, user_input: str) -> MenuResponse:
        choice = user_input.strip().lower()
        
        if choice == "b" or choice == "back":
            return MenuResponse(MenuAction.BACK)
        elif choice == "1":
            self._show_tasks()
            return MenuResponse(MenuAction.CONTINUE)
        elif choice == "2":
            self._show_skills()
            return MenuResponse(MenuAction.CONTINUE)
        elif choice == "3":
            self._show_entry_points()
            return MenuResponse(MenuAction.CONTINUE)
        elif choice == "4":
            self._launch_navigate_tool()
            return MenuResponse(MenuAction.CONTINUE)
        
        return MenuResponse(MenuAction.CONTINUE)
    
    def _show_tasks(self):
        """Show common tasks"""
        print("\n" + "=" * 80)
        print("COMMON TASKS")
        print("=" * 80)
        for i, task in enumerate(self.data["tasks"], 1):
            print(f"  {i}. {task}")
        print("\n[Press Enter to continue]")
        input()
    
    def _show_skills(self):
        """Show skills list"""
        skills = self.data["index"].get("skills", [])
        print("\n" + "=" * 80)
        print(f"SKILLS ({len(skills)} registered)")
        print("=" * 80)
        for skill in skills:
            print(f"  • {skill['name']:<30} {skill.get('purpose', 'No description')}")
        print("\n[Press Enter to continue]")
        input()
    
    def _show_entry_points(self):
        """Show entry points"""
        entry_points = self.data["index"].get("entry_points", [])
        print("\n" + "=" * 80)
        print(f"ENTRY POINTS ({len(entry_points)} executables)")
        print("=" * 80)
        for ep in entry_points:
            print(f"  • {ep['name']:<40}")
            print(f"    Command: {ep.get('usage', 'N/A')}")
            print()
        print("[Press Enter to continue]")
        input()
    
    def _launch_navigate_tool(self):
        """Launch the full navigate_codebase.py tool"""
        print("\nLaunching navigate_codebase.py...")
        print("(Run: py scripts/navigate_codebase.py)")
        print("\n[Press Enter to continue]")
        input()


class PlaceholderMenu(MenuItem):
    """Placeholder for not-yet-implemented menus"""
    
    def __init__(self, menu_id: str, number: int, title: str, emoji: str, status: MenuStatus):
        super().__init__(menu_id, title, emoji, status)
        self.number = number
    
    def render(self) -> str:
        return f"  {self.number}. {self.emoji} {self.title:<25} [{self.status.value}]"
    
    def render_detail(self) -> str:
        return f"\n{self.emoji} {self.title.upper()}\n\nThis menu is not yet implemented.\n\n[B]ack to main menu\n"
    
    def handle_input(self, user_input: str) -> MenuResponse:
        choice = user_input.strip().lower()
        if choice == "b" or choice == "back":
            return MenuResponse(MenuAction.BACK)
        return MenuResponse(MenuAction.CONTINUE)


# ============================================================================
# MENU SYSTEM
# ============================================================================


class MenuSystem:
    """Main menu orchestrator"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.current_menu = "main"
        self.menu_stack: List[str] = []
        self.menus: Dict[str, MenuItem] = self._load_menus()
    
    def _load_menus(self) -> Dict[str, MenuItem]:
        """Initialize all menu items"""
        return {
            "main": None,  # Special case, handled in render_main_menu
            "project_state": ProjectStateMenu(self.workspace_root),
            "memory_system": PlaceholderMenu("memory_system", 2, "Memory System", "🧠", MenuStatus.PARTIAL),
            "skills_registry": SkillsRegistryMenu(self.workspace_root),
            "test_results": PlaceholderMenu("test_results", 4, "Test Results", "🧪", MenuStatus.PARTIAL),
            "execution_history": PlaceholderMenu("execution_history", 5, "Execution History", "📝", MenuStatus.IMPLEMENTED),
            "codebase_nav": CodebaseNavMenu(self.workspace_root),
            "system_health": PlaceholderMenu("system_health", 7, "System Health", "🔧", MenuStatus.NOT_IMPLEMENTED),
            "settings": PlaceholderMenu("settings", 8, "Settings & Secrets", "⚙️", MenuStatus.NOT_IMPLEMENTED),
        }
    
    def render_header(self):
        """Render dashboard header"""
        print("\n" + "=" * 60)
        print("🚗 ROADTRIP DEV DASHBOARD")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Workspace: {self.workspace_root.name}")
        print("=" * 60)
    
    def render_main_menu(self):
        """Render main menu"""
        print("\nMain Menu:")
        print()
        
        # Render all menu items
        menu_order = [
            "project_state",
            "memory_system",
            "skills_registry",
            "test_results",
            "execution_history",
            "codebase_nav",
            "system_health",
            "settings"
        ]
        
        for menu_id in menu_order:
            menu = self.menus[menu_id]
            print(menu.render())
        
        print()
        print("Type number (1-8), 'help' for info, 'quit' to exit")
    
    def run(self):
        """Main interactive loop"""
        self.render_header()
        
        while True:
            if self.current_menu == "main":
                self.render_main_menu()
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nGoodbye! 👋")
                    break
                elif user_input.lower() == "help":
                    self.show_help()
                    continue
                elif user_input.isdigit():
                    menu_num = int(user_input)
                    if 1 <= menu_num <= 8:
                        menu_map = {
                            1: "project_state",
                            2: "memory_system",
                            3: "skills_registry",
                            4: "test_results",
                            5: "execution_history",
                            6: "codebase_nav",
                            7: "system_health",
                            8: "settings"
                        }
                        self.navigate_to(menu_map[menu_num])
                    else:
                        print("Invalid choice. Please enter 1-8.")
            else:
                # Render current submenu
                menu = self.menus[self.current_menu]
                print(menu.render_detail())
                
                user_input = input("> ").strip()
                response = menu.handle_input(user_input)
                
                if response.action == MenuAction.BACK:
                    self.go_back()
                elif response.action == MenuAction.QUIT:
                    print("\nGoodbye! 👋")
                    break
                elif response.action == MenuAction.REFRESH:
                    # Re-render same menu (data will be refreshed)
                    continue
                elif response.action == MenuAction.NAVIGATE and response.target_menu:
                    self.navigate_to(response.target_menu)
    
    def navigate_to(self, menu_id: str):
        """Navigate to a submenu"""
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu_id
    
    def go_back(self):
        """Return to previous menu"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
    
    def show_help(self):
        """Show help information"""
        print("\n" + "=" * 60)
        print("HELP")
        print("=" * 60)
        print()
        print("Navigation:")
        print("  • Type a number (1-8) to select a menu")
        print("  • Type 'back' or 'b' to return to previous menu")
        print("  • Type 'quit' or 'q' to exit")
        print()
        print("Menu Status:")
        print("  • ✅ IMPLEMENTED - Fully functional")
        print("  • ⚠️  PARTIAL - Partially implemented")
        print("  • ❌ NOT_IMPLEMENTED - Coming soon")
        print()
        print("[Press Enter to continue]")
        input()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RoadTrip Dev Dashboard")
    parser.add_argument("--menu", type=int, help="Jump directly to menu (1-8)")
    parser.add_argument("--chat", action="store_true", help="Start in chat mode (future)")
    args = parser.parse_args()
    
    # Find workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent
    
    if not (workspace_root / "MEMORY.md").exists():
        print(f"Error: Could not find workspace root (expected MEMORY.md in {workspace_root})")
        sys.exit(1)
    
    # Initialize menu system
    menu_system = MenuSystem(workspace_root)
    
    # Handle direct menu navigation
    if args.menu:
        if 1 <= args.menu <= 8:
            menu_map = {
                1: "project_state",
                2: "memory_system",
                3: "skills_registry",
                4: "test_results",
                5: "execution_history",
                6: "codebase_nav",
                7: "system_health",
                8: "settings"
            }
            menu_system.current_menu = menu_map[args.menu]
        else:
            print(f"Error: Menu number must be 1-8 (got {args.menu})")
            sys.exit(1)
    
    # Handle chat mode
    if args.chat:
        print("Chat mode is not yet implemented. Falling back to menu mode.")
    
    # Run interactive loop
    try:
        menu_system.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye! 👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
