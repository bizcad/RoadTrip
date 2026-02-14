# How to build a standalone Claude skill step by step

Based on Anthropic's documentation and resources, here's a comprehensive step-by-step guide to building a standalone Claude skill.

## Step 1: Enable Skills in Claude

First, ensure you have the prerequisites:
- A Claude Pro, Team, or Enterprise account [youtube](https://www.youtube.com/watch?v=kS1MJFZWMq4)
- Access to Claude.ai, Claude Code, or the API [skywork](https://skywork.ai/blog/ai-agent/how-to-create-claude-skill-step-by-step-guide/)

To enable skills: [youtube](https://www.youtube.com/watch?v=wO8EboopboU)
1. Click your profile icon and go to **Settings**
2. Navigate to **Capabilities** section
3. Scroll to the **Skills** section
4. Turn on the **skill-creator** skill (this helps you build new skills)

## Step 2: Create Your Skill Directory Structure

Every skill requires a folder with at least one file named `SKILL.md`: [code.claude](https://code.claude.com/docs/en/skills)

```
my-skill-name/
└── SKILL.md
```

For more complex skills, you can include: [youtube](https://www.youtube.com/watch?v=zCpTBNaaWmk)
- Scripts (Python, JavaScript, etc.)
- Asset files (templates, style guides)
- Reference documentation

## Step 3: Write the SKILL.md File

The `SKILL.md` file has two essential parts: [claudeskill](https://www.claudeskill.site/en/blog/skill-md-format-en)

### YAML Frontmatter

Start with YAML frontmatter between `---` markers: [deepwiki](https://deepwiki.com/anthropics/skills/2.2-skill.md-format-specification)

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---
```

**Required fields**: [deepwiki](https://deepwiki.com/spences10/claude-skills-cli/5.1-skill-file-structure)
- **name**: Lowercase alphanumeric + hyphens only; must match the directory name (max 64 characters)
- **description**: Describes what the skill does and when Claude should activate it (optimal: <200 characters; max: 1024)

**Optional fields**: [code.claude](https://code.claude.com/docs/en/skills)
- **disable-model-invocation**: Set to `true` if only you (not Claude) can invoke the skill
- **allowed-tools**: Specify which tools the skill can use (e.g., "Read, Grep")

### Markdown Instructions

After the frontmatter, add your skill instructions in markdown format: [claudeskill](https://www.claudeskill.site/en/blog/skill-md-format-en)

```markdown
# My Skill Name

[Instructions that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

## Step 4: Structure Your Skill Content

Use **progressive disclosure** to minimize token usage: [github](https://github.com/anthropics/skills)

- **Level 1** (YAML frontmatter): Always loaded - keep concise
- **Level 2** (SKILL.md body): Loaded when skill is relevant
- **Level 3** (Linked files): Discovered as needed

Write clear, action-oriented instructions that specify: [skywork](https://skywork.ai/blog/ai-agent/how-to-create-claude-skill-step-by-step-guide/)
- What the skill does
- When to use it
- Step-by-step workflow
- Expected outputs
- Any constraints or guidelines

## Step 5: Validate Your Skill Locally

Before uploading: [skywork](https://skywork.ai/blog/ai-agent/how-to-create-claude-skill-step-by-step-guide/)

1. Confirm `SKILL.md` is at the root of your skill folder
2. Check that frontmatter fences (`---`) are in place
3. Use spaces (not tabs) for indentation
4. Run the YAML through a validator to catch syntax errors
5. Verify your directory name matches the `name` field

## Step 6: Package Your Skill

Create a `.zip` file containing your skill folder: [codecademy](https://www.codecademy.com/article/how-to-build-claude-skills)

```
my-skill-name.zip
└── my-skill-name/
    └── SKILL.md
    └── [any additional files]
```

## Step 7: Upload to Claude

**For Claude.ai or Claude Desktop**: [youtube](https://www.youtube.com/watch?v=wO8EboopboU)

1. Go to **Settings** → **Capabilities** → **Skills**
2. Click **Upload skill**
3. Drag and drop your `.zip` file
4. After a few seconds, you'll see confirmation that the skill uploaded successfully

**For Claude Code**: [code.claude](https://code.claude.com/docs/en/skills)

Place your skill folder in the skills directory:
```bash
mkdir -p ~/.claude/skills/my-skill-name
cp SKILL.md ~/.claude/skills/my-skill-name/
```

## Step 8: Test Your Skill

### Automatic Invocation
Claude will automatically activate your skill when the conversation matches the description in your frontmatter. [support.claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

### Manual Invocation
You can trigger skills manually using slash commands: [code.claude](https://code.claude.com/docs/en/skills)
```
/my-skill-name
```

### Iteration and Refinement
Test your skill and monitor: [github](https://github.com/anthropics/skills)
- **Triggering accuracy**: Does it activate on relevant queries?
- **Efficiency**: Does it reduce tool calls and tokens?
- **Consistency**: Does it produce expected outputs?

## Step 9: Use the Skill Creator (Alternative Method)

Instead of manually creating files, you can use Claude's built-in **skill-creator** skill: [youtube](https://www.youtube.com/watch?v=kS1MJFZWMq4)

1. In a Claude conversation, ask: "Create a skill for [your use case]"
2. Claude will ask clarifying questions about:
   - What the skill should do
   - When it should activate
   - What outputs it should produce
3. Claude generates the complete `SKILL.md` file
4. Download the generated file
5. Upload it to your skills settings

## Best Practices

Based on Anthropic's guidelines: [platform.claude](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

1. **Keep descriptions clear and specific** - This determines when Claude activates the skill
2. **Use structured workflows** - Break complex tasks into clear steps
3. **Include examples** - Show Claude what good outputs look like
4. **Test iteratively** - Refine based on real usage
5. **Aim for reusability** - Design skills that work across multiple contexts
6. **Minimize token usage** - Use progressive disclosure and reference files

## Video Tutorials

Several comprehensive video guides are available:

1. **"Claude Skills Explained - Step-by-Step Tutorial for Beginners"** (November 5, 2025)
   - URL: `youtube.com/watch?v=wO8EboopboU`
   - Host: David DeWinter / Kevin Stratvert
   - Covers built-in skills, creating from scratch, and MCP integration [youtube](https://www.youtube.com/watch?v=wO8EboopboU)

2. **"How to Build Claude Skills in 10 Minutes"** (October 21, 2025)
   - URL: `youtube.com/watch?v=zCpTBNaaWmk`
   - Shows anatomy of SKILL.md, skills vs MCP comparison, real examples [youtube](https://www.youtube.com/watch?v=zCpTBNaaWmk)

3. **"The Only Claude Skills Guide You Need"** (October 23, 2025)
   - URL: `youtube.com/watch?v=421T2iWTQio`
   - Beginner to expert guide with custom skill building walkthrough [youtube](https://www.youtube.com/watch?v=421T2iWTQio)

4. **"Creating custom Skills with Claude"** (October 15, 2025)
   - URL: `youtube.com/watch?v=kS1MJFZWMq4`
   - Official Anthropic demo of the skill-creator in action [youtube](https://www.youtube.com/watch?v=kS1MJFZWMq4)

## Additional Resources

- **Platform documentation**: `platform.claude.com/cookbook/skills-notebooks-01-skills-introduction` [platform.claude](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction)
- **Claude Code documentation**: `code.claude.com/docs/en/skills` [code.claude](https://code.claude.com/docs/en/skills)
- **Official guide**: "The Complete Guide to Building Skills for Claude" (32-page PDF) [github](https://github.com/anthropics/skills)
- **Community repository**: `github.com/anthropics/skills` [github](https://github.com/anthropics/skills)

Your skill is now ready to use across Claude.ai, Claude Code, and the API, enabling consistent, automated workflows for your specific use case. [support.claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

