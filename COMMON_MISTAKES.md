# Common Mistakes & System Reminders

**Purpose**: Prevent repeated mistakes and provide quick solutions for common issues.  
**Target**: Developers (you + AI agents)  
**Last Updated**: February 19, 2026

---

## ⚠️ Critical Reminders

### 🔴 #1: Use `py` not `python` on Windows

**The Mistake:**
```bash
python scripts/dev_dashboard.py
# ERROR: Python was not found; run without arguments to install from Microsoft Store...
```

**Why It Fails:**
- Windows has a Microsoft Store Python stub at `python.exe`
- This stub intercepts `python` commands
- VS Code settings path mentioned in error **does not exist**
- The error message is misleading (App execution aliases setting may not be visible)

**The Fix:**
```bash
# ✅ CORRECT (Windows Python Launcher)
py scripts/dev_dashboard.py

# ✅ CORRECT (if python.exe is in PATH and not the stub)
python scripts/dev_dashboard.py

# ✅ CORRECT (direct path)
C:\Python311\python.exe scripts/dev_dashboard.py
```

**Rule of Thumb:**
- **On Windows**: Always use `py` in documentation and commands
- **On Linux/Mac**: Use `python3` or `python`
- **Cross-platform**: Use `py` (Python Launcher works on Windows, can alias on Unix)

**Update Docs:**
When updating docs, use this pattern:
```bash
# Windows
py scripts/my_script.py

# Or cross-platform with note
python3 scripts/my_script.py  # Use 'py' on Windows
```

---

### 🟡 #2: PowerShell Aliases Only Work in RoadTrip Directory

**The Mistake:**
```bash
cd C:\SomewhereElse
gpush
# ERROR: gpush : The term 'gpush' is not recognized...
```

**Why It Fails:**
- RoadTrip aliases defined in `infra/RoadTrip_profile.ps1`
- Profile is loaded **only when terminal starts in RoadTrip directory**
- Profile is **not** loaded globally in `$PROFILE`

**The Fix:**
```bash
# ✅ CORRECT: Be in RoadTrip directory
cd G:\repos\AI\RoadTrip
gpush

# ✅ CORRECT: Use full script
cd C:\SomewhereElse
pwsh -NoProfile -File G:\repos\AI\RoadTrip\scripts\git_push.ps1
```

**If You Want Global Access:**
Add to your global PowerShell profile (`$PROFILE`):
```powershell
# Load RoadTrip aliases globally
if (Test-Path "G:\repos\AI\RoadTrip\infra\RoadTrip_profile.ps1") {
    . "G:\repos\AI\RoadTrip\infra\RoadTrip_profile.ps1"
}
```

---

### 🟡 #3: GITHUB_TOKEN Must Be Set for Silent Push

**The Mistake:**
```bash
gpush
# Git prompts for username/password in browser
```

**Why It Fails:**
- `GITHUB_TOKEN` environment variable not set
- Git falls back to interactive authentication
- Breaks automation workflows

**The Fix:**
```powershell
# Check if token is set
$env:GITHUB_TOKEN
# If empty, load it:

# Option 1: From ProjectSecrets (recommended)
$env:GITHUB_TOKEN = Get-Content "ProjectSecrets\PAT.txt" -Raw

# Option 2: From Windows Credential Manager
# (Advanced: use Get-Secret cmdlet if configured)

# Option 3: Set manually (for testing only)
$env:GITHUB_TOKEN = "github_pat_..."
```

**Permanent Fix:**
Add to `$PROFILE` or `infra/RoadTrip_profile.ps1`:
```powershell
# Auto-load GitHub token on shell start
if (Test-Path "G:\repos\AI\RoadTrip\ProjectSecrets\PAT.txt") {
    $env:GITHUB_TOKEN = Get-Content "G:\repos\AI\RoadTrip\ProjectSecrets\PAT.txt" -Raw
}
```

---

### 🟡 #4: Always Use `gpush` Not `git push` for Auto-Commit

**The Mistake:**
```bash
# Make changes...
git add -A
git commit -m "update"
git push
# Works, but misses automation features
```

**Why It's Wrong:**
- `gpush` auto-generates semantic commit messages
- `gpush` stages all changes automatically
- `gpush` uses silent authentication (no browser prompts)
- `git push` alone requires manual staging + commit message

**The Fix:**
```bash
# ❌ INCORRECT (manual 3-step process)
git add -A
git commit -m "update"
git push

# ✅ CORRECT (one command, auto-message)
gpush

# ✅ CORRECT (one command, custom message)
gpush "feat: add new dashboard menu"
```

**When to Use `git push` Directly:**
- Never in RoadTrip (use `gpush` instead)
- Only if debugging git issues

---

### 🟢 #5: Run Tests Before Pushing

**The Mistake:**
```bash
# Make code changes...
gpush
# Tests fail in CI/CD (if we had CI/CD)
```

**Why It's Wrong:**
- Breaking changes pushed to main
- Other developers (or AI agents) pull broken code

**The Fix:**
```bash
# ✅ CORRECT workflow
# 1. Make changes
# 2. Run tests
pytest tests/ -v

# 3. If tests pass, push
gpush

# 4. If tests fail, fix and repeat
```

**Future:** Add pre-push hook to auto-run tests.

---

### 🟢 #6: Update MEMORY.md After Completing Phases

**The Mistake:**
- Complete Phase 4A
- Forget to update MEMORY.md
- Next session: Agent doesn't know Phase 4A is done

**Why It's Wrong:**
- MEMORY.md is "Auto Memory" (Layer 1) - always loaded
- If not updated, agent repeats completed work

**The Fix:**
```bash
# After completing major work:
# 1. Edit MEMORY.md
code MEMORY.md

# 2. Update phase status, add completion notes
# 3. Save and push
gpush "docs: update MEMORY.md - Phase 4A complete"
```

**Automation Opportunity:** Create script to auto-update MEMORY.md from completion reports.

---

## 📋 Checklists

### Before Pushing Code

```
[ ] Tests pass (`pytest tests/ -v`)
[ ] No syntax errors (`py -m py_compile src/**/*.py`)
[ ] Updated MEMORY.md if phase complete
[ ] GITHUB_TOKEN is set
[ ] Using `gpush` not `git push`
```

### Starting a New Session

```
[ ] cd G:\repos\AI\RoadTrip
[ ] Read MEMORY.md for current status
[ ] Check GITHUB_TOKEN is loaded
[ ] Run `py scripts/dev_dashboard.py --menu 1` to see project state
```

### Creating New Python Scripts

```
[ ] Use `py` in shebang: `#!/usr/bin/env python3`
[ ] Add to CODEBASE_INDEX_ENHANCED.json
[ ] Add tests in tests/ directory
[ ] Update skills-registry.yaml if it's a skill
[ ] Document in RUNNING_THE_PROJECT.md
```

---

## 🐛 Troubleshooting

### Issue: `gpush` not recognized

**Symptoms:**
```
gpush : The term 'gpush' is not recognized...
```

**Solution:**
```powershell
# 1. Check you're in RoadTrip directory
pwd
# Should show: G:\repos\AI\RoadTrip

# 2. If not, navigate there
cd G:\repos\AI\RoadTrip

# 3. Reload profile
. infra\RoadTrip_profile.ps1

# 4. If still fails, check profile exists
Test-Path infra\RoadTrip_profile.ps1
```

---

### Issue: `python` not found (Windows)

**Symptoms:**
```
python : The term 'python' is not recognized...
# OR
Python was not found; run without arguments to install from Microsoft Store
```

**Solution:**
```bash
# ✅ Use Python Launcher
py my_script.py

# ✅ Or find your Python installation
where.exe python
py --list  # Show installed Python versions

# ✅ Use specific version
py -3.11 my_script.py
```

**Permanent Fix:**
Add Python to PATH or always use `py` launcher.

---

### Issue: Git asks for credentials (browser prompt)

**Symptoms:**
- Browser opens asking for GitHub login
- Even though GITHUB_TOKEN is in ProjectSecrets/PAT.txt

**Solution:**
```powershell
# Check token is loaded
$env:GITHUB_TOKEN
# If empty or wrong:

# Load from file
$env:GITHUB_TOKEN = (Get-Content "ProjectSecrets\PAT.txt" -Raw).Trim()

# Verify it loaded
$env:GITHUB_TOKEN.Substring(0, 10)
# Should show: github_pat

# Now try push again
gpush
```

---

### Issue: Tests fail with import errors

**Symptoms:**
```
ImportError: No module named 'yaml'
ModuleNotFoundError: No module named 'pytest'
```

**Solution:**
```bash
# Install dependencies
py -m pip install -r requirements.txt

# Or manually
py -m pip install pyyaml pytest

# Or using py launcher
py -m pip install pyyaml pytest
```

---

### Issue: Dashboard shows "Unknown" for everything

**Symptoms:**
```
py scripts/dev_dashboard.py
# Menu 1 shows all "Unknown" or "N/A"
```

**Solution:**
```bash
# Check required files exist
dir MEMORY.md
dir config\skills-registry.yaml
dir test_results.txt

# If missing, generate them:
py src/registry_builder.py --build --force
pytest tests/ > test_results.txt
```

---

## 🎓 Learning from Mistakes

### Pattern: "Python not found" (Frequency: High)

**Root Cause:** Windows Microsoft Store stub  
**Prevention:** Always use `py` in docs and examples  
**Detection:** Search for `python scripts/` or `python src/` in docs  
**Fix Applied:** Created this guide, will update all docs

---

### Pattern: "Forgot to update MEMORY.md" (Frequency: Medium)

**Root Cause:** Manual process, easy to forget  
**Prevention:** Checklist in completion reports  
**Detection:** Compare PHASE_*_COMPLETION_REPORT.md dates vs MEMORY.md last updated  
**Fix Applied:** Added checklist above, future: auto-update script

---

### Pattern: "Tests not run before push" (Frequency: Medium)

**Root Cause:** No pre-push hook  
**Prevention:** Manual discipline (checklist)  
**Detection:** CI/CD would catch (not implemented yet)  
**Fix Applied:** Added checklist, future: add git pre-push hook

---

## 🔧 Prevention Systems

### System 1: This Document (COMMON_MISTAKES.md)

**How It Helps:**
- Searchable reference (`Ctrl+F`)
- Links from other docs
- Updated as new mistakes discovered

**How to Use:**
```bash
# When encountering error:
# 1. Search this file
# 2. Find solution
# 3. If not found, add new section
```

---

### System 2: Dev Dashboard Health Checks (Future)

**Proposed Menu 7 Features:**
- ✅ Check GITHUB_TOKEN is set
- ✅ Verify `py` vs `python` availability
- ✅ Check tests pass
- ✅ Verify MEMORY.md is recent
- ✅ Alert on common misconfigurations

---

### System 3: Pre-flight Checks Script (Future)

**Proposed:** `scripts/preflight_checks.py`
```python
# Run before starting work
py scripts/preflight_checks.py

# Checks:
# - Python launcher available
# - GITHUB_TOKEN set and valid
# - RoadTrip directory is cwd
# - Git repo is clean
# - Tests pass
# - Recent MEMORY.md update
```

---

### System 4: Git Hooks (Future)

**Proposed:** `.git/hooks/pre-push`
```bash
#!/bin/sh
# Auto-run tests before push
pytest tests/ || exit 1
```

---

## 📝 Documentation Standards

### When Writing Commands in Docs

**✅ DO:**
```bash
# Windows (use py launcher)
py scripts/my_script.py

# Cross-platform note
python scripts/my_script.py  # Use 'py' on Windows

# Specific version
py -3.11 scripts/my_script.py
```

**❌ DON'T:**
```bash
# Bad: assumes python is in PATH and works
python scripts/my_script.py

# Bad: no Windows guidance
python3 scripts/my_script.py

# Bad: hardcoded path
C:\Python311\python.exe scripts/my_script.py
```

### When Writing PowerShell Commands

**✅ DO:**
```powershell
# Note directory requirement
cd G:\repos\AI\RoadTrip
gpush

# Or use full path
pwsh -File G:\repos\AI\RoadTrip\infra\RoadTrip_profile.ps1
```

**❌ DON'T:**
```powershell
# Bad: assumes aliases work anywhere
gpush

# Bad: no directory context
scripts\git_push.ps1
```

---

## 🔍 How to Find Mistakes in Docs

### Quick Audit Commands

```bash
# Find all "python scripts/" usage
grep -r "python scripts/" *.md

# Find all "python src/" usage  
grep -r "python src/" *.md

# Find git push without gpush
grep -r "git push" *.md

# Find missing GITHUB_TOKEN checks
grep -r "push" *.md | grep -v "GITHUB_TOKEN"
```

### Automated Doc Updates (Future)

```python
# scripts/fix_python_commands.py
import re
from pathlib import Path

for md in Path(".").glob("**/*.md"):
    content = md.read_text()
    # Replace "python scripts/" with "py scripts/"
    fixed = re.sub(r'\bpython scripts/', 'py scripts/', content)
    fixed = re.sub(r'\bpython src/', 'py src/', fixed)
    md.write_text(fixed)
```

---

## 📌 Quick Reference Card

```
MISTAKE                       → SOLUTION
────────────────────────────────────────────────────────
python not found              → Use 'py' instead
gpush not recognized          → cd to RoadTrip directory
git asks for password         → Set GITHUB_TOKEN env var
tests not run                 → pytest tests/ before push
forgot to update MEMORY.md    → Edit after phase complete
import errors                 → py -m pip install -r requirements.txt
dashboard shows "Unknown"     → Check files exist, rebuild registry
───────────────────────────────────────────────────────────

COMMAND                       → PURPOSE
───────────────────────────────────────────────────────────
py scripts/dev_dashboard.py   → Launch dashboard
gpush                         → Auto-commit and push
pytest tests/ -v              → Run all tests
py src/registry_builder.py    → Rebuild skills registry
py scripts/navigate_codebase.py → Navigate files
───────────────────────────────────────────────────────────
```

---

## 🎯 Success Metrics

**Goal:** Reduce repeated mistakes by 90%

**Tracking (Manual for now):**
- Weekly review: Count mentions of same issue in chat
- Monthly audit: Search docs for outdated patterns
- Continuous: Update this guide when new mistake found

**Future:** Dashboard Menu 7 tracks error patterns from telemetry.

---

## 🔄 Maintenance

**Update Frequency:** After discovering new repeated mistake  
**Owner:** Project maintainers (you + AI agents)  
**Review Schedule:** Monthly audit of common errors  

**Process:**
1. Encounter mistake
2. Check if in this guide
3. If not, add new section
4. Update related docs
5. Push with `gpush "docs: add common mistake - [description]"`

---

## 📚 Related Documentation

- [CLAUDE.md](CLAUDE.md) - Project context and aliases
- [RUNNING_THE_PROJECT.md](RUNNING_THE_PROJECT.md) - How to run everything
- [DEV_DASHBOARD_USAGE.md](DEV_DASHBOARD_USAGE.md) - Dashboard extension guide
- [infra/RoadTrip_profile.ps1](infra/RoadTrip_profile.ps1) - PowerShell aliases

---

**Remember:** Mistakes are learning opportunities. When you find one, document it here so it only happens once.
