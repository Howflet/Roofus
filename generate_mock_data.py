#!/usr/bin/env python3
"""Generate realistic mock GeoJSON data for Roofus development.

Creates ~30 scored multifamily buildings and ~6 aggregation grids
in Hapeville, GA (R-4 and R-5 zoning districts).

Usage:
    python generate_mock_data.py
"""

import json
import math
import random
from pathlib import Path

random.seed(42)

# Hapeville, GA center
CENTER_LAT = 33.6693
CENTER_LON = -84.4102

OUTPUT_DIR = Path(__file__).resolve().parent / "pipeline" / "data" / "processed"

# ---------------------------------------------------------------------------
# Street / address data for Hapeville
# ---------------------------------------------------------------------------

STREETS = [
    "Dogwood Ave", "Birch St", "Elm St", "Cedar Ln", "Maple Dr",
    "Oak Ave", "Pine St", "Peach St", "Magnolia Blvd", "Poplar Way",
    "N Central Ave", "S Central Ave", "King Arnold St", "Virginia Ave",
    "Atlanta Ave", "Cleveland Ave", "Sylvan Rd", "Lee St",
    "Forest Pkwy", "Willingham Dr",
]

OWNER_NAMES = [
    "Dogwood Gardens LLC", "Hapeville Residential Partners",
    "ATL Urban Living Inc.", "Peach State Properties",
    "South Metro Apartments LLC", "Skyline Multifamily Group",
    "Georgia Green Homes", "Hapeville Housing Trust",
    "Magnolia Property Management", "Cedar Creek Investments",
    "ATL Southside Holdings", "Urban Core Realty",
    "Fulton Family Properties", "Heritage Living Co.",
    "Clayton-Fulton Apartments", "Metro South Residences",
]

OWNER_DOMAINS = [
    "dogwoodgardens.com", "hapresidential.com", "atlurbanliving.com",
    "peachstateprops.com", "smetro-apts.com", "skylinemf.com",
    "gagreenhomes.com", "haphousing.org", "magnoliapm.com",
    "cedarcreekinv.com", "atlsouthside.com", "urbancorerealty.com",
    "fultonfamily.com", "heritageliving.co", "cfapartments.com",
    "metrosouthres.com",
]


def _random_polygon(center_lat: float, center_lon: float, size_sqft: float) -> dict:
    """Create a roughly rectangular building polygon around a center point."""
    # Convert sqft to rough degrees (1 degree lat ≈ 364,000 ft at this latitude)
    side_ft = math.sqrt(size_sqft)
    dlat = (side_ft / 364000) / 2
    dlon = (side_ft / (364000 * math.cos(math.radians(center_lat)))) / 2

    # Add slight rotation / irregularity
    angle = random.uniform(-0.15, 0.15)

    corners = [
        (center_lon - dlon, center_lat - dlat),
        (center_lon + dlon, center_lat - dlat),
        (center_lon + dlon + angle * dlon, center_lat + dlat),
        (center_lon - dlon + angle * dlon, center_lat + dlat),
        (center_lon - dlon, center_lat - dlat),  # close ring
    ]

    return {
        "type": "Polygon",
        "coordinates": [[[round(lon, 7), round(lat, 7)] for lon, lat in corners]],
    }


def _convex_hull_polygon(points: list[tuple[float, float]]) -> dict:
    """Simple convex hull for a set of (lon, lat) points."""
    # Graham scan simplified — for small point sets this is fine
    if len(points) < 3:
        # Fallback: buffer around centroid
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        r = 0.004
        coords = [
            (cx - r, cy - r), (cx + r, cy - r),
            (cx + r, cy + r), (cx - r, cy + r),
            (cx - r, cy - r),
        ]
        return {"type": "Polygon", "coordinates": [[[round(x, 7), round(y, 7)] for x, y in coords]]}

    # Find centroid and sort by angle
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    sorted_pts = sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    # Buffer outward slightly
    buffered = []
    for px, py in sorted_pts:
        dx = px - cx
        dy = py - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            scale = 1.3
            buffered.append((cx + dx * scale, cy + dy * scale))
        else:
            buffered.append((px, py))

    buffered.append(buffered[0])  # close ring
    return {"type": "Polygon", "coordinates": [[[round(x, 7), round(y, 7)] for x, y in buffered]]}


def generate_buildings(n: int = 30) -> list[dict]:
    """Generate n mock building features."""
    buildings = []

    for i in range(n):
        bid = f"BLD-{i+1:03d}"
        # Spread buildings around Hapeville center
        lat = CENTER_LAT + random.uniform(-0.012, 0.012)
        lon = CENTER_LON + random.uniform(-0.012, 0.012)

        # Building characteristics
        zoning = random.choice(["R-4", "R-4", "R-4", "R-5", "R-5"])  # bias toward R-4
        num_units = random.choice([4, 6, 8, 12, 16, 20, 24, 32, 48])
        num_floors = random.choice([2, 2, 3, 3, 3, 4])
        year_built = random.randint(1968, 2022)
        roof_area = random.randint(3000, 15000)

        # Solar
        avg_ghi = round(random.uniform(4.5, 5.5), 2)
        in_food_desert = random.random() < 0.35

        # HVAC proxy score components
        hvac_score = 0
        if year_built >= 1990:
            hvac_score += 30
        if num_units >= 8:
            hvac_score += 25
        if roof_area >= 5000:
            hvac_score += 20
        if num_floors <= 4:
            hvac_score += 15
        if random.random() < 0.6:  # flat roof
            hvac_score += 10

        # Estimated peak kW (rough: ~1.5 kW per unit)
        peak_kw = round(num_units * random.uniform(1.2, 2.0), 1)

        # Viability score
        s_structural = hvac_score
        s_area = min(100, round(roof_area / 120))
        s_solar = round((avg_ghi - 4.0) / 1.5 * 100)
        s_zoning = 100 if zoning == "R-4" else 60
        s_food_desert = 100 if in_food_desert else 30
        s_aggregation = random.randint(40, 90)

        score = round(
            s_structural * 0.30
            + s_area * 0.20
            + s_solar * 0.15
            + s_zoning * 0.15
            + s_food_desert * 0.15
            + s_aggregation * 0.05,
            1,
        )

        street_num = random.randint(100, 999)
        street = random.choice(STREETS)
        address = f"{street_num} {street}, Hapeville, GA 30354"

        owner_idx = i % len(OWNER_NAMES)
        owner_name = OWNER_NAMES[owner_idx]
        owner_email = f"mgmt@{OWNER_DOMAINS[owner_idx]}"
        owner_phone = f"(404) 555-{random.randint(1000, 9999):04d}"
        owner_address = f"PO Box {random.randint(1000, 9999)}, Atlanta GA 30301"

        # Subsidy summary placeholder (will be enriched by pipeline)
        programs = ["VPP-Consumer", "VPP-Utility", "TempCheck"]
        if in_food_desert:
            programs.append("GEFA-HER")
        if num_units >= 8:
            programs.append("GP-MF-Efficiency")

        annual_val = round(peak_kw * 15 + peak_kw * 150 + num_units * 75, 0)
        onetime_val = round(peak_kw * 750 + num_units * 500, 0)

        feature = {
            "type": "Feature",
            "geometry": _random_polygon(lat, lon, roof_area),
            "properties": {
                "id": bid,
                "address": address,
                "roof_area_sqft": roof_area,
                "year_built": year_built,
                "num_units": num_units,
                "num_floors": num_floors,
                "zoning": zoning,
                "owner_name": owner_name,
                "owner_address": owner_address,
                "owner_phone": owner_phone,
                "owner_email": owner_email,
                "avg_ghi": avg_ghi,
                "in_food_desert": in_food_desert,
                "hvac_proxy_score": hvac_score,
                "estimated_peak_kw": peak_kw,
                "aggregation_grid_id": "",  # assigned during grid generation
                "score": score,
                "score_structural": s_structural,
                "score_area": s_area,
                "score_solar": s_solar,
                "score_zoning": s_zoning,
                "score_food_desert": s_food_desert,
                "score_aggregation": s_aggregation,
                "subsidy_summary": {
                    "eligible_programs": programs,
                    "total_annual_value": annual_val,
                    "total_onetime_value": onetime_val,
                    "aggregation_tier": "Below Threshold",
                    "grid_combined_kw": 0,
                    "grid_building_count": 0,
                },
                "_lat": lat,
                "_lon": lon,
            },
        }
        buildings.append(feature)

    return buildings


def assign_grids(buildings: list[dict], n_grids: int = 6) -> list[dict]:
    """Cluster buildings into grids and generate grid features."""
    # Simple geographic clustering: divide into n_grids by proximity
    # Sort buildings by latitude, then chunk
    sorted_bldgs = sorted(buildings, key=lambda b: (
        b["properties"]["_lat"], b["properties"]["_lon"]
    ))

    chunk_size = max(1, len(sorted_bldgs) // n_grids)
    grids = []

    for g in range(n_grids):
        start = g * chunk_size
        end = start + chunk_size if g < n_grids - 1 else len(sorted_bldgs)
        members = sorted_bldgs[start:end]
        if not members:
            continue

        grid_id = f"GRID-{g+1:03d}"

        # Assign grid to each member building
        centroids = []
        combined_kw = 0
        total_units = 0
        total_roof = 0

        for bldg in members:
            bldg["properties"]["aggregation_grid_id"] = grid_id
            lat = bldg["properties"]["_lat"]
            lon = bldg["properties"]["_lon"]
            centroids.append((lon, lat))
            combined_kw += bldg["properties"]["estimated_peak_kw"]
            total_units += bldg["properties"]["num_units"]
            total_roof += bldg["properties"]["roof_area_sqft"]

        combined_kw = round(combined_kw, 1)
        meets_vpp = combined_kw >= 100
        meets_cl1 = combined_kw >= 200

        if meets_cl1:
            tier = "CL-1"
        elif meets_vpp:
            tier = "VPP"
        else:
            tier = "Below Threshold"

        # Potential annual value
        if meets_cl1:
            annual_value = round(combined_kw * 5.5 * 12)
        elif meets_vpp:
            annual_value = round(combined_kw * 15 + combined_kw * 1.50 * 100)
        else:
            annual_value = round(combined_kw * 5 * 12)

        bldgs_needed = max(0, int(math.ceil((200 - combined_kw) / 30))) if not meets_cl1 else 0

        # Update building subsidy summaries with grid info
        for bldg in members:
            sub = bldg["properties"]["subsidy_summary"]
            sub["aggregation_tier"] = tier
            sub["grid_combined_kw"] = combined_kw
            sub["grid_building_count"] = len(members)
            # Update aggregation score component
            if meets_cl1:
                bldg["properties"]["score_aggregation"] = 100
            elif meets_vpp:
                bldg["properties"]["score_aggregation"] = 80
            else:
                bldg["properties"]["score_aggregation"] = 40

        grid_feature = {
            "type": "Feature",
            "geometry": _convex_hull_polygon(centroids),
            "properties": {
                "grid_id": grid_id,
                "building_count": len(members),
                "total_units": total_units,
                "total_roof_sqft": total_roof,
                "combined_peak_kw": combined_kw,
                "meets_vpp_threshold": meets_vpp,
                "meets_cl1_threshold": meets_cl1,
                "aggregation_tier": tier,
                "potential_annual_value": annual_value,
                "buildings_needed_for_cl1": bldgs_needed,
            },
        }
        grids.append(grid_feature)

    return grids


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating mock building data …")
    buildings = generate_buildings(30)
    grids = assign_grids(buildings, n_grids=6)

    # Remove internal lat/lon fields
    for b in buildings:
        b["properties"].pop("_lat", None)
        b["properties"].pop("_lon", None)

    buildings_geojson = {"type": "FeatureCollection", "features": buildings}
    grids_geojson = {"type": "FeatureCollection", "features": grids}

    bld_path = OUTPUT_DIR / "scored_buildings.geojson"
    grid_path = OUTPUT_DIR / "aggregation_grids.geojson"

    with open(bld_path, "w") as f:
        json.dump(buildings_geojson, f, indent=2)
    print(f"  ✓ {len(buildings)} buildings → {bld_path}")

    with open(grid_path, "w") as f:
        json.dump(grids_geojson, f, indent=2)
    print(f"  ✓ {len(grids)} grids → {grid_path}")

    # Quick stats
    scores = [b["properties"]["score"] for b in buildings]
    high = sum(1 for s in scores if s >= 70)
    print(f"\n  Avg score: {sum(scores)/len(scores):.1f}")
    print(f"  High-potential (≥70): {high}")
    print(f"  Zoning: R-4={sum(1 for b in buildings if b['properties']['zoning']=='R-4')}, "
          f"R-5={sum(1 for b in buildings if b['properties']['zoning']=='R-5')}")
    tiers = {}
    for g in grids:
        t = g["properties"]["aggregation_tier"]
        tiers[t] = tiers.get(t, 0) + 1
    print(f"  Grid tiers: {tiers}")


if __name__ == "__main__":
    main()
