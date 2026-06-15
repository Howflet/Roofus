"use client";

import { useEffect, useRef, useState } from "react";
import { getScoreColor, getScoreLabel } from "@/lib/types";
import styles from "./ScoreGauge.module.css";

interface ScoreGaugeProps {
  score: number;
  size?: number;
}

export default function ScoreGauge({ score, size = 160 }: ScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [mounted, setMounted] = useState(false);
  const rafRef = useRef<number>(0);

  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  // 270° sweep (open at the bottom)
  const arcLength = (270 / 360) * circumference;
  const center = size / 2;

  // Rotation to start the arc at bottom-left (135°)
  const startAngle = 135;

  const scoreColor = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);
  const fillLength = (score / 100) * arcLength;

  useEffect(() => {
    setMounted(true);
    // Count-up animation
    const start = performance.now();
    const duration = 800;

    function animate(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(eased * score));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    }

    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [score]);

  return (
    <div className={styles.container} style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className={styles.svg}
      >
        {/* Background track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(${startAngle} ${center} ${center})`}
        />
        {/* Filled arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={scoreColor}
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={mounted ? arcLength - fillLength : arcLength}
          strokeLinecap="round"
          transform={`rotate(${startAngle} ${center} ${center})`}
          className={styles.fillArc}
          style={{
            filter: `drop-shadow(0 0 6px ${scoreColor})`,
            transition: "stroke-dashoffset 800ms cubic-bezier(0.33, 1, 0.68, 1)",
          }}
        />
      </svg>
      <div className={styles.center}>
        <span className={styles.scoreNumber} style={{ color: "var(--text-primary)" }}>
          {animatedScore}
        </span>
        <span className={styles.scoreSuffix}>/100</span>
      </div>
      <div className={styles.label} style={{ color: scoreColor }}>
        {scoreLabel}
      </div>
    </div>
  );
}
