# Token Setup Quick Start

**Time required**: 5 minutes  
**Prerequisites**: GitHub account with access to bizcad/RoadTrip repo

---

## The Three Steps (Copy-Paste Ready)

### ✅ Step 1: Create Custom GitHub PAT

1. Open: **https://github.com/settings/tokens?type=beta**
2. Click: **Generate new token** (green button)
3. Fill in these fields:
   ```
   Token name:           RoadTrip 1-Button Push Automation
   Expiration:           90 days
   Repository access:    Only select repositories
   Select repository:    bizcad/RoadTrip
   ```
4. Scroll down → Permissions:
   ```
   ✓ Contents    →  Read and Write
   ✓ Metadata    →  Read (auto-selected)
   ```
5. Scroll down → Click: **Generate token** (green button)
6. **COPY TOKEN** (starts with `ghp_`)
   - **Save it somewhere secure** — you won't see it again!
   - It looks like: `ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456`

---

### ✅ Step 2: Store Token in Windows

1. Open PowerShell and navigate to RoadTrip:
   ```powershell
   cd G:\repos\AI\RoadTrip
   ```

2. Run the setup script (interactive):
   ```powershell
   .\scripts\setup-github-credentials.ps1 -Interactive
   ```

3. When prompted:
   ```
   Enter GitHub Personal Access Token (ghp_... or github_pat_...):
   ```
   - **Paste the token** from Step 1
   - Your input **will be hidden** (masked)
   - Press Enter

4. Success message:
   ```
   ✓ Token stored in Windows Credential Manager
   Setup complete! You can now use:
     .\invoke-git-push-with-token.ps1
   ```

---

### ✅ Step 3: Verify & Test

1. Verify token was stored:
   ```powershell
   .\scripts\setup-github-credentials.ps1 -Verify
   ```
   
   Expected output: `✓ GitHub token is stored and available`

2. Test silent push (dry run — doesn't actually push):
   ```powershell
   .\scripts\invoke-git-push-with-token.ps1 -DryRun
   ```
   
   Expected: Shows what would be committed, **no auth prompts**

3. If everything works, do a real push:
   ```powershell
   .\scripts\invoke-git-push-with-token.ps1 -Message "chore: test silent authentication"
   ```

---

## Now You Can:

✅ **Use silent authentication** in your automation:
```powershell
.\invoke-git-push-with-token.ps1 -Message "feat: your feature"
```

✅ **Your future orchestrator/skill can call it**:
```python
# From Python skill:
from src.skills.token_resolver import TokenResolver
resolver = TokenResolver("github_pat")
result = resolver.resolve()
if result.success:
    token = result.token
    # Use in API calls, git commands, etc.
```

✅ **All commits are traceable** (token never logged):
- Commits show your GitHub user
- All operations auditable
- Token stored securely by Windows
- Can revoke instantly if needed

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Permission denied" storing token | Run PowerShell as Administrator |
| "Token not found" when pushing | Run Step 2 again, paste token carefully |
| "Git push still prompts for auth" | Verify with `.\scripts\setup-github-credentials.ps1 -Verify` |
| "I lost the token from Step 1" | Generate new one; old one is lost (can't recover) |

---

## Important Reminders

🔒 **Security**:
- This token is like a password – keep it secret
- It's only scoped to `RoadTrip` repo (plus `Contents: Read/Write`)
- It expires in 90 days (you'll rotate it then)
- If it leaks, go to GitHub and revoke it instantly

📋 **Audit Trail**:
- GitHub logs all PAT usage
- All commits show your GitHub user (not the token)
- Token is never in logs, code, markdown, or git history
- This is the whole security point of the approach

🔄 **Rotation** (every 90 days):
- Create new token (Step 1)
- Store it (Step 2)
- Revoke old token on GitHub
- Takes ~2 minutes

---

**Done!** Your RoadTrip automation has secure, silent GitHub access. 🚀

For more details, see: [Token_Management_for_Silent_Auth.md](Token_Management_for_Silent_Auth.md)
