# Memory Stores (Folder-Native)

This directory is the canonical, machine-processable memory layout.

## Core idea
- Each memory store is a folder under `stores/`.
- Each memory entry is a folder under `<store>/entries/<entry_id>/`.
- Memory stores are classifications, not a hierarchy.
- Reclassification/expiration is implemented as a folder move between store paths.

## Stores
- `prospective`: pending reminders, future tasks, handoffs to be done.
- `working`: active in-session state and near-term scratchpad.
- `episodic`: session events and outcomes (time-ordered records).
- `semantic`: distilled facts and relationships.
- `long_term`: durable high-confidence patterns and rules.

## Lifecycle operations
- Reclassify: move entry folder to another memory class per policy.
- Expire: move entry folder to an expiration target or remove per policy.
- Quarantine: move entry folder to a quarantine area (optional future store).

Example (PowerShell):

```powershell
Move-Item `
  "data/memory/stores/prospective/entries/reminder-auth-rotation" `
  "data/memory/stores/working/entries/"
```

## Metadata
- Root metadata: `manifest.yaml`
- Schema metadata: `schema/memory-manifest.schema.yaml`
- Per-store metadata: `<store>/store.yaml`

The YAML format is intentionally JSON-compatible for direct conversion when model pipelines require JSON.
