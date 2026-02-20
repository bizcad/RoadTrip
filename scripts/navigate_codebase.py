#!/usr/bin/env python3
"""
Codebase Navigator: Interactive tool to explore RoadTrip structure

Usage:
    py scripts/navigate_codebase.py                        # Interactive mode
    py scripts/navigate_codebase.py --path user            # Show user path files
    py scripts/navigate_codebase.py --search "blog"        # Search for files
    py scripts/navigate_codebase.py --graph                # Show relationships
    py scripts/navigate_codebase.py --entry-points         # List all entry points
    py scripts/navigate_codebase.py --skills               # List all skills
    py scripts/navigate_codebase.py --task push_to_github  # Show task details
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import re


class CodebaseNavigator:
    """Navigate and explore RoadTrip codebase structure."""
    
    def __init__(self, index_path: str = "CODEBASE_INDEX_ENHANCED.json"):
        """Load codebase index (defaults to enhanced version)."""
        self.repo_root = Path(__file__).parent.parent
        self.index_path = self.repo_root / index_path
        
        # Fallback to old format if enhanced not found
        if not self.index_path.exists():
            index_path = "CODEBASE_INDEX.json"
            self.index_path = self.repo_root / index_path
        
        if not self.index_path.exists():
            print(f"❌ Index not found: {self.index_path}")
            print("   Run from repository root or ensure CODEBASE_INDEX.json exists")
            sys.exit(1)
        
        with open(self.index_path, 'r') as f:
            self.index = json.load(f)
        
        # Detect format version
        self.is_enhanced = 'taxonomies' in self.index
    
    def show_summary(self):
        """Display codebase summary."""
        metadata = self.index['metadata']
        print("=" * 70)
        print("🗺️  RoadTrip Codebase Navigator")
        print("=" * 70)
        print(f"Version:     {metadata['version']}")
        print(f"Generated:   {metadata['generated']}")
        
        if self.is_enhanced:
            print(f"\nUsing: Enhanced Index (CODEBASE_INDEX_ENHANCED.json)")
            print(f"\nFunctional Paths:")
            for path in self.index['taxonomies']['functional_paths']:
                print(f"  • {path}")
            print(f"\nArchitectural Layers:")
            for layer in self.index['taxonomies']['architectural_layers']:
                print(f"  • {layer}")
        else:
            print(f"Total Files: {metadata['total_files']}")
            print("\nFunctional Paths:")
            for key, desc in metadata['classification_schema'].items():
                print(f"  • {key.upper()}: {desc}")
        print()
    
    def show_path(self, path_name: str):
        """Show all files in a functional path."""
        if self.is_enhanced:
            # Enhanced format
            path_key = path_name.upper() + "_PATH" if not path_name.endswith("_PATH") else path_name.upper()
            classifications = self.index.get('file_classifications', {}).get('by_functional_path', {})
            
            if path_key not in classifications:
                print(f"❌ Unknown path: {path_name}")
                print(f"   Available: {', '.join(classifications.keys())}")
                return
            
            files = classifications[path_key]
            print(f"\n{'=' * 70}")
            print(f"📂 {path_key}")
            print(f"{'=' * 70}\n")
            
            for file in files:
                exists = (self.repo_root / file).exists()
                status = "✓" if exists else "✗"
                print(f"  {status} {file}")
            
            print(f"\n📊 Total files: {len(files)}")
        else:
            # Old format
            if path_name not in self.index['index']:
                print(f"❌ Unknown path: {path_name}")
                print(f"   Available: {', '.join(self.index['index'].keys())}")
                return
            
            path_data = self.index['index'][path_name]
            print(f"\n{'=' * 70}")
            print(f"📂 {path_name.upper()} PATH")
            print(f"{'=' * 70}")
            print(f"{path_data['description']}\n")
            
            total_files = 0
            for category, files in path_data.items():
                if category == 'description':
                    continue
                
                print(f"\n🔹 {category.replace('_', ' ').title()}")
                print(f"   ({len(files)} files)")
                for file in files:
                    exists = (self.repo_root / file).exists()
                    status = "✓" if exists else "✗"
                    print(f"   {status} {file}")
                    total_files += 1
            
            print(f"\n📊 Total files in {path_name} path: {total_files}")
    
    def search(self, query: str, case_sensitive: bool = False):
        """Search for files matching query."""
        pattern = re.compile(query if case_sensitive else query, 
                           flags=0 if case_sensitive else re.IGNORECASE)
        results = []
        
        # Search through all paths
        for path_name, path_data in self.index['index'].items():
            for category, files in path_data.items():
                if category == 'description' or not isinstance(files, list):
                    continue
                
                for file in files:
                    if pattern.search(file):
                        results.append({
                            'file': file,
                            'path': path_name,
                            'category': category
                        })
        
        if not results:
            print(f"❌ No files found matching: {query}")
            return
        
        print(f"\n🔍 Found {len(results)} file(s) matching '{query}':\n")
        for result in results:
            exists = (self.repo_root / result['file']).exists()
            status = "✓" if exists else "✗"
            print(f"{status} {result['file']}")
            print(f"   Path: {result['path']} > {result['category']}")
            print()
    
    def show_entry_points(self):
        """Display all entry points."""
        entry_points = self.index['entry_points']
        
        print(f"\n{'=' * 70}")
        print("🚀 Entry Points")
        print(f"{'=' * 70}\n")
        
        print("CLI Scripts (run with py):")
        for script in entry_points['cli_scripts']:
            exists = (self.repo_root / script).exists()
            status = "✓" if exists else "✗"
            print(f"  {status} py {script}")
        
        print("\nPowerShell Scripts (run with pwsh):")
        for script in entry_points['powershell_scripts']:
            exists = (self.repo_root / script).exists()
            status = "✓" if exists else "✗"
            print(f"  {status} pwsh {script}")
        
        print("\nProgrammatic APIs (import and use):")
        for api in entry_points['programmatic_apis']:
            parts = api.split('::')
            file_path = parts[0]
            api_name = parts[1] if len(parts) > 1 else "see file"
            exists = (self.repo_root / file_path).exists()
            status = "✓" if exists else "✗"
            print(f"  {status} from {file_path} import {api_name}")
    
    def show_relationships(self):
        """Display file relationships and pipelines."""
        relationships = self.index['file_relationships']
        
        print(f"\n{'=' * 70}")
        print("🔗 File Relationships & Pipelines")
        print(f"{'=' * 70}\n")
        
        for pipeline_name, pipeline_data in relationships.items():
            print(f"📊 {pipeline_name.replace('_', ' ').title()}")
            
            if 'flow' in pipeline_data:
                print("   Flow:")
                for step in pipeline_data['flow']:
                    print(f"     → {step}")
            
            if 'depends_on' in pipeline_data:
                print(f"   Dependencies: {pipeline_data['depends_on']}")
            
            if 'used_by' in pipeline_data:
                print(f"   Used by: {pipeline_data['used_by']}")
            
            print()
    
    def show_navigation_tips(self):
        """Display navigation tips."""
        tips = self.index['navigation_tips']
        
        print(f"\n{'=' * 70}")
        print("💡 Navigation Tips")
        print(f"{'=' * 70}\n")
        
        for tip_key, tip_text in tips.items():
            tip_title = tip_key.replace('_', ' ').title()
            print(f"• {tip_title}:")
            print(f"  {tip_text}\n")
    
    def show_reorganization_plan(self):
        """Display reorganization suggestions."""
        reorg = self.index['reorganization_suggestions']
        
        print(f"\n{'=' * 70}")
        print("🗂️  Reorganization Plan")
        print(f"{'=' * 70}\n")
        
        print(f"Current: {reorg['current_structure']}\n")
        
        print("Proposed Structure:")
        for folder, purpose in reorg['proposed_structure'].items():
            print(f"  • {folder:<20} {purpose}")
        
        print("\nBenefits:")
        for benefit in reorg['benefits']:
            print(f"  ✓ {benefit}")
        
        print(f"\nMigration Effort: {reorg['migration_effort']}")
    
    def show_skills(self):
        """Display all skills (enhanced format only)."""
        if not self.is_enhanced:
            print("❌ Skills listing requires enhanced index format")
            return
        
        skills = self.index.get('skills', [])
        print(f"\n{'=' * 70}")
        print(f"🎯 All Skills ({len(skills)})")
        print(f"{'=' * 70}\n")
        
        for skill in skills:
            name = skill.get('name', 'Unknown')
            file = skill.get('file', 'N/A')
            purpose = skill.get('purpose', 'N/A')
            status = skill.get('status', 'unknown')
            standalone = skill.get('standalone', False)
            
            exists = (self.repo_root / file).exists() if file != 'N/A' else False
            file_status = "✓" if exists else "✗"
            
            print(f"  {file_status} {name}")
            print(f"     File: {file}")
            print(f"     Purpose: {purpose}")
            print(f"     Status: {status} | Standalone: {standalone}")
            
            if skill.get('dependencies'):
                deps = ', '.join(skill['dependencies'])
                print(f"     Dependencies: {deps}")
            print()
    
    def show_task(self, task_name: str):
        """Display details about a common task (enhanced format only)."""
        if not self.is_enhanced:
            print("❌ Task details require enhanced index format")
            return
        
        tasks = self.index.get('common_tasks', {})
        if task_name not in tasks:
            print(f"❌ Task '{task_name}' not found")
            print(f"\nAvailable tasks:")
            for name in tasks.keys():
                print(f"  • {name}")
            return
        
        task_data = tasks[task_name]
        print(f"\n{'=' * 70}")
        print(f"✅ Task: {task_name}")
        print(f"{'=' * 70}\n")
        
        if 'methods' in task_data:
            print("Methods:")
            for method in task_data['methods']:
                cmd = method.get('command', 'N/A')
                cmd_type = method.get('type', 'N/A')
                file = method.get('file', 'N/A')
                exists = (self.repo_root / file).exists() if file != 'N/A' else False
                status = "✓" if exists else "✗"
                
                print(f"  {status} {cmd} ({cmd_type})")
                print(f"     File: {file}")
            print()
        
        if 'steps' in task_data:
            print("Steps:")
            for step in task_data['steps']:
                print(f"  {step}")
            print()
        
        if 'files' in task_data:
            print("Files involved:")
            for file in task_data['files']:
                exists = (self.repo_root / file).exists()
                status = "✓" if exists else "✗"
                print(f"  {status} {file}")
            print()
        
        if 'programmatic' in task_data:
            print("Programmatic usage:")
            print(f"  {task_data['programmatic']}")
            print()
    
    def list_tasks(self):
        """List all common tasks (enhanced format only)."""
        if not self.is_enhanced:
            print("❌ Task listing requires enhanced index format")
            return
        
        tasks = self.index.get('common_tasks', {})
        print(f"\n{'=' * 70}")
        print(f"✅ Common Tasks ({len(tasks)})")
        print(f"{'=' * 70}\n")
        
        for task_name in tasks.keys():
            print(f"  • {task_name}")
        
        print(f"\nUse --task <name> to see details")
    
    
    def interactive_mode(self):
        """Run interactive navigation session."""
        self.show_summary()
        
        while True:
            print("\nCommands:")
            print("  1. Show [user|developer|self-healing|safety|shared|testing] path")
            print("  2. Search for files")
            print("  3. Show entry points")
            print("  4. Show relationships")
            if self.is_enhanced:
                print("  5. Show all skills")
                print("  6. List common tasks")
                print("  7. Show task details")
            else:
                print("  5. Show navigation tips")
                print("  6. Show reorganization plan")
            print("  q. Quit")
            
            choice = input("\n> ").strip().lower()
            
            if choice == 'q' or choice == 'quit':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                path = input("Which path? (user/developer/self-healing/safety/shared/testing): ").strip().lower()
                self.show_path(path)
            elif choice == '2':
                query = input("Search query: ").strip()
                if query:
                    self.search(query)
            elif choice == '3':
                self.show_entry_points()
            elif choice == '4':
                self.show_relationships()
            elif choice == '5':
                if self.is_enhanced:
                    self.show_skills()
                else:
                    self.show_navigation_tips()
            elif choice == '6':
                if self.is_enhanced:
                    self.list_tasks()
                else:
                    self.show_reorganization_plan()
            elif choice == '7' and self.is_enhanced:
                task = input("Task name: ").strip()
                if task:
                    self.show_task(task)
            else:
                print("Invalid choice. Try again.")


def main():
    parser = argparse.ArgumentParser(
        description="Navigate RoadTrip codebase structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    py scripts/navigate_codebase.py                        # Interactive mode
    py scripts/navigate_codebase.py --path user            # Show user path
    py scripts/navigate_codebase.py --search "blog"        # Search files
    py scripts/navigate_codebase.py --graph                # Show relationships
    py scripts/navigate_codebase.py --entry-points         # List entry points
    py scripts/navigate_codebase.py --skills               # List all skills
    py scripts/navigate_codebase.py --task push_to_github  # Show task details
    py scripts/navigate_codebase.py --list-tasks           # List all tasks
"""
    )
    
    parser.add_argument('--path', help='Show files in specific path (user/developer/self-healing/safety)')
    parser.add_argument('--search', help='Search for files matching pattern')
    parser.add_argument('--graph', action='store_true', help='Show file relationships')
    parser.add_argument('--entry-points', action='store_true', help='List all entry points')
    parser.add_argument('--skills', action='store_true', help='List all skills (enhanced index only)')
    parser.add_argument('--task', help='Show details for a specific task (enhanced index only)')
    parser.add_argument('--list-tasks', action='store_true', help='List all common tasks (enhanced index only)')
    parser.add_argument('--tips', action='store_true', help='Show navigation tips')
    parser.add_argument('--reorg', action='store_true', help='Show reorganization plan')
    parser.add_argument('--summary', action='store_true', help='Show codebase summary')
    
    args = parser.parse_args()
    
    navigator = CodebaseNavigator()
    
    # If no arguments, run interactive mode
    if not any([args.path, args.search, args.graph, args.entry_points, 
                args.skills, args.task, args.list_tasks,
                args.tips, args.reorg, args.summary]):
        navigator.interactive_mode()
        return
    
    # Execute specific commands
    if args.summary or (args.path or args.search or args.graph or args.entry_points or args.skills):
        navigator.show_summary()
    
    if args.path:
        navigator.show_path(args.path)
    
    if args.search:
        navigator.search(args.search)
    
    if args.graph:
        navigator.show_relationships()
    
    if args.entry_points:
        navigator.show_entry_points()
    
    if args.skills:
        navigator.show_skills()
    
    if args.task:
        navigator.show_task(args.task)
    
    if args.list_tasks:
        navigator.list_tasks()
    
    if args.tips:
        navigator.show_navigation_tips()
    
    if args.reorg:
        navigator.show_reorganization_plan()


if __name__ == "__main__":
    main()
