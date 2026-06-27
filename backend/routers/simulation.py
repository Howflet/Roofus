"""
Greenhouse-network day-simulation endpoint (illustrative add-on).

GET /grids/{grid_id}/simulation -> 24-hour profile + evening peak-cut numbers.

This router + backend/services/network_sim_service.py + frontend/simulation.html
are an isolated feature. To remove it: delete those files and drop the
`include_router` line for it in backend/main.py.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services import geojson_service
from backend.services.network_sim_service import simulate_grid

router = APIRouter(prefix="/grids", tags=["simulation"])


@router.get("/{grid_id}/simulation")
def grid_simulation(grid_id: str):
    """Run the greenhouse-network day-simulation for one cluster."""
    grid = geojson_service.get_grid(grid_id)
    if grid is None:
        raise HTTPException(status_code=404, detail=f"Grid {grid_id} not found")
    return simulate_grid(grid["properties"])
