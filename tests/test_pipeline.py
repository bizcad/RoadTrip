from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config

config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

post = BlogPost(
    title='Full Pipeline Test',
    excerpt='Testing the complete pipeline without git push to verify structure.',
    content='# Full Pipeline\n\nThis tests validation and formatting together.\n\n' + 'x' * 200,
    author_name='Nicholas Stein',
    author_picture='/assets/blog/authors/ns.jpg'
)

# Phase 1: Validate
val_result = skill._validate_input(post)
print(f'Phase 1 Validation: {val_result.decision} (confidence {val_result.confidence})')

if val_result.decision == 'APPROVE':
    # Phase 2: Format
    formatted, filename = skill._format_post(post)
    print(f'Phase 2 Format: {filename}')
    print(f'  Content length: {len(formatted)} bytes')
    print(f'  Has YAML frontmatter: {formatted.startswith("---")}')
    print(f'  Contains title: {"Full Pipeline Test" in formatted}')
else:
    print('Validation failed, skipping format phase')
