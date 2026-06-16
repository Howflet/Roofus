# GES greenhouse under real Atlanta summer — the cooling question

This folder answers a key question for the project:

> In an Atlanta summer, can a greenhouse stay cool by just opening its vents,
> or does it overheat and need **active cooling** (an electric load that could
> do demand response)?

We use **GES** (Greenhouse Energy Simulation, Cambridge EECi) — a Python physics
model of the greenhouse heat balance — driven by **real Atlanta July weather**
(Open-Meteo). GES models ventilation explicitly, so it can tell us whether
venting is enough.

## What it found

| | Value |
|---|---|
| Peak indoor temp (vented, no AC) | **~37 °C** |
| Atlanta outdoor peak | ~35 °C |
| Time above the 28 °C crop-safe limit | **~37%** |
| Estimated peak electric cooling load | ~210 W/m² floor |
| When the cooling load peaks | **~2 pm (afternoon)** |

**Answer: venting is NOT enough.** The greenhouse tracks the hot outdoor air and
spends about a third of the time above a crop-safe temperature. It needs
**active cooling** — and crucially, that cooling load **peaks in the afternoon,
right when the summer power grid peaks.**

## Why this matters for the pitch

This is the key insight for the summer demand-response case:

- A greenhouse that *only* vents would use ~zero summer electricity — but GES
  shows that in Atlanta you **can't** just vent: it overheats.
- So the greenhouse needs **active cooling**, and that cooling load **lines up
  with the grid peak** (afternoon) — which is exactly the flexible load demand
  response pays for.

So the summer demand-response story is back on the table, but now honestly:
**it depends on the greenhouse running active cooling**, which GES shows is
genuinely necessary in Georgia. The afternoon cooling load is exactly the
flexible, sheddable load that demand-response programs pay for.

## Honest caveats (say these)

- **GES is a single-zone tomato greenhouse** that vents at 25 °C — not a custom
  Georgia leafy-greens rooftop. We changed the weather, not the greenhouse.
- **Solar is approximated**: real global sunlight split onto the model's 8
  surfaces (beam mostly on roofs, diffuse on all) — not full solar geometry.
- **The cooling number is a simple add-on**: GES itself has no AC. We estimate
  the electric cooling load as (sunlight through the cover) ÷ a cooling
  efficiency (COP 3.5). A real greenhouse using **evaporative cooling** would use
  *less* electricity than this AC-style estimate — so 210 W/m² is an upper-ish,
  conservative figure.
- One 2-week July window, one location.

## Run it

```
python run_ges_atlanta.py
```
Needs the GES code at `C:/Users/Vacav/Downloads/GES/python` (cloned from
https://github.com/EECi/GES) and `atlanta_july_weather.csv` in this folder.

## Sources
- GES — Greenhouse Energy Simulation, Cambridge EECi: https://github.com/EECi/GES
- Based on the GDGCM (Pieters & Deltour 2000) and Vanthoor (2011) greenhouse models.
- Weather: Open-Meteo historical API (Hapeville/Atlanta, July 2024).
