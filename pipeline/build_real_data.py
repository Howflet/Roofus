#!/usr/bin/env python3
"""Build REAL Hapeville GeoJSON data for Roofus.

Replaces generate_mock_data.py. Pulls live, public data — no API keys:

  * Parcels / owners / units / land use  -> Fulton County Tax Parcels (ArcGIS)
  * Roof area                            -> real lot acreage x ~35% coverage (estimate)
  * Solar (GHI)                          -> Open-Meteo archive API (real)
  * Food desert                          -> USDA Food Access Research Atlas 2019 (real)

Outputs the same schema the backend + frontend already expect:
  pipeline/data/processed/scored_buildings.geojson
  pipeline/data/processed/aggregation_grids.geojson

Usage:
    python pipeline/build_real_data.py
"""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CENTER_LAT, CENTER_LON = 33.6693, -84.4102
# Hapeville bounding box (lon/lat) — small city (~2.8 sq mi)
HAPEVILLE_BBOX = (-84.43, 33.635, -84.385, 33.695)  # minx, miny, maxx, maxy

MIN_UNITS = 5            # commercial-class threshold: 5+ units = commercial real estate
                         # (income property; typically a master-metered C&I utility account,
                         #  which is what Georgia Power CL-1/DCO-1 demand-response eligibility requires)
ROOF_COVERAGE = 0.35     # estimated building footprint as share of lot
SQFT_PER_ACRE = 43560
CLUSTER_RADIUS_M = 804   # 0.5 mile aggregation radius

# --- Rooftop DER / DCO-1 power-plant model --------------------------------
# Solar PV on the roof + battery storage = a dispatchable Distributed Energy
# Resource. Georgia Power DCO-1 tariff: >=250 kW dispatchable per account,
# aggregating to >=1 MW per cluster; credit = 75% of projected system value.
USABLE_ROOF_FRAC = 0.60          # share of roof usable for PV (setbacks, equipment, tilt spacing)
PV_KW_PER_SQFT = 0.011           # commercial flat-roof PV power density (~1 kW per 90 ft^2)
PV_PERFORMANCE_RATIO = 0.80      # real-world derate (inverter, heat, soiling)
BATTERY_DISPATCH_FRAC = 0.50     # firm dispatchable capacity = battery sized to ~50% of PV
DCO1_ACCOUNT_MIN_KW = 250        # DCO-1 per-account minimum (for aggregation)
DCO1_PREMISES_MIN_KW = 1000      # DCO-1 1 MW floor (single premises or aggregated cluster)
DCO1_CREDIT_SHARE = 0.75         # tariff: credit = 75% of projected system value
# Illustrative system-value inputs (tariff says negotiated per agreement):
AVOIDED_CAPACITY_PER_KW_YR = 90  # $/kW-yr illustrative avoided capacity value
AVOIDED_ENERGY_PER_KWH = 0.03    # $/kWh illustrative avoided energy value

# --- Demand-response CURTAILABLE load model -------------------------------
# DR programs enroll the load you can actually shed on command, NOT total peak.
# Two real, sheddable sources for a multifamily rooftop-greenhouse site:
THERMOSTAT_SHED_PER_UNIT = 1.0   # kW/unit sheddable via smart-thermostat AC cycling on a hot-day event
                                 # (assumes owner can control + meter unit AC; ~1 kW per home AC is realistic)
GH_SHED_PER_SQFT = 0.0018        # kW/sqft greenhouse lighting+pump load shiftable out of peak
GH_SHED_CAP_KW = 30              # realistic ceiling for one rooftop greenhouse's shiftable load

PARCELS_URL = ("https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/"
               "PropertyMapViewer/PropertyMapViewer/MapServer/11/query")
FARA_URL = ("https://gisportal.ers.usda.gov/server/rest/services/"
            "FARA/FARA_2019/MapServer/1/query")
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

OUTPUT_DIR = Path(__file__).resolve().parent / "data" / "processed"
DATA_SOURCE = "Fulton County Tax Assessor + USDA FARA 2019 + Open-Meteo (live, June 2026)"

UA = {"User-Agent": "Roofus-Hapeville/1.0 (hackathon)"}


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only)
# ---------------------------------------------------------------------------

def _get(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def _post(url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.load(r)
    if isinstance(out, dict) and out.get("error"):
        raise RuntimeError(f"ArcGIS error from {url}: {out['error']}")
    return out


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _ring_centroid(ring: list) -> tuple[float, float]:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _point_in_ring(x: float, y: float, ring: list) -> bool:
    """Ray-casting point-in-polygon for a single ring."""
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def _haversine_m(lon1, lat1, lon2, lat2) -> float:
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _convex_hull_polygon(points: list[tuple[float, float]]) -> dict:
    """Simple angular hull with slight outward buffer (matches mock output style)."""
    if len(points) < 3:
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        r = 0.0015
        coords = [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r), (cx - r, cy - r)]
        return {"type": "Polygon", "coordinates": [[[round(x, 7), round(y, 7)] for x, y in coords]]}
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    sorted_pts = sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    buffered = []
    for px, py in sorted_pts:
        dx, dy = px - cx, py - cy
        dist = math.hypot(dx, dy)
        if dist > 0:
            buffered.append((cx + dx * 1.25, cy + dy * 1.25))
        else:
            buffered.append((px, py))
    buffered.append(buffered[0])
    return {"type": "Polygon", "coordinates": [[[round(x, 7), round(y, 7)] for x, y in buffered]]}


# ---------------------------------------------------------------------------
# 1) Parcels (Fulton County) — real
# ---------------------------------------------------------------------------

def fetch_parcels() -> list[dict]:
    minx, miny, maxx, maxy = HAPEVILLE_BBOX
    env = f"{minx},{miny},{maxx},{maxy}"
    print(f"Fetching Fulton County multifamily parcels (LivUnits>={MIN_UNITS}) ...")

    # LUCode LIKE '2%' = Fulton multifamily/apartment land-use classes;
    # require real lot area so roof estimate isn't a placeholder.
    ids = _post(PARCELS_URL, {
        "where": f"LivUnits >= {MIN_UNITS} AND LandAcres > 0 AND LUCode LIKE '2%'",
        "geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects", "returnIdsOnly": "true", "f": "json",
    })
    oid_field = ids.get("objectIdFieldName", "OBJECTID")
    oids = ids.get("objectIds") or []
    print(f"  {len(oids)} parcels match. Downloading attributes + geometry ...")

    out_fields = ("OBJECTID,ParcelID,Address,Owner,OwnerAddr1,OwnerAddr2,"
                  "LivUnits,LUCode,ClassCode,LandAcres")
    feats: list[dict] = []
    for i in range(0, len(oids), 100):
        chunk = oids[i:i + 100]
        resp = _post(PARCELS_URL, {
            "where": f"{oid_field} IN ({','.join(str(o) for o in chunk)})",
            "outFields": out_fields, "returnGeometry": "true", "outSR": "4326", "f": "json",
        })
        feats.extend(resp.get("features", []))
    print(f"  Retrieved {len(feats)} parcel features.")
    return feats


# ---------------------------------------------------------------------------
# 2) Solar (Open-Meteo) — real
# ---------------------------------------------------------------------------

def fetch_avg_ghi() -> float:
    print("Fetching real annual solar (Open-Meteo, 2024) ...")
    r = _get(OPEN_METEO_URL, {
        "latitude": CENTER_LAT, "longitude": CENTER_LON,
        "start_date": "2024-01-01", "end_date": "2024-12-31",
        "daily": "shortwave_radiation_sum", "timezone": "America/New_York",
    })
    vals = [v for v in r["daily"]["shortwave_radiation_sum"] if v is not None]
    avg_mj = sum(vals) / len(vals)          # MJ/m^2/day
    avg_ghi = round(avg_mj / 3.6, 2)        # -> kWh/m^2/day
    print(f"  Hapeville annual avg GHI = {avg_ghi} kWh/m^2/day (from {len(vals)} days)")
    return avg_ghi


# ---------------------------------------------------------------------------
# 3) Food desert (USDA FARA 2019) — real
# ---------------------------------------------------------------------------

def fetch_food_desert_tracts() -> list[dict]:
    minx, miny, maxx, maxy = HAPEVILLE_BBOX
    env = f"{minx},{miny},{maxx},{maxy}"
    print("Fetching USDA food-access tracts (FARA 2019) ...")
    resp = _post(FARA_URL, {
        "where": "1=1", "geometry": env, "geometryType": "esriGeometryEnvelope",
        "inSR": "4326", "spatialRel": "esriSpatialRelIntersects",
        "outFields": "GEOID10,LILATracts_halfAnd10,LILATracts_1And10,LowIncomeTracts,PovertyRate",
        "returnGeometry": "true", "outSR": "4326", "f": "json",
    })
    tracts = []
    for f in resp.get("features", []):
        rings = f.get("geometry", {}).get("rings", [])
        if rings:
            tracts.append({"attr": f["attributes"], "rings": rings})
    print(f"  {len(tracts)} tracts intersect Hapeville.")
    return tracts


def lookup_tract(lon: float, lat: float, tracts: list[dict]) -> dict | None:
    for t in tracts:
        for ring in t["rings"]:
            if _point_in_ring(lon, lat, ring):
                return t["attr"]
    return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def landuse_favorability(units: int) -> int:
    if units >= 100: return 100
    if units >= 50:  return 85
    if units >= 20:  return 75
    if units >= 12:  return 65
    if units >= 5:   return 55
    return 45


def structural_score(units: int, roof_area: float) -> int:
    # Year-built / floors not in county data; proxy structural readiness from
    # unit count + roof footprint (both real), plus flat-roof MF assumption.
    s = 20 + min(40, units * 1.5) + min(40, roof_area / 250)
    return int(min(100, round(s)))


# ---------------------------------------------------------------------------
# Build buildings
# ---------------------------------------------------------------------------

def build_buildings(parcels, avg_ghi, tracts) -> list[dict]:
    buildings = []
    s_solar = max(0, min(100, round((avg_ghi - 4.0) / 1.5 * 100)))
    idx = 0

    for p in parcels:
        a = p["attributes"]
        rings = p.get("geometry", {}).get("rings", [])
        if not rings:
            continue
        units = int(a.get("LivUnits") or 0)
        if units < MIN_UNITS:
            continue

        lon, lat = _ring_centroid(rings[0])
        acres = float(a.get("LandAcres") or 0) or 0.0
        lot_sqft = round(acres * SQFT_PER_ACRE)
        roof_area = round(lot_sqft * ROOF_COVERAGE)
        if roof_area < 800:
            roof_area = 800  # floor so tiny-lot records still model a minimal greenhouse

        idx += 1
        bid = f"BLD-{idx:03d}"

        # food desert (real)
        t = lookup_tract(lon, lat, tracts)
        in_fd = bool(t and int(t.get("LILATracts_halfAnd10") or 0) == 1)
        low_income = bool(t and int(t.get("LowIncomeTracts") or 0) == 1)
        poverty = round(float(t["PovertyRate"]), 1) if t and t.get("PovertyRate") is not None else None
        tract_id = t.get("GEOID10") if t else None

        addr_raw = (a.get("Address") or "").strip().title()
        address = f"{addr_raw}, Hapeville, GA 30354" if addr_raw else "Hapeville, GA 30354"
        owner_addr = ", ".join(x for x in [(a.get("OwnerAddr1") or "").strip(),
                                           (a.get("OwnerAddr2") or "").strip()] if x)

        residential_peak = round(units * 1.5, 1)   # residential electrical peak
        thermostat_shed = round(units * THERMOSTAT_SHED_PER_UNIT, 1)
        greenhouse_shed = round(min(roof_area * GH_SHED_PER_SQFT, GH_SHED_CAP_KW), 1)
        greenhouse_peak = round(greenhouse_shed / 0.6, 1)  # shiftable ~60% of greenhouse connected load
        peak_kw = round(residential_peak + greenhouse_peak, 1)   # total site peak (residential + greenhouse)
        curtailable_kw = round(thermostat_shed + greenhouse_shed, 1)   # what DR can actually shed (<= peak)

        # --- Rooftop power-plant (DCO-1) potential ---
        solar_capacity_kw = round(roof_area * USABLE_ROOF_FRAC * PV_KW_PER_SQFT)
        der_dispatchable_kw = round(solar_capacity_kw * BATTERY_DISPATCH_FRAC)
        der_annual_mwh = round(solar_capacity_kw * avg_ghi * 365 * PV_PERFORMANCE_RATIO / 1000, 1)
        dco1_account_ready = der_dispatchable_kw >= DCO1_ACCOUNT_MIN_KW
        der_credit_est = round(DCO1_CREDIT_SHARE * (
            der_dispatchable_kw * AVOIDED_CAPACITY_PER_KW_YR
            + der_annual_mwh * 1000 * AVOIDED_ENERGY_PER_KWH))

        lu_code = (a.get("LUCode") or "").strip()

        s_structural = structural_score(units, roof_area)
        s_area = min(100, round(roof_area / 120))
        s_zoning = landuse_favorability(units)   # land-use favorability (no legal zoning data)
        s_food = 100 if in_fd else 30

        # Real, verified Georgia Power programs only (no VPP/TempCheck fiction)
        programs = []
        if curtailable_kw >= 200:
            programs.append("CL-1")                       # Curtailable Load (turn-down)
        if dco1_account_ready:
            programs.append("DCO-1 (aggregation account)")  # ≥250 kW dispatchable DER
        # Illustrative CL-1 credit: 75% of capacity value (~$90/kW-yr) minus $120/mo admin
        annual_val = max(0, round(0.75 * 90 * curtailable_kw - 1440)) if curtailable_kw >= 200 else 0
        onetime_val = 0   # CL-1 and DCO-1 are recurring credits, not one-time payments

        buildings.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": rings},
            "properties": {
                "id": bid,
                "parcel_id": (a.get("ParcelID") or "").strip(),
                "address": address,
                "roof_area_sqft": roof_area,
                "roof_area_basis": f"estimated: {int(ROOF_COVERAGE*100)}% of real lot ({acres:.2f} ac)",
                "lot_area_sqft": lot_sqft,
                "year_built": None,            # not in county data
                "num_units": units,
                "num_floors": None,            # not in county data
                "zoning": f"Land use {lu_code}" if lu_code else "Multifamily",
                "land_use_code": lu_code,
                "owner_name": (a.get("Owner") or "").strip().title(),
                "owner_address": owner_addr or None,
                "owner_phone": None,           # private — not in public data
                "owner_email": None,           # private — not in public data
                "avg_ghi": avg_ghi,
                "in_food_desert": in_fd,
                "low_income_tract": low_income,
                "poverty_rate": poverty,
                "census_tract": tract_id,
                "hvac_proxy_score": s_structural,
                "estimated_peak_kw": peak_kw,
                "curtailable_kw": curtailable_kw,
                "thermostat_shed_kw": thermostat_shed,
                "greenhouse_shed_kw": greenhouse_shed,
                "solar_capacity_kw": solar_capacity_kw,
                "der_dispatchable_kw": der_dispatchable_kw,
                "der_annual_mwh": der_annual_mwh,
                "dco1_account_ready": dco1_account_ready,
                "der_credit_est_annual": der_credit_est,
                "aggregation_grid_id": "",
                "score": 0.0,
                "score_structural": s_structural,
                "score_area": s_area,
                "score_solar": s_solar,
                "score_zoning": s_zoning,
                "score_food_desert": s_food,
                "score_aggregation": 40,
                "subsidy_summary": {
                    "eligible_programs": programs,
                    "total_annual_value": annual_val,
                    "total_onetime_value": onetime_val,
                    "aggregation_tier": "Below Threshold",
                    "grid_combined_kw": 0,
                    "grid_building_count": 0,
                },
                "data_source": DATA_SOURCE,
                "_lat": lat, "_lon": lon,
            },
        })
    return buildings


def finalize_score(b: dict) -> None:
    p = b["properties"]
    p["score"] = round(
        p["score_structural"] * 0.30 + p["score_area"] * 0.20 + p["score_solar"] * 0.15
        + p["score_zoning"] * 0.15 + p["score_food_desert"] * 0.15 + p["score_aggregation"] * 0.05,
        1,
    )


# ---------------------------------------------------------------------------
# 4) Real 0.5-mile clustering (connected components within radius)
# ---------------------------------------------------------------------------

def build_grids(buildings: list[dict]) -> list[dict]:
    # 0.5-mile grid tiling -> bounded "neighborhood blocks" (avoids chain-merging
    # the whole dense city into one cluster, which connected-components does here).
    minx, miny, _, _ = HAPEVILLE_BBOX
    cell_lat = 0.5 / 69.0                       # ~0.5 mi in degrees latitude
    cell_lon = 0.5 / (69.17 * math.cos(math.radians(CENTER_LAT)))

    cells: dict[tuple[int, int], list[int]] = {}
    for i, b in enumerate(buildings):
        pr = b["properties"]
        cx = int((pr["_lon"] - minx) / cell_lon)
        cy = int((pr["_lat"] - miny) / cell_lat)
        cells.setdefault((cx, cy), []).append(i)

    clusters = [comp for _, comp in sorted(cells.items())]

    grids = []
    for g, comp in enumerate(clusters):
        grid_id = f"GRID-{g+1:03d}"
        members = [buildings[k] for k in comp]
        centroids, combined_peak, combined_curt, total_units, total_roof = [], 0.0, 0.0, 0, 0
        combined_der, dco1_qualifying, dco1_accounts = 0.0, 0.0, 0
        for bldg in members:
            pr = bldg["properties"]
            pr["aggregation_grid_id"] = grid_id
            centroids.append((pr["_lon"], pr["_lat"]))
            combined_peak += pr["estimated_peak_kw"]
            combined_curt += pr["curtailable_kw"]
            total_units += pr["num_units"]
            total_roof += pr["roof_area_sqft"]
            combined_der += pr["der_dispatchable_kw"]
            if pr["dco1_account_ready"]:            # only >=250 kW accounts count toward DCO-1 aggregation
                dco1_qualifying += pr["der_dispatchable_kw"]
                dco1_accounts += 1

        combined_peak = round(combined_peak, 1)
        combined_curt = round(combined_curt, 1)        # DR thresholds compare against THIS
        meets_vpp = combined_curt >= 100
        meets_cl1 = combined_curt >= 200
        tier = "CL-1" if meets_cl1 else "VPP" if meets_vpp else "Below Threshold"
        if meets_cl1:
            annual_value = round(combined_curt * 5.5 * 12)
        elif meets_vpp:
            annual_value = round(combined_curt * 15 + combined_curt * 1.50 * 100)
        else:
            annual_value = round(combined_curt * 5 * 12)
        avg_curt = max(1.0, combined_curt / len(members))
        bldgs_needed = max(0, math.ceil((200 - combined_curt) / avg_curt)) if not meets_cl1 else 0

        for bldg in members:
            sub = bldg["properties"]["subsidy_summary"]
            sub["aggregation_tier"] = tier
            sub["grid_combined_kw"] = combined_curt
            sub["grid_building_count"] = len(members)
            bldg["properties"]["score_aggregation"] = 100 if meets_cl1 else 80 if meets_vpp else 40
            finalize_score(bldg)

        grids.append({
            "type": "Feature",
            "geometry": _convex_hull_polygon(centroids),
            "properties": {
                "grid_id": grid_id,
                "building_count": len(members),
                "total_units": total_units,
                "total_roof_sqft": total_roof,
                "combined_peak_kw": combined_peak,          # total demand (informational)
                "combined_curtailable_kw": combined_curt,   # sheddable load (DR threshold basis)
                "meets_vpp_threshold": meets_vpp,
                "meets_cl1_threshold": meets_cl1,
                "aggregation_tier": tier,
                "potential_annual_value": annual_value,
                "buildings_needed_for_cl1": bldgs_needed,
                # --- DCO-1 rooftop power-plant aggregation ---
                "combined_der_dispatchable_kw": round(combined_der, 1),
                "dco1_qualifying_kw": round(dco1_qualifying, 1),   # sum of >=250 kW accounts only
                "dco1_accounts": dco1_accounts,
                "dco1_cluster_eligible": dco1_qualifying >= DCO1_PREMISES_MIN_KW,
            },
        })
    return grids


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parcels = fetch_parcels()
    avg_ghi = fetch_avg_ghi()
    tracts = fetch_food_desert_tracts()

    buildings = build_buildings(parcels, avg_ghi, tracts)
    for b in buildings:
        finalize_score(b)
    grids = build_grids(buildings)

    for b in buildings:
        b["properties"].pop("_lat", None)
        b["properties"].pop("_lon", None)

    bld_path = OUTPUT_DIR / "scored_buildings.geojson"
    grid_path = OUTPUT_DIR / "aggregation_grids.geojson"
    with open(bld_path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": buildings}, f, indent=2)
    with open(grid_path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": grids}, f, indent=2)

    scores = [b["properties"]["score"] for b in buildings]
    fd = sum(1 for b in buildings if b["properties"]["in_food_desert"])
    li = sum(1 for b in buildings if b["properties"]["low_income_tract"])
    high = sum(1 for s in scores if s >= 70)
    tiers: dict[str, int] = {}
    for g in grids:
        t = g["properties"]["aggregation_tier"]
        tiers[t] = tiers.get(t, 0) + 1

    dco1_ready = sum(1 for b in buildings if b["properties"]["dco1_account_ready"])
    total_solar_mw = sum(b["properties"]["solar_capacity_kw"] for b in buildings) / 1000
    dco1_clusters = sum(1 for g in grids if g["properties"]["dco1_cluster_eligible"])

    print("\n=== REAL DATA BUILT ===")
    print(f"  {len(buildings)} multifamily buildings -> {bld_path}")
    print(f"  {len(grids)} aggregation grids -> {grid_path}")
    print(f"  Avg score: {sum(scores)/len(scores):.1f} | high-potential (>=70): {high}")
    print(f"  Food-desert (USDA half&10): {fd} | low-income tracts: {li}")
    print(f"  Grid tiers (curtailment DR): {tiers}")
    print(f"  DCO-1 power plant: {total_solar_mw:.1f} MW total rooftop solar potential")
    print(f"  DCO-1 ready buildings (>=250 kW dispatchable): {dco1_ready}")
    print(f"  DCO-1 eligible clusters (>=1 MW): {dco1_clusters} of {len(grids)}")


if __name__ == "__main__":
    main()
