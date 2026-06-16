"""Georgia Power subsidy & demand-response eligibility engine.

Calculates per-building subsidy eligibility across VPP, CL-1, DPEC-5,
TempCheck, GEFA, and Georgia Power multifamily efficiency programs.
"""

from __future__ import annotations

from typing import Any

from backend.models import (
    AggregationBonus,
    BuildingSubsidyDetail,
    DemandResponsePrograms,
    EfficiencyRebates,
    EnergyProfile,
    ProgramDetail,
    ThresholdIndicator,
)
from backend.services import geojson_service


# ---------------------------------------------------------------------------
# Georgia Power rate constants (R-30 residential schedule)
# ---------------------------------------------------------------------------

_RATE_SCHEDULE = "R-30"
_SUMMER_TIERS = [
    (650, 0.0874),   # first 650 kWh
    (1000, 0.1460),  # 651-1000 kWh
    (None, 0.1460),  # above 1000 kWh (same)
]
_COST_PER_KWH_AVG = 0.105  # blended average for estimation


def _estimate_annual_kwh(peak_kw: float) -> float:
    """Rough estimate: annual kWh ≈ peak_kw × hours/year × load factor."""
    # Multifamily load factor ~0.50, 8760 hours/year
    return round(peak_kw * 8760 * 0.50)


def _estimate_annual_cost(annual_kwh: float) -> float:
    return round(annual_kwh * _COST_PER_KWH_AVG)


def _summer_rate_tier(annual_kwh: float) -> str:
    monthly = annual_kwh / 12
    if monthly <= 650:
        return f"${_SUMMER_TIERS[0][1]}/kWh (0-650 kWh band)"
    elif monthly <= 1000:
        return f"${_SUMMER_TIERS[1][1]}/kWh (650-1000 kWh band)"
    else:
        return f"${_SUMMER_TIERS[2][1]}/kWh (>1000 kWh band)"


def _greenhouse_shed_kw(peak_kw: float) -> float:
    """Estimated kW that greenhouse lighting/pump loads can shed during peaks."""
    # ~15-20% of building peak can be shed via greenhouse load management
    return round(peak_kw * 0.18, 1)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_subsidy_detail(
    building_id: str,
    *,
    # Allow overrides for POST endpoint
    estimated_peak_kw: float | None = None,
    estimated_annual_kwh: float | None = None,
    num_units: int | None = None,
    is_lmi: bool = False,
) -> BuildingSubsidyDetail | None:
    """Full subsidy breakdown for a single building."""
    feat = geojson_service.get_building(building_id)
    if feat is None:
        return None

    props = feat["properties"]

    peak_kw = estimated_peak_kw or props.get("estimated_peak_kw", 45)
    annual_kwh = estimated_annual_kwh or _estimate_annual_kwh(peak_kw)
    units = num_units or props.get("num_units", 1)
    grid_id = props.get("aggregation_grid_id", "")

    # --- Energy profile ---
    energy = EnergyProfile(
        estimated_peak_kw=peak_kw,
        estimated_annual_kwh=annual_kwh,
        current_rate_schedule=_RATE_SCHEDULE,
        summer_rate_tier=_summer_rate_tier(annual_kwh),
        annual_energy_cost_estimate=_estimate_annual_cost(annual_kwh),
    )

    # --- Threshold indicator ---
    # Target = baseline tier (reduce ~12% to stay in lower rate bracket)
    target_kwh = round(annual_kwh * 0.88)
    reduction_needed = annual_kwh - target_kwh
    pct_reduction = round((reduction_needed / annual_kwh) * 100, 0) if annual_kwh > 0 else 0
    shed_kw = props.get("greenhouse_shed_kw") or _greenhouse_shed_kw(peak_kw)

    threshold = ThresholdIndicator(
        current_tier="Mid" if annual_kwh > target_kwh else "Baseline",
        target_tier="Baseline",
        kwh_reduction_needed=reduction_needed,
        pct_reduction_needed=pct_reduction,
        greenhouse_demand_shed_potential_kw=shed_kw,
    )

    # --- Grid info (for aggregation-dependent programs) ---
    grid_feat = geojson_service.get_grid(grid_id) if grid_id else None
    # DR thresholds compare against CURTAILABLE (sheddable) load, not total peak.
    grid_kw = 0
    if grid_feat:
        gp = grid_feat["properties"]
        grid_kw = gp.get("combined_curtailable_kw", gp.get("combined_peak_kw", 0))
    grid_count = grid_feat["properties"].get("building_count", 0) if grid_feat else 0

    meets_cl1 = grid_kw >= 200
    meets_dco1 = grid_kw >= 1000

    # --- CL-1 (aggregated, needs 200 kW) ---
    if meets_cl1:
        cl1 = ProgramDetail(
            eligible=True,
            estimated_annual_value=round(grid_kw * 5.5 * 12, 0),  # ~$5.50/kW/month
            description=f"CL-1 Curtailable Load — Grid {grid_id} qualifies at {grid_kw} kW.",
        )
    else:
        shortfall = round(200 - grid_kw, 0)
        needed = max(1, int(shortfall / 30))  # ~30 kW avg per building
        cl1 = ProgramDetail(
            eligible=False,
            reason=f"Grid {grid_id} at {grid_kw} kW — needs 200 kW for CL-1 eligibility",
            kw_shortfall=shortfall,
            buildings_needed=needed,
            potential_value_if_eligible="Negotiated — typically $3-8/kW/month",
        )

    # --- DCO-1 (1 MW / 1000 kW threshold) ---
    if meets_dco1:
        dco1 = ProgramDetail(
            eligible=True,
            estimated_annual_value=round(grid_kw * 15 * 12 * 0.75, 0),  # illustrative 75% system value
            description=f"DCO-1 Customer-owned dispatchable power — Grid {grid_id} qualifies at {grid_kw} kW.",
        )
    else:
        shortfall = round(1000 - grid_kw, 0)
        needed = max(1, int(shortfall / 30))
        dco1 = ProgramDetail(
            eligible=False,
            reason=f"Grid {grid_id} at {grid_kw} kW — needs 1 MW (1000 kW) for DCO-1 eligibility",
            kw_shortfall=shortfall,
            buildings_needed=needed,
            potential_value_if_eligible="Credited at 75% of the system's value",
        )

    demand_response = DemandResponsePrograms(
        cl1_aggregated=cl1,
        dco1_dispatchable=dco1,
    )

    # --- Efficiency rebates ---
    gp_mf_max = round(units * 500, 0)
    gp_mf = ProgramDetail(
        eligible=True,
        max_per_unit=500,
        total_property_max=gp_mf_max,
        measures=["Attic insulation ($125)", "Air sealing ($150)", "Duct sealing ($150)", "AC upgrade ($25)"],
        description="Georgia Power Multifamily Efficiency Program",
    )

    lmi_rebate = 10000 if is_lmi else 2000
    gefa_her_total = round(units * lmi_rebate, 0)
    gefa_her = ProgramDetail(
        eligible=True,
        savings_tier="20-34%",
        per_unit_rebate=2000,
        lmi_per_unit_rebate=10000,
        total_property_estimate=gefa_her_total,
        description="Georgia Energy Finance Authority Home Efficiency Rebates",
    )

    gefa_hear = ProgramDetail(
        eligible="income_dependent",
        max_per_household=14000,
        description="Heat pump, panel, wiring, water heater rebates for LMI properties",
    )

    efficiency = EfficiencyRebates(
        gp_multifamily=gp_mf,
        gefa_her=gefa_her,
        gefa_hear=gefa_hear,
    )

    # --- Aggregation bonus ---
    if grid_feat:
        grid_props = grid_feat["properties"]
        current_tier = grid_props.get("aggregation_tier", "Below Threshold")
        current_value = grid_props.get("potential_annual_value", 0)

        if meets_dco1:
            next_tier = "Fully Qualified (DCO-1)"
            kw_to_next = 0
            bldgs_to_next = 0
            next_value = current_value
        elif meets_cl1:
            next_tier = "DCO-1 (1 MW)"
            kw_to_next = round(1000 - grid_kw, 0)
            bldgs_to_next = max(1, int(kw_to_next / 30))
            next_value = round(1000 * 15 * 12 * 0.75, 0)
        else:
            next_tier = "CL-1 (200 kW)"
            kw_to_next = round(200 - grid_kw, 0)
            bldgs_to_next = max(1, int(kw_to_next / 30))
            next_value = round(200 * 5.5 * 12, 0)

        uplift = next_value - current_value

        agg_bonus = AggregationBonus(
            grid_id=grid_id,
            grid_combined_kw=grid_kw,
            current_tier=current_tier,
            next_tier=next_tier,
            kw_to_next_tier=kw_to_next,
            buildings_to_next_tier=bldgs_to_next,
            current_grid_annual_value=current_value,
            next_tier_annual_value=next_value,
            uplift_if_threshold_met=uplift,
        )
    else:
        agg_bonus = AggregationBonus(grid_id=grid_id)

    return BuildingSubsidyDetail(
        building_id=building_id,
        energy_profile=energy,
        threshold_indicator=threshold,
        demand_response_programs=demand_response,
        efficiency_rebates=efficiency,
        aggregation_bonus=agg_bonus,
    )
