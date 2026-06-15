"""Subsidy eligibility endpoints — per-building and per-grid."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models import SubsidyCustomRequest
from backend.services.subsidy_service import calculate_subsidy_detail
from backend.services.aggregation_service import get_grid_subsidies

router = APIRouter(tags=["subsidies"])


@router.get("/buildings/{building_id}/subsidies")
def get_building_subsidies(building_id: str):
    """Full subsidy eligibility breakdown for a building.

    Returns energy profile, threshold indicator, demand response programs,
    efficiency rebates, and aggregation bonus details.
    """
    result = calculate_subsidy_detail(building_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Building {building_id} not found")
    return result


@router.post("/buildings/{building_id}/subsidies")
def post_building_subsidies(building_id: str, body: SubsidyCustomRequest):
    """Recalculate subsidies with custom assumptions.

    Override peak kW, annual kWh, unit count, or LMI status.
    """
    result = calculate_subsidy_detail(
        building_id,
        estimated_peak_kw=body.estimated_peak_kw,
        estimated_annual_kwh=body.estimated_annual_kwh,
        num_units=body.num_units,
        is_lmi=body.is_lmi,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Building {building_id} not found")
    return result


@router.get("/grids/{grid_id}/subsidies")
def get_grid_subsidy_totals(grid_id: str):
    """Aggregation-level subsidy totals for a grid cluster.

    Shows combined program eligibility and total values.
    """
    result = get_grid_subsidies(grid_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Grid {grid_id} not found")
    return result
