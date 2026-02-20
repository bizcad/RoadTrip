# Dev Dashboard Design Document

**Purpose**: Developer state tracking interface for RoadTrip maintainers  
**Target Users**: You (bizcad) and AI agents (Claude)  
**Design Principle**: Modular, expandable menu system that evolves with functionality  
**Last Updated**: February 19, 2026

---

## Design Philosophy

### Core Constraints
1. **Modular & Expandable**: Menu structure must accept new functionality without redesign
2. **CLI + GUI Ready**: Design works for terminal CLI and future desktop/web UI
3. **State-First**: Dashboard is for tracking project state, not executing workflows (execution comes later)
4. **Dev-Focused First**: User dashboard comes after dev needs are met

### Interaction Patterns
- **Quiz/Survey/Choice**: Support multiple selection methods (numbered menus, checkboxes, dropdowns)
- **Chat Dialog**: Natural language fallback for menu navigation
- **Keyboard Shortcuts**: Fast navigation for power users (future)
- **Progressive Disclosure**: Show summaries first, drill down on demand

---

## Menu Structure v1.0 - Developer Dashboard

```
┌─ DEV DASHBOARD ──────────────────────────────────────────┐
│                                                           │
│  1. 📊 Project State               [IMPLEMENTED]         │
│  2. 🧠 Memory System               [PARTIAL]             │
│  3. ⚙️  Skills Registry             [IMPLEMENTED]         │
│  4. 🧪 Test Results                [PARTIAL]             │
│  5. 📝 Execution History           [IMPLEMENTED]         │
│  6. 🗺️  Codebase Navigation        [IMPLEMENTED]         │
│  7. 🔧 System Health               [NOT IMPLEMENTED]     │
│  8. ⚙️  Settings & Secrets         [NOT IMPLEMENTED]     │
│                                                           │
│  Type number or command, 'help' for info, 'quit' to exit │
└───────────────────────────────────────────────────────────┘
```

---

## Menu Details

### 1. 📊 Project State [IMPLEMENTED]

**Purpose**: High-level overview of where the project is RIGHT NOW

**Data Sources**:
- `MEMORY.md` (current phase, milestone, status)
- `PHASE_*_COMPLETION_REPORT.md` files
- `config/skills-registry.yaml` metadata

**Screen Layout**:
```
┌─ PROJECT STATE ─────────────────────────────────────────┐
│ Current Phase:     Phase 3 Complete ✅                  │
│ Next Milestone:    Phase 4A - Desktop UI                │
│ Active Skills:     7 registered, 7 ready                │
│ Recent Activity:   Last commit 2 hours ago              │
│ Blockers:          None                                 │
│                                                          │
│ Quick Stats:                                             │
│   ├─ Tests Passing:        42/42 (100%)                 │
│   ├─ Code Coverage:        85%                          │
│   ├─ Registry Fingerprints: All valid                   │
│   └─ Telemetry Events:     1,247 (last 7 days)         │
└──────────────────────────────────────────────────────────┘

[D]etails  [R]efresh  [B]ack
```

**Drill-Down Options**:
- `Details`: Show full MEMORY.md content
- `Refresh`: Re-scan all data sources
- `Timeline`: Show commit history + phase progression

**Expansion Points**:
- Add WIP tracking (work-in-progress memory type)
- Add blocker detection (scan logs for errors)
- Add health score (composite metric)

---

### 2. 🧠 Memory System [PARTIAL]

**Purpose**: Visibility into the 7 memory layers

**Data Sources**:
- `data/memory/manifest.yaml` (schema definitions)
- `data/memory/stores/` (actual memory files)
- `MEMORY.md` (Layer 1: Auto Memory)

**Screen Layout**:
```
┌─ MEMORY SYSTEM ─────────────────────────────────────────┐
│                                                          │
│  Memory Layer              Status        Size    Last    │
│  ─────────────────────────────────────────────────────── │
│  1. Auto Memory         [ACTIVE]      1.3 KB   2h ago   │
│  2. Session Bootstrap   [PARTIAL]       N/A    N/A      │
│  3. Working Memory      [PARTIAL]     247 B    5m ago   │
│  4. Episodic Memory     [PLANNED]       N/A    N/A      │
│  5. Semantic Memory     [PLANNED]       N/A    N/A      │
│  6. Associative Recall  [PLANNED]       N/A    N/A      │
│  7. Chunking (RLM)      [PLANNED]       N/A    N/A      │
│                                                          │
└──────────────────────────────────────────────────────────┘

[1-7] View layer  [S]chema  [B]ack
```

**Drill-Down Options (Per Layer)**:
```
┌─ AUTO MEMORY (Layer 1) ─────────────────────────────────┐
│ File:   MEMORY.md                                        │
│ Size:   1,342 bytes                                      │
│ Lines:  382                                              │
│ Status: ✅ Always loaded in system prompt                │
│                                                          │
│ Recent Entries:                                          │
│   ├─ Phase 3 Complete (Feb 17, 2026)                    │
│   ├─ 7 skills registered                                │
│   └─ Blog publisher deployed                            │
│                                                          │
│ [V]iew full  [E]dit  [H]istory  [B]ack                  │
└──────────────────────────────────────────────────────────┘
```

**Expansion Points**:
- Implement Session Bootstrap (Layer 2) tracking
- Add memory consolidation status
- Add memory retrieval gating (cost optimization)
- Track memory size vs token budget

---

### 3. ⚙️ Skills Registry [IMPLEMENTED]

**Purpose**: Catalog of all executable skills

**Data Sources**:
- `config/skills-registry.yaml` (source of truth)
- `src/skills/*.py` (skill implementations)
- Fingerprint verification results

**Screen Layout**:
```
┌─ SKILLS REGISTRY ───────────────────────────────────────┐
│                                                          │
│  Skill Name            Status   Fingerprint   Coverage  │
│  ──────────────────────────────────────────────────────  │
│  auth_validator        ACTIVE   84aa97d2      98%       │
│  blog_publisher        ACTIVE   b0ab276c      92%       │
│  commit_message        ACTIVE   c6dee9e3      100%      │
│  git_push_autonomous   ACTIVE   a1b2c3d4      95%       │
│  telemetry_logger      ACTIVE   e5f6g7h8      89%       │
│  memory_transition     ACTIVE   i9j0k1l2      76%       │
│  registry_builder      ACTIVE   m3n4o5p6      84%       │
│                                                          │
│  Total: 7 skills registered, 7 active, 0 deprecated     │
└──────────────────────────────────────────────────────────┘

[1-7] View skill  [F]ingerprint check  [S]earch  [B]ack
```

**Drill-Down Options (Per Skill)**:
```
┌─ SKILL: blog_publisher ─────────────────────────────────┐
│ Version:      1.0.0                                      │
│ Status:       ACTIVE ✅                                   │
│ Fingerprint:  b0ab276c (verified 2h ago)                │
│ Author:       roadtrip_team                              │
│ Entry Point:  src/skills/blog_publisher.py               │
│                                                          │
│ Description:                                             │
│   Five-phase blog publishing pipeline: format,          │
│   validate, commit, push (deferred), deploy via Vercel  │
│                                                          │
│ Source Files: 3 files, 679 lines                        │
│   ├─ src/skills/blog_publisher.py                       │
│   ├─ src/skills/blog_publisher_models.py                │
│   └─ tests/test_blog_publisher.py                       │
│                                                          │
│ Test Coverage: 92% (35/38 tests passing)                │
│                                                          │
│ Dependencies:                                            │
│   └─ commit_message (for git operations)                │
│                                                          │
│ [R]un  [T]ests  [F]ingerprint  [E]dit  [B]ack           │
└──────────────────────────────────────────────────────────┘
```

**Expansion Points**:
- Add skill dependency graph visualization
- Add skill usage statistics (how often invoked)
- Add skill performance metrics (avg execution time)
- Add CRUD operations (create/update/delete skills)

---

### 4. 🧪 Test Results [PARTIAL]

**Purpose**: Current test status and history

**Data Sources**:
- `test_results.txt` (latest run)
- `logs/test_*.log` (historical runs)
- pytest JSON reports (if enabled)

**Screen Layout**:
```
┌─ TEST RESULTS ──────────────────────────────────────────┐
│ Last Run: 2 hours ago                                    │
│ Status:   ✅ PASSING (42/42 tests)                       │
│ Duration: 8.3 seconds                                    │
│ Coverage: 85%                                            │
│                                                          │
│ Test Suites:                                             │
│   ├─ test_auth_validator.py         ✅ 8/8    (100%)    │
│   ├─ test_blog_publisher.py         ✅ 12/12  (100%)    │
│   ├─ test_commit_message.py         ✅ 10/10  (100%)    │
│   ├─ test_git_push_autonomous.py    ✅ 5/5    (100%)    │
│   └─ test_telemetry_logger.py       ✅ 7/7    (100%)    │
│                                                          │
│ Recent Failures: None (last 7 days)                     │
└──────────────────────────────────────────────────────────┘

[D]etails  [R]un tests  [C]overage report  [H]istory  [B]ack
```

**Drill-Down Options**:
- `Details`: Show full pytest output
- `Run tests`: Execute test suite now (with filter options)
- `Coverage report`: HTML coverage report
- `History`: Timeline of test runs with pass/fail stats

**Expansion Points**:
- Add flaky test detection (tests that intermittently fail)
- Add test duration trends (catch performance regressions)
- Add mutation testing results (future)
- Integrate with CI/CD status

---

### 5. 📝 Execution History [IMPLEMENTED]

**Purpose**: Audit trail of all workflow executions

**Data Sources**:
- `data/telemetry.jsonl` (structured logs)
- `logs/execution.log` (human-readable logs)
- `logs/execution_metrics.jsonl` (performance data)

**Screen Layout**:
```
┌─ EXECUTION HISTORY ─────────────────────────────────────┐
│ Showing last 20 executions (filter: all)                │
│                                                          │
│  Time        Workflow            Status    Duration     │
│  ────────────────────────────────────────────────────────│
│  14:23:12    blog_publisher      SUCCESS   3.2s         │
│  14:18:45    commit_message      SUCCESS   0.8s         │
│  12:05:33    auth_validator      SUCCESS   1.1s         │
│  11:42:19    registry_builder    SUCCESS   2.5s         │
│  10:15:08    blog_publisher      FAILED    5.1s         │
│  09:30:22    telemetry_logger    SUCCESS   0.3s         │
│  ...                                                     │
│                                                          │
│ Today: 12 executions, 11 success, 1 failure (92%)       │
└──────────────────────────────────────────────────────────┘

[1-20] View details  [F]ilter  [S]earch  [E]xport  [B]ack
```

**Drill-Down Options (Per Execution)**:
```
┌─ EXECUTION DETAILS ─────────────────────────────────────┐
│ Execution ID: exec_2026-02-19_142312                    │
│ Workflow:     blog_publisher                             │
│ Status:       ✅ SUCCESS                                 │
│ Duration:     3.2 seconds                                │
│ Timestamp:    2026-02-19 14:23:12 EST                   │
│                                                          │
│ Phases:                                                  │
│   1. Format markdown       ✅ 0.8s                       │
│   2. Validate schema       ✅ 0.4s                       │
│   3. Generate commit msg   ✅ 0.6s                       │
│   4. Commit to git         ✅ 1.2s                       │
│   5. Push (deferred)       ⏸️  N/A                        │
│                                                          │
│ Telemetry Events: 7                                      │
│ Errors: None                                             │
│                                                          │
│ [L]ogs  [T]elemetry  [R]eplay  [B]ack                   │
└──────────────────────────────────────────────────────────┘
```

**Expansion Points**:
- Add execution comparison (diff between two runs)
- Add anomaly detection (executions that deviate from baseline)
- Add cost tracking (API calls, tokens used)
- Add execution chains (visualize workflow dependencies)

---

### 6. 🗺️ Codebase Navigation [IMPLEMENTED]

**Purpose**: Explore project structure and file relationships

**Data Sources**:
- `CODEBASE_INDEX_ENHANCED.json` (file classifications)
- `CODEBASE_MAP.md` (human guide)
- `scripts/navigate_codebase.py` (interactive tool)

**Screen Layout**:
```
┌─ CODEBASE NAVIGATION ───────────────────────────────────┐
│                                                          │
│  View By:                                                │
│    1. Functional Path (USER/DEVELOPER/HEALING/SAFETY)   │
│    2. File Type (ENTRY_POINT/LIBRARY/SKILL/AGENT)       │
│    3. Architectural Layer (ORCHESTRATION/AGENT/SKILL)   │
│    4. Common Tasks (push_to_github, run_tests, etc.)    │
│    5. Search Files                                       │
│    6. View Dependencies                                  │
│                                                          │
│  Quick Stats:                                            │
│    ├─ Total Files: 119 Python files                     │
│    ├─ Entry Points: 15                                  │
│    ├─ Skills: 7                                          │
│    └─ Agents: 2                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘

[1-6] Select view  [S]earch  [M]ap  [B]ack
```

**Expansion Points**:
- Add file recently modified view
- Add "related files" recommendations
- Add unused file detection
- Integrate git blame/history

---

### 7. 🔧 System Health [NOT IMPLEMENTED]

**Purpose**: Continuous monitoring of system vitals

**Data Sources** (Future):
- Git status (uncommitted changes, branch state)
- Dependency versions (outdated packages)
- Disk usage (logs, cache, memory stores)
- API quota remaining (if using external APIs)
- Error rates (from telemetry)

**Screen Layout** (Mockup):
```
┌─ SYSTEM HEALTH ─────────────────────────────────────────┐
│ Overall Status: ✅ HEALTHY                               │
│                                                          │
│  Component            Status       Details               │
│  ──────────────────────────────────────────────────────  │
│  Git Repository       ✅ CLEAN     0 uncommitted files   │
│  Dependencies         ⚠️  WARN     2 packages outdated   │
│  Disk Usage           ✅ OK        2.3 GB / 100 GB       │
│  Memory Stores        ✅ OK        1.2 MB / 10 MB        │
│  Error Rate           ✅ LOW       0.5% (last 24h)       │
│  API Quotas           ✅ OK        8,234 / 10,000        │
│                                                          │
│  Recommendations:                                        │
│    • Update pytest (5.4.0 → 7.2.0)                      │
│    • Update pyyaml (5.3.1 → 6.0.1)                      │
│                                                          │
└──────────────────────────────────────────────────────────┘

[D]etails  [F]ix issues  [R]efresh  [B]ack
```

**Expansion Points**:
- Add self-healing integration (auto-fix known issues)
- Add alerting thresholds
- Add system metric trends (disk usage over time)

---

### 8. ⚙️ Settings & Secrets [NOT IMPLEMENTED]

**Purpose**: Configuration management and secret storage

**Data Sources** (Future):
- `config/*.yaml` files
- `ProjectSecrets/` directory (git-ignored)
- Environment variables
- Windows Credential Manager (for GITHUB_TOKEN)

**Screen Layout** (Mockup):
```
┌─ SETTINGS & SECRETS ────────────────────────────────────┐
│                                                          │
│  Configuration Files:                                    │
│    ├─ authorization.yaml        [E]dit  [V]iew          │
│    ├─ commit-strategy.yaml      [E]dit  [V]iew          │
│    ├─ safety-rules.yaml         [E]dit  [V]iew          │
│    ├─ skills-registry.yaml      [E]dit  [V]iew          │
│    └─ telemetry-config.yaml     [E]dit  [V]iew          │
│                                                          │
│  Secrets:                                                │
│    ├─ GITHUB_TOKEN              ✅ Set (expires 64d)    │
│    └─ OPENAI_API_KEY            ❌ Not set              │
│                                                          │
│  Environment:                                            │
│    ├─ Python Version:  3.11.8                           │
│    ├─ PowerShell:      7.5.4                            │
│    └─ Git:             2.40.0                           │
│                                                          │
└──────────────────────────────────────────────────────────┘

[E]dit config  [S]ecrets manager  [V]alidate  [B]ack
```

**Expansion Points**:
- Add config validation (schema checking)
- Add secret rotation reminders (90-day PAT expiry)
- Add environment sanity checks
- Add backup/restore for configs

---

## Technical Implementation Notes

### Menu Framework Requirements

**Core Interface** (abstract base class):
```python
class MenuItem:
    def __init__(self, id: str, title: str, status: MenuStatus):
        self.id = id
        self.title = title
        self.status = status  # IMPLEMENTED, PARTIAL, NOT_IMPLEMENTED
    
    def render(self) -> str:
        """Return menu display text"""
        pass
    
    def handle_input(self, user_input: str) -> MenuAction:
        """Process user input, return next action"""
        pass
    
    def can_execute(self) -> bool:
        """Check if menu item is available"""
        return self.status == MenuStatus.IMPLEMENTED
```

**Menu System** (orchestrator):
```python
class MenuSystem:
    def __init__(self):
        self.current_menu = "main"
        self.menu_stack = []  # For back navigation
        self.menus = self._load_menus()
    
    def run(self):
        """Main interactive loop"""
        while True:
            self.render_current_menu()
            user_input = self.get_user_input()
            action = self.handle_input(user_input)
            if action == MenuAction.QUIT:
                break
    
    def navigate_to(self, menu_id: str):
        """Push current menu to stack, navigate to new menu"""
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu_id
    
    def go_back(self):
        """Pop menu stack, return to previous menu"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
```

### Data Provider Pattern

Each menu should have a **data provider** that abstracts data source:

```python
class ProjectStateProvider:
    def get_current_phase(self) -> str:
        """Parse MEMORY.md for current phase"""
        pass
    
    def get_test_stats(self) -> dict:
        """Parse test_results.txt"""
        pass
    
    def get_skill_count(self) -> int:
        """Query skills-registry.yaml"""
        pass
```

This allows menus to work even if data sources change.

### Extensibility Patterns

**Adding New Menu Item**:
1. Create `MenuItem` subclass (e.g., `ProspectiveMemoryMenu`)
2. Create `DataProvider` for that menu
3. Register in `MenuSystem._load_menus()`
4. Menu automatically appears in dashboard

**Adding New View Within Menu**:
1. Add method to `MenuItem` subclass (e.g., `show_by_status()`)
2. Add keyboard shortcut in `handle_input()`
3. Update `render()` to show new shortcut

**Adding New Data Source**:
1. Extend `DataProvider` with new method
2. Menus using that provider automatically get new data

---

## Quiz/Survey/Choice Support

The CLI must support multiple selection patterns:

### Pattern 1: Numbered Menu
```
Select a memory layer:
  1. Auto Memory
  2. Session Bootstrap
  3. Working Memory
  4. Episodic Memory
  5. Semantic Memory
  6. Associative Recall
  7. Chunking (RLM)

Enter number (1-7):
```

### Pattern 2: Multiple Choice (Checkboxes)
```
Select skills to run tests for (space to toggle, enter to confirm):
  [x] auth_validator
  [ ] blog_publisher
  [x] commit_message
  [ ] git_push_autonomous
  [ ] telemetry_logger
  [x] memory_transition
  [ ] registry_builder
```

### Pattern 3: Yes/No Confirmation
```
This will delete 3 archived memory entries. Continue? [y/N]:
```

### Pattern 4: Free Text Input
```
Enter search query: memory transition
```

### Pattern 5: Autocomplete (Future)
```
Search files (type to filter): mem
  → memory_store_transition.py
  → memory_loop_orchestrator.py
  → MEMORY.md
```

### Implementation Strategy

Use **prompt_toolkit** library (Python) for rich CLI interactions:
- Supports numbered menus, checkboxes, autocomplete
- Cross-platform (Windows/Linux/Mac)
- Keyboard navigation built-in
- Can be wrapped in simple API for quiz/choice patterns

Example:
```python
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog

# Numbered menu (radio buttons)
result = radiolist_dialog(
    title="Select Memory Layer",
    text="Choose a layer to view:",
    values=[
        ("auto", "1. Auto Memory"),
        ("session", "2. Session Bootstrap"),
        # ...
    ]
).run()

# Multiple choice (checkboxes)
results = checkboxlist_dialog(
    title="Select Skills",
    text="Choose skills to test:",
    values=[
        ("auth", "auth_validator", True),  # True = pre-selected
        ("blog", "blog_publisher", False),
        # ...
    ]
).run()
```

---

## Natural Language Command Support (Future)

The CLI should support NL shortcuts:

| User Input | Interpreted As |
|------------|---------------|
| `show skills` | Navigate to Skills Registry menu |
| `run tests` | Navigate to Test Results → Run tests |
| `memory status` | Navigate to Memory System menu |
| `what's the latest execution?` | Navigate to Execution History → show most recent |
| `search blog` | Navigate to Codebase Navigation → Search "blog" |

**Implementation**:
- Use simple keyword matching first (map "show skills" → menu ID)
- Later: Use AI model for intent classification (local model, no API cost)
- Provide autocomplete suggestions based on recent/frequent commands

---

## Chat Dialog Integration

The CLI should have a **chat mode** where user can type natural language:

```
┌─ DEV DASHBOARD (Chat Mode) ─────────────────────────────┐
│ Type commands or ask questions. Type 'menu' for menu.   │
│                                                          │
│ You: show me the latest test results                    │
│                                                          │
│ Dashboard: Last test run was 2 hours ago.               │
│            Status: ✅ PASSING (42/42 tests)              │
│            Duration: 8.3 seconds                         │
│                                                          │
│            Would you like to:                            │
│              1. View detailed results                    │
│              2. Run tests again                          │
│              3. See test history                         │
│                                                          │
│ You: 1                                                   │
│                                                          │
│ [Shows detailed test results...]                        │
│                                                          │
│ You: █                                                   │
└──────────────────────────────────────────────────────────┘
```

**Implementation**:
- Use LLM (local or API) to parse user intent
- Map intent to menu actions
- Provide structured responses with quick action options
- Allow switching between chat mode and menu mode

---

## Roadmap: Phased Implementation

### Phase 4A: Dev Dashboard Foundation (THIS PHASE)
- ✅ Design document (this file)
- 🔲 CLI framework (MenuSystem, MenuItem base classes)
- 🔲 Main menu with 8 items (show status badges)
- 🔲 Implement Menu 1: Project State (simplest, quick win)
- 🔲 Implement Menu 3: Skills Registry (already have data)
- 🔲 Implement Menu 6: Codebase Navigation (already have tool)
- 🔲 Basic quiz/choice support (numbered menus)

**Deliverable**: Working CLI that shows project state, skills, and navigation

### Phase 4B: Memory & Execution Views
- 🔲 Implement Menu 2: Memory System (show 7 layers)
- 🔲 Implement Menu 4: Test Results (parse test_results.txt)
- 🔲 Implement Menu 5: Execution History (query telemetry.jsonl)
- 🔲 Add drill-down views (per-skill, per-memory-layer, per-execution)
- 🔲 Add checkbox support (multi-select)

**Deliverable**: Full visibility into memory, tests, and execution logs

### Phase 4C: System Health & Settings
- 🔲 Implement Menu 7: System Health (git status, dependencies, disk)
- 🔲 Implement Menu 8: Settings & Secrets (config CRUD, secret manager)
- 🔲 Add auto-refresh (poll system state periodically)
- 🔲 Add alerting (notify when tests fail, git is dirty, etc.)

**Deliverable**: Complete dev dashboard with health monitoring

### Phase 4D: Natural Language & Chat
- 🔲 Add NL command parsing (keyword matching first)
- 🔲 Add chat dialog mode
- 🔲 Add autocomplete (recent/frequent commands)
- 🔲 Add command history (up/down arrow navigation)
- 🔲 (Optional) Integrate local LLM for intent classification

**Deliverable**: Conversational CLI interface

### Phase 5: User Dashboard (Future)
- Adapt dev dashboard design for end users
- Implement "What can I do now?" menu
- Implement Prospective Memory CRUD
- Implement Scheduler (cron jobs, calendar)
- (Use learnings from dev dashboard to iterate faster)

---

## Open Questions

1. **CLI vs Desktop App First?**
   - Decision: CLI first (faster, dev-focused, validates design)
   - Desktop app reuses menu structure + data providers

2. **How Dynamic Should Menu Structure Be?**
   - Proposal: Load menu definitions from YAML (similar to skills-registry)
   - Benefit: Add new menus without code changes
   - Trade-off: More abstraction, harder to debug

3. **Should Dashboard Execute Workflows?**
   - Phase 4A: No, view-only (state tracking)
   - Phase 4B: Yes, add "Run" buttons (execute via orchestrator)
   - Rationale: Separation of concerns (view first, actions later)

4. **Local LLM vs API for NL Commands?**
   - Proposal: Start with keyword matching (no LLM)
   - Later: Offer local model option (e.g., LLaMA 3.2 1B)
   - Trade-off: Local = slower but free, API = fast but costs tokens

5. **Dashboard Should Have Memory?**
   - Proposal: Yes, dashboard state is part of Working Memory
   - Use case: "Show me what I was looking at 10 minutes ago"
   - Implementation: Persist current menu path + filters to working memory

---

## Success Metrics

How we'll know the dev dashboard is working:

1. **Time to Answer "Where are we?"**: < 10 seconds (vs. 5+ minutes of file scanning)
2. **Zero Re-Explanation**: Agent can see project state without asking
3. **Navigation Speed**: Find any file in < 3 interactions (vs. 10+ greps)
4. **Execution Debugging**: See full execution trace in < 30 seconds
5. **Memory Visibility**: Know which memory layers are active in < 5 seconds

---

## Appendix: User Dashboard Preview (Future)

For completeness, here's what the **User Dashboard** will look like (Phase 5+):

```
┌─ USER DASHBOARD ────────────────────────────────────────┐
│                                                          │
│  1. 🎯 What Can I Do Now?      [View capabilities]      │
│  2. 💭 What Would I Like?      [Prospective Memory]     │
│  3. 📜 What Have I Done?       [History & Logs]         │
│  4. ⏰ When Should It Happen?  [Scheduler]              │
│                                                          │
│  Recent Activity:                                        │
│    • Blog published 2h ago ✅                            │
│    • 3 pending feature requests 💭                       │
│    • Next scheduled task: 6h from now ⏰                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

This keeps user focus on **outcomes** (what I want to achieve) vs. dev focus on **state** (what's implemented and working).

---

## Conclusion

This design gives RoadTrip a **modular, expandable menu system** that:
- ✅ Serves developers first (you + Claude)
- ✅ Works in CLI and GUI
- ✅ Supports quiz/survey/choice interactions
- ✅ Maps to existing functionality (quick wins)
- ✅ Has clear expansion points (future functionality)
- ✅ Provides state visibility (no more "where are we?" confusion)

**Next Step**: Implement Phase 4A (CLI framework + 3 working menus).
