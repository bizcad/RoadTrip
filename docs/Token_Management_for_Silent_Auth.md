# Token Management: Silent Authentication for Agentic Workflows

**Date**: February 8, 2026  
**Status**: Phase 1b Implementation  
**Owner**: RoadTrip Framework  

---

## The Problem: Interactive Auth Blocks Automation

When you run `git push` and credentials aren't cached, git prompts for authentication:

```
> .\git_push.ps1
Staging all changes...
[GitHub browser dialog appears]
→ "Select your account"
→ "Click Authorize"
→ Back to terminal...
```

This interactive flow is incompatible with agentic automation. A skill or orchestrator can't click buttons or respond to prompts. **We need silent, token-based authentication.**

---

## The Solution: Token Resolver Skill + Credential Storage

RoadTrip solves this with a **three-layer architecture**:

### Layer 1: Token Resolver Skill (`src/skills/token_resolver.py`)

A reusable Python skill that manages credential storage and retrieval. It supports multiple backends in priority order:

1. **Environment Variables** (fastest, CI/CD-friendly)
   - `GITHUB_TOKEN=ghp_...` 
   - Used in GitHub Actions, external services
   
2. **Windows Credential Manager** (secure, per-machine)
   - Native Windows encryption
   - Only accessible by current user
   - Survives reboot, persists across sessions
   
3. **Dotenv File** (dev-only, must be `.gitignored`)
   - `~/.env` with `GITHUB_TOKEN=ghp_...`
   - Portable, but less secure

**Key principle**: Never log or expose the actual token. All operations log metadata only (token hash, source, creation date).

### Layer 2: Setup Script (`scripts/setup-github-credentials.ps1`)

One-time setup that user runs to store their GitHub PAT:

```powershell
# Option A: Provide token directly
.\setup-github-credentials.ps1 -GitHubToken "ghp_your_token_here"

# Option B: Interactive (masked prompt)
.\setup-github-credentials.ps1 -Interactive

# Option C: Verify it was stored
.\setup-github-credentials.ps1 -Verify
```

This stores the token securely in Windows Credential Manager. **User runs this once, never again.**

### Layer 3: Authenticated Push Wrapper (`scripts/invoke-git-push-with-token.ps1`)

A wrapper that:
1. Resolves token via token resolver skill
2. Makes it available to git (via `GITHUB_TOKEN` environment variable)
3. Calls the immutable `git_push.ps1`
4. Cleans up environment after push

```powershell
# Replaces: .\git_push.ps1
# Use:      .\invoke-git-push-with-token.ps1

# With explicit message
.\invoke-git-push-with-token.ps1 -Message "feat: add something"

# With dry run (preview commit message)
.\invoke-git-push-with-token.ps1 -DryRun
```

**Result**: No prompts, no buttons, silent authentication.

---

## Architecture: Why Three Components?

This design makes token management:

### ✅ **Reusable** 
The token resolver skill can be called by any tool (Python, PowerShell, orchestrator). Any future skill that needs GitHub API access can use the same token resolver.

### ✅ **Secure**
- Tokens stored encrypted by Windows Credential Manager
- Never logged to console or files
- Only accessible by current user
- Can be rotated or revoked at any time

### ✅ **Flexible**
- Works in three environments: local dev, CI/CD, cloud
- Supports multiple credential backends
- Fallback chains (missing env var? check WCM. Missing WCM? check .env)

### ✅ **Auditable**
- All token operations logged (without exposing token)
- Token metadata searchable (creation date, last accessed, hash)
- Can trace which operations used which token

### ✅ **Immutable**
- `git_push.ps1` unchanged (remains trusted prototype)
- Token handling in separate wrapper (clean separation of concerns)
- Easy to test independently

---

## Best Practice: Custom Fine-Grained PAT

**Important**: Based on security research and GitHub's recommendations, you should **create a dedicated, custom PAT specifically for this automation skill** rather than reusing an existing or long-lived token.

### Why Custom PAT?

✅ **Principle of Least Privilege** — Limited to only what's needed (RoadTrip repo, push only)  
✅ **Rotation & Revocation** — If compromised, you revoke just this token, not your main GitHub access  
✅ **Auditability** — Named clearly ("RoadTrip 1-Button Automation"), trackable in GitHub security log  
✅ **Time-Limited** — Set 90-day expiration; rotate regularly  
✅ **Blast Radius** — If the skill has a bug, damage is isolated to this token's permissions  

### Why NOT Reuse Your Personal PAT?

❌ If compromised, attacker has access to ALL your GitHub activity  
❌ Harder to audit which access came from the skill vs. your manual work  
❌ No way to revoke the skill without revoking your personal access  
❌ Violates principle of least privilege  

---

## Quick Start: Create Custom PAT + Store It

### Step 1: Create Custom Fine-Grained PAT on GitHub

1. Go to: **https://github.com/settings/tokens?type=beta** (fine-grained tokens page)
   
2. Click **"Generate new token"** button
   
3. Fill in:
   - **Token name**: `RoadTrip 1-Button Push Automation`
   - **Description** (optional): `Automated commits from RoadTrip skill. Limited to this repo only.`
   - **Expiration**: `90 days` (recommended for regular rotation)
   - **Repository access**: `Only select repositories` → select `bizcad/RoadTrip`
   - **Permissions** (scroll down):
     - ✅ `Contents` → Select `Read and Write` (needed for git push)
     - ✅ `Metadata` → Read (default, always included)
     - ⚠️ **Don't add** Pull requests, Issues, or Actions unless you plan to use them
   
4. Scroll down → Click **"Generate token"**
   
5. **COPY THE TOKEN IMMEDIATELY** (you won't see it again)
   - Looks like: `ghp_ab1cd2ef3gh4ijk5lmn6opqr7stuvwxyz...`

### Step 2: Store Token in Windows Credential Manager

Now store that custom token securely so your automation skill can access it:

```powershell
# Navigate to RoadTrip repo
cd G:\repos\AI\RoadTrip

# Store the token (paste your custom PAT when prompted)
.\scripts\setup-github-credentials.ps1 -Interactive

# You'll see:
# [00:00:00] [INFO] You will be prompted for your GitHub PAT
# [00:00:00] [INFO] Your input will be masked and not logged
# Enter GitHub Personal Access Token (ghp_... or github_pat_...):
# [paste your custom PAT here - input will be masked]
```

Output on success:
```
=== Storing GitHub Token ===
ℹ Storing in Windows Credential Manager...
✓ Token stored in Windows Credential Manager

Setup complete! You can now use:
  .\invoke-git-push-with-token.ps1
```

### Step 3: Verify Token is Stored

```powershell
.\scripts\setup-github-credentials.ps1 -Verify
```

Output:
```
=== Verifying GitHub Token Storage ===
✓ GitHub token is stored and available
ℹ Location: Windows Credential Manager
ℹ Entry name: github_pat
Credential details (token contents hidden):
[Windows Credential Manager entry for github_pat]
ℹ To validate token freshness, you can test with: 
   python src/skills/token_resolver.py --token-name github_pat --validate
```

### Step 4: Use Silent Authentication

```powershell
# All staged changes → commit → push (no auth prompts)
.\scripts\invoke-git-push-with-token.ps1

# Or with explicit message
.\scripts\invoke-git-push-with-token.ps1 -Message "feat: implement something"

# Or dry run (preview without pushing)
.\scripts\invoke-git-push-with-token.ps1 -DryRun
```

**That's it.** Your automation skill now has silent access to the repo. No more clicking GitHub buttons.

---

## For Skill Developers: Using Token Resolver

If you're building a skill that needs a GitHub token (API calls, GraphQL queries, etc.):

```python
from src.skills.token_resolver import TokenResolver, ResolvedToken

# Create resolver
resolver = TokenResolver(token_name="github_pat", verbose=True)

# Resolve token silently
result = resolver.resolve()

if result.success:
    token = result.token  # The actual token
    print(f"Using token from {result.source}")  # Will be "env", "wcm", or "env_file"
    
    # Use token in your API call
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
else:
    print(f"Error: {result.message}")
    # Handle missing/invalid token
```

Or from command line:

```bash
# Get token (outputs just the token)
GITHUB_TOKEN=$(python src/skills/token_resolver.py --token-name github_pat --resolve)

# Use in curl
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Validate token format
python src/skills/token_resolver.py --token-name github_pat --validate

# List where token is stored (without exposing it)
python src/skills/token_resolver.py --token-name github_pat --list-sources
```

---

## Security Considerations

### ✅ What We Do Right

1. **Token never logged** — Only metadata (hash, creation date) is stored
2. **Secure storage** — Windows Credential Manager uses OS-level encryption
3. **Per-user access** — Token only accessible by the user who stored it
4. **Isolated retrieval** — Token retrieved at runtime, not cached between runs
5. **Clean environment** — Token cleared from environment immediately after use
6. **Multiple backends** — Don't put all eggs in one basket (env var OR WCM OR .env)

### ⚠️ What You Should Do

1. **Use strong tokens** — GitHub PATs are like passwords; treat them that way
2. **Scope tokens** — Fine-grained tokens with minimal required permissions
3. **Rotate regularly** — GitHub recommends 90-day rotation
4. **Don't commit tokens** — .env files MUST be in `.gitignore`
5. **Revoke if leaked** — If token appears in git history, revoke immediately
6. **Monitor usage** — Check GitHub token logs for unexpected activity

### ⚠️ Cross-Platform Considerations

**Current status**: Windows-only (uses Windows Credential Manager)

**For macOS/Linux users**:
- Environment variables work (`GITHUB_TOKEN=ghp_...`)
- `.env` files work (must be `.gitignored`)
- Equivalent: macOS Keychain, Linux credential stores (future implementation)

This is **acceptable for Phase 1b MVP** because:
- RoadTrip targets Windows developers initially
- PAT + environment variable works everywhere
- WCM is an optimization, not a blocker
- Phase 2 can add macOS/Linux-native stores

---

## Files Created / Modified

### New Files

| File | Purpose |
|------|---------|
| `src/skills/token_resolver.py` | Core token resolution skill (Python) |
| `scripts/setup-github-credentials.ps1` | One-time user setup to store PAT |
| `scripts/invoke-git-push-with-token.ps1` | Authenticated wrapper for git_push |

### Unchanged

| File | Status |
|------|--------|
| `scripts/git_push.ps1` | ✅ **Immutable** — No changes |

---

## Testing: Silent Push

To verify the setup works:

```powershell
# 1. Create a test file
"test content" | Add-Content tests/manual-token-test.txt

# 2. Stage it
git add tests/manual-token-test.txt

# 3. Push with token (no prompts should appear)
.\scripts\invoke-git-push-with-token.ps1 -Message "test: verify silent authentication"

# 4. Verify on GitHub
# → Go to repo, check latest commit
# → Should see "test: verify silent authentication" with your GitHub user
```

Expected behavior:
- No auth dialog appears
- Commit succeeds silently
- Commit appears on GitHub

---

## Token Lifecycle: Rotation & Maintenance

### Rotation Schedule (Best Practice)

| Action | Frequency | Details |
|--------|-----------|---------|
| **Check token age** | Weekly | Verify 90-day expiration date |
| **Rotate token** | Every 90 days | GitHub recommends this cadence |
| **Review audit log** | Monthly | Check GitHub token usage for anomalies |
| **Revoke if leak suspected** | Immediately | Replace token immediately if exposed |

### How to Rotate Your PAT

**When a token approaches 90-day expiration:**

1. **Create new token** (follow Step 1 above)
2. **Store new token** in Windows Credential Manager
   ```powershell
   .\scripts\setup-github-credentials.ps1 -Interactive
   # Paste new token when prompted
   ```
3. **Verify new token works**
   ```powershell
   .\scripts\setup-github-credentials.ps1 -Verify
   .\scripts\invoke-git-push-with-token.ps1 -DryRun
   ```
4. **Revoke old token on GitHub**
   - Go to: https://github.com/settings/tokens
   - Find `RoadTrip 1-Button Push Automation` (old one)
   - Click **Delete** button

**Automated reminder** (Phase 2):
- We'll build a skill that checks token age weekly
- Alerts you when rotation approaching (60-day mark)
- Can be integrated with your CI/CD pipeline

### If Token is Compromised

**Immediate steps**:
1. Go to: https://github.com/settings/tokens
2. Click **Delete** next to `RoadTrip 1-Button Push Automation`
3. Create new PAT (Step 1 above)
4. Store new PAT (Step 2 above)
5. Review GitHub security log for suspicious activity

**Happens instantly** — attacker can no longer access your repo.

---

## Phase 2: Maintenance & Rotation Skill

The current implementation stores credentials indefinitely. **Phase 2 should add**:

1. **Token rotation skill** — Cron-like skill that:
   - Checks token age
   - Alerts when rotation needed
   - Can be triggered automatically on schedule

2. **Token validation** — Periodic checks to ensure token:
   - Still valid (not revoked)
   - Not compromised
   - Hasn't exceeded rate limits

3. **Multi-token support**:
   - GitHub PAT, OpenAI key, Azure credentials all in one resolver
   - Policy-based access (only certain skills can access certain tokens)

4. **Cross-platform**:
   - macOS Keychain integration
   - Linux credential store support
   - Azure Key Vault for cloud deployments

---

## Design Decisions

### Why Windows Credential Manager?

**Chosen**: Windows Credential Manager (`cmdkey`)

**Alternatives considered**:

| Option | Pros | Cons |
|--------|------|------|
| **Environment variables** | Fast, CI/CD-friendly, portable | Less secure locally |
| **WCM** | Secure, encrypted, per-user | Windows-only |
| **Azure Key Vault** | Cloud-native, RBAC, rotating | Requires Azure subscription |
| **Env file (.env)** | Simple, portable | Manual management, easy to leak |
| **SSH keys** | Proven pattern | Credential format mismatch |

**Decision**: WCM for local, env vars for CI/CD → best of both worlds

### Why Three Files?

| Component | Purpose | Immutability |
|-----------|---------|--------------|
| `token_resolver.py` | Core logic, reusable | Can be enhanced |
| `setup-github-credentials.ps1` | User setup, one-time | User responsibility |
| `invoke-git-push-with-token.ps1` | Integration wrapper | Can be enhanced |
| `git_push.ps1` | Reference implementation | ✅ **IMMUTABLE** |

This separation ensures git_push.ps1 remains a trustworthy prototype while allowing credential handling to evolve independently.

---

## Troubleshooting

### "cmdkey: Permission denied"

**Issue**: Cannot store token in Windows Credential Manager
**Solution**: Run PowerShell as Administrator
```powershell
# Right-click PowerShell → "Run as administrator"
# Then run setup script
```

### "Token not found" at runtime

**Issue**: Token was stored but resolver can't find it
**Solution**: Verify it's stored
```powershell
.\scripts\setup-github-credentials.ps1 -Verify
```

If not found, restore it:
```powershell
.\scripts\setup-github-credentials.ps1 -GitHubToken "ghp_..."
```

### "GitHub API returned 401 Unauthorized"

**Issue**: Token is stored but GitHub rejects it
**Possible causes**:
- Token was revoked
- Token has incorrect permissions
- Token expired (90-day rotation)

**Solution**:
1. Check token on GitHub: https://github.com/settings/tokens
2. If missing/revoked, regenerate: https://github.com/settings/tokens/new
3. Update stored token: `.\setup-github-credentials.ps1 -Interactive`

### "Python interpreter not found"

**Issue**: `invoke-git-push-with-token.ps1` can't find Python
**Solution**: Ensure Python is on PATH
```powershell
python --version
if ($?) { "Python found" } else { "Install Python" }
```

---

## Next Steps

### For Users
1. Run `.\scripts\setup-github-credentials.ps1 -Interactive`
2. Replace `.\git_push.ps1` with `.\invoke-git-push-with-token.ps1` in your workflows
3. Enjoy silent authentication ✅

### For Developers
1. Call token resolver from any skill that needs GitHub access
2. Phase 2: Add token rotation, multi-credential support
3. Phase 3: Cross-platform (macOS/Linux native stores)

### For the Initiative
This pattern demonstrates **Verified Agentic Work (VAW)**:
- ✅ Token never exposed (audit trail clean)
- ✅ Storage is verifiable (WCM, env var, .env)
- ✅ Usage is traceable (metadata logged)
- ✅ System is trustworthy (can't access token outside intended flow)

---

## References

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [Windows Credential Manager](https://support.microsoft.com/en-us/windows/save-your-passwords-in-windows-11-f5a57e97-76ca-428e-a11d-fa43feec81b6)
- [Git Credentials Helper](https://git-scm.com/docs/gitcredentials)
- [RoadTrip Principles & Processes](../docs/Principles-and-Processes.md)

---

**Built as part of Phase 1b, Option C: Token Management for Agentic Workflows**
