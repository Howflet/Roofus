"""Roofus FastAPI backend — serves scored building data, revenue projections,
subsidy calculations, and aggregation grids for the Hapeville multifamily
rooftop agriculture platform.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import buildings, grids, revenue, subsidies
from backend.routers import simulation  # optional add-on (greenhouse-network sim)
from backend.services import geojson_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load GeoJSON data into memory on startup."""
    logger.info("Loading GeoJSON data …")
    geojson_service.load_data()
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Roofus API",
    description=(
        "Multifamily rooftop agriculture scoring platform for Hapeville, GA. "
        "Serves building viability data, developer revenue projections, "
        "Georgia Power subsidy eligibility, and aggregation grid clusters."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# --- CORS (allow all origins for dev — covers Replit proxy + local) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(buildings.router)
app.include_router(revenue.router)
app.include_router(subsidies.router)
app.include_router(grids.router)
app.include_router(simulation.router)  # optional add-on (greenhouse-network sim)


# --- Health check ---
@app.get("/health", tags=["system"])
def health_check():
    """Simple health-check endpoint."""
    return {"status": "healthy", "service": "roofus-api", "version": "0.1.0"}
