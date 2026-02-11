# RoadTrip Workspace Profile Infrastructure

## Overview

This is a **modular, mode-based workspace profile system** that provides:

✅ **Auto-detection** - Works automatically when you open the RoadTrip workspace  
✅ **Mode switching** - Switch between coding, testing, and content modes  
✅ **Workspace isolation** - Safe to load in global `$PROFILE` without breaking other workspaces  
✅ **Secure secrets** - No credentials in Git, uses Windows Credential Manager  
✅ **Model switching** - Use different AI models for different tasks  
✅ **Skill discovery** - Python skills automatically registered in PYTHONPATH  

## Quick Start

### 1. Add to Your Global PowerShell Profile

Open `$PROFILE` and add:

```powershell
# RoadTrip Workspace Auto-Load
$roadTripDev = "G:\repos\AI\RoadTrip\.dev\profile.ps1"
if (Test-Path $roadTripDev) { . $roadTripDev }
```

Then reload:
```powershell
. $PROFILE
```

### 2. Store Secrets (One-Time Setup)

Store credentials in Windows Credential Manager:

```powershell
cmdkey /add:github_pat /user:github /pass:"your_personal_access_token"
cmdkey /add:openai_key /user:openai /pass:"your_api_key"
cmdkey /add:vercel_token /user:vercel /pass:"your_vercel_token"
```

List stored credentials:
```powershell
cmdkey /list
```

Delete a credential:
```powershell
cmdkey /delete:github_pat
```

### 3. Switch Modes

```powershell
# Coding mode (default)
use-mode coding

# Testing mode
use-mode testing

# Content/blog mode
use-mode content

# Show current mode
show-current-mode

# List all modes
use-mode -List
```

## Modes Explained

### 🧑‍💻 Coding Mode (Default)
- **AI Model**: Claude 3.5 Sonnet (fast, good code)
- **Focus**: Development, git workflows
- **Commands**: `gpush`, `bpublish`, `show-skills`
- **Skills**: All available

### 🧪 Testing Mode
- **AI Model**: GPT-4 (deterministic for testing)
- **Focus**: Test automation, QA, regression testing
- **Commands**: `test-unit`, `test-integration`, `test-e2e`
- **Skills**: Testing only

### 📝 Content Mode
- **AI Model**: Claude 3 Opus (better for long-form)
- **Image Model**: DALL-E 3
- **Focus**: Blog posts, documentation
- **Commands**: `draft-blog`, `list-drafts`, `bpublish`
- **Skills**: Blog publishing only

## File Structure

```
.dev/
  profile.ps1                 # Entry point (auto-loads when workspace opens)
  modes/
    coding.ps1               # Coding mode (default)
    testing.ps1              # Testing mode
    content.ps1              # Content mode

infra/
  common-profile.ps1         # Unix utilities (head, tail, wc, grep)
  load-secrets.ps1           # Secure credential loading
  git-push-profile.ps1       # Git push aliases
  blog-publishing-profile.ps1 # Blog functions
  testing-profile.ps1        # Test utilities
  skills-registry.ps1        # Python skills catalog
```

## Common Commands

### Available in All Modes

```powershell
# Unix-style utilities
head [file]                     # Show first 10 lines
tail [file]                     # Show last 10 lines
wc [file]                       # Count lines/words/chars
grep 'pattern' [file]           # Search for pattern
cat [file]                      # Display file
ls                              # List directory

# Navigation
cdp                             # Go to project root
cd-dev                          # Go to .dev folder
cd-src                          # Go to src folder
cd-scripts                      # Go to scripts folder
cd-prompts                       # Go to PromptTracking folder
```

### Coding Mode

```powershell
gpush                           # Push with auto-generated commit
gpush-dry                       # Dry run (see what would push)
gpush-log                       # Push and log to file
gs                              # Git status (quick)
gl                              # Git log (recent)
gb                              # Git branch info

bpublish / bp                   # Publish blog post
bl                              # List blog posts

show-skills                     # List available Python skills
list-skills                     # Same as above
get-skill 'skill-name'          # Details about specific skill
```

### Testing Mode

```powershell
test-unit                       # Run unit tests
test-integration                # Run integration tests
test-e2e                        # Run end-to-end tests
test-all                        # Run all tests
test-coverage                   # Generate coverage report
discover-tests                  # Find tests in project
```

### Content Mode

```powershell
draft-blog 'Title'              # Create draft post
list-drafts                     # List draft posts
bpublish / bp                   # Publish blog
show-content-help               # Show content commands
```

## Switching to Another Workspace

1. Open a different workspace (File > Open Workspace from File...)
2. The RoadTrip profile automatically **disables itself**
3. Create a `.dev/profile.ps1` in the new workspace (copy template from RoadTrip if needed)
4. Your global `$PROFILE` loads BOTH without conflicts ✅

## Secrets Management

Secrets are stored in **Windows Credential Manager** (built-in Windows feature). This is much more secure than hardcoding or committing to Git.

### Why Credential Manager?

✅ **Secure** - Uses Windows DPAPI encryption  
✅ **Built-in** - No extra software needed  
✅ **Auditable** - Can see what's stored with `cmdkey /list`  
✅ **Per-user** - Each Windows user has their own credentials  
✅ **Easy to rotate** - Delete and re-add with new value  

### Adding More Secrets

Edit `infra/load-secrets.ps1` to add new credentials:

```powershell
$env:MY_NEW_KEY = Get-StoredCredential "my_new_key"
```

Then store once:
```powershell
cmdkey /add:my_new_key /user:myapp /pass:"the_secret_value"
```

## Advanced: Adding New Modes

Create `.dev/modes/mymode.ps1`:

```powershell
# MyMode - Your description
$script:ProjectDefaultModel = "your-model"
$script:ImageModel = "image-model"

# Load profiles
. (Join-Path $PSScriptRoot "..\..\infra\your-profile.ps1")

# Define mode-specific aliases
function my-special-command { ... }

# Startup message
Write-Host "✅ MY MODE ACTIVATED" -ForegroundColor Green
```

Then use:
```powershell
use-mode mymode
```

## Troubleshooting

### Profile Not Loading

```powershell
# Check if RoadTrip workspace is detected
$devProfile = ".\.dev\profile.ps1"
Test-Path $devProfile

# Manually load
. ".\.dev\profile.ps1"
```

### Secrets Not Found

```powershell
# List all stored credentials
cmdkey /list

# Check if credential exists
cmdkey /list:github_pat

# Store new one
cmdkey /add:github_pat /user:github /pass:"your_token"
```

### Skills Not Found

```powershell
# Check PYTHONPATH
$env:PYTHONPATH

# List available skills
list-skills

# Test skill import
skill-import-test
```

## Next Steps

1. ✅ Add `.dev/profile.ps1` to your global `$PROFILE`
2. ✅ Store your secrets with `cmdkey /add:...`
3. ✅ Try switching modes: `use-mode testing`
4. ✅ Use help: `show-coding-help`, `show-testing-help`, etc.

Happy developing! 🚀
