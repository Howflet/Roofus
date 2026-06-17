"use client";

import { useEffect, useState } from "react";
import { type ScoreFactor } from "@/lib/types";
import styles from "./ScoreBreakdown.module.css";

interface ScoreBreakdownProps {
  factors: ScoreFactor[];
}

// Two-color system: good scores read emerald, low/at-risk scores read amber.
const GOOD_THRESHOLD = 50;

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
        const good = factor.score >= GOOD_THRESHOLD;
        const color = good ? "var(--accent)" : "var(--warn)";
        const fill = good
          ? "linear-gradient(90deg, #2BD39A, var(--accent))"
          : "linear-gradient(90deg, #D98A3A, var(--warn))";
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
                  backgroundImage: fill,
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
