#!/usr/bin/env python3
"""
Blog Publishing Orchestrator - Phase 1b Implementation

Purpose: Orchestrate the blog publishing workflow by chaining skills:
  1. blog_publisher SKILL - Validate, format, and commit post
  2. push_with_token SKILL - Authenticate and push to remote

This follows Phase 1b principles:
- Deterministic orchestration (hardcoded sequence, not dynamic routing)
- Clear separation of concerns (format vs. push)
- Leverages existing tested infrastructure (push_with_token)
- Ready for Phase 2b migration to dynamic skill discovery

Usage:
    python orchestrate_blog_publish.py <title> <excerpt> <content>
    
    Or import as a module:
        from orchestrate_blog_publish import orchestrate_blog_publish
        result = orchestrate_blog_publish(title, excerpt, content)
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any

# Add src to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))

from skills.blog_publisher import BlogPublisherSkill, BlogPost, load_config


def orchestrate_blog_publish(
    title: str,
    excerpt: str,
    content: str,
    author_name: str = "Nicholas Stein",
    author_picture: str = "/assets/blog/authors/nick.jpeg",
    cover_image: str = "/assets/blog/default-cover.jpg",
) -> Dict[str, Any]:
    """
    Orchestrate blog post publishing workflow.
    
    Phase 1: blog_publisher SKILL
        - Validate post metadata and content
        - Format with YAML frontmatter
        - Stage and commit to local blog repo
        - Return: commit_hash, filename, url
    
    Phase 2: push_with_token SKILL
        - Load GitHub PAT from environment/file
        - Push committed changes to origin/main
        - Return: success/failure status
    
    Args:
        title: Post title (1-100 chars)
        excerpt: SEO excerpt (auto-truncated to 160 chars with ...)
        content: Markdown content (50+ chars)
        author_name: Post author (default: Nicholas Stein)
        author_picture: Author image path (default: /assets/blog/authors/nick.jpeg)
        cover_image: Cover image path (default: /assets/blog/default-cover.jpg)
    
    Returns:
        Dict with keys:
            - success: bool (True if both phases succeeded)
            - phase_1_result: BlogPublishResult (from blog_publisher)
            - phase_2_result: dict (from push_with_token)
            - filename: str (generated filename)
            - url: str (live blog URL)
            - commit_hash: str (git commit hash)
            - errors: list (aggregated errors)
    """
    
    result = {
        "success": False,
        "phase_1_result": None,
        "phase_2_result": None,
        "filename": "",
        "url": "",
        "commit_hash": "",
        "errors": [],
    }
    
    # ===== PHASE 1: Blog Publisher Skill =====
    print("\n" + "=" * 60)
    print("PHASE 1: Blog Publisher (Validate, Format, Commit)")
    print("=" * 60)
    
    try:
        # Load config and skill
        config = load_config("config/blog-config.yaml")
        blog_skill = BlogPublisherSkill(config)
        
        # Create post
        post = BlogPost(
            title=title,
            excerpt=excerpt,
            content=content,
            author_name=author_name,
            author_picture=author_picture,
            coverImage=cover_image,
        )
        
        # Execute blog publisher skill
        phase_1_result = blog_skill.publish(post)
        result["phase_1_result"] = phase_1_result
        result["filename"] = phase_1_result.filename
        result["url"] = phase_1_result.url
        result["commit_hash"] = phase_1_result.commit_hash
        
        print(f"Decision: {phase_1_result.decision}")
        print(f"Filename: {phase_1_result.filename}")
        print(f"Commit: {phase_1_result.commit_hash}")
        print(f"URL: {phase_1_result.url}")
        
        if phase_1_result.warnings:
            print(f"\nWarnings:")
            for warn in phase_1_result.warnings:
                print(f"  WARNING: {warn}")
        
        if phase_1_result.decision != "APPROVE":
            result["errors"].append(f"Phase 1 rejected: {', '.join(phase_1_result.errors)}")
            print(f"\n[REJECTED] Phase 1 FAILED")
            for err in phase_1_result.errors:
                print(f"  - {err}")
            return result
        
        print(f"[OK] Phase 1 SUCCESS (commit: {phase_1_result.commit_hash})")
        
    except Exception as e:
        result["errors"].append(f"Phase 1 exception: {str(e)}")
        print(f"[ERROR] Phase 1 EXCEPTION: {e}")
        return result
    
    # ===== PHASE 2: Push (Deferred to `gpush`) =====
    print("\n" + "=" * 60)
    print("PHASE 2: Push (Use `gpush` command)")
    print("=" * 60)
    
    blog_repo_path = Path(config.get("blog", {}).get("repo", {}).get("local_path", ""))
    print(f"\nTo complete publishing:")
    print(f"  1. cd {blog_repo_path}")
    print(f"  2. gpush")
    print(f"\n(gpush handles authentication silently via PowerShell infrastructure)")
    result["success"] = True
    result["phase_2_result"] = {"status": "deferred", "instruction": "use gpush"}
    
    
    # ===== Summary =====
    print("\n" + "=" * 60)
    print("ORCHESTRATION SUMMARY")
    print("=" * 60)
    status = 'YES' if result['success'] else 'NO'
    print(f"Overall Success: {status}")
    print(f"Filename: {result['filename']}")
    print(f"Commit: {result['commit_hash']}")
    print(f"URL: {result['url']}")
    
    if result["errors"]:
        print(f"\nErrors ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"  - {err}")
    
    return result


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrate_blog_publish.py <config_file>")
        print("  where config_file contains post metadata in JSON format")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        with open(config_file, "r") as f:
            post_config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    result = orchestrate_blog_publish(
        title=post_config.get("title"),
        excerpt=post_config.get("excerpt"),
        content=post_config.get("content"),
        author_name=post_config.get("author_name", "Nicholas Stein"),
        author_picture=post_config.get("author_picture", "/assets/blog/authors/nick.jpeg"),
        cover_image=post_config.get("cover_image", "/assets/blog/default-cover.jpg"),
    )
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
