# Roofus — Session Handoff (energy plan work)

**Date:** 2026-06-16 · **Branch:** `viviana-work` · Written from a second laptop to bring the full-stack laptop up to speed.

---

## What Roofus is
A tool that scores Hapeville commercial rooftops (mostly apartment complexes) for **rooftop greenhouses**, and shows the financial + grid-services case to building owners. Real data in `pipeline/data/processed/scored_buildings.geojson` (66 buildings).

## What this session was about
We pressure-tested the **energy / "energy plan"** part of the pitch and made it honest. The big realization: **apartment-complex owners are already on Georgia Power commercial *demand* rates** (PLS/PLM/PLL), not a flat residential rate. That's a *strength* — demand charges make peak reduction valuable.

---

## Key facts established (use these in the pitch)

**Real GA Power bill** — ran Georgia Power's own commercial bill calculator for building **301 North Central Ave** (192-unit complex, Apsilon Mgmt):
- Inputs: Inside City Limits, Commercial, Summer, **Billing Demand 338 kW**, **Monthly Usage 33,308 kWh**, 7% tax
- **Result: $7,025.01/month** (~$75k/yr whole property)
- Inputs map to pipeline fields: Billing Demand = `estimated_peak_kw`; Monthly Usage = `der_annual_mwh` × 1000 ÷ 12

**Three energy revenue streams (keep them labeled SEPARATELY — do not conflate):**

| Stream | What it is | Value (bldg 301) | Capex |
|---|---|---|---|
| **CL-1** (the core) | Curtailable Load = get paid to *use less* on peak (AC cycling + greenhouse lighting/pumps), aggregated across buildings to clear 200 kW / 1 MW | shown in Subsidies tab | ~zero |
| **DCO-1** | Distributed Capacity = install **solar + battery** and get paid to *supply more*; 75% of system value | ~$18,713/yr (`der_credit_est_annual`) | large |
| Passive green-roof savings | ~3% of the electric bill (roof cools top floor only) | ~$2,173/yr ($0.05/sq ft) | n/a |

**CL-1 vs DCO-1 in one line:** CL-1 = use less when asked (reduce demand). DCO-1 = generate more (add supply).

---

## Code changes made this session (need commit)
- `backend/services/revenue_service.py` — `calculate_owner_revenue` default `energy_savings_per_sqft` **0.45 → 0.05** (old value implied saving ~25% of the whole bill — indefensible). Added comment citing the $7,025 bill + 3% basis (EPA/GSA green-roof studies).
- `docs/revenue_calculator_spec.md` — relabeled the energy line to "Commercial demand-rate savings (GA Power PLM)" and replaced the flat-rate guess with the real calculator run + tenant-benefit note.
- `HANDOFF.md` — this file.

> Note: the passive savings number is NOT shown in the current UI — `calculate_owner_revenue` isn't called by the frontend. The Profitability tab shows the *greenhouse developer* P&L (`calculate_developer_revenue`).

## Where things live in the UI (`frontend/index.html`)
- **DCO-1 section** — `derSection()`, shown prominently in the detail panel above the tabs ("☀️ Rooftop Power Plant — Georgia Power DCO-1", shows the $18,713 credit).
- **CL-1 demand response** — inside the **Subsidies tab** (`loadTab`, "Demand Response — Georgia Power CL-1") — currently one tab deep / a bit buried.
- **Cluster panel** (`renderCluster`) — aggregates `curtailable_kw` across selected buildings toward the CL-1 200 kW threshold.
- Map has two views: `score` and `der` ("Power-Plant View").

---

## OPEN DECISION (not yet done) — DCO-1 vs CL-1 focus
The project's heart is **CL-1** (greenhouse-as-flexible-load — novel, near-zero capex, no roof conflict). **DCO-1 requires solar panels, which compete with the greenhouse for the same roof space** → invites the judge question *"is this roof a greenhouse or a solar farm?"*

**Recommendation:** lead with CL-1; demote DCO-1 to a single optional line (*"roofs with spare area can also host solar — separate play"*). Alternative: cut DCO-1 entirely for a sharper thesis, or keep both as-is. **No code changed for this yet — awaiting decision.**

## Suggested next steps on the full-stack laptop
1. `git pull` this branch to get the edits + this file.
2. Decide the DCO-1 question above.
3. If demoting DCO-1: shrink `derSection()` and consider pulling the CL-1 demand-response block out of the Subsidies tab to sit alongside it.
4. Sanity-check the revenue endpoints still run with the new `$0.05` default.
