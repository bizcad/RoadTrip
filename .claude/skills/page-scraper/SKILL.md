---
name: page-scraper
version: specs-v1.0
description: Route page-scrape intents to RoadTrip prompt helper or direct runner. Supports normal URL mode and clipboard URL mode.
---

# Claude Skill: Page Scraper

## Detect Intent

Match phrases like:
- "I want to scrape a page"
- "I want to scrape a page from the clipboard"

## Execute

For prompt generation:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1
```

Clipboard prompt generation:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1 -FromClipboard -CopyToClipboard
```

For immediate scraping:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1
```

Clipboard immediate scrape:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1 -FromClipboard
```

## Required Question Order

1. source URL (unless clipboard mode)
2. destination path (allow blank)
3. prefer raw markdown
4. localize images

If destination is blank, auto-generate in `./docs`.
