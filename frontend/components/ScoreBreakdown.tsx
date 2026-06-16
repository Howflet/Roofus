"use client";

import { useEffect, useState } from "react";
import { getScoreColor, type ScoreFactor } from "@/lib/types";
import styles from "./ScoreBreakdown.module.css";

interface ScoreBreakdownProps {
  factors: ScoreFactor[];
}

export default function ScoreBreakdown({ factors }: ScoreBreakdownProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Small delay to trigger the CSS animation
    const timer = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={styles.container}>
      <h3 className="text-label" style={{ marginBottom: 16 }}>
        Score Breakdown
      </h3>
      {factors.map((factor, i) => {
        const color = getScoreColor(factor.score);
        return (
          <div
            key={factor.key}
            className={styles.row}
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className={styles.rowHeader}>
              <span className={styles.label}>{factor.label}</span>
              <span className={styles.score} style={{ color }}>
                {factor.score}
              </span>
            </div>
            <div className={styles.barTrack}>
              <div
                className={styles.barFill}
                style={{
                  width: mounted ? `${Math.min(factor.score, 100)}%` : "0%",
                  backgroundColor: color,
                  transitionDelay: `${i * 100}ms`,
                }}
              />
            </div>
            <span className={styles.rawValue}>{factor.rawValue}</span>
          </div>
        );
      })}
    </div>
  );
}
