"use client";

import { useEffect, useState, useCallback } from "react";
import { AlertTriangle, Hammer, Wrench, Minus } from "lucide-react";
import type { RevenueProjection, CropMix } from "@/lib/types";
import { fetchRevenue, postRevenue } from "@/lib/api";
import CropMixSliders from "./CropMixSliders";
import ProjectionChart from "./ProjectionChart";
import styles from "./DeveloperRevenueTab.module.css";

interface DeveloperRevenueTabProps {
  buildingId: string;
}

export default function DeveloperRevenueTab({ buildingId }: DeveloperRevenueTabProps) {
  const [data, setData] = useState<RevenueProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cropMix, setCropMix] = useState<CropMix>({
    leafy_greens_pct: 60,
    herbs_pct: 25,
    microgreens_pct: 15,
  });

  // Initial fetch
  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchRevenue(buildingId)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [buildingId]);

  // Debounced re-fetch when crop mix changes
  const handleCropMixChange = useCallback(
    (newMix: CropMix) => {
      setCropMix(newMix);
      // Debounce the API call
      const timer = setTimeout(() => {
        postRevenue(buildingId, { crop_mix: newMix })
          .then(setData)
          .catch(() => {}); // silently fail on slider updates
      }, 400);
      return () => clearTimeout(timer);
    },
    [buildingId]
  );

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
        <AlertTriangle size={16} strokeWidth={1.7} className="lucide" />
        <span>{error ?? "Failed to load revenue data"}</span>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Crop Mix Sliders */}
      <CropMixSliders mix={cropMix} onChange={handleCropMixChange} />

      <div className="divider" />

      {/* Crop Revenue Breakdown */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Crop Revenue
        </h4>
        {data.crop_revenues.map((crop) => (
          <div key={crop.crop} className={styles.cropRow}>
            <div className={styles.cropHeader}>
              <span className={styles.cropName}>{crop.crop}</span>
              <span className={styles.cropRevenue}>
                ${crop.revenue.toLocaleString()}
              </span>
            </div>
            <div className={styles.cropMeta}>
              {crop.area_sqft.toLocaleString()} sq ft ·{" "}
              {crop.yield_lbs.toLocaleString()} lbs ·{" "}
              ${crop.price_per_lb.toFixed(2)}/lb
            </div>
          </div>
        ))}
        <div className={styles.totalLine}>
          <span>Total Annual Revenue</span>
          <span>${data.total_annual_revenue.toLocaleString()}</span>
        </div>
      </div>

      <div className="divider" />

      {/* Operating Costs */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Operating Costs
        </h4>
        {data.operating_costs.map((cost) => (
          <div key={cost.category} className={styles.costRow}>
            <Minus size={14} strokeWidth={1.7} className={`lucide ${styles.costIcon}`} />
            <span className={styles.costLabel}>{cost.category}</span>
            <span className={styles.costAmount}>
              ${cost.amount.toLocaleString()}
            </span>
          </div>
        ))}
        <div className={styles.totalLine} style={{ color: "var(--score-poor)" }}>
          <span>Total Annual Costs</span>
          <span>−${data.total_annual_costs.toLocaleString()}</span>
        </div>
      </div>

      <div className="divider" />

      {/* Bottom Line */}
      <div className={styles.bottomLine}>
        <div className={styles.profitRow}>
          <span className={styles.profitLabel}>Annual Net Profit</span>
          <span
            className={styles.profitValue}
            style={{
              color:
                data.annual_net_profit >= 0
                  ? "var(--accent-emerald)"
                  : "var(--score-poor)",
            }}
          >
            {data.annual_net_profit >= 0 ? "+" : ""}$
            {data.annual_net_profit.toLocaleString()}
          </span>
        </div>
        <div className={styles.marginRow}>
          <span>Margin</span>
          <span>{data.margin_pct.toFixed(1)}%</span>
        </div>
      </div>

      <div className="divider" />

      {/* Startup Costs */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Startup Costs
        </h4>
        <div className={styles.costRow}>
          <Hammer size={14} strokeWidth={1.7} className={`lucide ${styles.costIcon}`} />
          <span className={styles.costLabel}>Greenhouse Build</span>
          <span className={styles.costAmount}>
            ${data.startup_greenhouse.toLocaleString()}
          </span>
        </div>
        <div className={styles.costRow}>
          <Wrench size={14} strokeWidth={1.7} className={`lucide ${styles.costIcon}`} />
          <span className={styles.costLabel}>Structural Upgrade</span>
          <span className={styles.costAmount}>
            ${data.startup_structural.toLocaleString()}
          </span>
        </div>
        <div className={styles.totalLine}>
          <span>Total Startup</span>
          <span>${data.startup_total.toLocaleString()}</span>
        </div>
      </div>

      <div className="divider" />

      {/* ROI */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Return on Investment
        </h4>
        <div className={styles.roiStat}>
          <span className={styles.roiNumber}>
            {data.months_to_breakeven}
          </span>
          <span className={styles.roiUnit}>months to breakeven</span>
        </div>

        {/* 5-Year Cash Flow Chart */}
        {data.five_year_cash_flow.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <div className={styles.chartLabel}>5-Year Cumulative Cash Flow</div>
            <ProjectionChart
              data={data.five_year_cash_flow}
              labels={["Y1", "Y2", "Y3", "Y4", "Y5"]}
              height={160}
            />
          </div>
        )}
      </div>
    </div>
  );
}
