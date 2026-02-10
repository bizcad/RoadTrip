"""
Blog Publisher Skill - Phase 3 Implementation

Purpose: Autonomous blog post publishing with validation, formatting, git operations, and live deployment.

Specification: skills/blog-publisher/SKILL.md
Decision Logic: skills/blog-publisher/CLAUDE.md

Key Principles:
- ALL decisions are deterministic (no LLM-based guessing)
- Confidence scores reflect validation strictness, not probability
- Conservative defaults: block on uncertain operations
- Idempotent: re-running with same input is safe
- All-or-nothing: post is either published or not
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import re
import subprocess
import json
import yaml


@dataclass
class BlogPost:
    """A blog post ready for publishing.
    
    Phase 2 Discovery: Actual blog template requires coverImage and excerpt.
    """
    title: str                          # Required: 1-100 chars
    excerpt: str                        # Required: 50-160 chars (SEO description)
    content: str                        # Required: Markdown content (50+ chars)
    author_name: str = "RoadTrip"      # Optional, defaults to "RoadTrip"
    author_picture: str = ""           # Optional, path to author image
    coverImage: str = ""               # Optional, path to cover image
    date: str = ""                     # Optional ISO format, defaults to today
    ogImage: str = ""                  # Optional, Open Graph image path


@dataclass
class BlogPublishResult:
    """Result of a blog publish operation."""
    decision: str                       # "APPROVE" | "REJECT"
    success: bool                       # True if post went live
    filename: str = ""                  # Generated filename (e.g., "2026-02-09-my-post.md")
    url: str = ""                       # Live URL on blog
    commit_hash: str = ""               # Git commit hash (first 8 chars)
    git_push_confirmed: bool = False    # True if push succeeded
    confidence: float = 0.0             # 0.0-1.0 (1.0 = certain)
    warnings: list[str] = field(default_factory=list)  # Non-blocking issues
    errors: list[str] = field(default_factory=list)    # Blocking errors
    metadata: dict = field(default_factory=dict)       # Additional info


class BlogPublisherSkill:
    """Blog Publisher implementation with 5-phase pipeline."""
    
    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.blog_config = config.get("blog", {})
        self.repo_config = self.blog_config.get("repo", {})
        self.validation_config = self.blog_config.get("validation", {})
        self.defaults = self.blog_config.get("defaults", {})
        self.vercel_config = self.blog_config.get("vercel", {})
    
    def publish(self, post: BlogPost) -> BlogPublishResult:
        """Execute the complete publishing pipeline.
        
        Returns: BlogPublishResult with decision, success, and metadata.
        """
        # Phase 1: Validate Input
        result = self._validate_input(post)
        if result.decision == "REJECT":
            return result
        
        # Phase 2: Format Post
        formatted_content, filename = self._format_post(post)
        if formatted_content is None:
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append("Failed to format post")
            return result
        
        result.filename = filename
        
        # Phase 3: Prepare Git Commit
        git_ready = self._prepare_git_commit(filename, formatted_content)
        if not git_ready:
            result.decision = "REJECT"
            result.confidence = 0.95
            result.errors.append("Failed to stage git changes")
            return result
        
        # Phase 4: Push to Blog Repo
        commit_hash, push_success = self._push_to_blog_repo(filename, post)
        result.commit_hash = commit_hash
        result.git_push_confirmed = push_success
        
        if not push_success:
            result.decision = "REJECT"
            result.success = False
            result.confidence = 0.0
            result.errors.append("Git push failed")
            return result
        
        # Phase 5: Return Result
        result.decision = "APPROVE"
        result.success = True
        result.confidence = 0.99  # Push succeeded; Vercel build TBD
        result.url = self._generate_live_url(filename)
        result.metadata["build_time_estimate_sec"] = self.vercel_config.get("estimated_build_time_sec", 30)
        result.metadata["vercel_domain"] = self.vercel_config.get("domain", "")
        
        return result
    
    def _validate_input(self, post: BlogPost) -> BlogPublishResult:
        """Phase 1: Validate input against specification.
        
        Returns:
            BlogPublishResult with APPROVE or REJECT decision
        """
        result = BlogPublishResult(decision="APPROVE", success=False, confidence=1.0)
        
        # Title validation
        if not post.title or not post.title.strip():
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append("title is required and non-empty")
            return result
        
        if len(post.title) > 100:
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append(f"title too long ({len(post.title)} > 100 chars)")
            return result
        
        # Excerpt validation
        if not post.excerpt or not post.excerpt.strip():
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append("excerpt is required and non-empty")
            return result
        
        min_excerpt = self.validation_config.get("min_excerpt_length", 50)
        max_excerpt = self.validation_config.get("max_excerpt_length", 160)
        
        if len(post.excerpt) < min_excerpt:
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append(f"excerpt too short ({len(post.excerpt)} < {min_excerpt} chars)")
            return result
        
        if len(post.excerpt) > max_excerpt:
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append(f"excerpt too long ({len(post.excerpt)} > {max_excerpt} chars)")
            return result
        
        # Content validation
        if not post.content or not post.content.strip():
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append("content is required and non-empty")
            return result
        
        min_content = self.validation_config.get("min_content_length", 50)
        if len(post.content) < min_content:
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append(f"content too short ({len(post.content)} < {min_content} chars)")
            return result
        
        # HTML check
        if re.search(r'<[^>]+>', post.content):
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append("HTML not allowed; markdown only")
            return result
        
        # Date format validation
        if post.date:
            if not self._validate_iso_date(post.date):
                result.decision = "REJECT"
                result.confidence = 1.0
                result.errors.append(f"date must be ISO 8601 format (YYYY-MM-DDTHH:mm:ss.000Z), got: {post.date}")
                return result
        
        # File size check
        projected_size = len(post.title) + len(post.excerpt) + len(post.content) + 500  # 500 for frontmatter
        max_size_mb = self.validation_config.get("max_file_size_mb", 1)
        if projected_size > (max_size_mb * 1024 * 1024):
            result.decision = "REJECT"
            result.confidence = 1.0
            result.errors.append(f"projected file size too large ({projected_size} > {max_size_mb * 1024 * 1024} bytes)")
            return result
        
        # Secrets check (delegate to rules-engine simulation)
        if self.validation_config.get("check_for_secrets", True):
            secrets_check = self._check_for_secrets(post.content)
            if not secrets_check:
                result.decision = "REJECT"
                result.confidence = 1.0
                result.errors.append("content contains potential secrets or credentials")
                return result
        
        # Defaults for optional fields
        if not post.author_picture:
            post.author_picture = self.defaults.get("author_picture", "/assets/blog/authors/roadtrip.jpeg")
            result.warnings.append("author_picture not provided; using default")
        
        if not post.coverImage:
            post.coverImage = self.defaults.get("coverImage", "/assets/blog/default-cover.jpg")
            result.warnings.append("coverImage not provided; using default")
        
        if not post.ogImage:
            post.ogImage = post.coverImage  # Default to coverImage
            result.warnings.append("ogImage not provided; defaulting to coverImage")
        
        # Success: all validations passed
        result.decision = "APPROVE"
        result.confidence = 0.99 if result.warnings else 1.0
        
        return result
    
    def _validate_iso_date(self, date_str: str) -> bool:
        """Validate ISO 8601 date format with milliseconds."""
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,}Z$'
        return bool(re.match(pattern, date_str))
    
    def _check_for_secrets(self, content: str) -> bool:
        """Check content for obvious secrets/credentials.
        
        Returns: True if no secrets found, False if suspicious patterns detected.
        """
        # Simple Pattern matching for common secrets
        suspicious_patterns = [
            r'API[_-]?KEY\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            r'PASSWORD\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            r'SECRET\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            r'Token\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            r'GITHUB_TOKEN\s*[=:]\s*(.+)',
            r'aws_access_key_id\s*[=:]\s*(.+)',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True
    
    def _format_post(self, post: BlogPost) -> tuple[Optional[str], str]:
        """Phase 2: Format post with frontmatter and generate filename.
        
        Returns:
            (formatted_content, filename) or (None, "") on error
        """
        # Generate slug from title
        slug = self._generate_slug(post.title)
        
        # Generate filename
        if post.date:
            date_part = post.date.split('T')[0]  # Extract YYYY-MM-DD
        else:
            date_part = datetime.utcnow().strftime('%Y-%m-%d')
        
        filename = f"{date_part}-{slug}.md"
        
        # Parse/generate date
        if post.date:
            iso_date = post.date
        else:
            iso_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Build frontmatter YAML
        frontmatter = {
            "title": post.title,
            "excerpt": post.excerpt,
            "coverImage": post.coverImage,
            "date": iso_date,
            "author": {
                "name": post.author_name,
                "picture": post.author_picture
            },
            "ogImage": {
                "url": post.ogImage
            }
        }
        
        # Serialize to YAML
        try:
            yaml_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error serializing frontmatter: {e}")
            return None, ""
        
        # Combine frontmatter + content
        formatted_content = f"---\n{yaml_frontmatter}---\n\n{post.content}"
        
        return formatted_content, filename
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title.
        
        Algorithm:
        1. Lowercase
        2. Remove punctuation
        3. Replace spaces with dashes
        4. Remove consecutive dashes
        """
        # Lowercase
        slug = title.lower()
        
        # Remove punctuation (keep alphanumeric, spaces, dashes)
        slug = re.sub(r'[^a-z0-9\s\-]', '', slug)
        
        # Replace spaces with dashes
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove consecutive dashes
        slug = re.sub(r'-+', '-', slug)
        
        # Trim dashes from start/end
        slug = slug.strip('-')
        
        # Limit length to 50 chars
        slug = slug[:50].rstrip('-')
        
        return slug
    
    def _prepare_git_commit(self, filename: str, formatted_content: str) -> bool:
        """Phase 3: Stage file and prepare for git commit.
        
        Returns: True if successful, False on error.
        """
        try:
            repo_path = Path(self.repo_config.get("local_path", "."))
            posts_folder = self.repo_config.get("posts_folder", "_posts")
            file_path = repo_path / posts_folder / filename
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(formatted_content, encoding='utf-8')
            
            # Stage file
            result = subprocess.run(
                ["git", "add", str(file_path)],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"Error preparing git commit: {e}")
            return False
    
    def _push_to_blog_repo(self, filename: str, post: BlogPost) -> tuple[str, bool]:
        """Phase 4: Commit and push to blog repository.
        
        Returns:
            (commit_hash, push_success)
        """
        try:
            repo_path = Path(self.repo_config.get("local_path", "."))
            branch = self.repo_config.get("branch", "main")
            git_config = self.blog_config.get("git", {})
            author_name = git_config.get("author_name", "RoadTrip Orchestrator")
            author_email = git_config.get("author_email", "workflow@roadtrip.local")
            commit_prefix = git_config.get("commit_prefix", "blog")
            
            # Extract date from filename
            date_part = filename.split('-')[0]  # YYYY-MM-DD
            
            # Generate commit message
            commit_message = f"{commit_prefix}: publish {post.title} ({date_part})"
            
            # Set git config
            subprocess.run(
                ["git", "config", "user.name", author_name],
                cwd=str(repo_path),
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.email", author_email],
                cwd=str(repo_path),
                capture_output=True,
                timeout=5
            )
            
            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if commit_result.returncode != 0:
                # File might already exist; check status
                status_result = subprocess.run(
                    ["git", "log", "-1", "--pretty=format:%H"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return status_result.stdout[:8], False
            
            # Get commit hash
            hash_result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            commit_hash = hash_result.stdout[:8]
            
            # Push with retries
            max_retries = 3
            for attempt in range(max_retries):
                push_result = subprocess.run(
                    ["git", "push", "origin", branch],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if push_result.returncode == 0:
                    return commit_hash, True
                
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            return commit_hash, False
        
        except Exception as e:
            print(f"Error pushing to blog repo: {e}")
            return "", False
    
    def _generate_live_url(self, filename: str) -> str:
        """Generate the live blog URL for this post.
        
        Filename: 2026-02-09-my-post.md
        Slug: my-post
        URL: https://roadtrip-blog-ten.vercel.app/blog/my-post
        """
        # Extract slug from filename
        # Format: YYYY-MM-DD-{slug}.md
        parts = filename.split('-', 3)  # Split on first 3 dashes
        slug = parts[3].replace('.md', '') if len(parts) > 3 else ""
        
        domain = self.vercel_config.get("domain", "roadtrip-blog-ten.vercel.app")
        return f"https://{domain}/blog/{slug}"


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


if __name__ == "__main__":
    # Example usage
    config = load_config("config/blog-config.yaml")
    
    skill = BlogPublisherSkill(config)
    
    # Test post
    test_post = BlogPost(
        title="Test Blog Post",
        excerpt="This is a test blog post for demonstration purposes.",
        content="# Test Blog Post\n\nThis is the content of the test post. It demonstrates the blog publisher skill.",
        author_name="Nicholas Stein",
        author_picture="/assets/blog/authors/ns.jpg",
        coverImage="/assets/blog/test/cover.jpg"
    )
    
    result = skill.publish(test_post)
    
    print("\n=== Blog Publisher Result ===")
    print(f"Decision: {result.decision}")
    print(f"Success: {result.success}")
    print(f"Filename: {result.filename}")
    print(f"URL: {result.url}")
    print(f"Commit: {result.commit_hash}")
    print(f"Confidence: {result.confidence}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
