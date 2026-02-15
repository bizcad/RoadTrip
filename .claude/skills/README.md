# Skills Directory - Claude

This directory mirrors the skills from `./skills` for **semantic discovery** by Claude during IDE-based development and chat sessions.

## Skills Available

1. **auth-validator** - 4-layer authorization validation (groups, role, tools, resources)
2. **blog-publisher** - Autonomous blog post publishing with validation
3. **commit-message** - Semantic commit message generation (Tier 1→2→3 approach)
4. **git-push-autonomous** - Autonomous git push with safety checks
5. **rules-engine** - File pattern and safety rules validation  
6. **telemetry-logger** - Structured logging for autonomous operations

## Usage

Claude can discover and reference skills in:
- Chat: "commit and push these changes" → Claude finds `git-push-autonomous` skill
- Code generation: Skills provide specifications for implementation
- Decision-making: Skills define decision trees and validation logic

## File Structure

Each skill contains:
- `{skill-name}-SKILL.md` - Main specification
- `{skill-name}-CLAUDE.md` - Decision logic & reasoning (when available)
- `{skill-name}-examples.md` - Usage examples (when available)

## Integration

Skills are meant to be called **semantically**:
- User writes: "push my changes with a commit message"
- Claude reads available skills from `.claude/skills/`
- Claude invokes `git-push-autonomous` which internally calls `commit-message`
- Result: one-liner prompts, no "python vs py" issues, no explicit PS1 script calls

## See Also

- `./skills/` - Original skill definitions (canonical source)
- `.github/skills/` - Mirror for GitHub Actions contexts

## Known Issues Resolved

✅ No more "python vs py" Windows issues — skills normalize this  
✅ No more explicit PS1 script calls — git-push-autonomous wraps them  
✅ No more token request dialogs — credentials handled by auth-validator  
✅ No more semantic prompts failing — agent discovers skills automatically
