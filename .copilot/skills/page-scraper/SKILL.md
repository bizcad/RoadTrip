---
name: page-scraper
version: specs-v1.0
description: Handle RoadTrip page scrape intent using interactive PowerShell helpers. Supports clipboard-first URL capture.
---

# Copilot Skill: Page Scraper

## Trigger Phrases

- I want to scrape a page
- I want to scrape a page from the clipboard

## Actions

Prompt helper:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1
```

Prompt helper from clipboard:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1 -FromClipboard -CopyToClipboard
```

Direct scrape:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1
```

Direct scrape from clipboard:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1 -FromClipboard
```

## Question Order

1. source URL (unless clipboard mode)
2. destination path (blank = auto-generate under `./docs`)
3. prefer raw markdown endpoint
4. localize images
