"use client";

import { useEffect, useState, useCallback } from "react";
import type { BuildingCollection, BuildingProperties, BuildingStats, GridCollection, Persona } from "@/lib/types";
import { fetchBuildings, fetchBuildingStats, fetchGrids } from "@/lib/api";
import type { FilterState } from "@/components/Header";
import MapView from "@/components/MapView";
import Header from "@/components/Header";
import Legend from "@/components/Legend";
import DetailPanel from "@/components/DetailPanel";

export default function Home() {
  const [buildings, setBuildings] = useState<BuildingCollection | null>(null);
  const [stats, setStats] = useState<BuildingStats | null>(null);
  const [grids, setGrids] = useState<GridCollection | null>(null);
  const [selectedBuilding, setSelectedBuilding] = useState<BuildingProperties | null>(null);
  const [hiddenTiers, setHiddenTiers] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [persona, setPersona] = useState<Persona>("developer");

  // Restore persona from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("roofus-persona");
    if (stored === "developer" || stored === "owner") {
      setPersona(stored);
    }
  }, []);

  // Load initial data
  useEffect(() => {
    async function load() {
      try {
        const [bldgs, bldgStats, gridData] = await Promise.all([
          fetchBuildings(),
          fetchBuildingStats(),
          fetchGrids().catch(() => null), // grids are optional
        ]);
        setBuildings(bldgs);
        setStats(bldgStats);
        if (gridData) setGrids(gridData);
      } catch (err) {
        console.error("Failed to load data:", err);
        setError("Failed to load building data. Make sure the API server is running on port 8000.");
      }
    }
    load();
  }, []);

  // Handle persona change
  const handlePersonaChange = useCallback((newPersona: Persona) => {
    setPersona(newPersona);
    localStorage.setItem("roofus-persona", newPersona);
  }, []);

  // Handle filter application
  const handleApplyFilters = useCallback(async (filters: FilterState) => {
    try {
      const bldgs = await fetchBuildings({
        min_score: filters.minScore > 0 ? filters.minScore : undefined,
        zoning: filters.buildingTypes.length === 1 ? filters.buildingTypes[0] : undefined,
        in_food_desert: filters.foodDesertOnly ? true : undefined,
        min_roof_area: filters.minRoofSize > 0 ? filters.minRoofSize : undefined,
      });
      setBuildings(bldgs);

      // Update stats based on filtered data
      const filteredStats: BuildingStats = {
        total_buildings: bldgs.features.length,
        avg_score:
          bldgs.features.length > 0
            ? Math.round(
                (bldgs.features.reduce((s, f) => s + f.properties.score, 0) /
                  bldgs.features.length) *
                  10
              ) / 10
            : 0,
        high_potential: bldgs.features.filter((f) => f.properties.score >= 70).length,
        total_roof_sqft: bldgs.features.reduce(
          (s, f) => s + f.properties.roof_area_sqft,
          0
        ),
        total_units: bldgs.features.reduce((s, f) => s + f.properties.num_units, 0),
        by_zoning: {},
        by_score_tier: {
          Excellent: 0,
          Good: 0,
          Moderate: 0,
          "Below Average": 0,
          Poor: 0,
        },
      };

      for (const f of bldgs.features) {
        const z = f.properties.zoning;
        filteredStats.by_zoning[z] = (filteredStats.by_zoning[z] || 0) + 1;

        const s = f.properties.score;
        if (s >= 85) filteredStats.by_score_tier["Excellent"]++;
        else if (s >= 70) filteredStats.by_score_tier["Good"]++;
        else if (s >= 50) filteredStats.by_score_tier["Moderate"]++;
        else if (s >= 30) filteredStats.by_score_tier["Below Average"]++;
        else filteredStats.by_score_tier["Poor"]++;
      }

      setStats(filteredStats);
    } catch (err) {
      console.error("Failed to apply filters:", err);
    }
  }, []);

  // Toggle legend tier visibility
  const handleToggleTier = useCallback((tier: string) => {
    setHiddenTiers((prev) => {
      const next = new Set(prev);
      if (next.has(tier)) {
        next.delete(tier);
      } else {
        next.add(tier);
      }
      return next;
    });
  }, []);

  // Select building
  const handleSelectBuilding = useCallback((building: BuildingProperties | null) => {
    setSelectedBuilding(building);
  }, []);

  return (
    <main style={{ position: "relative", width: "100vw", height: "100vh", overflow: "hidden" }}>
      {/* Full-screen map */}
      <MapView
        buildings={buildings}
        selectedBuildingId={selectedBuilding?.id ?? null}
        hiddenTiers={hiddenTiers}
        onSelectBuilding={handleSelectBuilding}
        grids={grids}
        persona={persona}
      />

      {/* Floating UI overlays */}
      <Header
        stats={stats}
        onApplyFilters={handleApplyFilters}
        persona={persona}
        onPersonaChange={handlePersonaChange}
      />
      <Legend stats={stats} hiddenTiers={hiddenTiers} onToggleTier={handleToggleTier} />

      {/* Detail panel (conditional) */}
      {selectedBuilding && (
        <DetailPanel
          key={selectedBuilding.id}
          building={selectedBuilding}
          onClose={() => setSelectedBuilding(null)}
          persona={persona}
        />
      )}

      {/* Error overlay */}
      {error && (
        <div
          style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            zIndex: 9999,
            maxWidth: 400,
            textAlign: "center",
          }}
          className="glass"
        >
          <div style={{ padding: 32 }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>⚠️</div>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
              Connection Error
            </h2>
            <p style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.5 }}>
              {error}
            </p>
            <button
              className="btn btn-primary"
              style={{ marginTop: 16 }}
              onClick={() => {
                setError(null);
                window.location.reload();
              }}
            >
              Retry
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
