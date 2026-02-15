# Skills Directory - GitHub

This directory mirrors the skills from `./skills` for **semantic discovery** by LLM agents during CI/CD and GitHub workflow automations.

## Skills Available

1. **auth-validator** - 4-layer authorization validation (groups, role, tools, resources)
2. **blog-publisher** - Autonomous blog post publishing with validation
3. **commit-message** - Semantic commit message generation (Tier 1→2→3 approach)
4. **git-push-autonomous** - Autonomous git push with safety checks
5. **rules-engine** - File pattern and safety rules validation  
6. **telemetry-logger** - Structured logging for autonomous operations

## Usage

GitHub Actions workflows can reference skills in:
- `${{ github.workspace }}/.github/skills/` when running CI/CD
- Enables semantic prompts: "use a skill to validate files before pushing"
- Improves discovery over explicit script/tool calls

## File Structure

Each skill contains:
- `{skill-name}-SKILL.md` - Main specification
- `{skill-name}-CLAUDE.md` - Decision logic & reasoning (when available)
- `{skill-name}-examples.md` - Usage examples (when available)

## Integration

Skills are meant to be called **semantically**:
- Agent reads the prompt: "commit and push these changes"
- Agent discovers available skills in `.github/skills/`
- Agent selects `git-push-autonomous` without explicit instruction
- Result: cleaner prompts, better discoverability

## See Also

- `./skills/` - Original skill definitions (canonical source)
- `.claude/skills/` - Mirror for Claude in IDE contexts
