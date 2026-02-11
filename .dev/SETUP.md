# 🚀 Quick Setup - RoadTrip Workspace Profile

## 3-Step Setup (5 minutes)

### Step 1: Add to Global PowerShell Profile

```powershell
# Open your profile
notepad $PROFILE

# Add these lines (at the end):
$roadTripDev = "G:\repos\AI\RoadTrip\.dev\profile.ps1"
if (Test-Path $roadTripDev) { . $roadTripDev }

# Reload
. $PROFILE
```

### Step 2: Store Your Secrets

```powershell
# GitHub PAT (get from github.com/settings/tokens)
cmdkey /add:github_pat /user:github /pass:"ghp_xxxxxxxxxxxxxxxxxxxx"

# OpenAI API Key (get from platform.openai.com/account/api-keys)
cmdkey /add:openai_key /user:openai /pass:"sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# Vercel Token (optional, if using blog publishing)
cmdkey /add:vercel_token /user:vercel /pass:"xxxxxxxxxxxxxxxxxxxxxxxx"
```

### Step 3: Start Using

```powershell
# Open PowerShell in RoadTrip folder
cd G:\repos\AI\RoadTrip

# You should see:
# ✅ RoadTrip workspace initialized
# 🧑‍💻 CODING MODE ACTIVATED

# Try a command
list-skills

# Switch modes
use-mode testing
use-mode content
use-mode coding
```

## Available Commands

| Mode | Command | Effect |
|------|---------|--------|
| All | `head`, `tail`, `wc`, `grep` | Unix utilities |
| All | `cdp`, `cd-src`, `cd-scripts` | Quick navigation |
| Coding | `gpush`, `gpush-dry` | Git push workflows |
| Coding | `list-skills`, `show-skills` | View Python skills |
| Testing | `test-unit`, `test-integration` | Run tests |
| Content | `draft-blog`, `list-drafts` | Manage blog posts |

## Verify Everything Works

```powershell
# Check mode
show-current-mode

# List skills
list-skills

# Test git
gs  # git status

# Try help
show-coding-help
show-testing-help
show-content-help
```

## Troubleshooting

### Profile won't load?
```powershell
# Check manually
. "G:\repos\AI\RoadTrip\.dev\profile.ps1"
```

### Secrets not working?
```powershell
# List what you have stored
cmdkey /list

# Re-add if missing
cmdkey /add:github_pat /user:github /pass:"your_token"
```

### Commands not found?
```powershell
# Reload profile
. $PROFILE

# Or manually load mode
use-mode coding
```

## Documentation

- **Full guide**: `.dev/README.md`
- **Modes explained**: See mode startup messages (`show-coding-help`, etc.)
- **Skills**: `list-skills` (in coding mode)

---

**Once set up**, you just do:
```powershell
use-mode testing  # Switch modes
gpush             # Git push with auto-commit
draft-blog "My Post"  # Create blog draft
```

🎉 **That's it!** Everything else depends on your config.
