
# Road Trip – POC Workspace

- A proof of concept for planning and tracking a road trip using Google Sheets and My Maps. 
1. Start with a google maps and add a starting location and destination to visualize the route.
2. Describe your car and fuel assumptions.
3. Let AI Plan the route and stops based on your preferences.
4. It will generate a CSV for Google Sheets and a CSV for Google My Maps, and compute your gasoline cost.
5. As you proceed, it will check for weather risks and update the plan accordingly.
6. As you proceed, you can update the Sheet and My Maps will be updated automagically with new information.
7. Review the plan and make adjustments as needed.

## Files in this drop
- `RoadTrip_TripPlan_SheetsTemplate.csv` – master plan for Google Sheets
- `RoadTrip_MyMaps_Import.csv` – quick import to Google My Maps
- `RoadTrip_WeatherRisk_Playbook.md` – conservative risk rules

## Quick Start
1. Create a **Google Sheet** named `RoadTrip TripPlan`.
2. Import `RoadTrip_TripPlan_SheetsTemplate.csv` into the first tab.
3. Create a **Google My Maps** map named `Road Trip` with layers: Fuel, Sleep, Risk.
4. Import `RoadTrip_MyMaps_Import.csv` into each layer (filter by `Kind`).
5. Open on iPhone/iPad; tap pins for addresses and notes. Update the Sheet as plans change.

## (Optional) Apps Script “Refresh Pins”
- Add a Sheets **Apps Script** that exports the active rows (by `Status`) to a Drive CSV/KML and re‑imports to My Maps.

## Cost Guardrails (when we automate)
- Use local timers/heartbeats (no LLM) and **escalate** only for summaries.
- Route “dumb work” to a local or cheap model; escalate to larger models only on blockers.
- Cap daily token & HTTP budgets; fail closed.

## Aspire/Entra Next
- `Agent.Orchestrator` (policy‑bounded planner)
- `Agent.Skills.Sheets`, `Agent.Skills.Maps`, `Agent.Skills.Weather`
- Secrets: UserSecrets (dev) → Key Vault (prod)
- Allow‑list outbound: Sheets, Maps, Weather only; no email, no purchasing.

## Workspace convenience

- This workspace adds a `RoadTrip PowerShell` integrated terminal profile that automatically runs `infra\RoadTrip_profile.ps1` when a new terminal is opened. It sets project defaults (paths, environment variables, helpers). If you prefer not to run the script automatically, open the terminal dropdown and choose a different profile.
