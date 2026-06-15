"""GeoJSON data service — loads and queries building & grid data."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# In-memory stores — populated at startup
_buildings: dict[str, dict[str, Any]] = {}  # id → feature
_buildings_list: list[dict[str, Any]] = []
_grids: dict[str, dict[str, Any]] = {}  # grid_id → feature
_grids_list: list[dict[str, Any]] = []

# Default data directory (relative to backend/)
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "pipeline" / "data" / "processed"


def load_data(
    buildings_path: str | Path | None = None,
    grids_path: str | Path | None = None,
) -> None:
    """Load GeoJSON files into memory.  Called once at startup."""
    global _buildings, _buildings_list, _grids, _grids_list

    buildings_file = Path(buildings_path) if buildings_path else DATA_DIR / "scored_buildings.geojson"
    grids_file = Path(grids_path) if grids_path else DATA_DIR / "aggregation_grids.geojson"

    # --- Buildings ---
    if buildings_file.exists():
        with open(buildings_file) as f:
            data = json.load(f)
        _buildings_list = data.get("features", [])
        _buildings = {feat["properties"]["id"]: feat for feat in _buildings_list}
        logger.info("Loaded %d buildings from %s", len(_buildings), buildings_file)
    else:
        logger.warning("Buildings file not found: %s", buildings_file)

    # --- Grids ---
    if grids_file.exists():
        with open(grids_file) as f:
            data = json.load(f)
        _grids_list = data.get("features", [])
        _grids = {feat["properties"]["grid_id"]: feat for feat in _grids_list}
        logger.info("Loaded %d grids from %s", len(_grids), grids_file)
    else:
        logger.warning("Grids file not found: %s", grids_file)


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def get_all_buildings(
    *,
    min_score: float | None = None,
    zoning: str | None = None,
    grid_id: str | None = None,
    in_food_desert: bool | None = None,
    min_roof_area: float | None = None,
) -> dict[str, Any]:
    """Return a GeoJSON FeatureCollection, optionally filtered."""
    features = _buildings_list

    if min_score is not None:
        features = [f for f in features if f["properties"].get("score", 0) >= min_score]
    if zoning is not None:
        features = [f for f in features if f["properties"].get("zoning") == zoning]
    if grid_id is not None:
        features = [f for f in features if f["properties"].get("aggregation_grid_id") == grid_id]
    if in_food_desert is not None:
        features = [f for f in features if f["properties"].get("in_food_desert") == in_food_desert]
    if min_roof_area is not None:
        features = [f for f in features if f["properties"].get("roof_area_sqft", 0) >= min_roof_area]

    return {"type": "FeatureCollection", "features": features}


def get_building(building_id: str) -> dict[str, Any] | None:
    """Return a single building feature by ID."""
    return _buildings.get(building_id)


def get_building_stats() -> dict[str, Any]:
    """Aggregate statistics across all loaded buildings."""
    total = len(_buildings_list)
    if total == 0:
        return {
            "total_buildings": 0,
            "avg_score": 0,
            "high_potential": 0,
            "total_roof_sqft": 0,
            "total_units": 0,
            "by_zoning": {},
            "by_score_tier": {},
        }

    scores = [f["properties"].get("score", 0) for f in _buildings_list]
    avg_score = sum(scores) / total

    high_potential = sum(1 for s in scores if s >= 70)
    total_roof = sum(f["properties"].get("roof_area_sqft", 0) for f in _buildings_list)
    total_units = sum(f["properties"].get("num_units", 0) for f in _buildings_list)

    by_zoning: dict[str, int] = {}
    for f in _buildings_list:
        z = f["properties"].get("zoning", "Unknown")
        by_zoning[z] = by_zoning.get(z, 0) + 1

    by_tier: dict[str, int] = {"Excellent": 0, "Good": 0, "Moderate": 0, "Below Average": 0, "Poor": 0}
    for s in scores:
        if s >= 85:
            by_tier["Excellent"] += 1
        elif s >= 70:
            by_tier["Good"] += 1
        elif s >= 50:
            by_tier["Moderate"] += 1
        elif s >= 30:
            by_tier["Below Average"] += 1
        else:
            by_tier["Poor"] += 1

    return {
        "total_buildings": total,
        "avg_score": round(avg_score, 1),
        "high_potential": high_potential,
        "total_roof_sqft": round(total_roof, 0),
        "total_units": total_units,
        "by_zoning": by_zoning,
        "by_score_tier": by_tier,
    }


# ---------------------------------------------------------------------------
# Grid queries
# ---------------------------------------------------------------------------


def get_all_grids() -> dict[str, Any]:
    """Return all aggregation grids as a GeoJSON FeatureCollection."""
    return {"type": "FeatureCollection", "features": _grids_list}


def get_grid(grid_id: str) -> dict[str, Any] | None:
    """Return a single grid feature by ID."""
    return _grids.get(grid_id)


def get_buildings_in_grid(grid_id: str) -> list[dict[str, Any]]:
    """Return all building features belonging to the given grid."""
    return [
        f for f in _buildings_list
        if f["properties"].get("aggregation_grid_id") == grid_id
    ]
