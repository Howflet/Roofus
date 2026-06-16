"use client";

import { useCallback } from "react";
import type { CropMix } from "@/lib/types";
import styles from "./CropMixSliders.module.css";

interface CropMixSlidersProps {
  mix: CropMix;
  onChange: (mix: CropMix) => void;
}

const CROPS = [
  { key: "leafy_greens_pct" as const, label: "Leafy Greens", emoji: "🥬" },
  { key: "herbs_pct" as const, label: "Herbs", emoji: "🌿" },
  { key: "microgreens_pct" as const, label: "Microgreens", emoji: "🌱" },
];

export default function CropMixSliders({ mix, onChange }: CropMixSlidersProps) {
  const handleChange = useCallback(
    (changedKey: keyof CropMix, newValue: number) => {
      const clampedValue = Math.min(100, Math.max(0, newValue));
      const remaining = 100 - clampedValue;

      // Get the other two keys
      const otherKeys = CROPS
        .map((c) => c.key)
        .filter((k) => k !== changedKey) as (keyof CropMix)[];

      const otherTotal = otherKeys.reduce((s, k) => s + mix[k], 0);

      let newMix: CropMix;
      if (otherTotal === 0) {
        // Distribute remaining equally
        newMix = {
          ...mix,
          [changedKey]: clampedValue,
          [otherKeys[0]]: Math.round(remaining / 2),
          [otherKeys[1]]: remaining - Math.round(remaining / 2),
        };
      } else {
        // Distribute proportionally
        const ratio0 = mix[otherKeys[0]] / otherTotal;
        const val0 = Math.round(remaining * ratio0);
        const val1 = remaining - val0;
        newMix = {
          ...mix,
          [changedKey]: clampedValue,
          [otherKeys[0]]: val0,
          [otherKeys[1]]: val1,
        };
      }

      onChange(newMix);
    },
    [mix, onChange]
  );

  return (
    <div className={styles.container}>
      <h4 className="text-label" style={{ marginBottom: 14 }}>
        Crop Mix Allocation
      </h4>
      {CROPS.map((crop) => {
        const value = mix[crop.key];
        return (
          <div key={crop.key} className={styles.sliderRow}>
            <div className={styles.sliderHeader}>
              <span className={styles.cropLabel}>
                {crop.emoji} {crop.label}
              </span>
              <span className={styles.cropPct}>{Math.round(value)}%</span>
            </div>
            <div className={styles.sliderTrack}>
              <div
                className={styles.sliderFill}
                style={{ width: `${value}%` }}
              />
              <input
                type="range"
                min={0}
                max={100}
                value={value}
                onChange={(e) =>
                  handleChange(crop.key, Number(e.target.value))
                }
                className={styles.sliderInput}
              />
            </div>
          </div>
        );
      })}
      <div className={styles.totalRow}>
        <span>Total</span>
        <span>
          {Math.round(
            mix.leafy_greens_pct + mix.herbs_pct + mix.microgreens_pct
          )}
          %
        </span>
      </div>
    </div>
  );
}
