"""Developer revenue projection engine.

Calculates crop revenues, operating costs, startup costs, ROI, and
multi-year cash flows for a rooftop greenhouse operation.
"""

from __future__ import annotations

from backend.models import (
    CostLineItem,
    CropMix,
    CropRevenueDetail,
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

    # --- Crop revenues ---
    crop_mix = a.crop_mix
    crops: list[CropRevenueDetail] = []

    for crop_key, pct_field, yield_override, price_override in [
        ("leafy_greens", crop_mix.leafy_greens_pct, a.leafy_greens_yield, a.leafy_greens_price),
        ("herbs", crop_mix.herbs_pct, a.herbs_yield, a.herbs_price),
        ("microgreens", crop_mix.microgreens_pct, a.microgreens_yield, a.microgreens_price),
    ]:
        pct = pct_field / 100.0
        area = roof_area_sqft * pct
        yield_lbs = area * yield_override
        revenue = yield_lbs * price_override
        crops.append(CropRevenueDetail(
            crop=_CROP_DEFAULTS[crop_key]["label"],
            area_sqft=round(area, 0),
            pct=pct_field,
            yield_lbs=round(yield_lbs, 0),
            price_per_lb=price_override,
            revenue=round(revenue, 0),
        ))

    total_revenue = sum(c.revenue for c in crops)

    # --- Operating costs ---
    costs: list[CostLineItem] = [
        CostLineItem(category="Lease to Owner", icon="🏠", amount=round(roof_area_sqft * a.lease_rate, 0)),
        CostLineItem(category="Electricity", icon="⚡", amount=round(roof_area_sqft * a.electricity_cost_per_sqft, 0)),
        CostLineItem(category="Water", icon="💧", amount=round(roof_area_sqft * a.water_cost_per_sqft, 0)),
        CostLineItem(category="Natural Gas", icon="🔥", amount=round(roof_area_sqft * a.gas_cost_per_sqft, 0)),
        CostLineItem(category="Labor", icon="👷", amount=round(roof_area_sqft * a.labor_cost_per_sqft, 0)),
        CostLineItem(category="Supplies & Insurance", icon="📦", amount=round(roof_area_sqft * a.supplies_cost_per_sqft, 0)),
    ]
    total_costs = sum(c.amount for c in costs)

    # --- Bottom line ---
    net_profit = total_revenue - total_costs
    margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

    # --- Startup ---
    startup_gh = round(roof_area_sqft * a.construction_cost_per_sqft, 0)
    startup_struct = round(roof_area_sqft * a.structural_cost_per_sqft, 0)
    startup_total = startup_gh + startup_struct

    # --- ROI / breakeven ---
    if net_profit > 0:
        months = int(round(startup_total / (net_profit / 12)))
    else:
        months = 0  # never breaks even

    # --- 5-year cash flow (net per year, year 1 includes startup) ---
    cash_flow: list[float] = []
    for year in range(1, 6):
        if year == 1:
            cash_flow.append(round(net_profit - startup_total, 0))
        else:
            cash_flow.append(round(net_profit, 0))

    return RevenueProjection(
        building_id=building_id,
        roof_area_sqft=roof_area_sqft,
        crop_revenues=crops,
        total_annual_revenue=round(total_revenue, 0),
        operating_costs=costs,
        total_annual_costs=round(total_costs, 0),
        annual_net_profit=round(net_profit, 0),
        margin_pct=round(margin, 1),
        startup_greenhouse=startup_gh,
        startup_structural=startup_struct,
        startup_total=startup_total,
        months_to_breakeven=months,
        five_year_cash_flow=cash_flow,
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
