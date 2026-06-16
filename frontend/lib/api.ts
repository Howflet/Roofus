/**
 * API fetch helpers for the Roofus backend.
 */

import type {
  BuildingCollection,
  BuildingFeature,
  BuildingStats,
  GridCollection,
  RevenueProjection,
  RevenueAssumptions,
  BuildingSubsidyDetail,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ---------------------------------------------------------------------------
// Generic fetcher
// ---------------------------------------------------------------------------

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Buildings
// ---------------------------------------------------------------------------

export interface BuildingFilters {
  min_score?: number;
  zoning?: string;
  grid_id?: string;
  in_food_desert?: boolean;
  min_roof_area?: number;
}

export async function fetchBuildings(filters?: BuildingFilters): Promise<BuildingCollection> {
  const params = new URLSearchParams();
  if (filters) {
    if (filters.min_score !== undefined) params.set("min_score", String(filters.min_score));
    if (filters.zoning) params.set("zoning", filters.zoning);
    if (filters.grid_id) params.set("grid_id", filters.grid_id);
    if (filters.in_food_desert !== undefined)
      params.set("in_food_desert", String(filters.in_food_desert));
    if (filters.min_roof_area !== undefined)
      params.set("min_roof_area", String(filters.min_roof_area));
  }
  const qs = params.toString();
  return fetchJSON<BuildingCollection>(`/buildings${qs ? `?${qs}` : ""}`);
}

export async function fetchBuilding(id: string): Promise<BuildingFeature> {
  return fetchJSON<BuildingFeature>(`/buildings/${id}`);
}

export async function fetchBuildingStats(): Promise<BuildingStats> {
  return fetchJSON<BuildingStats>(`/buildings/stats`);
}

// ---------------------------------------------------------------------------
// Grids
// ---------------------------------------------------------------------------

export async function fetchGrids(): Promise<GridCollection> {
  return fetchJSON<GridCollection>("/grids");
}

// ---------------------------------------------------------------------------
// Revenue
// ---------------------------------------------------------------------------

export async function fetchRevenue(buildingId: string, view: "developer" | "owner" = "developer"): Promise<RevenueProjection> {
  return fetchJSON<RevenueProjection>(`/buildings/${buildingId}/revenue?view=${view}`);
}

export async function postRevenue(buildingId: string, assumptions: RevenueAssumptions): Promise<RevenueProjection> {
  return fetchJSON<RevenueProjection>(`/buildings/${buildingId}/revenue`, {
    method: "POST",
    body: JSON.stringify(assumptions),
  });
}

// ---------------------------------------------------------------------------
// Subsidies
// ---------------------------------------------------------------------------

export async function fetchSubsidies(buildingId: string): Promise<BuildingSubsidyDetail> {
  return fetchJSON<BuildingSubsidyDetail>(`/buildings/${buildingId}/subsidies`);
}

