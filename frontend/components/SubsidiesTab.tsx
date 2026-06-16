"use client";

import { useEffect, useState } from "react";
import type { BuildingSubsidyDetail } from "@/lib/types";
import { fetchSubsidies } from "@/lib/api";
import ThresholdMeter from "./ThresholdMeter";
import DemandResponseCard from "./DemandResponseCard";
import AggregationBonusCard from "./AggregationBonusCard";
import styles from "./SubsidiesTab.module.css";

interface SubsidiesTabProps {
  buildingId: string;
}

export default function SubsidiesTab({ buildingId }: SubsidiesTabProps) {
  const [data, setData] = useState<BuildingSubsidyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchSubsidies(buildingId)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [buildingId]);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <span>Loading subsidy data...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className={styles.error}>
        <span>⚠️</span>
        <span>{error ?? "Failed to load subsidy data"}</span>
      </div>
    );
  }

  const { demand_response_programs: dr, efficiency_rebates: eff } = data;

  // Calculate totals
  const totalOnetime =
    (eff?.gp_multifamily?.total_property_max ?? 0) +
    (eff?.gefa_her?.total_property_estimate ?? 0);

  const totalAnnual =
    (dr?.dco1_dispatchable?.eligible === true
      ? dr.dco1_dispatchable.estimated_annual_value ?? 0
      : dr?.cl1_aggregated?.eligible === true
      ? dr.cl1_aggregated.estimated_annual_value ?? 0
      : 0);

  return (
    <div className={styles.container}>
      {/* Section 1: Threshold Meter */}
      <ThresholdMeter
        data={data.threshold_indicator}
        annualKwh={data.energy_profile.estimated_annual_kwh}
      />

      <div className="divider" />

      {/* Section 2: Demand Response Programs */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Demand Response Programs
        </h4>

        <DemandResponseCard
          name="DCO-1 Dispatchable Power"
          program={dr.dco1_dispatchable}
        />
        <DemandResponseCard
          name="CL-1 Curtailable Load"
          program={dr.cl1_aggregated}
        />
      </div>

      <div className="divider" />

      {/* Section 2b: Efficiency Rebates */}
      <div className={styles.section}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Efficiency Rebates
        </h4>

        <DemandResponseCard
          name="GA Power Multifamily Efficiency"
          program={eff.gp_multifamily}
        />
        <DemandResponseCard
          name="GEFA Home Efficiency Rebates (HER)"
          program={eff.gefa_her}
        />
        <DemandResponseCard
          name="GEFA Home Electrification (HEAR)"
          program={eff.gefa_hear}
        />
      </div>

      <div className="divider" />

      {/* Section 3: Aggregation Bonus */}
      <AggregationBonusCard data={data.aggregation_bonus} />

      <div className="divider" />

      {/* Total Summary */}
      <div className={styles.summary}>
        <h4 className="text-label" style={{ marginBottom: 12 }}>
          Total Potential Value
        </h4>
        <div className={styles.summaryRow}>
          <span className={styles.summaryLabel}>One-time incentives</span>
          <span className={styles.summaryValue}>
            ${totalOnetime.toLocaleString()}+
          </span>
        </div>
        <div className={styles.summaryRow}>
          <span className={styles.summaryLabel}>Annual recurring</span>
          <span
            className={styles.summaryValue}
            style={{ color: "var(--accent-emerald)" }}
          >
            ${totalAnnual.toLocaleString()}/year
          </span>
        </div>
      </div>
    </div>
  );
}
