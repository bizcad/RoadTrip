# RoadTrip Project - Claude's Context File

This file documents the custom commands, aliases, and project-specific setup for the RoadTrip repository so they're available in Claude's memory for future sessions.

## 🔴 Critical Reminders - READ FIRST

### ⚠️ #1: Use `py` not `python` on Windows
```bash
# ❌ WRONG - Will fail with "Python was not found"
python scripts/dev_dashboard.py

# ✅ CORRECT - Use Python Launcher
py scripts/dev_dashboard.py
```

**Why:** Windows Microsoft Store Python stub intercepts `python` commands. The error message about Settings is misleading - that path doesn't exist. Always use `py` on Windows.

### ⚠️ #2: PowerShell Aliases Only Work in RoadTrip Directory
```powershell
# ✅ CORRECT
cd G:\repos\AI\RoadTrip
gpush

# ❌ WRONG - Will fail if not in RoadTrip directory
cd C:\SomewhereElse
gpush  # ERROR: gpush not recognized
```

### ⚠️ #3: GITHUB_TOKEN Must Be Set for Silent Push
```powershell
# Check if set
$env:GITHUB_TOKEN

# If empty, load it
$env:GITHUB_TOKEN = (Get-Content "ProjectSecrets\PAT.txt" -Raw).Trim()
```

**📚 Full Guide:** See [COMMON_MISTAKES.md](COMMON_MISTAKES.md) for complete troubleshooting and prevention systems.

---

## Project Location
- **Repository**: `G:\repos\AI\RoadTrip`
- **GitHub**: https://github.com/bizcad/RoadTrip

## GitHub Authentication

**Environment Variable**: `GITHUB_TOKEN`  
**Storage**: Windows Credential Manager (encrypted per-user)  
**Token Name**: "1-Button Push Automation Skill"  
**Token Type**: Fine-grained Personal Access Token  
**Repository Scope**: All repositories (all current and future repos owned by bizcad)  
**Permissions**:
- Deployments (read + write)
- Issues (read + write)
- Pull requests (read + write)
- Secrets (read + write)
- Metadata (read-only, required)

**Expiration**: 90 days (expires May 09, 2026 - rotate quarterly)  
**Setup**: Stored in `ProjectSecrets/PAT.txt` for agent setup during CI/CD initialization

This enables silent `git push` operations without interactive authentication prompts.

---

## Custom PowerShell Aliases & Commands

### Git Push Workflow
These commands are automatically loaded from `infra/RoadTrip_profile.ps1`:

#### `gpush [message]`
**Full git push workflow in one command**
- Stages all changes (`git add -A`)
- Auto-generates descriptive commit message from staged changes
- Commits the changes
- Pushes to `origin/main`

**Usage:**
```powershell
gpush                           # Auto-generate message
gpush "Custom commit message"   # Use custom message
gpush -DryRun                   # Show message without committing
gpush -Log                      # Enable logging to logs/push.log
```

#### `gpush-dry`
**Dry-run with verbose output** - Shows the generated commit message without performing any git operations
```powershell
gpush-dry
```

#### `gpush-log`
**Push with logging enabled** - Executes `gpush` and logs to `logs/push.log`
```powershell
gpush-log
```

### Unix-Style Shell Commands
Available for piping and text processing:

- `head` - Show first 10 lines: `command | head -5`
- `tail` - Show last 10 lines: `command | tail -20`
- `wc` - Count lines: `command | wc`
- `grep` - Pattern matching: `grep 'pattern' file.txt` or `command | grep 'pattern'`

### Testing Commands
- `test-fast` - Run tests excluding E2E tests
- `test-e2e` - Run smoke tests
- `test-build` - Build with summary output

## Repository Structure
```
RoadTrip/
├── data/                      # CSV data files for road trip itinerary
├── docs/                      # Documentation and guides
├── infra/                     # Infrastructure (PowerShell profiles, config)
│   └── RoadTrip_profile.ps1  # Project-specific aliases & functions
├── PromptTracking/            # Session logs and tracking
│   ├── session-log.ps1       # Session logging script
│   ├── log-aliases.ps1       # Logging command aliases
│   └── Session Log [DATE].md # Daily session logs
├── ProjectSecrets/            # (Git-ignored) Secret configs
├── scripts/                   # Executable scripts
│   └── git_push.ps1          # Core git push automation script
├── src/                       # Source code
├── tests/                     # Test files
├── .gitignore                # Git ignore rules
└── RoadTrip.code-workspace   # VS Code workspace config
```

## Key Features

### Auto-Generated Commit Messages
The `git_push.ps1` script analyzes staged changes and generates semantic commit messages:
- Single file: `"Add: filename"`, `"Remove: filename"`, `"Update: filename"`
- Multiple files: `"chore: update N files (+added ~modified -deleted)"`
  - Includes categorized lists: Added, Modified, Renamed, Deleted, Copied

### Session Logging
- Daily session logs track command history and context
- Located in: `PromptTracking/Session Log [DATE].md`
- Automatically appends clipboard content for context preservation
- Aliases: `log-help`, `log-start`, `log-end`

### Shell Integration Ready
- PowerShell 7.5.4 installed
- Shell integration enabled (VS Code `terminal.integrated.shellIntegration.enabled`)
- Command decorations, exit codes, and status display active

## Quick Reference

### One-Command Workflow
```powershell
# Make changes to files...
# Then one command pushes everything:
gpush

# Or preview the message first:
gpush-dry
```

### Manual Control
If you need direct git control:
```powershell
git status                    # Check status
git add -A                    # Stage all
git commit -m "message"       # Commit
git push origin main          # Push
```

### Common Scenarios

**Make changes and push with auto-generated message:**
```powershell
gpush
```

**Make changes and push with custom message:**
```powershell
gpush "feat: add new feature description"
```

**Test message generation without committing:**
```powershell
gpush-dry
```

**Push and log the operation:**
```powershell
gpush-log
```

## Context & Conversation Management

### When to Start Fresh Conversations

Start a **new conversation** when:
- Beginning a new feature or significant work unit
- Changing focus domains (e.g., from infrastructure to data analysis)
- Instructions need a reset or clarification
- Previous conversation context has grown unwieldy

This keeps instructions sharp and prevents instruction decay. Instructions are strongest at the beginning of a conversation when CLAUDE.md context is loaded fresh.

**Within a conversation**: Make iterative changes and build on progress naturally. Use sessions for cohesive work on a single feature.

## Documentation Style Guide

Write responses using this style (inspired by `Transcript.md`):

### Structure & Format
- **Use clear hierarchy**: Headers (##, ###) for major sections, list bullets for options
- **Visual organization**: Strategic use of emojis for quick scanning
  - ✈️ main topics / 📌 important points / ⭐ recommendations
  - ✔️ verified / 🔹 sub-options / ❌ avoid or warnings
- **Data-driven**: Provide specific details, comparisons, and numbers when available
- **Tables for comparison**: Use markdown tables for side-by-side analysis

### Tone & Language
- **Accessible**: Conversational and direct, not overly technical
- **Professional but friendly**: Substantive content with approachable voice
- **Action-oriented**: End sections with clear next steps or options
- **Concrete examples**: Show real usage, not just abstractions

### Example Opening Response Pattern
```
[Brief answer to question]

[Visual section header with emoji]
[Structured details with bullets/tables]

📌 [Key insight or recommendation]

✔️ [What's next / How to proceed]
```

## Plan Validation Process

Before implementing any complex feature or significant work:

1. **Create a detailed plan** with requirements, architecture, and steps
2. **Validate the plan** separately (don't skip this)
   - Ask: "Verify this plan covers all requirements from the original request"
   - Identify gaps, partial implementations, and missing features
   - Score coverage and list top gaps by impact
3. **Review the validation report** for any surprises
4. **Replan if needed** based on gaps identified
5. **Proceed with implementation** only after plan is verified

This prevents silent requirement drops (research shows ~40% can be missed without this step).

## Important Notes

- The `origin` remote is configured: `https://github.com/bizcad/RoadTrip.git`
- All commands respect `.gitignore` rules
- CRLF/LF line endings are normalized by git (Windows warning is normal)
- Environment PATH is auto-refreshed in git_push.ps1 for fresh git installs
- Session logging is automatically ready when VS Code terminal starts in this directory
