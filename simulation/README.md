# Greenhouse-Network Simulation (rough, illustrative)

This folder answers one question for the team:

> "Instead of just *citing* a research paper, can we **show** roughly what a
> coordinated greenhouse-energy network would look like for one of our clusters?"

It is a **rough, one-day, back-of-the-envelope estimate** — not an engineering
model. We do **not** know the exact greenhouse design, the real rooftop layout,
or the zoning. The point is to make the idea *visible* and *plausible*, with
every assumption labelled, so we don't overstate it.

## What it does

For our **biggest cluster (GRID-016** — 7 buildings, 792 units), it simulates a
single hot **summer day** in Hapeville, GA and compares:

- **No coordination** — the buildings + greenhouse just use solar as it comes.
- **Coordinated network** — a battery stores midday solar and discharges it into
  the evening grid peak, and the greenhouse defers some flexible load during the
  peak (demand response).

Output: a chart (`network_day_simulation.png`) + printed headline numbers.

## Headline result (illustrative)

| | Value |
|---|---|
| Evening peak grid demand, no coordination | ~1,670 kW |
| Evening peak grid demand, coordinated | ~1,460 kW |
| **Peak demand cut** | **~12% (~200 kW)** |
| Peak-window grid energy cut | ~26% |

For reference, the Cornell study (Applied Energy 2024) reports up to **28%**
net-load reduction using a full AI controller. Our simpler rule-based estimate
landing a bit *under* that is the expected, honest direction.

## What's real vs. assumed (important)

| Input | Source | Label |
|---|---|---|
| Cluster size, roof area, building load | Our real Fulton County pipeline | **Real (est.)** |
| Solar capacity | Derived from real roof area | **Real-derived** |
| Hourly sunlight | Open-Meteo, live (real July day) | **Real** |
| Greenhouse lighting intensity | Published research (see below) | **Literature-based** |
| Greenhouse **cooling** load | Grounded in our GES physics run (`ges/`): driven by real sunlight, peaks afternoon | **Model-grounded** |
| Daily load *shape* (hour to hour) | Typical profile | **Assumption** |
| Battery duration, dispatch rule, DR window | Engineering judgement | **Assumption** |
| Greenhouse uses 50% of roof | Round number | **Assumption** |

Everything is a tunable constant at the top of `simulate_network.py` — change a
number, re-run, see what happens.

## Known limitations (say these out loud)

- One representative summer day, not a full year.
- Summer was chosen on purpose: greenhouse **cooling** peaks in the afternoon and
  lines up with the **grid peak** — good for demand response. A winter day would
  look different (more lighting, less cooling).
- The greenhouse load is built from cited *intensities*, not a physics model of an
  actual greenhouse. A rigorous version would use a building-energy or greenhouse
  model (e.g. EnergyPlus, or the open-source Modelica Greenhouses Library).
- Simple rule-based battery/DR control, not the AI optimisation in the literature.

## Sources

- Ajagekar, Decardi-Nelson & You (2024). *Energy management for demand response in
  networked greenhouses with multi-agent deep reinforcement learning.* Applied
  Energy 355, 122349. https://doi.org/10.1016/j.apenergy.2023.122349
- Harbick & Albright (2016). *Comparison of energy consumption: greenhouses and
  plant factories* (modeled Atlanta climate). https://www.ishs.org/ishs-article/1134_38
- DOE, *Energy Savings Potential of SSL in Agricultural Applications* (2020).
- DOE Better Buildings, *CHP Market Sector: Greenhouses* fact sheet.
- Open-Meteo Historical Weather API (solar irradiance).

## Run it

```
python simulation/simulate_network.py
```
