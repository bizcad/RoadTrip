#!/usr/bin/env python3
"""
Publish the blog post: How We Built a Trusted AI Skill
"""

from src.skills.blog_publisher import BlogPublisherSkill, BlogPost, load_config

def main():
    # Load config
    config = load_config('config/blog-config.yaml')
    skill = BlogPublisherSkill(config)
    
    # Read the blog post markdown
    with open('docs/Blog_Rigor_in_Agentic_Development.md', 'r') as f:
        markdown_content = f.read()
    
    # Extract content (remove title and date section)
    parts = markdown_content.split('---')
    content = parts[2].strip() if len(parts) > 2 else markdown_content
    
    # Create post
    post = BlogPost(
        title='How We Built a Trusted AI Skill: A Case Study in Rigorous Development',
        excerpt='When building AI agents, how do you stay honest when the system is complex? This case study shows how immutable prototypes, invisible test infrastructure, and oracle-based verification create trustworthy agentic systems.',
        content=content,
        author_name='Nick Stein',
        coverImage='/assets/blog/rigor-in-agentic-development.jpg'
    )
    
    # Publish
    print("Publishing blog post...")
    result = skill.publish(post)
    
    # Report results
    print("\n" + "="*50)
    print("Blog Publisher Result")
    print("="*50)
    print(f"Decision: {result.decision}")
    print(f"Success: {result.success}")
    print(f"Filename: {result.filename}")
    print(f"URL: {result.url}")
    print(f"Commit: {result.commit_hash}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Git Push Confirmed: {result.git_push_confirmed}")
    
    if result.errors:
        print(f"\nErrors:")
        for err in result.errors:
            print(f"  - {err}")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warn in result.warnings:
            print(f"  - {warn}")
    
    print("="*50)

if __name__ == '__main__':
    main()
