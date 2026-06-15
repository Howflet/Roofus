"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { BuildingStats, Persona } from "@/lib/types";
import styles from "./Header.module.css";

interface HeaderProps {
  stats: BuildingStats | null;
  onApplyFilters: (filters: FilterState) => void;
  persona: Persona;
  onPersonaChange: (persona: Persona) => void;
}

export interface FilterState {
  minScore: number;
  buildingTypes: string[];
  minRoofSize: number;
  foodDesertOnly: boolean;
}

const DEFAULT_FILTERS: FilterState = {
  minScore: 0,
  buildingTypes: ["R-4", "R-5"],
  minRoofSize: 0,
  foodDesertOnly: false,
};

function AnimatedNumber({ value, duration = 800 }: { value: number; duration?: number }) {
  const [display, setDisplay] = useState(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const start = performance.now();
    function animate(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * value));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    }
    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [value, duration]);

  return <>{display.toLocaleString()}</>;
}

export default function Header({ stats, onApplyFilters, persona, onPersonaChange }: HeaderProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [leafHover, setLeafHover] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowFilters(false);
      }
    }
    if (showFilters) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showFilters]);

  const toggleBuildingType = useCallback((type: string) => {
    setFilters((prev) => {
      const types = prev.buildingTypes.includes(type)
        ? prev.buildingTypes.filter((t) => t !== type)
        : [...prev.buildingTypes, type];
      return { ...prev, buildingTypes: types };
    });
  }, []);

  const handleApply = useCallback(() => {
    onApplyFilters(filters);
    setShowFilters(false);
  }, [filters, onApplyFilters]);

  const handleReset = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
    onApplyFilters(DEFAULT_FILTERS);
    setShowFilters(false);
  }, [onApplyFilters]);

  return (
    <header className={`glass ${styles.header}`} id="header-bar">
      {/* Left: Brand */}
      <div className={styles.brand}>
        <span
          className={styles.leafIcon}
          style={{
            transform: leafHover ? "rotate(15deg)" : "rotate(0)",
          }}
          onMouseEnter={() => setLeafHover(true)}
          onMouseLeave={() => setLeafHover(false)}
        >
          🌿
        </span>
        <span className={styles.wordmark}>Roofus</span>
      </div>

      {/* Center: Stats */}
      <div className={styles.stats}>
        {stats ? (
          <>
            <span className={styles.statNumber}>
              <AnimatedNumber value={stats.total_buildings} />
            </span>
            <span className={styles.statText}> scored · </span>
            <span className={styles.statHighlight}>
              <AnimatedNumber value={stats.high_potential} />
            </span>
            <span className={styles.statText}> </span>
            <span className={styles.statHighlight}>high-potential</span>
          </>
        ) : (
          <span className={styles.statText}>Loading...</span>
        )}
      </div>

      {/* Right: Persona Toggle + Controls */}
      <div className={styles.controls} ref={dropdownRef}>
        {/* Persona Toggle */}
        <div className={styles.personaToggle} id="persona-toggle">
          <button
            className={`${styles.personaBtn} ${persona === "developer" ? styles.personaBtnActive : ""}`}
            onClick={() => onPersonaChange("developer")}
          >
            🌱 Developer
          </button>
          <button
            className={`${styles.personaBtn} ${persona === "owner" ? styles.personaBtnActive : ""}`}
            onClick={() => onPersonaChange("owner")}
          >
            🏢 Owner
          </button>
        </div>

        <button
          className={`btn btn-ghost btn-pill ${styles.filterBtn}`}
          onClick={() => setShowFilters(!showFilters)}
          id="filter-button"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <line x1="2" y1="4" x2="14" y2="4" />
            <line x1="4" y1="8" x2="12" y2="8" />
            <line x1="6" y1="12" x2="10" y2="12" />
          </svg>
          Filters
        </button>

        {/* Filter Dropdown */}
        {showFilters && (
          <div className={`glass ${styles.dropdown}`} id="filter-dropdown">
            {/* Score Range */}
            <div className={styles.filterGroup}>
              <label className="text-label">Score Range</label>
              <input
                type="range"
                className="range-slider"
                min="0"
                max="100"
                value={filters.minScore}
                onChange={(e) =>
                  setFilters((prev) => ({ ...prev, minScore: Number(e.target.value) }))
                }
              />
              <span className={styles.filterValue}>Min: {filters.minScore}</span>
            </div>

            {/* Building Type */}
            <div className={styles.filterGroup}>
              <label className="text-label">Building Type</label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={filters.buildingTypes.includes("R-4")}
                  onChange={() => toggleBuildingType("R-4")}
                />
                R-4 (General Multifamily)
              </label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={filters.buildingTypes.includes("R-5")}
                  onChange={() => toggleBuildingType("R-5")}
                />
                R-5 (Single-Family Attached)
              </label>
            </div>

            {/* Roof Size */}
            <div className={styles.filterGroup}>
              <label className="text-label">Roof Size</label>
              <input
                type="range"
                className="range-slider"
                min="0"
                max="15000"
                step="500"
                value={filters.minRoofSize}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    minRoofSize: Number(e.target.value),
                  }))
                }
              />
              <span className={styles.filterValue}>
                Min: {filters.minRoofSize.toLocaleString()} sq ft
              </span>
            </div>

            {/* Food Desert */}
            <label className="checkbox" style={{ marginBottom: 16 }}>
              <input
                type="checkbox"
                checked={filters.foodDesertOnly}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    foodDesertOnly: e.target.checked,
                  }))
                }
              />
              Food desert areas only
            </label>

            {/* Actions */}
            <div className={styles.filterActions}>
              <button className="btn btn-primary" onClick={handleApply} id="apply-filters-btn">
                Apply Filters
              </button>
              <button className={styles.resetBtn} onClick={handleReset}>
                Reset
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
