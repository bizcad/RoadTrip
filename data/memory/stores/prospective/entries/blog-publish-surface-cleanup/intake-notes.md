# Intake Notes — Blog Publish Surface Cleanup (Deferred)

## Status
- Classification: **deferred cleanup**
- Priority: **medium**
- Action timing: **later (not now)**

## Problem Statement
There are many blog-related `.ps1`, `.py`, and `.md` files in RoadTrip from older publishing paths (including Next.js-era logic). This increases cognitive overhead and makes it harder to maintain a simple static publish workflow.

## Current Decision
Do **not** clean this up now. Preserve momentum on the new static-site workflow.

## Future Objective
When scheduled, identify and classify blog-publish files into:
1. active path,
2. legacy-but-keep,
3. archive/remove candidates.

## Desired Outcome
A minimal publishing surface aligned to:
- Markdown source of truth,
- Python static generation,
- git push -> Vercel auto-deploy.

## Exit Criteria (for future execution)
- Inventory complete with keep/remove rationale.
- Legacy files marked clearly as deprecated or moved to archive.
- One clear runbook path remains for blog publishing.
