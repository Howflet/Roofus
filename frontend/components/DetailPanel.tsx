"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import type { BuildingProperties, Persona } from "@/lib/types";
import { getBuildingScoreFactors } from "@/lib/types";
import ScoreGauge from "./ScoreGauge";
import ScoreBreakdown from "./ScoreBreakdown";
import OwnerContact from "./OwnerContact";
import DeveloperRevenueTab from "./DeveloperRevenueTab";
import SubsidiesTab from "./SubsidiesTab";
import styles from "./DetailPanel.module.css";

interface DetailPanelProps {
  building: BuildingProperties;
  onClose: () => void;
  persona?: Persona;
}

type TabKey = "revenue" | "subsidies";

export default function DetailPanel({ building, onClose, persona = "developer" }: DetailPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<TabKey>(
    persona === "owner" ? "subsidies" : "revenue"
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  // Update default tab when persona changes
  useEffect(() => {
    setActiveTab(persona === "owner" ? "subsidies" : "revenue");
  }, [persona]);

  const factors = getBuildingScoreFactors(building);

  const buildingType = building.zoning === "R-4" ? "Multifamily (R-4)" : "Multifamily (R-5)";

  const renderTabContent = () => {
    switch (activeTab) {
      case "revenue":
        return <DeveloperRevenueTab buildingId={building.id} />;
      case "subsidies":
        return <SubsidiesTab buildingId={building.id} />;
    }
  };

  const panelContent = (isMobile: boolean) => (
    <>
      {/* Score Gauge */}
      <div className={styles.gaugeSection}>
        <ScoreGauge score={Math.round(building.score)} size={isMobile ? 120 : 160} />
      </div>

      <div className="divider" />

      {/* Score Breakdown */}
      <ScoreBreakdown factors={factors} />

      <div className="divider" />

      {/* Property Details */}
      <div className={styles.propertySection}>
        <h3 className="text-label" style={{ marginBottom: isMobile ? 12 : 16 }}>
          Property Details
        </h3>
        <div className={styles.propertyItem}>
          <span className={styles.propIcon}>📍</span>
          <span>{building.address}</span>
        </div>
        <div className={styles.propertyItem}>
          <span className={styles.propIcon}>🏢</span>
          <span>
            {buildingType} · {building.zoning} Zoning
          </span>
        </div>
        <div className={styles.propertyItem}>
          <span className={styles.propIcon}>📐</span>
          <span>{building.roof_area_sqft.toLocaleString()} sq ft roof area</span>
        </div>
        <div className={styles.propertyItem}>
          <span className={styles.propIcon}>🏗️</span>
          <span>Built {building.year_built}</span>
        </div>
        <div className={styles.propertyItem}>
          <span className={styles.propIcon}>🏠</span>
          <span>{building.num_units} units · {building.num_floors} floors</span>
        </div>
        {building.in_food_desert && (
          <div className={styles.propertyItem}>
            <span className={styles.propIcon}>🌾</span>
            <span style={{ color: "var(--accent-emerald)" }}>In food desert area</span>
          </div>
        )}
      </div>

      <div className="divider" />

      {/* Owner Contact */}
      <OwnerContact building={building} />

      <div className="divider" />

      {/* Tab Bar */}
      <div className={styles.tabBar}>
        <button
          className={`${styles.tab} ${activeTab === "revenue" ? styles.tabActive : ""}`}
          onClick={() => setActiveTab("revenue")}
          id="tab-revenue"
        >
          🌱 Developer Revenue
        </button>
        <button
          className={`${styles.tab} ${activeTab === "subsidies" ? styles.tabActive : ""}`}
          onClick={() => setActiveTab("subsidies")}
          id="tab-subsidies"
        >
          🏢 Subsidies
        </button>
      </div>

      {/* Tab Content */}
      <div className={styles.tabContent}>
        {renderTabContent()}
      </div>
    </>
  );

  return (
    <>
      {/* Desktop panel */}
      <div className={styles.panel} ref={panelRef} id="detail-panel">
        {/* Close button */}
        <button
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Close detail panel"
          id="detail-panel-close"
        >
          ✕
        </button>

        <div className={styles.content}>
          {panelContent(false)}
        </div>
      </div>

      {/* Mobile bottom sheet overlay */}
      <div className={styles.mobileOverlay} onClick={onClose} />
      <div className={styles.mobileSheet} id="detail-panel-mobile">
        <div className={styles.dragHandle}>
          <div className={styles.dragBar} />
        </div>
        <div className={styles.mobileContent}>
          {panelContent(true)}
        </div>
      </div>
    </>
  );
}
