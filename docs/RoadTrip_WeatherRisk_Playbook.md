
# Road Trip – Weather Risk Playbook (Conservative)

**Goal:** Turn a few “battle‑proven” weather readings into simple, binary decisions and clear fallback stops.

## Inputs (read‑only)
- NWS grid forecasts / hourly temp & precip (or any trusted app)
- Sustained wind + gusts along segments (I‑17, I‑40, US‑54/US‑50)
- Wet‑bulb proxy: temp near 32°F + precip = freezing risk

## Rules
1) **I‑17 (Black Canyon → Cordes Lakes)**  
   - If **T ≤ 32°F** or **freezing rain** within 3 hrs → *Delay departure*, fuel at Cordes Lakes if < 1/2 tank.
2) **I‑40 (Holbrook → Tucumcari, ~406 mi)**  
   - If **wind ≥ 20 mph** from **N/W** *and* road is wet or sub‑freezing overnight → *Avoid night driving*; stop Holbrook/Tucumcari.
3) **US‑54/US‑50 (TX Panhandle / KS)**  
   - If **cross‑winds ≥ 25 mph** or blowing snow → *Fuel early at Liberal*, reduce cruise, avoid passing in gusts.

## Actions
- Create a “Risk” pin with the **rule that fired**, the **next safe stop**, and a **one‑line plan** (Delay, Detour, or Overnight).
- Log the decision to the Sheet (Status = `Planned` → `Done`).

## Notes
- **Conservative policy** favors earlier stops to eliminate compounding risk at night.  
- This is a **deterministic layer** on top of your route; the LLM can draft friendly summaries but cannot change the rules.
