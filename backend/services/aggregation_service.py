"""Aggregation grid service — cluster-level calculations.

Works with the in-memory grid data loaded by geojson_service.
Provides grid-level subsidy totals and building membership lookups.
"""

from __future__ import annotations

from typing import Any

from backend.services import geojson_service


# ---------------------------------------------------------------------------
# Tier thresholds (kW)
# ---------------------------------------------------------------------------

VPP_THRESHOLD_KW = 100
CL1_THRESHOLD_KW = 200


def get_grid_detail(grid_id: str) -> dict[str, Any] | None:
    """Return grid feature plus its member buildings."""
    grid = geojson_service.get_grid(grid_id)
    if grid is None:
        return None

    buildings = geojson_service.get_buildings_in_grid(grid_id)
    return {
        "grid": grid,
        "buildings": buildings,
    }


def get_grid_subsidies(grid_id: str) -> dict[str, Any] | None:
    """Aggregation-level subsidy totals for a grid cluster."""
    grid = geojson_service.get_grid(grid_id)
    if grid is None:
        return None

    props = grid["properties"]
    # DR thresholds compare against curtailable (sheddable) load, not total peak.
    combined_kw = props.get("combined_curtailable_kw", props.get("combined_peak_kw", 0))
    peak_kw = props.get("combined_peak_kw", 0)
    building_count = props.get("building_count", 0)
    tier = props.get("aggregation_tier", "Below Threshold")

    # Sum subsidy values across member buildings
    buildings = geojson_service.get_buildings_in_grid(grid_id)
    total_annual = 0.0
    total_onetime = 0.0
    for bldg in buildings:
        sub = bldg["properties"].get("subsidy_summary", {})
        total_annual += sub.get("total_annual_value", 0)
        total_onetime += sub.get("total_onetime_value", 0)

    # Aggregation-dependent program values
    programs: dict[str, Any] = {}

    if combined_kw >= CL1_THRESHOLD_KW:
        programs["cl1"] = {
            "eligible": True,
            "estimated_annual_value": round(combined_kw * 5.5 * 12),
            "description": f"CL-1 Curtailable Load — {combined_kw} kW qualifies.",
        }
        programs["dpec5"] = {
            "eligible": True,
            "estimated_annual_value": round(combined_kw * 4.0 * 4),
            "description": "DPEC-5 summer demand + energy credits (Jun-Sep).",
        }
    else:
        shortfall = round(CL1_THRESHOLD_KW - combined_kw)
        programs["cl1"] = {
            "eligible": False,
            "kw_shortfall": shortfall,
            "buildings_needed": max(1, int(shortfall / 30)),
            "description": f"Need {shortfall} more kW to reach CL-1 threshold.",
        }
        programs["dpec5"] = {
            "eligible": False,
            "kw_shortfall": shortfall,
            "description": "Same 200 kW threshold as CL-1.",
        }

    if combined_kw >= VPP_THRESHOLD_KW:
        programs["vpp_aggregated"] = {
            "eligible": True,
            "estimated_annual_value": round(combined_kw * 15 + combined_kw * 1.50 * 100),
            "description": "VPP aggregated value across grid.",
        }
    else:
        programs["vpp_aggregated"] = {
            "eligible": False,
            "kw_shortfall": round(VPP_THRESHOLD_KW - combined_kw),
            "description": f"Grid at {combined_kw} kW — needs {VPP_THRESHOLD_KW} kW for VPP.",
        }

    return {
        "grid_id": grid_id,
        "aggregation_tier": tier,
        "combined_curtailable_kw": combined_kw,
        "combined_peak_kw": peak_kw,
        "building_count": building_count,
        "total_annual_subsidy_value": round(total_annual),
        "total_onetime_value": round(total_onetime),
        "programs": programs,
    }
