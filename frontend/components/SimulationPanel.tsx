"use client";

/**
 * Greenhouse-Network Simulation panel (optional add-on).
 *
 * A floating modal that lets you pick an aggregation cluster and shows the
 * 24-hour demand-response day-simulation: net grid demand with vs without
 * coordination (battery + greenhouse cooling shedding), plus headline numbers.
 *
 * Talks to GET /grids/{id}/simulation via fetchSimulation().
 * This is a React port of the old standalone frontend/simulation.html.
 */

import { useEffect, useMemo, useState } from "react";
import type { GridCollection, SimulationResult } from "@/lib/types";
import { fetchSimulation } from "@/lib/api";
import styles from "./SimulationPanel.module.css";

interface SimulationPanelProps {
  grids: GridCollection | null;
  onClose: () => void;
}

const COLORS = {
  red: "#d9534f",
  green: "#2e9e6b",
  orange: "#e8a33d",
  blue: "#5a82c0",
};

function fmt(n: number | undefined | null): string {
  if (n === undefined || n === null) return "–";
  return Math.round(n).toLocaleString();
}

export default function SimulationPanel({ grids, onClose }: SimulationPanelProps) {
  // Clusters sorted biggest-first (by units), so the headline cluster is on top.
  const clusters = useMemo(() => {
    if (!grids) return [];
    return [...grids.features]
      .map((f) => f.properties)
      .sort((a, b) => (b.total_units || 0) - (a.total_units || 0));
  }, [grids]);

  const [gridId, setGridId] = useState<string>("");
  const [data, setData] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pick the biggest cluster by default once grids arrive.
  useEffect(() => {
    if (!gridId && clusters.length) setGridId(clusters[0].grid_id);
  }, [clusters, gridId]);

  // Fetch the simulation whenever the selected cluster changes.
  useEffect(() => {
    if (!gridId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchSimulation(gridId)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch(() => {
        if (!cancelled) setError(`Simulation failed for ${gridId}.`);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [gridId]);

  // Close on Escape.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <>
      <div className={styles.overlay} onClick={onClose} />
      <div className={`glass ${styles.panel}`} role="dialog" aria-label="Greenhouse-network simulation">
        <button className={styles.closeBtn} onClick={onClose} aria-label="Close simulation">
          ✕
        </button>

        <div className={styles.header}>
          <h2 className={styles.title}>🌱 Greenhouse-Network Simulation</h2>
          <p className={styles.subtitle}>
            One representative summer day for a cluster — how coordinating solar + battery +
            greenhouse cooling shaves the evening grid peak. <strong>Illustrative.</strong>
          </p>
        </div>

        <div className={styles.controls}>
          <label htmlFor="sim-cluster" className="text-label">
            Cluster
          </label>
          <select
            id="sim-cluster"
            className={styles.select}
            value={gridId}
            onChange={(e) => setGridId(e.target.value)}
          >
            {clusters.map((c) => (
              <option key={c.grid_id} value={c.grid_id}>
                {c.grid_id} — {c.building_count} buildings
                {c.meets_cl1_threshold ? " · CL-1 ✓" : ""}
              </option>
            ))}
          </select>
        </div>

        {loading && <div className={styles.status}>Running simulation…</div>}
        {error && <div className={styles.error}>{error}</div>}

        {data && !error && (
          <>
            <div className={styles.cards}>
              <Card big value={`${data.peak_cut_pct}%`} label="evening peak cut" />
              <Card
                money
                value={data.cl1_eligible ? `$${fmt(data.est_annual_credit)}/yr` : "n/a"}
                label="est. CL-1 credit"
              />
              <Card value={`${fmt(data.peak_cut_kw)} kW`} label="peak demand cut" />
              <Card value={`${data.energy_cut_pct}%`} label="peak-window energy cut" />
              <Card value={fmt(data.n_buildings)} label={`buildings · ${fmt(data.units)} units`} />
              <Card value={`${fmt(data.solar_kw)} kW`} label="solar" />
              <Card value={`${fmt(data.batt_power_kw)} kW`} label="battery" />
            </div>

            <SimChart data={data} />

            <div className={styles.note}>
              <strong>How to read it:</strong> the{" "}
              <span style={{ color: COLORS.red }}>red</span> line is what the cluster pulls from the
              grid with no coordination; the <span style={{ color: COLORS.green }}>green</span> line
              is with the coordinated network. In the shaded evening window the green line sits below
              the red — that gap is the demand-response saving.
              <br />
              <br />
              <strong>Honest labels:</strong> sunlight is real (Open-Meteo); greenhouse cooling is
              grounded in the GES physics run (it overheats in Atlanta summer → needs afternoon
              cooling); building load shape, battery rule, and demand-response window are modelled
              assumptions. Not a precise prediction.
            </div>
          </>
        )}
      </div>
    </>
  );
}

// ---------------------------------------------------------------------------
// Headline metric card
// ---------------------------------------------------------------------------
function Card({
  value,
  label,
  big,
  money,
}: {
  value: string;
  label: string;
  big?: boolean;
  money?: boolean;
}) {
  return (
    <div className={`${styles.card} ${big ? styles.cardBig : ""} ${money ? styles.cardMoney : ""}`}>
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 24-hour SVG line chart: baseline vs coordinated net grid demand
// ---------------------------------------------------------------------------
function SimChart({ data }: { data: SimulationResult }) {
  const W = 940;
  const H = 420;
  const padL = 56;
  const padR = 18;
  const padT = 18;
  const padB = 34;
  const x0 = padL;
  const x1 = W - padR;
  const y0 = H - padB;
  const y1 = padT;

  const series = [data.total_load, data.solar_gen, data.baseline_net, data.coordinated_net];
  let lo = 0;
  let hi = 0;
  for (const s of series) {
    for (const v of s) {
      lo = Math.min(lo, v);
      hi = Math.max(hi, v);
    }
  }
  hi *= 1.08;
  lo *= 1.12;

  const sx = (h: number) => x0 + (h / 23) * (x1 - x0);
  const sy = (v: number) => y0 - ((v - lo) / (hi - lo || 1)) * (y0 - y1);

  const path = (arr: number[]) =>
    arr.map((v, h) => `${h === 0 ? "M" : "L"}${sx(h).toFixed(1)},${sy(v).toFixed(1)}`).join(" ");

  // y-axis gridlines at "nice" round kW values
  const ticks: number[] = [];
  const step = niceStep((hi - lo) / 5);
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);

  const pw = data.peak_window;
  const bandX = sx(pw[0] - 0.5);
  const bandW = sx(pw[pw.length - 1] + 0.5) - bandX;

  return (
    <div className={styles.chartBox}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" className={styles.chart} preserveAspectRatio="xMidYMid meet">
        {/* peak-window band */}
        <rect x={bandX} y={y1} width={bandW} height={y0 - y1} fill="rgba(255,210,138,0.10)" />
        <text x={bandX + bandW / 2} y={y1 + 14} textAnchor="middle" className={styles.bandLabel}>
          grid peak {pw[0]}:00–{pw[pw.length - 1] + 1}:00
        </text>

        {/* y gridlines + labels */}
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x0} y1={sy(t)} x2={x1} y2={sy(t)} stroke="rgba(255,255,255,0.07)" />
            <text x={x0 - 8} y={sy(t) + 4} textAnchor="end" className={styles.axisLabel}>
              {Math.round(t).toLocaleString()}
            </text>
          </g>
        ))}
        {/* zero line */}
        <line x1={x0} y1={sy(0)} x2={x1} y2={sy(0)} stroke="rgba(255,255,255,0.25)" />

        {/* x labels every 3h */}
        {data.hours
          .filter((h) => h % 3 === 0)
          .map((h) => (
            <text key={h} x={sx(h)} y={H - 12} textAnchor="middle" className={styles.axisLabel}>
              {h}:00
            </text>
          ))}

        {/* series */}
        <path d={path(data.total_load)} fill="none" stroke={COLORS.blue} strokeWidth={1.4} strokeDasharray="2 3" />
        <path d={path(data.solar_gen)} fill="none" stroke={COLORS.orange} strokeWidth={1.4} strokeDasharray="5 4" />
        <path d={path(data.baseline_net)} fill="none" stroke={COLORS.red} strokeWidth={2.6} />
        <path d={path(data.coordinated_net)} fill="none" stroke={COLORS.green} strokeWidth={2.6} />
      </svg>

      <div className={styles.legend}>
        <span>
          <i style={{ background: COLORS.red }} />
          Net grid demand — no coordination
        </span>
        <span>
          <i style={{ background: COLORS.green }} />
          Net grid demand — coordinated
        </span>
        <span>
          <i style={{ background: COLORS.orange }} />
          Solar generation
        </span>
        <span>
          <i style={{ background: COLORS.blue }} />
          Total load (buildings + greenhouse)
        </span>
        <span>
          <i style={{ background: "#ffd28a" }} />
          Grid peak window
        </span>
      </div>
    </div>
  );
}

function niceStep(raw: number): number {
  if (raw <= 0) return 1;
  const pow = Math.pow(10, Math.floor(Math.log10(raw)));
  const n = raw / pow;
  const nice = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
  return nice * pow;
}
