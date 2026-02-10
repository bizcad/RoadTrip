#!/usr/bin/env python3
"""
commit_message.py

Generates semantic commit messages using cost-optimized Tier 1→2→3 approach.
- Tier 1 (deterministic, $0): 90% of commits
- Tier 2 (LLM fallback, ~$0.001-0.01): Complex cases
- Tier 3 (user override, $0): Explicit message

Standalone module; can be called directly or imported.

Usage:
    python commit_message.py --staged-files src/auth.py src/models.py --diff-file changes.patch
    python commit_message.py --user-message "feat: custom message" --dry-run
"""

import sys
import json
import argparse
import os
from pathlib import Path
from fnmatch import fnmatch
from dataclasses import asdict
from typing import Optional, List, Dict, Tuple
from datetime import datetime

# Import models from same package
try:
    from .commit_message_models import (
        CommitApproach,
        Tier1Score,
        CostTracking,
        CommitMessageResult,
        CommitMessageInput,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from commit_message_models import (
            CommitApproach,
            Tier1Score,
            CostTracking,
            CommitMessageResult,
            CommitMessageInput,
        )
    except ImportError:
        sys.stderr.write("Error: commit_message_models.py not found. Must be in same directory.\n")
        sys.exit(1)

try:
    import yaml
except ImportError:
    sys.stderr.write("Error: PyYAML not installed. Run: pip install pyyaml\n")
    sys.exit(1)


class CommitMessageSkill:
    """Generates commit messages using Tier 1→2→3 strategy."""

    def __init__(self, config_path: str = "config/commit-strategy.yaml"):
        """Load configuration from YAML."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.cost_log: List[Dict] = []

    def _load_config(self) -> Dict:
        """Load commit-strategy.yaml configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config not found: {self.config_path}\n"
                f"Expected at: {self.config_path.absolute()}"
            )
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config or 'commit_message' not in config:
            raise ValueError("Invalid config: missing 'commit_message' section")
        
        return config['commit_message']

    def generate(
        self,
        staged_files: List[str],
        diff: str = "",
        user_message: Optional[str] = None,
        dry_run: bool = False,
    ) -> CommitMessageResult:
        """
        Generate commit message using Tier 1→2→3 strategy.
        
        Args:
            staged_files: List of staged file paths
            diff: Unified diff content (optional, for Tier 2)
            user_message: User-provided message (Tier 3, overrides all)
            dry_run: If True, only calculate; don't call external APIs
        
        Returns:
            CommitMessageResult with message, approach, confidence, cost, etc.
        """
        
        # =====================================================================
        # TIER 3: User Override
        # =====================================================================
        if user_message:
            return CommitMessageResult(
                message=user_message,
                approach_used=CommitApproach.TIER_3,
                confidence=1.0,
                cost_estimate=0.0,
                reasoning="User-provided message (Tier 3 override)",
                tier1_score=None,
                cost_tracking=CostTracking(
                    model=None,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )

        # =====================================================================
        # TIER 1: Deterministic Logic
        # =====================================================================
        tier1_result = self._tier1_generate(staged_files, diff)
        
        confidence_threshold = self.config.get('confidence_threshold', 0.85)
        
        if tier1_result.confidence >= confidence_threshold:
            # Tier 1 passed
            return CommitMessageResult(
                message=tier1_result.message,
                approach_used=CommitApproach.TIER_1,
                confidence=tier1_result.confidence,
                cost_estimate=0.0,
                reasoning=tier1_result.reasoning,
                tier1_score=tier1_result,
                cost_tracking=CostTracking(
                    model=None,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )

        # =====================================================================
        # TIER 2: LLM Fallback
        # =====================================================================
        if not self.config.get('tier2', {}).get('enabled', True):
            # Tier 2 disabled; use Tier 1 result even if low confidence
            return CommitMessageResult(
                message=tier1_result.message,
                approach_used=CommitApproach.TIER_1,
                confidence=tier1_result.confidence,
                cost_estimate=0.0,
                reasoning=f"{tier1_result.reasoning} (Tier 2 disabled)",
                tier1_score=tier1_result,
                cost_tracking=CostTracking(
                    model=None,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )

        # Tier 2 enabled; call LLM
        if dry_run:
            # Don't actually call API in dry-run
            return CommitMessageResult(
                message=f"[DRY-RUN] {tier1_result.message}",
                approach_used=CommitApproach.TIER_2,
                confidence=0.85,
                cost_estimate=0.005,  # Estimate
                reasoning=f"{tier1_result.reasoning}; Tier 2 would be called (dry-run mode)",
                tier1_score=tier1_result,
                cost_tracking=CostTracking(
                    model=self.config['tier2'].get('model', 'claude-3-5-sonnet-20241022'),
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )

        tier2_result = self._tier2_generate(staged_files, diff)
        return tier2_result

    def _tier1_generate(self, staged_files: List[str], diff: str = "") -> Tier1Score:
        """Tier 1: Deterministic heuristics."""
        
        if not staged_files:
            return Tier1Score(
                file_count=0,
                categories=[],
                single_category=False,
                pattern_match="chore: empty commit",
                message="chore: empty commit",
                confidence=0.5,
                reasoning="No staged files",
            )

        # --------- Step 1: Categorize Files ---------
        categories = self._categorize_files(staged_files)
        file_count = len(staged_files)
        
        # --------- Step 2: Determine confidence and pattern ---------
        
        # Case 1: Single file
        if file_count == 1:
            return self._tier1_single_file(staged_files[0], categories, diff)
        
        # Case 2: Multiple files, same category
        if len(categories) == 1 and file_count <= 10:
            return self._tier1_multiple_files_same_category(
                staged_files, categories[0], diff
            )
        
        # Case 3: Too many files
        if file_count > 10:
            return Tier1Score(
                file_count=file_count,
                categories=categories,
                single_category=False,
                pattern_match="chore: bulk update",
                message=f"chore: bulk update {file_count} files",
                confidence=0.70,
                reasoning="Too many files (>10); ambiguous intent",
            )
        
        # Case 4: Mixed categories
        return Tier1Score(
            file_count=file_count,
            categories=categories,
            single_category=False,
            pattern_match="chore: update multiple modules",
            message="chore: update multiple modules",
            confidence=0.60,
            reasoning=f"Mixed categories: {', '.join(categories)}; Tier 2 recommended",
        )

    def _categorize_files(self, files: List[str]) -> List[str]:
        """Determine file categories (src, docs, tests, etc.)."""
        categories = set()
        
        for file_path in files:
            path = Path(file_path)
            
            # Check extension-based rules
            ext = path.suffix.lower()
            if ext in ['.md', '.txt']:
                categories.add('documentation')
                continue
            if ext in ['.yml', '.yaml', '.json']:
                categories.add('config')
                continue
            
            # Check directory-based rules
            parts = path.parts
            
            if 'src' in parts:
                categories.add('src')
                continue
            if 'tests' in parts:
                categories.add('tests')
                continue
            if 'skills' in parts:
                categories.add('skills')
                continue
            if 'docs' in parts or 'docs' == parts[0]:
                categories.add('documentation')
                continue
            
            # Fallback: treat as 'other'
            categories.add('other')
        
        return sorted(list(categories))

    def _tier1_single_file(self, file_path: str, categories: List[str], diff: str) -> Tier1Score:
        """Generate message for single-file change."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # Documentation
        if ext in ['.md', '.txt'] or 'documentation' in categories:
            verb = self._extract_action_from_diff(diff) or "update"
            message = f"docs: {verb} {path.name}"
            return Tier1Score(
                file_count=1,
                categories=categories,
                single_category=True,
                pattern_match="docs: {action}",
                message=message,
                confidence=0.95,
                reasoning=f"Single documentation file: {path.name}",
            )
        
        # Config
        if ext in ['.yml', '.yaml', '.json'] or 'config' in categories:
            verb = self._extract_action_from_diff(diff) or "update"
            message = f"chore: {verb} configuration"
            return Tier1Score(
                file_count=1,
                categories=categories,
                single_category=True,
                pattern_match="chore: {action}",
                message=message,
                confidence=0.93,
                reasoning=f"Single config file: {path.name}",
            )
        
        # Source code
        if 'src' in categories:
            verb = self._extract_action_from_diff(diff) or "update"
            message = f"feat: {verb} {self._infer_module(file_path)}"
            return Tier1Score(
                file_count=1,
                categories=categories,
                single_category=True,
                pattern_match="feat: {action}",
                message=message,
                confidence=0.90,
                reasoning=f"Single source file: {path.name}",
            )
        
        # Tests
        if 'tests' in categories:
            verb = self._extract_action_from_diff(diff) or "update"
            message = f"test: {verb} {self._infer_module(file_path, prefix='test_')}"
            return Tier1Score(
                file_count=1,
                categories=categories,
                single_category=True,
                pattern_match="test: {action}",
                message=message,
                confidence=0.92,
                reasoning=f"Single test file: {path.name}",
            )
        
        # Skills
        if 'skills' in categories:
            verb = self._extract_action_from_diff(diff) or "update"
            message = f"feat: {verb} skill"
            return Tier1Score(
                file_count=1,
                categories=categories,
                single_category=True,
                pattern_match="feat: {action}",
                message=message,
                confidence=0.88,
                reasoning=f"Single skill file: {path.name}",
            )
        
        # Default fallback
        verb = self._extract_action_from_diff(diff) or "update"
        message = f"chore: {verb} {path.name}"
        return Tier1Score(
            file_count=1,
            categories=categories,
            single_category=True,
            pattern_match="chore: {action}",
            message=message,
            confidence=0.80,
            reasoning=f"Default category for: {path.name}",
        )

    def _tier1_multiple_files_same_category(
        self, files: List[str], category: str, diff: str
    ) -> Tier1Score:
        """Generate message for multiple files in same category."""
        
        message_type = {
            'src': 'feat',
            'tests': 'test',
            'documentation': 'docs',
            'config': 'chore',
            'skills': 'feat',
        }.get(category, 'chore')
        
        verb = self._extract_action_from_diff(diff) or "update"
        message = f"{message_type}: {verb} {category}"
        
        return Tier1Score(
            file_count=len(files),
            categories=[category],
            single_category=True,
            pattern_match=f"{message_type}: {{action}}",
            message=message,
            confidence=0.88,
            reasoning=f"{len(files)} files in {category}/",
        )

    def _extract_action_from_diff(self, diff: str) -> Optional[str]:
        """Try to infer action verb from diff content."""
        
        if not diff:
            return None
        
        diff_lower = diff.lower()
        
        # Simple heuristics
        if '+' in diff and '-' not in diff:
            return 'add'
        if '-' in diff and '+' not in diff:
            return 'remove'
        if '+' in diff and '-' in diff:
            return 'update'
        
        # Based on keywords
        if 'def ' in diff or 'class ' in diff:
            return 'implement'
        if 'raise ' in diff or 'error' in diff or 'exception' in diff:
            return 'handle error'
        
        return None

    def _infer_module(self, file_path: str, prefix: str = '') -> str:
        """Infer module name from file path."""
        path = Path(file_path)
        name = path.stem
        if name.startswith(prefix):
            name = name[len(prefix):]
        return name.replace('_', ' ')

    def _tier2_generate(self, staged_files: List[str], diff: str) -> CommitMessageResult:
        """
        Tier 2: Call Claude API to generate message.
        
        NOTE: This requires ANTHROPIC_API_KEY environment variable.
        """
        try:
            import anthropic
        except ImportError:
            sys.stderr.write("Error: anthropic library not installed. Run: pip install anthropic\n")
            # Fallback to Tier 1 result
            tier1 = self._tier1_generate(staged_files, diff)
            return CommitMessageResult(
                message=tier1.message,
                approach_used=CommitApproach.TIER_1,
                confidence=tier1.confidence,
                cost_estimate=0.0,
                reasoning=f"{tier1.reasoning} (Tier 2: anthropic library not installed, fallback to Tier 1)",
                tier1_score=tier1,
                cost_tracking=CostTracking(
                    model=None,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            sys.stderr.write("Warning: ANTHROPIC_API_KEY not set. Falling back to Tier 1.\n")
            tier1 = self._tier1_generate(staged_files, diff)
            return CommitMessageResult(
                message=tier1.message,
                approach_used=CommitApproach.TIER_1,
                confidence=tier1.confidence,
                cost_estimate=0.0,
                reasoning=f"{tier1.reasoning} (Tier 2: API key not set)",
                tier1_score=tier1,
                cost_tracking=CostTracking(
                    model=None,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )

        # Build prompt
        files_list = '\n'.join(f"  - {f}" for f in staged_files)
        prompt = f"""You are generating a git commit message using Conventional Commits format (https://www.conventionalcommits.org/).

Staged files:
{files_list}

Changes:
{diff[:2000]}  # Truncate to 2000 chars

Generate a concise commit message following these rules:
- Format: type(scope): subject
- Types: feat, fix, refactor, docs, test, chore, perf, ci
- Subject: imperative mood, no period
- Max 72 chars for subject line
- Keep it short (under 100 words total)

Output ONLY the commit message, no explanations or markdown formatting."""

        model = self.config['tier2'].get('model', 'claude-3-5-sonnet-20241022')
        max_tokens = self.config['tier2'].get('max_tokens', 500)

        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            message = response.content[0].text.strip()
            
            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            pricing = self.config.get('pricing', {})
            input_cost_per_1m = pricing.get('input_cost_per_1m_tokens', 0.003)
            output_cost_per_1m = pricing.get('output_cost_per_1m_tokens', 0.015)
            
            cost_usd = (
                (input_tokens / 1_000_000) * input_cost_per_1m +
                (output_tokens / 1_000_000) * output_cost_per_1m
            )
            
            # Log cost
            self.cost_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'model': model,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': cost_usd,
            })
            
            return CommitMessageResult(
                message=message,
                approach_used=CommitApproach.TIER_2,
                confidence=0.95,
                cost_estimate=cost_usd,
                reasoning=f"Tier 2 LLM called (Tier 1 confidence < threshold)",
                tier1_score=None,
                cost_tracking=CostTracking(
                    model=model,
                    tokens_input=input_tokens,
                    tokens_output=output_tokens,
                    cost_usd=cost_usd,
                ),
            )
        
        except Exception as e:
            sys.stderr.write(f"Error calling Tier 2 API: {e}\n")
            # Fallback to Tier 1
            tier1 = self._tier1_generate(staged_files, diff)
            return CommitMessageResult(
                message=tier1.message,
                approach_used=CommitApproach.TIER_1,
                confidence=tier1.confidence,
                cost_estimate=0.0,
                reasoning=f"{tier1.reasoning} (Tier 2 failed, fallback to Tier 1)",
                tier1_score=tier1,
                cost_tracking=CostTracking(
                    model=None,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                ),
            )


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate semantic commit messages using Tier 1→2→3 strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --staged-files src/auth.py src/models.py
  %(prog)s --staged-files src/ tests/ --diff-file changes.patch
  %(prog)s --user-message "feat: my custom message"
  %(prog)s --dry-run --staged-files src/skill.py
        """,
    )
    
    parser.add_argument(
        '--staged-files',
        nargs='+',
        help='List of staged file paths',
    )
    parser.add_argument(
        '--diff-file',
        help='Path to unified diff file (optional)',
    )
    parser.add_argument(
        '--diff',
        help='Unified diff as string (optional)',
    )
    parser.add_argument(
        '--user-message',
        help='User-provided commit message (Tier 3 override)',
    )
    parser.add_argument(
        '--config',
        default='config/commit-strategy.yaml',
        help='Path to commit-strategy.yaml (default: config/commit-strategy.yaml)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Do not call external APIs; show what would happen',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON instead of plain text',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output including reasoning',
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.staged_files and not args.user_message:
        parser.print_help()
        print("\nError: Must provide --staged-files or --user-message", file=sys.stderr)
        sys.exit(1)
    
    try:
        skill = CommitMessageSkill(config_path=args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Read diff if provided
    diff = ""
    if args.diff:
        diff = args.diff
    elif args.diff_file:
        try:
            with open(args.diff_file, 'r') as f:
                diff = f.read()
        except IOError as e:
            print(f"Error reading diff file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Generate commit message
    try:
        result = skill.generate(
            staged_files=args.staged_files or [],
            diff=diff,
            user_message=args.user_message,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"Error generating message: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output result
    if args.json:
        output = {
            'message': result.message,
            'approach': result.approach_used.value,
            'confidence': result.confidence,
            'cost_usd': result.cost_estimate,
            'reasoning': result.reasoning,
        }
        if result.cost_tracking:
            output['tokens'] = {
                'input': result.cost_tracking.tokens_input,
                'output': result.cost_tracking.tokens_output,
            }
        print(json.dumps(output, indent=2))
    else:
        print(f"Commit Message (Tier {result.approach_used.value[-1]}):")
        print(f"  {result.message}")
        if args.verbose:
            print(f"\nConfidence: {result.confidence:.2%}")
            print(f"Cost: ${result.cost_estimate:.4f}")
            if result.cost_tracking.tokens_input > 0:
                print(f"Tokens: {result.cost_tracking.tokens_input} input, {result.cost_tracking.tokens_output} output")
            print(f"Reasoning: {result.reasoning}")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
