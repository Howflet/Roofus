"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { MapPin, Building2, Ruler, Hammer, Home, Sprout, Sun, X } from "lucide-react";
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
}

type TabKey = "revenue" | "subsidies";

export default function DetailPanel({ building, onClose }: DetailPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("revenue");

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


  const factors = getBuildingScoreFactors(building);

  const buildingType = "Multifamily";

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

      {/* Greenhouse spec — what's actually being proposed on this roof */}
      <div className={styles.propertySection}>
        <h3 className="text-label" style={{ marginBottom: isMobile ? 12 : 16 }}>
          Greenhouse
        </h3>
        <div className={styles.propertyItem}>
          <Sprout
            size={15}
            strokeWidth={1.7}
            className={`lucide ${styles.propIcon}`}
            style={{ color: "var(--accent-emerald)" }}
          />
          <span>
            {building.roof_area_sqft.toLocaleString()} sq ft footprint · ~
            {Math.round(building.roof_area_sqft * 0.65).toLocaleString()} sq ft growing
          </span>
        </div>
        <div className={styles.propertyItem}>
          <Building2 size={15} strokeWidth={1.7} className={`lucide ${styles.propIcon}`} />
          <span>
            {building.num_units} units · {building.num_floors} floors · 1 rooftop
          </span>
        </div>
        <div className={styles.propertyItem}>
          <Sun
            size={15}
            strokeWidth={1.7}
            className={`lucide ${styles.propIcon}`}
            style={{ color: "var(--accent-amber, #fbbf24)" }}
          />
          <span>
            {building.solar_capacity_kw?.toLocaleString() ?? "—"} kW rooftop solar
            <span style={{ opacity: 0.6 }}> · optional, over non-growing roof</span>
          </span>
        </div>
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
          <MapPin size={15} strokeWidth={1.7} className={`lucide ${styles.propIcon}`} />
          <span>{building.address}</span>
        </div>
        <div className={styles.propertyItem}>
          <Building2 size={15} strokeWidth={1.7} className={`lucide ${styles.propIcon}`} />
          <span>
            {buildingType} · {building.num_units} units
          </span>
        </div>
        <div className={styles.propertyItem}>
          <Ruler size={15} strokeWidth={1.7} className={`lucide ${styles.propIcon}`} />
          <span>{building.roof_area_sqft.toLocaleString()} sq ft roof area</span>
        </div>
        <div className={styles.propertyItem}>
          <Hammer size={15} strokeWidth={1.7} className={`lucide ${styles.propIcon}`} />
          <span>Built {building.year_built}</span>
        </div>
        <div className={styles.propertyItem}>
          <Home size={15} strokeWidth={1.7} className={`lucide ${styles.propIcon}`} />
          <span>{building.num_units} units · {building.num_floors} floors</span>
        </div>
        {building.in_food_desert && (
          <div className={styles.propertyItem}>
            <Sprout
              size={15}
              strokeWidth={1.7}
              className={`lucide ${styles.propIcon}`}
              style={{ color: "var(--accent-emerald)" }}
            />
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
          <Sprout size={15} strokeWidth={1.7} className={styles.tabIcon} />
          Developer Revenue
        </button>
        <button
          className={`${styles.tab} ${activeTab === "subsidies" ? styles.tabActive : ""}`}
          onClick={() => setActiveTab("subsidies")}
          id="tab-subsidies"
        >
          <Building2 size={15} strokeWidth={1.7} className={styles.tabIcon} />
          Subsidies
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
      <div className={`${styles.panel} viability-panel`} ref={panelRef} id="detail-panel">
        {/* Close button */}
        <button
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Close detail panel"
          id="detail-panel-close"
        >
          <X size={16} strokeWidth={1.7} />
        </button>

        <div className={styles.content}>
          {panelContent(false)}
        </div>
      </div>

      {/* Mobile bottom sheet overlay */}
      <div className={styles.mobileOverlay} onClick={onClose} />
      <div className={`${styles.mobileSheet} viability-panel`} id="detail-panel-mobile">
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
