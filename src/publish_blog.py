#!/usr/bin/env python3
"""
⚠️  DEPRECATED - Use src/skills/blog_publisher.py directly instead

This file is maintained for historical reference only (Phase 5-6 experiments).
The canonical blog publisher skill implementation is now at: src/skills/blog_publisher.py

This script calls the blog publishing orchestrator which handles:
1. Blog Publisher SKILL - Format and commit
2. Push with Token SKILL - Authenticate and push

DEPRECATED: For new implementations, use:
    from src.skills.blog_publisher import BlogPublisherSkill, BlogPost
    skill = BlogPublisherSkill(config)
    result = skill.publish(blog_post)
"""

from orchestrate_blog_publish import orchestrate_blog_publish


def main():
    # Read the blog post markdown
    with open('docs/Blog_Rigor_in_Agentic_Development.md', 'r') as f:
        markdown_content = f.read()
    
    # Extract content (remove title and date section)
    parts = markdown_content.split('---')
    content = parts[2].strip() if len(parts) > 2 else markdown_content
    
    # Publish via orchestrator
    result = orchestrate_blog_publish(
        title='How We Built a Trusted AI Skill: A Case Study in Rigorous Development',
        excerpt='How immutable prototypes, test infrastructure, and oracle-based verification create trustworthy agentic systems.',
        content=content,
        author_name='Nick Stein',
        author_picture='/assets/blog/authors/nick.jpeg',
        cover_image='/assets/blog/rigor-in-agentic-development.jpg'
    )
    
    # Report results
    print("\n" + "="*50)
    print("Blog Publish Orchestration Result")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Filename: {result['filename']}")
    print(f"URL: {result['url']}")
    print(f"Commit: {result['commit_hash']}")
    
    if result["errors"]:
        print(f"\nErrors:")
        for err in result["errors"]:
            print(f"  - {err}")
    
    print("="*50)


if __name__ == '__main__':
    main()

