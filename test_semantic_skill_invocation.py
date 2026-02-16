#!/usr/bin/env python3
"""
Test Step 4: Semantic Skill Invocation
Publishes README.md as a blog post using blog-publisher skill
"""

from src.skills.blog_publisher import BlogPublisherSkill, BlogPost, load_config

# Read README.md
with open('README.md', 'r', encoding='utf-8') as f:
    full_content = f.read()

# Extract title and excerpt from README
title = 'RoadTrip: An Intelligent, Trusted Travel Partner'
excerpt = 'How do you trust an AI agent that needs access to the internet? RoadTrip is a proof-of-concept framework for building verifiable, auditable AI skills.'

# Use full README as content
content = full_content

# Load configuration from skill directory
config = load_config(".claude/skills/blog-publisher/config.yaml")

# Create blog post object
post = BlogPost(
    title=title,
    excerpt=excerpt,
    content=content,
    author_name='Nicholas Stein'
)

# Initialize skill and publish
skill = BlogPublisherSkill(config)
blog_result = skill.publish(post)

# Convert to dict for consistent output
result = {
    "decision": blog_result.decision,
    "success": blog_result.success,
    "filename": blog_result.filename,
    "url": blog_result.url,
    "commit_hash": blog_result.commit_hash,
    "git_push_confirmed": blog_result.git_push_confirmed,
    "confidence": blog_result.confidence,
    "errors": blog_result.errors,
    "warnings": blog_result.warnings,
    "metadata": blog_result.metadata
}

# Display result
print('\n' + '='*70)
print('SKILL INVOCATION: blog-publisher')
print('='*70)
print(f'Decision:      {result["decision"]}')
print(f'Success:       {result["success"]}')
print(f'Confidence:    {result["confidence"]:.2f}')
print(f'Filename:      {result["filename"]}')
print(f'URL:           {result["url"]}')
print(f'Commit:        {result["commit_hash"]}')
print(f'Push Status:   {"✓ Confirmed" if result["git_push_confirmed"] else "○ Pending"}')

if result['warnings']:
    print(f'\nWarnings:')
    for w in result['warnings']:
        print(f'  ⚠ {w}')

if result['errors']:
    print(f'\nErrors:')
    for e in result['errors']:
        print(f'  ✗ {e}')

print('='*70)
