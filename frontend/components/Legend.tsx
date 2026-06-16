"use client";

import { useState, useCallback } from "react";
import type { BuildingStats } from "@/lib/types";
import styles from "./Legend.module.css";

interface LegendProps {
  stats: BuildingStats | null;
  hiddenTiers: Set<string>;
  onToggleTier: (tier: string) => void;
}

const TIERS = [
  { key: "Excellent", label: "Excellent (85-100)", color: "#10B981" },
  { key: "Good", label: "Good (70-84)", color: "#84CC16" },
  { key: "Moderate", label: "Moderate (50-69)", color: "#F59E0B" },
  { key: "Below Average", label: "Below Avg (30-49)", color: "#F97316" },
  { key: "Poor", label: "Poor (0-29)", color: "#EF4444" },
];

export default function Legend({ stats, hiddenTiers, onToggleTier }: LegendProps) {
  const [collapsed, setCollapsed] = useState(false);

  const toggleCollapse = useCallback(() => {
    setCollapsed((prev) => !prev);
  }, []);

  const total = stats?.total_buildings ?? 0;

  if (collapsed) {
    return (
      <button
        className={`glass ${styles.collapsedPill}`}
        onClick={toggleCollapse}
        id="legend-expand"
      >
        <div className={styles.miniGradient} />
        <span className={styles.miniLabel}>{total}</span>
      </button>
    );
  }

  return (
    <div className={`glass ${styles.legend}`} id="legend-panel">
      <div className={styles.header}>
        <h3 className="text-label">Viability Score</h3>
        <button className={styles.collapseBtn} onClick={toggleCollapse} title="Collapse legend">
          −
        </button>
      </div>

      {/* Gradient bar */}
      <div className={styles.gradientBar} />
      <div className={styles.gradientLabels}>
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>

      {/* Category rows */}
      <div className={styles.tiers}>
        {TIERS.map((tier) => {
          const count = stats?.by_score_tier?.[tier.key] ?? 0;
          const hidden = hiddenTiers.has(tier.key);
          return (
            <button
              key={tier.key}
              className={`${styles.tierRow} ${hidden ? styles.tierHidden : ""}`}
              onClick={() => onToggleTier(tier.key)}
              id={`legend-tier-${tier.key.toLowerCase().replace(" ", "-")}`}
            >
              <span
                className={styles.tierDot}
                style={{
                  backgroundColor: hidden ? "var(--text-muted)" : tier.color,
                }}
              />
              <span
                className={styles.tierLabel}
                style={{
                  textDecoration: hidden ? "line-through" : "none",
                }}
              >
                {tier.label}
              </span>
              <span className={styles.tierCount}>{count}</span>
            </button>
          );
        })}
      </div>

      {/* Total */}
      <div className={styles.total}>
        <div className={styles.totalDivider} />
        <span>Total: {total.toLocaleString()} buildings</span>
      </div>

      {/* Grid info */}
      <div className={styles.gridInfo}>
        <div className={styles.gridItem}>
          <div className={styles.dashedBox} />
          <span className={styles.gridLabel}>Aggregation Grids (0.5mi)</span>
        </div>
      </div>
    </div>
  );
}
