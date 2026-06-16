"use client";

import { useEffect, useState } from "react";
import type { AggregationBonus } from "@/lib/types";
import styles from "./AggregationBonusCard.module.css";

interface AggregationBonusCardProps {
  data: AggregationBonus;
}

const TIERS = [
  { kw: 100, label: "VPP", color: "var(--accent-cyan)" },
  { kw: 200, label: "CL-1", color: "var(--accent-emerald)" },
];

export default function AggregationBonusCard({ data }: AggregationBonusCardProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 300);
    return () => clearTimeout(timer);
  }, []);

  const maxKw = 260; // visual max for the progress bar
  const currentPct = Math.min((data.grid_combined_kw / maxKw) * 100, 100);
  const hasNextTier = data.next_tier && data.kw_to_next_tier > 0;

  return (
    <div className={styles.container}>
      <h4 className="text-label" style={{ marginBottom: 16 }}>
        Neighborhood Aggregation Bonus
      </h4>

      {/* Grid info */}
      <div className={styles.gridInfo}>
        <span className={styles.gridId}>Grid: {data.grid_id}</span>
        <span className={styles.gridMeta}>
          Combined Load: {Math.round(data.grid_combined_kw)} kW
        </span>
      </div>

      {/* Progress bar with tier markers */}
      <div className={styles.progressContainer}>
        <div className={styles.progressTrack}>
          <div
            className={styles.progressFill}
            style={{
              width: mounted ? `${currentPct}%` : "0%",
            }}
          />
          {/* Tier markers */}
          {TIERS.map((tier) => {
            const pct = (tier.kw / maxKw) * 100;
            const reached = data.grid_combined_kw >= tier.kw;
            return (
              <div
                key={tier.label}
                className={styles.tierMarker}
                style={{ left: `${pct}%` }}
              >
                <div
                  className={styles.tierLine}
                  style={{
                    backgroundColor: reached
                      ? tier.color
                      : "var(--text-muted)",
                  }}
                />
                <span
                  className={styles.tierLabel}
                  style={{
                    color: reached ? tier.color : "var(--text-muted)",
                  }}
                >
                  {tier.label}
                  {reached && " ✓"}
                </span>
                <span className={styles.tierKw}>{tier.kw} kW</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Current tier + value */}
      <div className={styles.currentTier}>
        <div className={styles.tierRow}>
          <span className={styles.tierKey}>Current tier</span>
          <span className={styles.tierVal}>{data.current_tier}</span>
        </div>
        <div className={styles.tierRow}>
          <span className={styles.tierKey}>Grid annual value</span>
          <span className={styles.tierVal} style={{ color: "var(--accent-emerald)" }}>
            ${data.current_grid_annual_value.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Unlock section */}
      {hasNextTier && (
        <div className={styles.unlockSection}>
          <div className={styles.unlockHeader}>
            <span className={styles.unlockIcon}>🔓</span>
            <span className={styles.unlockTitle}>
              Unlock {data.next_tier}
            </span>
          </div>
          <div className={styles.unlockStats}>
            <div className={styles.unlockRow}>
              <span>Need</span>
              <span>
                {Math.round(data.kw_to_next_tier)} kW more (≈
                {data.buildings_to_next_tier} building
                {data.buildings_to_next_tier !== 1 ? "s" : ""})
              </span>
            </div>
            <div className={styles.unlockRow}>
              <span>Unlocks</span>
              <span style={{ color: "var(--accent-emerald)", fontWeight: 600 }}>
                ${data.next_tier_annual_value.toLocaleString()}/yr{" "}
                <span style={{ color: "var(--score-good)" }}>
                  (+${data.uplift_if_threshold_met.toLocaleString()})
                </span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
