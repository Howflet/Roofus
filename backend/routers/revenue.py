"""Developer revenue projection endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.models import RevenueAssumptions
from backend.services import geojson_service
from backend.services.revenue_service import (
    calculate_developer_revenue,
    calculate_owner_revenue,
)

router = APIRouter(tags=["revenue"])


@router.get("/buildings/{building_id}/revenue")
def get_revenue_projection(
    building_id: str,
    view: str = Query("developer", description="'developer' or 'owner'"),
):
    """Default revenue projection using standard assumptions.

    Use `?view=owner` for the building-owner perspective.
    """
    feat = geojson_service.get_building(building_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"Building {building_id} not found")

    props = feat["properties"]
    roof = props.get("roof_area_sqft", 0)

    if view == "owner":
        return calculate_owner_revenue(building_id, roof)

    return calculate_developer_revenue(building_id, roof)


@router.post("/buildings/{building_id}/revenue")
def post_revenue_projection(
    building_id: str,
    assumptions: RevenueAssumptions,
):
    """Custom revenue projection with user-adjusted assumptions.

    Pass a full RevenueAssumptions body to override crop mix,
    costs, prices, or lease rates.
    """
    feat = geojson_service.get_building(building_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"Building {building_id} not found")

    props = feat["properties"]
    roof = props.get("roof_area_sqft", 0)

    return calculate_developer_revenue(building_id, roof, assumptions=assumptions)
