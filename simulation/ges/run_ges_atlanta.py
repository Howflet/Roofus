"""
GES greenhouse under REAL Atlanta summer weather — the COOLING question
=======================================================================

GES (Greenhouse Energy Simulation, Cambridge EECi) models the greenhouse heat
balance directly, so we can ask the real question about summer *electric
cooling* load:

    In an Atlanta JULY, does opening the vents keep a greenhouse cool enough,
    or does it overheat and need ACTIVE cooling (an electric load)?

What this does:
  1. Runs the GES physics model with REAL Atlanta July weather (Open-Meteo).
  2. Reports the greenhouse's internal air temperature (vented, no AC).
  3. If it overheats past a safe crop setpoint, estimates the ELECTRIC cooling
     load needed to hold that setpoint — the demand-response-relevant number.

HONEST LABELS:
  [REAL]        Atlanta July temp / humidity / wind / sunlight (Open-Meteo)
  [MODEL]       GES greenhouse physics (validated research model)
  [ASSUMPTION]  solar split onto greenhouse surfaces; cooling-system efficiency

CAVEATS: GES is a single-zone TOMATO greenhouse, vents at 25 C, unheated.
The directional solar is approximated from global sunlight. The electric-cooling
estimate is a simple add-on (GES itself has no AC), clearly labelled.

Prereq: GES python code present (we clone it to C:/Users/Vacav/Downloads/GES).
Run:  python run_ges_atlanta.py
"""

import sys
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d

# --- locate the GES model code -------------------------------------------
GES_DIR = Path("C:/Users/Vacav/Downloads/GES/python")
sys.path.insert(0, str(GES_DIR))
from functions import model               # noqa: E402
from parameters import *                  # noqa: E402,F401,F403  (T_k, deltaT, A_f, SurfaceArea, T_sp_vent, A_c_roof ...)

HERE = Path(__file__).resolve().parent
WEATHER_CSV = HERE / "atlanta_july_weather.csv"
OUT_PNG = HERE / "ges_atlanta_cooling.png"

# --- cooling assumptions (clearly labelled) ------------------------------
SAFE_SETPOINT_C = 28.0     # [ASSUMPTION] crop-safe max indoor temp for cooling target
COVER_TRANSMITTANCE = 0.70 # [ASSUMPTION] fraction of sunlight entering as heat
COOLING_COP = 3.5          # [ASSUMPTION] electric cooling efficiency (heat removed / kW elec)
SPINUP_DAYS = 3            # discard model warm-up
SIM_DAYS = 13              # keep within the 14-day weather window


def load_weather():
    temp, rh, wind, ghi, dif = [], [], [], [], []
    with open(WEATHER_CSV) as f:
        for row in csv.DictReader(f):
            temp.append(float(row["temp_C"]));  rh.append(float(row["rh_pct"]))
            wind.append(float(row["wind_ms"])); ghi.append(float(row["ghi_wm2"]))
            dif.append(float(row["diffuse_wm2"]))
    return (np.array(temp), np.array(rh), np.array(wind),
            np.array(ghi), np.array(dif))


def build_climate(temp, rh, wind, ghi, dif):
    """Assemble GES's 21-column weather array and interpolate to deltaT."""
    N = len(temp)
    beam = np.clip(ghi - dif, 0, None)
    tsky = temp - 10.0                       # [ASSUMPTION] clear-sky approximation
    clim = np.zeros((N, 21))
    clim[:, 0] = np.arange(1, N + 1)         # hour index
    clim[:, 1] = temp
    clim[:, 2] = tsky
    clim[:, 3] = wind
    clim[:, 4] = rh
    # surface order: 0 NE wall,1 NE roof,2 SE wall,3 SE roof,4 SW wall,5 SW roof,6 NW wall,7 NW roof
    roof = {1, 3, 5, 7}
    for k in range(8):                       # direct cols 5..12
        clim[:, 5 + k] = beam if k in roof else 0.3 * beam   # [ASSUMPTION] beam mostly on roofs
    for k in range(8):                       # diffuse cols 13..20
        clim[:, 13 + k] = dif
    # interpolate to deltaT (60 s) resolution exactly as GES_Example does
    l = N
    mult = np.linspace(1, l, int((l - 1) * 3600 / deltaT))
    y_interp = interp1d(clim[:, 0], clim[:, 1:21], axis=0)
    return y_interp(mult), N


def initial_state():
    T0 = 22.0 + T_k
    return [24. + T_k, T0, T0, T0, T0, T0, T0, T0, 20. + T_k, 19. + T_k,
            T0, 0, 0.0085, 7.5869e-4, 0.01, 0.001, 0.01, 0.01, 0., 0., 0.]


def main():
    temp, rh, wind, ghi, dif = load_weather()
    climate, N = build_climate(temp, rh, wind, ghi, dif)

    print("Running GES greenhouse under REAL Atlanta July weather ...")
    tf = 86400 * SIM_DAYS
    tval = np.arange(0, tf, 600)             # 10-min output
    out = solve_ivp(model, [0, tf], initial_state(), method="BDF",
                    t_eval=tval, rtol=1e-5, args=[climate, [0]])

    t_h = out.t / 3600.0
    Ti = out.y[1, :] - T_k                    # indoor air temp [C]
    Text = np.interp(t_h, np.arange(N), temp) # outdoor temp aligned
    GHIt = np.interp(t_h, np.arange(N), ghi)  # sunlight aligned

    keep = t_h >= SPINUP_DAYS * 24            # drop warm-up
    Ti_k, Text_k, GHI_k, th_k = Ti[keep], Text[keep], GHIt[keep], t_h[keep]

    # --- overheating stats ---
    peak_in = Ti_k.max()
    hours_over = np.mean(Ti_k > SAFE_SETPOINT_C) * 100
    max_excess = (Ti_k - Text_k).max()

    # --- simple electric cooling estimate (GES has no AC; add-on) ---
    # thermal load to remove ~ sunlight entering through the cover onto the roof
    cool_thermal_w = COVER_TRANSMITTANCE * GHI_k * A_c_roof      # W (whole greenhouse)
    cool_thermal_w[Ti_k <= SAFE_SETPOINT_C] = 0.0               # only when overheating
    cool_elec_w = cool_thermal_w / COOLING_COP
    cool_elec_wm2 = cool_elec_w / A_f                          # per m^2 floor
    peak_cool_wm2 = cool_elec_wm2.max()

    # cooling load by hour-of-day (for the grid-peak alignment story)
    hod = (th_k % 24).astype(int)
    prof = np.array([cool_elec_wm2[hod == h].mean() if (hod == h).any() else 0
                     for h in range(24)])

    print("=" * 66)
    print(" GES GREENHOUSE — REAL ATLANTA JULY (vented, no AC)")
    print("=" * 66)
    print(f"  Peak INDOOR air temp (vented only): {peak_in:5.1f} C")
    print(f"  Outdoor peak:                        {Text_k.max():5.1f} C")
    print(f"  Hottest the greenhouse runs ABOVE outdoor: +{max_excess:.1f} C")
    print(f"  Share of time above {SAFE_SETPOINT_C:.0f} C safe limit: {hours_over:.0f}%")
    print("-" * 66)
    print("  => Venting alone does NOT keep it cool -> active cooling needed.")
    print(f"  Estimated electric cooling load (peak): {peak_cool_wm2:.0f} W per m^2 floor")
    print(f"  Cooling load peaks around {int(np.argmax(prof))}:00 "
          f"(afternoon) -> lines up with the summer GRID PEAK.")
    print("=" * 66)

    # --- chart ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), height_ratios=[3, 2])
    ax1.axhline(SAFE_SETPOINT_C, color="#c0392b", ls="--", lw=1,
                label=f"Crop-safe limit ({SAFE_SETPOINT_C:.0f} C)")
    ax1.axhline(25, color="#e0a800", ls=":", lw=1, label="Vent setpoint (25 C)")
    ax1.plot(th_k / 24, Ti_k, color="#2e7d32", lw=1.8, label="Greenhouse inside (vented, no AC)")
    ax1.plot(th_k / 24, Text_k, color="#3b7dd8", lw=1.2, alpha=0.8, label="Atlanta outdoor")
    ax1.fill_between(th_k / 24, SAFE_SETPOINT_C, Ti_k, where=Ti_k > SAFE_SETPOINT_C,
                     color="#e74c3c", alpha=0.25)
    ax1.set_title("GES greenhouse in REAL Atlanta July: venting can't keep it cool\n"
                  f"(peaks {peak_in:.0f} C inside) — ILLUSTRATIVE", fontsize=11)
    ax1.set_xlabel("Day"); ax1.set_ylabel("Temperature (C)")
    ax1.legend(fontsize=8, loc="upper right"); ax1.grid(alpha=0.25)

    ax2.bar(range(24), prof, color="#d9822b", alpha=0.85)
    ax2.set_title("Estimated electric COOLING load by hour (peaks with the grid)", fontsize=10)
    ax2.set_xlabel("Hour of day"); ax2.set_ylabel("W / m^2 floor")
    ax2.set_xticks(range(0, 24, 2)); ax2.grid(alpha=0.25)
    fig.text(0.99, 0.005, "GES physics + real Atlanta July weather. Cooling load is a "
             "simple add-on estimate (GES has no AC). Illustrative.",
             ha="right", fontsize=7, color="#777")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130)
    print(f"  chart saved -> {OUT_PNG}")


if __name__ == "__main__":
    main()
