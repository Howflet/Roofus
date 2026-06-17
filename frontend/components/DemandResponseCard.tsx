"use client";

import { CheckCircle2, AlertTriangle, MinusCircle, type LucideIcon } from "lucide-react";
import type { ProgramDetail } from "@/lib/types";
import styles from "./DemandResponseCard.module.css";

interface DemandResponseCardProps {
  name: string;
  program?: ProgramDetail;
}

function getStatusInfo(eligible: boolean | string): {
  Icon: LucideIcon;
  borderClass: string;
  color: string;
} {
  if (eligible === true) {
    return { Icon: CheckCircle2, borderClass: styles.eligible, color: "var(--accent)" };
  }
  if (eligible === "income_dependent" || eligible === "conditional") {
    return { Icon: AlertTriangle, borderClass: styles.conditional, color: "var(--warn)" };
  }
  return { Icon: MinusCircle, borderClass: styles.ineligible, color: "var(--text-faint)" };
}

function formatDollars(val: number | undefined): string {
  if (val === undefined || val === null) return "";
  return `$${val.toLocaleString()}`;
}

export default function DemandResponseCard({
  name,
  program,
}: DemandResponseCardProps) {
  if (!program) return null;

  const { Icon, borderClass, color } = getStatusInfo(program.eligible);

  // Build value summary lines
  const valueLines: string[] = [];

  if (program.upfront_incentive_per_kw) {
    let line = `$${program.upfront_incentive_per_kw}/kW upfront`;
    if (program.performance_incentive_per_kwh) {
      line += ` + $${program.performance_incentive_per_kwh}/kWh`;
    }
    valueLines.push(line);
  }

  if (program.lmi_incentive_per_kw) {
    valueLines.push(
      `$${program.lmi_incentive_per_kw}/kW (standard) or LMI rates available`
    );
  }

  if (program.enrollment_bonus) {
    let line = `$${program.enrollment_bonus} enrollment`;
    if (program.annual_incentive) {
      line += ` + $${program.annual_incentive}/yr per unit`;
    }
    valueLines.push(line);
  }

  if (program.max_per_unit) {
    valueLines.push(`Up to $${program.max_per_unit.toLocaleString()}/unit`);
  }

  if (program.savings_tier) {
    valueLines.push(`Savings tier: ${program.savings_tier}`);
  }

  if (program.max_per_household) {
    valueLines.push(
      `Up to $${program.max_per_household.toLocaleString()}/household`
    );
  }

  // Estimated value
  const annualVal = program.estimated_annual_value;
  const onetimeVal =
    program.estimated_onetime_value ??
    program.total_property_value ??
    program.total_property_estimate;

  return (
    <div className={`${styles.card} ${borderClass}`}>
      <div className={styles.header}>
        <Icon size={16} strokeWidth={1.7} className={styles.statusIcon} style={{ color, flexShrink: 0 }} />
        <span className={styles.programName}>{name}</span>
      </div>

      {valueLines.map((line, i) => (
        <div key={i} className={styles.valueLine}>
          {line}
        </div>
      ))}

      {(annualVal || onetimeVal) && (
        <div className={styles.estimate}>
          {onetimeVal ? (
            <span>Est. one-time: {formatDollars(onetimeVal)}</span>
          ) : null}
          {annualVal ? (
            <span>Est. value: {formatDollars(annualVal)}/year</span>
          ) : null}
        </div>
      )}

      {program.reason && (
        <div className={styles.reason}>{program.reason}</div>
      )}

      {program.potential_value_if_eligible && (
        <div className={styles.potential}>
          Potential: {program.potential_value_if_eligible}
        </div>
      )}

      {program.description && (
        <div className={styles.description}>{program.description}</div>
      )}
    </div>
  );
}
