"use client";

import { useEffect, useState } from "react";
import { Leaf } from "lucide-react";
import type { ThresholdIndicator as ThresholdIndicatorType } from "@/lib/types";
import styles from "./ThresholdMeter.module.css";

interface ThresholdMeterProps {
  data: ThresholdIndicatorType;
  annualKwh: number;
}

export default function ThresholdMeter({ data, annualKwh }: ThresholdMeterProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 200);
    return () => clearTimeout(timer);
  }, []);

  const targetKwh = annualKwh - data.kwh_reduction_needed;
  const maxKwh = Math.max(annualKwh * 1.1, targetKwh * 1.2);
  const currentPct = (annualKwh / maxKwh) * 100;
  const targetPct = (targetKwh / maxKwh) * 100;
  const isAbove = data.pct_reduction_needed > 0;

  return (
    <div className={styles.container}>
      <h4 className="text-label" style={{ marginBottom: 16 }}>
        Energy Threshold Status
      </h4>

      <div className={styles.stats}>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Current Annual Usage</span>
          <span className={styles.statValue}>
            {annualKwh.toLocaleString()} kWh
          </span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Target Baseline</span>
          <span className={styles.statValue}>
            {targetKwh.toLocaleString()} kWh
          </span>
        </div>
        <div className={styles.statRow}>
          <span className={styles.statLabel}>Reduction Needed</span>
          <span
            className={styles.statValue}
            style={{
              color: isAbove
                ? "var(--score-moderate)"
                : "var(--accent-emerald)",
            }}
          >
            {Math.round(data.pct_reduction_needed)}%
          </span>
        </div>
      </div>

      {/* Meter bar */}
      <div className={styles.meterContainer}>
        <div className={styles.meterTrack}>
          {/* Current usage bar */}
          <div
            className={styles.meterFill}
            style={{
              width: mounted ? `${currentPct}%` : "0%",
              backgroundColor: isAbove
                ? "var(--score-moderate)"
                : "var(--accent-emerald)",
            }}
          />
          {/* Target marker */}
          <div
            className={styles.targetMarker}
            style={{ left: `${targetPct}%` }}
          >
            <div className={styles.targetLine} />
            <span className={styles.targetLabel}>target</span>
          </div>
        </div>
        <div className={styles.meterLabels}>
          <span>0</span>
          <span>CURRENT</span>
          <span>{Math.round(maxKwh / 1000)}k kWh</span>
        </div>
      </div>

      {/* Explainer */}
      <div className={styles.explainer}>
        <Leaf size={15} strokeWidth={1.7} className={`lucide ${styles.explainerIcon}`} />
        <span>
          Greenhouse load-shedding can reduce peak demand by ~
          {Math.round(data.greenhouse_demand_shed_potential_kw)} kW, helping
          maintain baseline tier.
        </span>
      </div>
    </div>
  );
}
