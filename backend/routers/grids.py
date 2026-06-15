"""Aggregation grid endpoints — list, detail, member buildings."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services import geojson_service
from backend.services.aggregation_service import get_grid_detail

router = APIRouter(prefix="/grids", tags=["grids"])


@router.get("")
def list_grids():
    """Return all aggregation grid polygons as a GeoJSON FeatureCollection."""
    return geojson_service.get_all_grids()


@router.get("/{grid_id}")
def get_grid(grid_id: str):
    """Single grid detail including member buildings."""
    detail = get_grid_detail(grid_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Grid {grid_id} not found")
    return detail


@router.get("/{grid_id}/buildings")
def get_grid_buildings(grid_id: str):
    """Return all buildings belonging to a specific aggregation grid."""
    grid = geojson_service.get_grid(grid_id)
    if grid is None:
        raise HTTPException(status_code=404, detail=f"Grid {grid_id} not found")

    buildings = geojson_service.get_buildings_in_grid(grid_id)
    return {"type": "FeatureCollection", "features": buildings}
