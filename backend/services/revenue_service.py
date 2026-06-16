"""Developer revenue projection engine.

Calculates crop revenues, operating costs, startup costs, ROI, and
multi-year cash flows for a rooftop greenhouse operation.
"""

from __future__ import annotations

from backend.models import (
    CropMix,
    CropProductionDetail,
    OwnerRevenueProjection,
    RevenueAssumptions,
    RevenueProjection,
)

# ---------------------------------------------------------------------------
# Default crop parameters
# ---------------------------------------------------------------------------

_CROP_DEFAULTS = {
    "leafy_greens": {"yield_per_sqft": 8.0, "price_per_lb": 4.50, "emoji": "🥬", "label": "Leafy Greens"},
    "herbs":        {"yield_per_sqft": 5.0, "price_per_lb": 18.0, "emoji": "🌿", "label": "Herbs"},
    "microgreens":  {"yield_per_sqft": 12.0, "price_per_lb": 30.0, "emoji": "🌱", "label": "Microgreens"},
}


def calculate_developer_revenue(
    building_id: str,
    roof_area_sqft: float,
    assumptions: RevenueAssumptions | None = None,
) -> RevenueProjection:
    """Build a full developer P&L projection for a single building."""
    a = assumptions or RevenueAssumptions()

    # --- Crop yields ---
    crop_mix = a.crop_mix
    crops: list[CropProductionDetail] = []

    for crop_key, pct_field, yield_override in [
        ("leafy_greens", crop_mix.leafy_greens_pct, a.leafy_greens_yield),
        ("herbs", crop_mix.herbs_pct, a.herbs_yield),
        ("microgreens", crop_mix.microgreens_pct, a.microgreens_yield),
    ]:
        pct = pct_field / 100.0
        area = roof_area_sqft * pct
        yield_lbs = area * yield_override
        crops.append(CropProductionDetail(
            crop=_CROP_DEFAULTS[crop_key]["label"],
            area_sqft=round(area, 0),
            pct=pct_field,
            yield_lbs=round(yield_lbs, 0),
        ))

    return RevenueProjection(
        building_id=building_id,
        roof_area_sqft=roof_area_sqft,
        crop_production=crops,
    )


# ---------------------------------------------------------------------------
# Owner revenue projection
# ---------------------------------------------------------------------------


def calculate_owner_revenue(
    building_id: str,
    roof_area_sqft: float,
    *,
    lease_rate: float = 8.0,
    property_value: float = 850_000,
    green_roof_premium_pct: float = 3.5,
    energy_savings_per_sqft: float = 0.45,
    tax_incentive_per_sqft: float = 2.50,
) -> OwnerRevenueProjection:
    """Owner-side revenue projection: lease income, energy savings, etc."""
    annual_lease = round(roof_area_sqft * lease_rate, 0)
    annual_energy = round(roof_area_sqft * energy_savings_per_sqft, 0)
    onetime_tax = round(roof_area_sqft * tax_incentive_per_sqft, 0)
    total_annual = annual_lease + annual_energy

    new_value = round(property_value * (1 + green_roof_premium_pct / 100), 0)
    value_increase = new_value - property_value

    ten_year = round(total_annual * 10 + onetime_tax, 0)

    return OwnerRevenueProjection(
        building_id=building_id,
        roof_area_sqft=roof_area_sqft,
        lease_rate=lease_rate,
        annual_lease_income=annual_lease,
        annual_energy_savings=annual_energy,
        onetime_tax_incentive=onetime_tax,
        total_annual_revenue=total_annual,
        property_value_current=property_value,
        green_roof_premium_pct=green_roof_premium_pct,
        property_value_new=new_value,
        property_value_increase=value_increase,
        ten_year_cumulative=ten_year,
    )
