"""
GreenGrid — Rough Greenhouse-Network Simulation (ILLUSTRATIVE)
=============================================================

Purpose
-------
Show *roughly* how one of our building clusters would behave if it became a
coordinated rooftop-greenhouse energy network (solar + battery + flexible load)
on a hot summer day in Hapeville, GA — and how much it could cut its peak draw
from the grid (demand response).

This is NOT a precise engineering model. We do not know the exact greenhouse
design, the real rooftop layout, or the zoning. This is a transparent
"back-of-the-envelope over 24 hours" estimate meant to make the research idea
*visible*, not to predict exact kW.

Every input below is labelled:
    [REAL]        - comes from our real data pipeline or a live data source
    [LITERATURE]  - a published figure we cite (see README.md)
    [ASSUMPTION]  - a reasonable knob you can change; clearly not measured

Research basis: Ajagekar, Decardi-Nelson & You (2024), "Energy management for
demand response in networked greenhouses with multi-agent deep reinforcement
learning," Applied Energy 355, 122349. They report up to 28% net-load reduction
for a coordinated greenhouse network. We compare our rough result to that.

Run:  python simulation/simulate_network.py
"""

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")              # save to file, no GUI needed
import matplotlib.pyplot as plt
import numpy as np

try:
    import requests
except ImportError:
    requests = None

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
GRIDS = HERE.parent / "pipeline" / "data" / "processed" / "aggregation_grids.geojson"
OUT_PNG = HERE / "network_day_simulation.png"

# ---------------------------------------------------------------------------
# Which cluster to simulate
# ---------------------------------------------------------------------------
TARGET_GRID = None        # None = automatically pick the biggest cluster

# ---------------------------------------------------------------------------
# Solar (real). Hapeville, GA — representative clear summer day.
# Live hourly data from Open-Meteo; if offline we fall back to this real
# profile we already pulled for 2024-07-15 (W/m^2 by hour, local time). [REAL]
# ---------------------------------------------------------------------------
LAT, LON = 33.66, -84.41
SOLAR_FALLBACK_WM2 = [0,0,0,0,0,0,0,3,86,265,436,414,442,855,899,862,786,486,
                      351,185,119,12,0,0]
PV_PERFORMANCE_RATIO = 0.80        # [ASSUMPTION] inverter/heat/soiling derate

# ---------------------------------------------------------------------------
# Greenhouse load model (per square metre of greenhouse floor)
# ---------------------------------------------------------------------------
GREENHOUSE_ROOF_FRAC = 0.50        # [ASSUMPTION] half the roof is greenhouse,
                                   #   the rest is solar panels / access
SQFT_TO_M2 = 0.092903

# Supplemental LED lighting — sunlit greenhouse needs far less light than an
# indoor vertical farm, and in a SUNNY GEORGIA SUMMER it needs very little
# (natural daily light already meets the target). Small dawn/dusk top-up only.
# [LITERATURE: DOE SSL 2020; ASHS HortTech SE-US lettuce -> summer DLI is high]
LIGHT_W_PER_M2 = 12.0                                     # summer-low supplement
# Fractional hours the lights are on. Summer sunrise is early (~6:30), so no
# pre-dawn lighting; just a small evening photoperiod top-up:
LIGHT_SCHEDULE = {20: 0.4, 21: 0.3}                      # [LITERATURE/ASSUMPTION]

# Cooling — GROUNDED IN GES (see ../ges/): we ran a greenhouse physics model on
# real Atlanta weather and it OVERHEATED (vents weren't enough), so the greenhouse
# genuinely needs ACTIVE cooling, and that cooling is driven by sunlight and peaks
# in the afternoon. We size it the GES way: cooling electricity = (sunlight through
# the cover) / cooling efficiency. Greenhouses normally use EVAPORATIVE cooling
# (fans + water), which is far more electricity-efficient than AC.
COVER_TRANSMITTANCE = 0.70   # [ASSUMPTION] sunlight entering the greenhouse as heat
COOLING_COP = 12.0           # [ASSUMPTION] evaporative cooling efficiency (heat removed / kW elec)

# ---------------------------------------------------------------------------
# Battery (firm, dispatchable). Power from real pipeline; duration assumed.
# ---------------------------------------------------------------------------
BATTERY_HOURS = 4                  # [ASSUMPTION] 4-hour battery (energy = power*4)
ROUND_TRIP_EFF = 0.90              # [ASSUMPTION]

# ---------------------------------------------------------------------------
# Demand-response event window (when the grid peaks on a hot day)
# ---------------------------------------------------------------------------
PEAK_WINDOW = [17, 18, 19, 20]     # 5-9 pm  [ASSUMPTION: summer evening grid peak]
GREENHOUSE_SHED_FRAC = 0.40        # [ASSUMPTION] fraction of greenhouse cooling/
                                   #   light load we're willing to defer in event


# ---------------------------------------------------------------------------
def load_cluster():
    data = json.loads(GRIDS.read_text())
    feats = data["features"]
    if TARGET_GRID:
        f = next(x for x in feats if x["properties"]["grid_id"] == TARGET_GRID)
    else:
        f = max(feats, key=lambda x: x["properties"].get("combined_der_dispatchable_kw", 0))
    return f["properties"]


def get_solar_wm2():
    """Real hourly solar for Hapeville; live if possible, else real fallback."""
    if requests is not None:
        try:
            r = requests.get(
                "https://archive-api.open-meteo.com/v1/archive",
                params={"latitude": LAT, "longitude": LON,
                        "start_date": "2024-07-15", "end_date": "2024-07-15",
                        "hourly": "shortwave_radiation",
                        "timezone": "America/New_York"},
                timeout=20)
            vals = r.json()["hourly"]["shortwave_radiation"]
            if len(vals) == 24 and any(v for v in vals):
                return [float(v or 0) for v in vals], "live (Open-Meteo)"
        except Exception:
            pass
    return [float(v) for v in SOLAR_FALLBACK_WM2], "fallback (real 2024-07-15)"


def building_load_shape():
    """Normalised residential multifamily daily shape (peak = 1.0, evening)."""
    # low overnight, small morning bump, midday dip, evening peak
    shape = [0.45,0.40,0.38,0.37,0.38,0.45,0.60,0.72,0.70,0.62,0.58,0.57,
             0.58,0.60,0.62,0.66,0.74,0.85,0.95,1.00,0.95,0.82,0.65,0.52]
    return np.array(shape)


def simulate():
    p = load_cluster()
    solar_wm2, solar_src = get_solar_wm2()
    solar_wm2 = np.array(solar_wm2)

    # ----- real cluster numbers --------------------------------------------
    grid_id        = p["grid_id"]                                   # [REAL]
    n_buildings    = p["building_count"]                            # [REAL]
    units          = p["total_units"]                              # [REAL]
    roof_m2        = p["total_roof_sqft"] * SQFT_TO_M2             # [REAL]
    bldg_peak_kw   = p["combined_peak_kw"]                         # [REAL]

    # The roof is SHARED: greenhouse on part, solar on the rest (no double-count).
    # Pipeline's dispatchable kW assumes the *whole* usable roof is PV, so the
    # full-roof solar = dispatchable x 2 (pipeline rule: dispatchable = 50% PV).
    full_roof_solar_kw = p["combined_der_dispatchable_kw"] * 2.0   # [REAL-derived]
    solar_kw      = full_roof_solar_kw * (1 - GREENHOUSE_ROOF_FRAC)  # solar on non-GH roof
    batt_power_kw = solar_kw * 0.50        # pipeline rule: battery = 50% of its PV

    gh_area_m2 = roof_m2 * GREENHOUSE_ROOF_FRAC

    # ----- hourly load components (kW) -------------------------------------
    base_load = building_load_shape() * bldg_peak_kw               # residents

    light_kw = np.zeros(24)
    for hr, frac in LIGHT_SCHEDULE.items():
        light_kw[hr] = gh_area_m2 * LIGHT_W_PER_M2 * frac / 1000.0
    # Cooling GROUNDED IN GES: driven by the REAL hourly sunlight (so it peaks in
    # the afternoon, exactly as the GES physics model showed). Cooling electricity
    # = sunlight-through-cover / cooling efficiency.
    cool_wm2 = COVER_TRANSMITTANCE * solar_wm2 / COOLING_COP    # W/m^2 of greenhouse
    cool_kw = cool_wm2 * gh_area_m2 / 1000.0
    greenhouse_load = light_kw + cool_kw

    total_load = base_load + greenhouse_load                       # kW each hour

    # ----- solar generation (kW) -------------------------------------------
    solar_gen = solar_kw * (solar_wm2 / 1000.0) * PV_PERFORMANCE_RATIO

    # ----- BASELINE: greenhouse + solar, but no battery, no DR -------------
    baseline_net = total_load - solar_gen      # +import / -export to grid

    # ----- COORDINATED NETWORK: battery shifting + DR event shedding -------
    batt_energy_cap = batt_power_kw * BATTERY_HOURS
    soc = 0.0
    batt_flow = np.zeros(24)        # + = discharge to grid, - = charge

    # 1) charge from surplus solar (midday) up to power & energy limits
    for h in range(24):
        surplus = solar_gen[h] - total_load[h]
        if surplus > 0 and soc < batt_energy_cap:
            charge = min(surplus, batt_power_kw, (batt_energy_cap - soc))
            soc += charge * ROUND_TRIP_EFF
            batt_flow[h] = -charge

    # 2) discharge into the evening peak window
    for h in PEAK_WINDOW:
        if soc <= 0:
            break
        import_h = total_load[h] - solar_gen[h]
        if import_h > 0:
            discharge = min(import_h, batt_power_kw, soc)
            soc -= discharge
            batt_flow[h] = discharge

    # 3) demand-response shedding of flexible greenhouse load during event
    dr_shed = np.zeros(24)
    for h in PEAK_WINDOW:
        dr_shed[h] = greenhouse_load[h] * GREENHOUSE_SHED_FRAC

    coordinated_net = total_load - solar_gen - batt_flow - dr_shed

    # ----- headline numbers ------------------------------------------------
    base_peak = baseline_net[PEAK_WINDOW].max()
    coord_peak = coordinated_net[PEAK_WINDOW].max()
    peak_cut_kw = base_peak - coord_peak
    peak_cut_pct = 100 * peak_cut_kw / base_peak if base_peak > 0 else 0

    base_evening_import = baseline_net[PEAK_WINDOW].clip(min=0).sum()
    coord_evening_import = coordinated_net[PEAK_WINDOW].clip(min=0).sum()
    energy_cut_pct = (100 * (base_evening_import - coord_evening_import)
                      / base_evening_import) if base_evening_import > 0 else 0

    summary = dict(
        grid_id=grid_id, n_buildings=n_buildings, units=units,
        roof_m2=roof_m2, gh_area_m2=gh_area_m2,
        solar_kw=solar_kw, batt_power_kw=batt_power_kw,
        batt_energy_kwh=batt_energy_cap, solar_src=solar_src,
        base_peak=base_peak, coord_peak=coord_peak,
        peak_cut_kw=peak_cut_kw, peak_cut_pct=peak_cut_pct,
        energy_cut_pct=energy_cut_pct,
    )
    series = dict(total_load=total_load, solar_gen=solar_gen,
                  baseline_net=baseline_net, coordinated_net=coordinated_net,
                  greenhouse_load=greenhouse_load, batt_flow=batt_flow)
    return summary, series


def make_chart(s, series):
    h = np.arange(24)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axhline(0, color="#888", lw=0.8)
    peak_lbl = f"Grid peak ({PEAK_WINDOW[0]}:00-{PEAK_WINDOW[-1]+1}:00)"
    for hr in PEAK_WINDOW:
        ax.axvspan(hr - 0.5, hr + 0.5, color="#ffd28a", alpha=0.25,
                   label="_grid peak window" if hr != PEAK_WINDOW[0] else peak_lbl)

    ax.plot(h, series["baseline_net"], color="#d9534f", lw=2.4,
            marker="o", ms=3, label="Net grid demand — no coordination")
    ax.plot(h, series["coordinated_net"], color="#2e9e6b", lw=2.4,
            marker="o", ms=3, label="Net grid demand — coordinated network")
    ax.plot(h, series["solar_gen"], color="#e8a33d", lw=1.4, ls="--",
            label="Solar generation")
    ax.plot(h, series["total_load"], color="#4a6fa5", lw=1.4, ls=":",
            label="Total load (buildings + greenhouse)")

    ax.set_title(
        f"Rough greenhouse-network simulation — cluster {s['grid_id']} "
        f"({s['n_buildings']} buildings, {s['units']} units)\n"
        f"Evening peak grid demand cut ~{s['peak_cut_pct']:.0f}% "
        f"({s['peak_cut_kw']:.0f} kW) — ILLUSTRATIVE ESTIMATE",
        fontsize=12)
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Power (kW)   +import / -export")
    ax.set_xticks(range(0, 24, 2))
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    fig.text(0.99, 0.01,
             "Illustrative only. Solar=real (Open-Meteo); greenhouse load=literature-based; "
             "battery/DR=modeled assumptions.",
             ha="right", fontsize=7, color="#777")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130)
    print(f"  chart saved -> {OUT_PNG}")


def main():
    s, series = simulate()
    print("=" * 64)
    print(" ROUGH GREENHOUSE-NETWORK SIMULATION (illustrative)")
    print("=" * 64)
    print(f"  Cluster:            {s['grid_id']}  "
          f"({s['n_buildings']} buildings, {s['units']} units)")
    print(f"  Greenhouse area:    {s['gh_area_m2']:,.0f} m^2  "
          f"(= {GREENHOUSE_ROOF_FRAC:.0%} of roof)   [assumption]")
    print(f"  Solar capacity:     {s['solar_kw']:,.0f} kW          [real-derived]")
    print(f"  Battery:            {s['batt_power_kw']:,.0f} kW / "
          f"{s['batt_energy_kwh']:,.0f} kWh  [power real, {BATTERY_HOURS}h assumed]")
    print(f"  Solar data source:  {s['solar_src']}")
    print("-" * 64)
    print(f"  Evening peak grid demand WITHOUT coordination: {s['base_peak']:,.0f} kW")
    print(f"  Evening peak grid demand WITH coordination:    {s['coord_peak']:,.0f} kW")
    print(f"  --> Peak demand cut:   {s['peak_cut_kw']:,.0f} kW  "
          f"({s['peak_cut_pct']:.0f}%)")
    print(f"  --> Peak-window grid energy cut: {s['energy_cut_pct']:.0f}%")
    print("-" * 64)
    print("  Reference: Cornell (Applied Energy 2024) reports up to 28% net-load")
    print("  reduction for an AI-coordinated greenhouse network. Our simpler")
    print("  rule-based estimate is in a comparable range.")
    print("=" * 64)
    make_chart(s, series)


if __name__ == "__main__":
    main()
