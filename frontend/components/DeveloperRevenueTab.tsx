"use client";

import { useEffect, useState, useCallback } from "react";
import type { RevenueProjection, CropMix, BuildingProperties } from "@/lib/types";
import { postRevenue } from "@/lib/api";
import styles from "./DeveloperRevenueTab.module.css";

interface DeveloperRevenueTabProps {
  building: BuildingProperties;
}

export default function DeveloperRevenueTab({ building }: DeveloperRevenueTabProps) {
  const [data, setData] = useState<RevenueProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Determine recommendation based on solar exposure
  let recommendedType = "";
  let recommendedMix: CropMix;
  
  if (building.avg_ghi >= 5.0) {
    recommendedType = "Herbs & Microgreens (High Solar)";
    recommendedMix = { leafy_greens_pct: 10, herbs_pct: 60, microgreens_pct: 30 };
  } else if (building.avg_ghi >= 4.5) {
    recommendedType = "Leafy Greens & Herbs (Moderate Solar)";
    recommendedMix = { leafy_greens_pct: 50, herbs_pct: 40, microgreens_pct: 10 };
  } else {
    recommendedType = "Leafy Greens (Low Solar)";
    recommendedMix = { leafy_greens_pct: 80, herbs_pct: 10, microgreens_pct: 10 };
  }

  // Initial fetch with recommended mix
  useEffect(() => {
    setLoading(true);
    setError(null);
    postRevenue(building.id, { crop_mix: recommendedMix })
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [building.id, building.avg_ghi]);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <span>Loading revenue projections...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className={styles.error}>
        <span>⚠️</span>
        <span>{error ?? "Failed to load revenue data"}</span>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Recommendation UI */}
      <div className={styles.section} style={{ backgroundColor: 'var(--bg-card-hover)', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
        <h4 className="text-label" style={{ marginBottom: 8, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>☀️</span> Solar Exposure: {building.avg_ghi} GHI
        </h4>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: 0 }}>
          Recommended Crop Mix: <strong style={{ color: 'var(--text-primary)' }}>{recommendedType}</strong>
        </p>
      </div>

      {/* Production Potential */}
      <div className={styles.section}>

        {data.crop_production?.map((crop) => (
          <div key={crop.crop} className={styles.cropRow}>
            <div className={styles.cropHeader}>
              <span className={styles.cropName}>{crop.crop}</span>
              <span className={styles.cropRevenue}>
                {crop.yield_lbs.toLocaleString()} lbs
              </span>
            </div>
            <div className={styles.cropMeta}>
              {crop.area_sqft.toLocaleString()} sq ft allocated
            </div>
          </div>
        ))}
      </div>

      <div className="divider" />

      {/* Analysis Resources */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Financial Analysis Resources
        </h4>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "16px", lineHeight: "1.5" }}>
          To build an accurate pro-forma, leverage these trusted resources for current pricing, operational benchmarks, and local agricultural insights:
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <a href="https://www.ams.usda.gov/market-news/fruits-vegetables" target="_blank" rel="noreferrer" style={{ padding: "12px", border: "1px solid var(--border-light)", borderRadius: "8px", textDecoration: "none" }}>
            <strong style={{ display: "block", color: "var(--text-primary)", marginBottom: "4px" }}>USDA AMS Market News</strong>
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Current wholesale pricing for specialty crops.</span>
          </a>
          <a href="https://cea.cals.cornell.edu/" target="_blank" rel="noreferrer" style={{ padding: "12px", border: "1px solid var(--border-light)", borderRadius: "8px", textDecoration: "none" }}>
            <strong style={{ display: "block", color: "var(--text-primary)", marginBottom: "4px" }}>Cornell CEA</strong>
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Research and enterprise budgets for controlled environments.</span>
          </a>
          <a href="https://www.agritecture.com/" target="_blank" rel="noreferrer" style={{ padding: "12px", border: "1px solid var(--border-light)", borderRadius: "8px", textDecoration: "none" }}>
            <strong style={{ display: "block", color: "var(--text-primary)", marginBottom: "4px" }}>Agritecture</strong>
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Urban agriculture consulting and feasibility planning.</span>
          </a>
          <a href="https://ceac.arizona.edu/" target="_blank" rel="noreferrer" style={{ padding: "12px", border: "1px solid var(--border-light)", borderRadius: "8px", textDecoration: "none" }}>
            <strong style={{ display: "block", color: "var(--text-primary)", marginBottom: "4px" }}>Univ. of Arizona CEAC</strong>
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Technical resources for intensive greenhouse operations.</span>
          </a>
        </div>
      </div>
    </div>
  );
}
