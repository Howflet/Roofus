"use client";

import { useEffect, useState } from "react";
import styles from "./ProjectionChart.module.css";

interface ProjectionChartProps {
  data: number[];
  labels?: string[];
  height?: number;
}

export default function ProjectionChart({
  data,
  labels,
  height = 180,
}: ProjectionChartProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 150);
    return () => clearTimeout(timer);
  }, []);

  if (!data.length) return null;

  const maxVal = Math.max(...data.map(Math.abs), 1);
  const barWidth = 100 / data.length;
  const chartPadding = 40;
  const barPadding = 8;

  const defaultLabels = data.map((_, i) => `Y${i + 1}`);
  const displayLabels = labels ?? defaultLabels;

  return (
    <div className={styles.container} style={{ height }}>
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${data.length * 60 + chartPadding} ${height}`}
        preserveAspectRatio="none"
        className={styles.svg}
      >
        <defs>
          <linearGradient id="barGradientPos" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10B981" stopOpacity={0.9} />
            <stop offset="100%" stopColor="#059669" stopOpacity={0.6} />
          </linearGradient>
          <linearGradient id="barGradientNeg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#EF4444" stopOpacity={0.7} />
            <stop offset="100%" stopColor="#DC2626" stopOpacity={0.9} />
          </linearGradient>
        </defs>

        {/* Zero line */}
        <line
          x1={chartPadding}
          y1={height / 2}
          x2={data.length * 60 + chartPadding}
          y2={height / 2}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={1}
        />

        {data.map((val, i) => {
          const isPositive = val >= 0;
          const barH =
            (Math.abs(val) / maxVal) * (height / 2 - 28);
          const x = chartPadding + i * 60 + barPadding;
          const y = isPositive ? height / 2 - barH : height / 2;
          const w = 60 - barPadding * 2;

          return (
            <g key={i}>
              {/* Bar */}
              <rect
                x={x}
                y={mounted ? y : height / 2}
                width={w}
                height={mounted ? barH : 0}
                rx={4}
                fill={isPositive ? "url(#barGradientPos)" : "url(#barGradientNeg)"}
                className={styles.bar}
                style={{ transitionDelay: `${i * 80}ms` }}
              />
              {/* Value label */}
              <text
                x={x + w / 2}
                y={isPositive ? y - 6 : y + barH + 14}
                textAnchor="middle"
                className={styles.valueLabel}
                style={{
                  opacity: mounted ? 1 : 0,
                  transitionDelay: `${i * 80 + 200}ms`,
                }}
              >
                {val >= 0 ? "+" : ""}${Math.round(Math.abs(val) / 1000)}k
              </text>
              {/* Year label */}
              <text
                x={x + w / 2}
                y={height - 4}
                textAnchor="middle"
                className={styles.yearLabel}
              >
                {displayLabels[i]}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
