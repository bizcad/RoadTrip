# Page Scraper Prompt Template

Use this when you want Copilot to run the page-scraper MCP against a web page and save it into RoadTrip.

## Best Place To Keep The Reminder

This file is the durable reminder. It belongs in [docs/Page_Scraper_Prompt_Template.md](docs/Page_Scraper_Prompt_Template.md) so it is easy to find from the repo and easy to reference in future chats.

## Recommended Prompt

```text
Use the page scraper MCP to scrape this page into this file.

Source URL: https://example.com/article
Destination path: G:\repos\AI\RoadTrip\docs\Self-Improvement\Part_14_-_Example.md
Prefer raw markdown endpoint if available: yes
Localize images: yes
Do the cleanup/polish pass: yes
Record scrape metadata in frontmatter: yes
```

## Fast Helper Script

Generate the prompt interactively:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1
```

Generate the prompt and copy it to the clipboard:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1 -CopyToClipboard
```

Clipboard-first prompt generation:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1 -FromClipboard -CopyToClipboard
```

Generate the prompt non-interactively:

```powershell
pwsh -File .\infra\new-page-scrape-prompt.ps1 `
  -SourceUrl "https://example.com/article" `
  -DestinationPath "G:\repos\AI\RoadTrip\docs\Self-Improvement\Part_14_-_Example.md" `
  -PreferRaw $true `
  -LocalizeImages $true
```

If you leave destination blank, the script fetches the page, derives a title from `<h1>` or `<title>`, and auto-generates a markdown filename under `./docs`.

## Direct Scrape (No Prompt Roundtrip)

Run the actual scrape interactively:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1
```

Run scrape from clipboard URL:

```powershell
pwsh -File .\infra\invoke-page-scrape.ps1 -FromClipboard
```

If destination is blank, it auto-generates a file under `./docs`.

When the profile is loaded, aliases are available:

- `scrape-prompt`
- `scrape-page`
- `scrape-prompt-clipboard`
- `scrape-page-clipboard`

## Chat Shortcut

You can also just say:

```text
I want to scrape a page.
```

Then provide or let Copilot ask for:

- source URL
- destination path, or leave it blank so the helper generates one under `./docs`
- whether to prefer raw markdown
- whether to localize images

Clipboard-first chat trigger:

```text
I want to scrape a page from the clipboard.
```

## Frontmatter Metadata Added By The Scraper

Future scrapes now record:

- `scrape_method`
- `raw_markdown_url`
- `polished`
- `localized_images`
