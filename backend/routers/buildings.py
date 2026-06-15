"""Building endpoints — list, filter, detail, and aggregate stats."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.services import geojson_service

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("")
def list_buildings(
    min_score: float | None = Query(None, description="Minimum viability score (0-100)"),
    zoning: str | None = Query(None, description="Zoning code filter (R-4 or R-5)"),
    grid_id: str | None = Query(None, description="Aggregation grid ID"),
    in_food_desert: bool | None = Query(None, description="Filter to food desert areas"),
    min_roof_area: float | None = Query(None, description="Minimum roof area in sq ft"),
):
    """Return a GeoJSON FeatureCollection of scored multifamily buildings.

    All parameters are optional filters that can be combined.
    """
    return geojson_service.get_all_buildings(
        min_score=min_score,
        zoning=zoning,
        grid_id=grid_id,
        in_food_desert=in_food_desert,
        min_roof_area=min_roof_area,
    )


@router.get("/stats")
def building_stats():
    """Aggregate statistics across all scored buildings."""
    return geojson_service.get_building_stats()


@router.get("/{building_id}")
def get_building(building_id: str):
    """Return a single building feature by ID with full detail."""
    feat = geojson_service.get_building(building_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"Building {building_id} not found")
    return feat
