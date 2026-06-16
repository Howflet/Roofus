"""
Greenhouse-network day-simulation for one cluster (used by the optional
/grids/{id}/simulation endpoint and the standalone frontend/simulation.html page).

This is a JSON-returning port of simulation/simulate_network.py: for a given
aggregation grid it returns a 24-hour profile (total load, solar, net grid demand
with vs without coordination) plus headline numbers (evening peak cut).

ILLUSTRATIVE — same labelled assumptions as the standalone script. The greenhouse
cooling is grounded in the GES physics run (simulation/ges/): driven by sunlight,
peaks in the afternoon.

This file + backend/routers/simulation.py + frontend/simulation.html are an
isolated add-on; delete the three to remove the feature entirely.
"""
from __future__ import annotations

import numpy as np

# Real Hapeville summer-day solar (W/m^2 by hour) — same profile as the script.
SOLAR_WM2 = [0, 0, 0, 0, 0, 0, 0, 3, 86, 265, 436, 414, 442, 855, 899, 862,
             786, 486, 351, 185, 119, 12, 0, 0]

PV_PERFORMANCE_RATIO = 0.80
GREENHOUSE_ROOF_FRAC = 0.50
SQFT_TO_M2 = 0.092903
LIGHT_W_PER_M2 = 12.0
LIGHT_SCHEDULE = {20: 0.4, 21: 0.3}
COVER_TRANSMITTANCE = 0.70      # sunlight entering greenhouse as heat
COOLING_COP = 12.0              # evaporative cooling efficiency (GES-grounded)
BATTERY_HOURS = 4
ROUND_TRIP_EFF = 0.90
PEAK_WINDOW = [17, 18, 19, 20]  # 5-9 pm summer grid peak
GREENHOUSE_SHED_FRAC = 0.40

_BLDG_SHAPE = np.array(
    [0.45, 0.40, 0.38, 0.37, 0.38, 0.45, 0.60, 0.72, 0.70, 0.62, 0.58, 0.57,
     0.58, 0.60, 0.62, 0.66, 0.74, 0.85, 0.95, 1.00, 0.95, 0.82, 0.65, 0.52])


def simulate_grid(p: dict) -> dict:
    """Run the day-simulation for one grid's properties dict; return JSON-able data."""
    solar_wm2 = np.array(SOLAR_WM2, dtype=float)

    roof_m2 = p["total_roof_sqft"] * SQFT_TO_M2
    bldg_peak_kw = p["combined_peak_kw"]
    full_roof_solar_kw = p["combined_der_dispatchable_kw"] * 2.0
    solar_kw = full_roof_solar_kw * (1 - GREENHOUSE_ROOF_FRAC)
    batt_power_kw = solar_kw * 0.50
    gh_area_m2 = roof_m2 * GREENHOUSE_ROOF_FRAC

    # hourly loads (kW)
    base_load = _BLDG_SHAPE * bldg_peak_kw
    light_kw = np.zeros(24)
    for hr, frac in LIGHT_SCHEDULE.items():
        light_kw[hr] = gh_area_m2 * LIGHT_W_PER_M2 * frac / 1000.0
    cool_kw = (COVER_TRANSMITTANCE * solar_wm2 / COOLING_COP) * gh_area_m2 / 1000.0
    greenhouse_load = light_kw + cool_kw
    total_load = base_load + greenhouse_load

    solar_gen = solar_kw * (solar_wm2 / 1000.0) * PV_PERFORMANCE_RATIO
    baseline_net = total_load - solar_gen

    # battery: charge midday surplus, discharge into the evening peak
    batt_energy_cap = batt_power_kw * BATTERY_HOURS
    soc = 0.0
    batt_flow = np.zeros(24)
    for h in range(24):
        surplus = solar_gen[h] - total_load[h]
        if surplus > 0 and soc < batt_energy_cap:
            charge = min(surplus, batt_power_kw, batt_energy_cap - soc)
            soc += charge * ROUND_TRIP_EFF
            batt_flow[h] = -charge
    for h in PEAK_WINDOW:
        if soc <= 0:
            break
        imp = total_load[h] - solar_gen[h]
        if imp > 0:
            dis = min(imp, batt_power_kw, soc)
            soc -= dis
            batt_flow[h] = dis

    dr_shed = np.zeros(24)
    for h in PEAK_WINDOW:
        dr_shed[h] = greenhouse_load[h] * GREENHOUSE_SHED_FRAC
    coordinated_net = total_load - solar_gen - batt_flow - dr_shed

    pw = np.array(PEAK_WINDOW)
    base_peak = float(baseline_net[pw].max())
    coord_peak = float(coordinated_net[pw].max())
    peak_cut_kw = base_peak - coord_peak
    peak_cut_pct = (100 * peak_cut_kw / base_peak) if base_peak > 0 else 0.0
    be = float(baseline_net[pw].clip(min=0).sum())
    ce = float(coordinated_net[pw].clip(min=0).sum())
    energy_cut_pct = (100 * (be - ce) / be) if be > 0 else 0.0

    # --- CL-1 money (illustrative) — what the owner(s) could be paid -----------
    # Pulled straight from the pipeline: CL-1 pays for CURTAILABLE CAPACITY (kW the
    # cluster can shed on command), NOT the peak-cut %. Rate is illustrative.
    curtailable_kw = float(p.get("combined_curtailable_kw", 0.0))
    cl1_eligible = bool(p.get("meets_cl1_threshold", False))
    est_annual_credit = int(p.get("potential_annual_value", 0)) if cl1_eligible else 0

    def rnd(a):
        return [round(float(x), 1) for x in a]

    return {
        "grid_id": p.get("grid_id"),
        "n_buildings": p.get("building_count"),
        "units": p.get("total_units"),
        "solar_kw": round(solar_kw),
        "batt_power_kw": round(batt_power_kw),
        "batt_energy_kwh": round(batt_energy_cap),
        "gh_area_m2": round(gh_area_m2),
        "curtailable_kw": round(curtailable_kw),
        "cl1_eligible": cl1_eligible,
        "est_annual_credit": est_annual_credit,
        "peak_window": PEAK_WINDOW,
        "base_peak_kw": round(base_peak),
        "coord_peak_kw": round(coord_peak),
        "peak_cut_kw": round(peak_cut_kw),
        "peak_cut_pct": round(peak_cut_pct),
        "energy_cut_pct": round(energy_cut_pct),
        "hours": list(range(24)),
        "total_load": rnd(total_load),
        "solar_gen": rnd(solar_gen),
        "baseline_net": rnd(baseline_net),
        "coordinated_net": rnd(coordinated_net),
    }
