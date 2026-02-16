#!/usr/bin/env python3
"""
Blog Publisher CLI - Modern Entry Point

This is the canonical way to publish blog posts using the RoadTrip blog publisher skill.

Usage:
    python -m src.blog_publisher_cli \
        --title "Post Title" \
        --excerpt "Short description" \
        --content "# Post content..." \
        --author "Author Name" \
        --cover-image "/path/to/cover.jpg"

Or programmatically:
    from src.blog_publisher_cli import publish_blog_post
    result = publish_blog_post(title, excerpt, content, author, cover_image)
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add repository root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from src.skills.blog_publisher import (
    BlogPublisherSkill,
    BlogPost,
    load_config
)


def publish_blog_post(
    title: str,
    excerpt: str,
    content: str,
    author_name: str = "RoadTrip",
    author_picture: str = "",
    cover_image: str = "",
    date: str = "",
    og_image: str = ""
) -> dict:
    """
    Publish a blog post to the RoadTrip blog.
    
    Args:
        title: Post title (required, 1-100 chars)
        excerpt: SEO excerpt (required, 50-160 chars)
        content: Markdown content (required, 50+ chars)
        author_name: Author name (optional, defaults to "RoadTrip")
        author_picture: Author image path (optional)
        cover_image: Cover image path (optional)
        date: ISO 8601 date (optional, defaults to today)
        og_image: Open Graph image path (optional)
    
    Returns:
        dict with keys: decision, success, filename, url, commit_hash, errors, warnings
    """
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        # Fall back to defaults if config not found
        config = {
            "blog": {
                "repo": {
                    "url": "https://github.com/bizcad/roadtrip-blog.git",
                    "branch": "main",
                    "local_path": None,
                    "posts_folder": "_posts"
                },
                "vercel": {
                    "domain": "roadtrip-blog-ten.vercel.app",
                    "estimated_build_time_sec": 30
                },
                "git": {
                    "author_name": "RoadTrip Orchestrator",
                    "author_email": "workflow@roadtrip.local",
                    "commit_prefix": "blog"
                },
                "validation": {
                    "min_content_length": 50,
                    "min_excerpt_length": 50,
                    "max_excerpt_length": 160,
                    "max_file_size_mb": 1,
                    "check_for_secrets": True
                },
                "defaults": {
                    "author_name": "RoadTrip",
                    "author_picture": "/assets/blog/authors/roadtrip.jpeg",
                    "coverImage": "/assets/blog/default-cover.jpg"
                }
            }
        }
    
    # Create blog post object
    post = BlogPost(
        title=title,
        excerpt=excerpt,
        content=content,
        author_name=author_name,
        author_picture=author_picture,
        coverImage=cover_image,
        date=date,
        ogImage=og_image
    )
    
    # Initialize skill and publish
    skill = BlogPublisherSkill(config)
    result = skill.publish(post)
    
    # Convert result to dict for API compatibility
    return {
        "decision": result.decision,
        "success": result.success,
        "filename": result.filename,
        "url": result.url,
        "commit_hash": result.commit_hash,
        "git_push_confirmed": result.git_push_confirmed,
        "confidence": result.confidence,
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Publish a blog post to the RoadTrip blog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple post
  python -m src.blog_publisher_cli \\
    --title "My Post Title" \\
    --excerpt "Short description here" \\
    --content "# Post content..."
  
  # With all options
  python -m src.blog_publisher_cli \\
    --title "Advanced Post" \\
    --excerpt "Detailed description" \\
    --content "$(cat post.md)" \\
    --author "John Doe" \\
    --cover-image "/assets/blog/post-cover.jpg" \\
    --date "2026-02-15T10:30:00.000Z"
        """
    )
    
    parser.add_argument(
        "--title",
        required=True,
        help="Post title (1-100 characters)"
    )
    parser.add_argument(
        "--excerpt",
        required=True,
        help="SEO excerpt (50-160 characters)"
    )
    parser.add_argument(
        "--content",
        required=True,
        help="Markdown content (50+ characters)"
    )
    parser.add_argument(
        "--author",
        default="RoadTrip",
        help="Author name (default: RoadTrip)"
    )
    parser.add_argument(
        "--author-picture",
        default="",
        help="Author image path (optional)"
    )
    parser.add_argument(
        "--cover-image",
        default="",
        help="Cover image path (optional)"
    )
    parser.add_argument(
        "--og-image",
        default="",
        help="Open Graph image path (optional)"
    )
    parser.add_argument(
        "--date",
        default="",
        help="ISO 8601 date (optional, defaults to today)"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    args = parser.parse_args()
    
    # Publish
    result = publish_blog_post(
        title=args.title,
        excerpt=args.excerpt,
        content=args.content,
        author_name=args.author,
        author_picture=args.author_picture,
        cover_image=args.cover_image,
        date=args.date,
        og_image=args.og_image
    )
    
    # Output result
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        # Text output
        print("\n" + "="*60)
        print("Blog Publisher Result")
        print("="*60)
        print(f"Decision:     {result['decision']}")
        print(f"Success:      {result['success']}")
        print(f"Confidence:   {result['confidence']:.2f}")
        
        if result['success']:
            print(f"\n📝 Post Details:")
            print(f"   Filename: {result['filename']}")
            print(f"   URL:      {result['url']}")
            print(f"   Commit:   {result['commit_hash']}")
        
        if result['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"   - {warning}")
        
        if result['errors']:
            print(f"\n❌ Errors:")
            for error in result['errors']:
                print(f"   - {error}")
        
        print("="*60)
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
