"use client";

import { useRef, useCallback, useState } from "react";
import Map, {
  Source,
  Layer,
  NavigationControl,
  type MapRef,
  type MapLayerMouseEvent,
} from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import type { BuildingCollection, BuildingProperties, GridCollection, Persona } from "@/lib/types";
import { getScoreColor } from "@/lib/types";
import AggregationGridLayer from "./AggregationGridLayer";
import styles from "./MapView.module.css";

// MapTiler dark style (if key provided) or CARTO Dark Matter (free)
const MAPTILER_KEY = process.env.NEXT_PUBLIC_MAPTILER_KEY;
const MAP_STYLE = MAPTILER_KEY
  ? `https://api.maptiler.com/maps/dataviz-dark/style.json?key=${MAPTILER_KEY}`
  : "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

// Hapeville, GA center
const INITIAL_VIEW = {
  longitude: -84.4102,
  latitude: 33.6693,
  zoom: 14,
};

interface MapViewProps {
  buildings: BuildingCollection | null;
  selectedBuildingId: string | null;
  hiddenTiers: Set<string>;
  onSelectBuilding: (building: BuildingProperties | null) => void;
  grids: GridCollection | null;
  showGrids: boolean;
}

interface TooltipData {
  x: number;
  y: number;
  address: string;
  score: number;
  area: number;
  zoning: string;
}

function getScoreTierName(score: number): string {
  if (score >= 85) return "Excellent";
  if (score >= 70) return "Good";
  if (score >= 50) return "Moderate";
  if (score >= 30) return "Below Average";
  return "Poor";
}

function makeScoreDots(score: number): { filled: number; empty: number } {
  const filled = Math.round(score / 10);
  return { filled, empty: 10 - filled };
}

export default function MapView({
  buildings,
  selectedBuildingId,
  hiddenTiers,
  onSelectBuilding,
  grids,
  showGrids,
}: MapViewProps) {
  const mapRef = useRef<MapRef>(null);
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // Filter out hidden tiers from the GeoJSON data
  const filteredBuildings = buildings
    ? {
        ...buildings,
        features: buildings.features.filter((f) => {
          const tier = getScoreTierName(f.properties.score);
          return !hiddenTiers.has(tier);
        }),
      }
    : null;

  // Handle hover
  const onMouseMove = useCallback(
    (e: MapLayerMouseEvent) => {
      if (!e.features?.length) {
        setTooltip(null);
        setHoveredId(null);
        if (mapRef.current) {
          mapRef.current.getCanvas().style.cursor = "";
        }
        return;
      }

      const feature = e.features[0];
      const props = feature.properties;
      if (!props) return;

      setHoveredId(props.id as string);
      if (mapRef.current) {
        mapRef.current.getCanvas().style.cursor = "pointer";
      }

      setTooltip({
        x: e.point.x,
        y: e.point.y - 12,
        address: props.address as string,
        score: props.score as number,
        area: props.roof_area_sqft as number,
        zoning: props.zoning as string,
      });
    },
    []
  );

  const onMouseLeave = useCallback(() => {
    setTooltip(null);
    setHoveredId(null);
    if (mapRef.current) {
      mapRef.current.getCanvas().style.cursor = "";
    }
  }, []);

  // Handle click
  const onClick = useCallback(
    (e: MapLayerMouseEvent) => {
      if (!e.features?.length) {
        onSelectBuilding(null);
        return;
      }

      const feature = e.features[0];
      const props = feature.properties;
      if (!props) return;

      // We need full properties including nested subsidy_summary
      // Since MapLibre flattens GeoJSON properties, find the full feature
      const fullFeature = buildings?.features.find(
        (f) => f.properties.id === props.id
      );
      if (!fullFeature) return;

      // Fly to the building
      const geom = fullFeature.geometry;
      if (geom.type === "Polygon") {
        const coords = (geom as GeoJSON.Polygon).coordinates[0];
        const avgLng = coords.reduce((s, c) => s + c[0], 0) / coords.length;
        const avgLat = coords.reduce((s, c) => s + c[1], 0) / coords.length;

        mapRef.current?.flyTo({
          center: [avgLng, avgLat],
          zoom: 16,
          duration: 500,
          padding: { top: 0, bottom: 0, left: 0, right: 440 },
        });
      }

      onSelectBuilding(fullFeature.properties);
      setTooltip(null);
    },
    [buildings, onSelectBuilding]
  );

  // Build the fill-color expression for MapLibre
  // Using "step" for discrete color tiers
  const fillColorExpr: maplibregl.ExpressionSpecification = [
    "step",
    ["get", "score"],
    "#EF4444", // 0-29: red
    30,
    "#F97316", // 30-49: orange
    50,
    "#F59E0B", // 50-69: amber
    70,
    "#84CC16", // 70-84: lime
    85,
    "#10B981", // 85-100: emerald
  ];

  // Opacity dims non-selected buildings when one is selected
  const fillOpacityExpr: maplibregl.ExpressionSpecification = selectedBuildingId
    ? [
        "case",
        ["==", ["get", "id"], selectedBuildingId],
        0.9,
        0.35,
      ]
    : [
        "case",
        ["==", ["get", "id"], hoveredId ?? ""],
        0.9,
        0.7,
      ];

  return (
    <div className={styles.container}>
      <Map
        ref={mapRef}
        initialViewState={INITIAL_VIEW}
        mapStyle={MAP_STYLE}
        style={{ width: "100%", height: "100%" }}
        interactiveLayerIds={["buildings-fill"]}
        onMouseMove={onMouseMove}
        onMouseLeave={onMouseLeave}
        onClick={onClick}
        attributionControl={{ compact: true }}
      >
        <NavigationControl position="bottom-right" showCompass={false} />

        {/* Aggregation grid layer */}
        <AggregationGridLayer
          grids={grids}
          visible={showGrids}
        />

        {filteredBuildings && (
          <Source
            id="buildings"
            type="geojson"
            data={filteredBuildings as GeoJSON.FeatureCollection}
          >
            {/* Fill layer */}
            <Layer
              id="buildings-fill"
              type="fill"
              paint={{
                "fill-color": fillColorExpr,
                "fill-opacity": fillOpacityExpr as unknown as number,
              }}
            />

            {/* Outline layer */}
            <Layer
              id="buildings-outline"
              type="line"
              paint={{
                "line-color": selectedBuildingId
                  ? [
                      "case",
                      ["==", ["get", "id"], selectedBuildingId],
                      "#10B981",
                      "rgba(255, 255, 255, 0.15)",
                    ]
                  : hoveredId
                    ? [
                        "case",
                        ["==", ["get", "id"], hoveredId],
                        "#10B981",
                        "rgba(255, 255, 255, 0.15)",
                      ]
                    : ("rgba(255, 255, 255, 0.15)" as unknown as maplibregl.ExpressionSpecification),
                "line-width": selectedBuildingId
                  ? [
                      "case",
                      ["==", ["get", "id"], selectedBuildingId],
                      2.5,
                      1,
                    ]
                  : hoveredId
                    ? [
                        "case",
                        ["==", ["get", "id"], hoveredId],
                        2,
                        1,
                      ]
                    : (1 as unknown as maplibregl.ExpressionSpecification),
              }}
            />
          </Source>
        )}
      </Map>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="building-tooltip"
          style={{
            left: tooltip.x,
            top: tooltip.y,
            transform: "translate(-50%, -100%)",
          }}
        >
          <div className="tooltip-address">📍 {tooltip.address}</div>
          <div className="tooltip-score">
            Score: {Math.round(tooltip.score)}{" "}
            <span
              className="tooltip-dots"
              style={{ color: getScoreColor(tooltip.score) }}
            >
              {"●".repeat(makeScoreDots(tooltip.score).filled)}
              {"○".repeat(makeScoreDots(tooltip.score).empty)}
            </span>
          </div>
          <div className="tooltip-meta">
            {tooltip.area.toLocaleString()} sq ft
          </div>
        </div>
      )}
    </div>
  );
}
