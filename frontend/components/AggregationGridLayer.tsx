"use client";

import { Source, Layer } from "react-map-gl/maplibre";
import type { GridCollection } from "@/lib/types";

interface AggregationGridLayerProps {
  grids: GridCollection | null;
  visible: boolean;
}

export default function AggregationGridLayer({
  grids,
  visible,
}: AggregationGridLayerProps) {
  if (!grids || !visible) return null;

  // Color by tier: CL-1 = emerald, VPP = cyan, Below = amber
  const fillColorExpr: maplibregl.ExpressionSpecification = [
    "match",
    ["get", "aggregation_tier"],
    "CL-1",
    "rgba(16, 185, 129, 0.12)",
    "DPEC-5",
    "rgba(16, 185, 129, 0.12)",
    "VPP",
    "rgba(6, 182, 212, 0.10)",
    "rgba(245, 158, 11, 0.08)", // Below Threshold / default
  ];

  const lineColorExpr: maplibregl.ExpressionSpecification = [
    "match",
    ["get", "aggregation_tier"],
    "CL-1",
    "#10B981",
    "DPEC-5",
    "#10B981",
    "VPP",
    "#06B6D4",
    "#F59E0B",
  ];

  return (
    <Source
      id="grids"
      type="geojson"
      data={grids as unknown as GeoJSON.FeatureCollection}
    >
      {/* Fill layer */}
      <Layer
        id="grids-fill"
        type="fill"
        paint={{
          "fill-color": fillColorExpr,
        }}
      />
      {/* Dashed outline */}
      <Layer
        id="grids-outline"
        type="line"
        paint={{
          "line-color": lineColorExpr,
          "line-width": 1.5,
          "line-dasharray": [4, 3],
          "line-opacity": 0.6,
        }}
      />
    </Source>
  );
}
