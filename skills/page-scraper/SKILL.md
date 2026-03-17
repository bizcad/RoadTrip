---
name: page-scraper
description: Scrapes a web page to markdown using RoadTrip MCP helpers. Supports URL input and clipboard URL workflows. Writes output to docs/ with provenance frontmatter.
license: Internal use. RoadTrip project.
metadata:
  version: "1.0.0"
  tags:
    - scrape
    - web
    - markdown
    - mcp
    - docs
  examples:
    - "I want to scrape a page"
    - "I want to scrape a page from the clipboard"
    - "scrape this url to markdown"
    - "convert this web page to markdown"
    - "save this page as markdown"
  entry_point: infra/invoke-page-scrape.ps1
  runtime: powershell
  trust_level: verified
  # Update fingerprint: py src/skills/skill_scanner.py stamp
  fingerprint: "9103346584bcd286"
---

# Page Scraper Skill

## Trigger Phrases

- I want to scrape a page
- I want to scrape a page from the clipboard

## Inputs

- `source_url` (required unless clipboard mode)
- `destination_path` (optional; blank auto-generates in `./docs`)
- `prefer_raw_markdown` (default: true)
- `localize_images` (default: true)
- `from_clipboard` (default: false)

## Execution Paths

### Prompt Builder Path

Use when user wants to generate a well-formed prompt:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1
```

Clipboard mode:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1 -FromClipboard -CopyToClipboard
```

### Direct Scrape Path

Use when user wants the scrape executed immediately:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1
```

Clipboard mode:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1 -FromClipboard
```

## Interaction Sequence

Ask in this order when values are missing:

1. Source URL (or use clipboard if requested)
2. Destination markdown path
3. Prefer raw markdown endpoint?
4. Localize images?

If destination is blank:
- derive filename from `<h1>` or `<title>` (fallback to URL slug)
- place file under `./docs`

## Output Guarantees

- Markdown file is written to destination
- Frontmatter records scrape provenance:
  - `scrape_method`
  - `raw_markdown_url`
  - `prefer_raw_markdown`
  - `polished`
  - `localized_images`

## Notes

- This repository is Windows-first; use `py` and `pwsh` commands.
- Use `docs/Page_Scraper_Prompt_Template.md` for user-facing instructions.
