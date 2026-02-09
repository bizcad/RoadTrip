# Blog Publisher Skill - Manual Test Checklist

**Phase 4 Testing**: Manual verification checklist for blog publisher skill.

**Test Environment**: 
- Local blog repo cloned: `G:\repos\AI\roadtrip-blog-repo`
- Author photo added: `public\assets\blog\authors\ns.jpg`
- Configuration: `config\blog-config.yaml`

---

## Pre-Test Setup

- [ ] Python environment ready (`py --version` → 3.10+)
- [ ] Dependencies installed:
  ```powershell
  py -m pip install pyyaml
  ```
- [ ] Blog repo available locally
- [ ] Configuration file `config/blog-config.yaml` is readable

---

## Test Group 1: Validation - Happy Path

### Test 1.1: Simple Post (All Fields)
```powershell
cd G:\repos\AI\RoadTrip
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(
    title='Manual Test Post 1',
    excerpt='This is a test of the blog publisher with all fields.',
    content='# Manual Test\n\nThis is a complete test with all fields provided.\n\n' + 'x' * 200,
    author_name='Nicholas Stein',
    author_picture='/assets/blog/authors/ns.jpg',
    coverImage='/assets/blog/test/cover.jpg'
)
result = skill._validate_input(post)
print(f'Decision: {result.decision}')
print(f'Confidence: {result.confidence}')
print(f'Errors: {result.errors}')
print(f'Warnings: {result.warnings}')
"
```

**Expected Output**:
```
Decision: APPROVE
Confidence: 1.0
Errors: []
Warnings: []
```

- [ ] Result shows APPROVE decision
- [ ] Confidence is 1.0 (perfect input)
- [ ] No errors or warnings

### Test 1.2: Minimal Input (Defaults Applied)
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(
    title='Minimal Test Post',
    excerpt='Valid excerpt for testing minimal input mode.',
    content='Content here ' * 10
)
result = skill._validate_input(post)
print(f'Decision: {result.decision}')
print(f'Confidence: {result.confidence}')
print(f'Warnings: {result.warnings}')
"
```

**Expected Output**:
```
Decision: APPROVE
Confidence: 0.99
Warnings: [...author_picture..., ...coverImage...]
```

- [ ] Decision is still APPROVE
- [ ] Confidence is 0.99 (defaults applied)
- [ ] Warnings logged for missing author_picture and coverImage

---

## Test Group 2: Validation - Rejection Cases

### Test 2.1: Empty Title
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(
    title='',
    excerpt='Valid excerpt.',
    content='x' * 100
)
result = skill._validate_input(post)
print(f'Decision: {result.decision}')
print(f'Errors: {result.errors}')
"
```

**Expected Output**:
```
Decision: REJECT
Errors: ['title is required...']
```

- [ ] Rejected (REJECT decision)
- [ ] Error message mentions title

### Test 2.2: Content Too Short
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(
    title='Valid Title',
    excerpt='Valid excerpt.',
    content='Short'
)
result = skill._validate_input(post)
print(f'Decision: {result.decision}')
print(f'Errors: {result.errors}')
"
```

- [ ] Rejected (REJECT decision)
- [ ] Error mentions content length requirement

### Test 2.3: Secrets Detected
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)
post = BlogPost(
    title='API Guide',
    excerpt='How to use the API securely.',
    content='API_KEY=secret123abc\n' + 'x' * 100
)
result = skill._validate_input(post)
print(f'Decision: {result.decision}')
print(f'Has secret errors: {any(\"secret\" in e.lower() for e in result.errors)}')
"
```

- [ ] Rejected (REJECT decision)
- [ ] Error mentions secret/credentials

---

## Test Group 3: Formatting

### Test 3.1: Slug Generation
```powershell
py -c "
from src.skills.blog_publisher import BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

test_cases = [
    ('REST API Best Practices! Q&A Edition (2026)', 'rest-api-best-practices-qa-edition-2026'),
    ('Simple Title', 'simple-title'),
    ('Title---with---dashes', 'title-with-dashes'),
]

for title, expected in test_cases:
    slug = skill._generate_slug(title)
    status = '✓' if slug == expected else '✗'
    print(f'{status} {title!r} → {slug!r} (expected {expected!r})')
"
```

**Expected Output**: All check marks (✓)

- [ ] All slugs generated correctly
- [ ] Special characters removed
- [ ] Dashes normalized

### Test 3.2: Frontmatter YAML
```powershell
py -c "
import yaml
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

post = BlogPost(
    title='YAML Test',
    excerpt='Testing YAML frontmatter generation.',
    content='x' * 100,
    author_name='Test Author',
    author_picture='/assets/test.jpg',
    coverImage='/assets/cover.jpg'
)

formatted, filename = skill._format_post(post)
yaml_block = formatted.split('---')[1]
parsed = yaml.safe_load(yaml_block)

print(f'Title: {parsed.get(\"title\")}')
print(f'Author: {parsed.get(\"author\", {})}')
print(f'Has coverImage: {\"coverImage\" in parsed}')
print(f'Has date: {\"date\" in parsed}')
"
```

**Expected Output**:
```
Title: YAML Test
Author: {'name': 'Test Author', 'picture': '/assets/test.jpg'}
Has coverImage: True
Has date: True
```

- [ ] YAML parses without errors
- [ ] All fields present in frontmatter
- [ ] Author is an object with name and picture

### Test 3.3: Filename Generation
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
from datetime import datetime
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

# Test with custom date
post1 = BlogPost(
    title='Historical Post',
    excerpt='Valid excerpt.',
    content='x' * 100,
    date='2026-01-09T10:00:00.000Z'
)
formatted1, filename1 = skill._format_post(post1)
print(f'Custom date: {filename1}')
print(f'Starts with 2026-01-09: {filename1.startswith(\"2026-01-09\")}')

# Test without date (should use today)
post2 = BlogPost(
    title='Today Post',
    excerpt='Valid excerpt.',
    content='x' * 100
)
formatted2, filename2 = skill._format_post(post2)
today = datetime.utcnow().strftime('%Y-%m-%d')
print(f'Today date: {filename2}')
print(f'Starts with today: {filename2.startswith(today)}')
"
```

- [ ] Custom date used when provided
- [ ] Today's date used when empty
- [ ] Filename includes slug from title

---

## Test Group 4: URL Generation

### Test 4.1: Live URL Creation
```powershell
py -c "
from src.skills.blog_publisher import BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

filenames = [
    '2026-02-09-orchestrator-architecture.md',
    '2026-02-09-rest-api-best-practices.md',
]

for filename in filenames:
    url = skill._generate_live_url(filename)
    print(f'URL: {url}')
    print(f'  Contains vercel domain: {\"roadtrip-blog-ten.vercel.app\" in url}')
"
```

**Expected Output**:
```
URL: https://roadtrip-blog-ten.vercel.app/blog/orchestrator-architecture
  Contains vercel domain: True
URL: https://roadtrip-blog-ten.vercel.app/blog/rest-api-best-practices
  Contains vercel domain: True
```

- [ ] URL includes correct vercel domain
- [ ] URL includes /blog/ path
- [ ] URL includes slug from filename

---

## Test Group 5: Determinism Check

### Test 5.1: Same Input → Same Output
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

post = BlogPost(
    title='Determinism Test',
    excerpt='Testing that same input produces same output.',
    content='x' * 100
)

results = []
for i in range(3):
    result = skill._validate_input(post)
    results.append((result.decision, result.confidence, len(result.errors)))

print(f'All decisions same: {all(r[0] == results[0][0] for r in results)}')
print(f'All confidences same: {all(r[1] == results[0][1] for r in results)}')
print(f'All error counts same: {all(r[2] == results[0][2] for r in results)}')
"
```

**Expected Output**:
```
All decisions same: True
All confidences same: True
All error counts same: True
```

- [ ] All three runs produce identical results
- [ ] No variation based on time or order

---

## Test Group 6: End-to-End (Dry-Run, Without Git Push)

### Test 6.1: Full Pipeline (Validation + Formatting)
```powershell
py -c "
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

post = BlogPost(
    title='Full Pipeline Test',
    excerpt='Testing the complete pipeline without git push.',
    content='# Full Pipeline\n\nThis tests validation and formatting together.\n\n' + 'x' * 200,
    author_name='Nicholas Stein',
    author_picture='/assets/blog/authors/ns.jpg'
)

# Phase 1: Validate
val_result = skill._validate_input(post)
print(f'✓ Phase 1 Validation: {val_result.decision} (confidence {val_result.confidence})')

if val_result.decision == 'APPROVE':
    # Phase 2: Format
    formatted, filename = skill._format_post(post)
    print(f'✓ Phase 2 Format: {filename}')
    print(f'  Content length: {len(formatted)} bytes')
    print(f'  Has YAML frontmatter: {formatted.startswith(\"---\")}')
else:
    print('✗ Validation failed, skipping format phase')
"
```

**Expected Output**:
```
✓ Phase 1 Validation: APPROVE (confidence 1.0)
✓ Phase 2 Format: 2026-02-09-full-pipeline-test.md
  Content length: ... bytes
  Has YAML frontmatter: True
```

- [ ] Validation passes
- [ ] Formatting produces valid filename
- [ ] YAML frontmatter is present
- [ ] Content length is reasonable

---

## Test Group 7: Compare Prototype vs Implementation

After Phase 2 manual prototype, we published 2 posts:
1. `2026-02-09-orchestrator-architecture-proven.md`
2. `2026-02-09-skill-development-methodology.md`

### Test 7.1: Verify Implementation Matches Prototype Output

```powershell
# Read one of the published posts from blog repo
Get-Content G:\repos\AI\roadtrip-blog-repo\_posts\2026-02-09-orchestrator-architecture-proven.md -Head 20
```

**Expected**: YAML frontmatter with:
```yaml
---
title: "Orchestrator Architecture Proven"
excerpt: "..."
coverImage: "/assets/blog/..."
date: 2026-02-09T...
author:
  name: "..."
  picture: "/assets/..."
ogImage:
  url: "..."
---
```

Now verify our implementation generates the same structure:

```powershell
py -c "
import yaml
from src.skills.blog_publisher import BlogPost, BlogPublisherSkill, load_config
config = load_config('config/blog-config.yaml')
skill = BlogPublisherSkill(config)

# Reconstruct a similar post
post = BlogPost(
    title='Orchestrator Architecture Proven',
    excerpt='We have successfully demonstrated that the RoadTrip orchestrator...',
    content='# Orchestrator Architecture Proven\n\n...' + 'x' * 200,
    author_name='Nicholas Stein',
    author_picture='/assets/blog/authors/ns.jpg',
    coverImage='/assets/blog/orchestrator/cover.jpg'
)

formatted, filename = skill._format_post(post)
yaml_block = formatted.split('---')[1]
parsed = yaml.safe_load(yaml_block)

print('Frontmatter Structure:')
print(f'  title: {parsed[\"title\"]}')
print(f'  excerpt: {parsed[\"excerpt\"][:50]}...')
print(f'  author (object): {\"name\" in parsed.get(\"author\", {})}')
print(f'  coverImage: {\"coverImage\" in parsed}')
print(f'  ogImage: {\"ogImage\" in parsed}')
print(f'  date (ISO): {\"T\" in str(parsed[\"date\"]) and \"Z\" in str(parsed[\"date\"])}')
"
```

- [ ] Implementation frontmatter matches prototype structure
- [ ] Author is an object (not string)
- [ ] Excerpt is separate field
- [ ] CoverImage and ogImage present
- [ ] Date is ISO 8601 with milliseconds

---

## Test Summary

After completing all tests above, record results:

- [ ] Test Group 1 (Happy Path): __ / 2 passed
- [ ] Test Group 2 (Rejections): __ / 3 passed
- [ ] Test Group 3 (Formatting): __ / 3 passed
- [ ] Test Group 4 (URL Generation): __ / 1 passed
- [ ] Test Group 5 (Determinism): __ / 1 passed
- [ ] Test Group 6 (End-to-End): __ / 1 passed
- [ ] Test Group 7 (vs Prototype): __ / 1 passed

**Total**: __ / 12 test groups

---

## Next Steps After Manual Testing

Once manual tests pass:

1. Run pytest suite:
   ```powershell
   pytest tests/test_blog_publisher.py -v
   ```

2. Check coverage:
   ```powershell
   pytest tests/test_blog_publisher.py --cov=src.skills.blog_publisher
   ```

3. If all pass: Commit Phase 4 completion and proceed to Phase 5 (CLI integration)

---

## Troubleshooting

**Import Error**: 
```
ModuleNotFoundError: No module named 'src'
```
→ Run from RoadTrip root: `cd G:\repos\AI\RoadTrip`

**Config Error**:
```
FileNotFoundError: config/blog-config.yaml
```
→ Check config file exists at `G:\repos\AI\RoadTrip\config\blog-config.yaml`

**YAML Error**:
```
ModuleNotFoundError: No module named 'yaml'
```
→ Install: `pip install pyyaml`

---

**Phase 4 Testing Document**  
**Status**: Ready for execution  
**Created**: 2026-02-09
