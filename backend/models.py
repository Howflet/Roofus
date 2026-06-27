"""Pydantic schemas for the Roofus API."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ZoningCode(str, Enum):
    R4 = "R-4"
    R5 = "R-5"


class AggregationTier(str, Enum):
    VPP = "VPP"
    CL1 = "CL-1"
    DPEC5 = "DPEC-5"
    BELOW = "Below Threshold"


class ScoreTier(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    MODERATE = "Moderate"
    BELOW_AVG = "Below Average"
    POOR = "Poor"


# ---------------------------------------------------------------------------
# Sub‑models
# ---------------------------------------------------------------------------


class SubsidySummary(BaseModel):
    eligible_programs: list[str] = Field(default_factory=list)
    total_annual_value: float = 0
    total_onetime_value: float = 0
    aggregation_tier: str = "Below Threshold"
    grid_combined_kw: float = 0
    grid_building_count: int = 0


class ScoreBreakdown(BaseModel):
    score_structural: float = 0
    score_area: float = 0
    score_solar: float = 0
    score_zoning: float = 0
    score_food_desert: float = 0
    score_aggregation: float = 0


class EnergyProfile(BaseModel):
    estimated_peak_kw: float = 0
    estimated_annual_kwh: float = 0
    current_rate_schedule: str = "R-30"
    summer_rate_tier: str = ""
    annual_energy_cost_estimate: float = 0


class ThresholdIndicator(BaseModel):
    current_tier: str = "Mid"
    target_tier: str = "Baseline"
    kwh_reduction_needed: float = 0
    pct_reduction_needed: float = 0
    greenhouse_demand_shed_potential_kw: float = 0


class ProgramDetail(BaseModel):
    eligible: bool | str = False
    description: str = ""
    # Monetary fields – optional because not every program uses all of them
    upfront_incentive_per_kw: float | None = None
    performance_incentive_per_kwh: float | None = None
    estimated_annual_value: float | None = None
    estimated_onetime_value: float | None = None
    upfront_incentive_per_kw_lmi: float | None = Field(None, alias="lmi_incentive_per_kw")
    enrollment_bonus: float | None = None
    annual_incentive: float | None = None
    per_unit_value: float | None = None
    total_property_value: float | None = None
    max_per_unit: float | None = None
    total_property_max: float | None = None
    max_per_household: float | None = None
    measures: list[str] | None = None
    savings_tier: str | None = None
    per_unit_rebate: float | None = None
    lmi_per_unit_rebate: float | None = None
    total_property_estimate: float | None = None
    reason: str | None = None
    kw_shortfall: float | None = None
    buildings_needed: int | None = None
    potential_value_if_eligible: str | None = None
    summer_credit_months: str | None = None

    model_config = {"populate_by_name": True}


class DemandResponsePrograms(BaseModel):
    cl1_aggregated: ProgramDetail = Field(default_factory=ProgramDetail)
    dpec5_aggregated: ProgramDetail = Field(default_factory=ProgramDetail)


class EfficiencyRebates(BaseModel):
    gp_multifamily: ProgramDetail = Field(default_factory=ProgramDetail)
    gefa_her: ProgramDetail = Field(default_factory=ProgramDetail)
    gefa_hear: ProgramDetail = Field(default_factory=ProgramDetail)


class AggregationBonus(BaseModel):
    grid_id: str = ""
    grid_combined_kw: float = 0
    current_tier: str = "Below Threshold"
    next_tier: str = ""
    kw_to_next_tier: float = 0
    buildings_to_next_tier: int = 0
    current_grid_annual_value: float = 0
    next_tier_annual_value: float = 0
    uplift_if_threshold_met: float = 0


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------


class BuildingProperties(BaseModel):
    id: str
    address: str = ""
    roof_area_sqft: float = 0
    year_built: int = 0
    num_units: int = 0
    num_floors: int = 0
    zoning: str = ""
    owner_name: str = ""
    owner_address: str = ""
    owner_phone: str = ""
    owner_email: str = ""
    avg_ghi: float = 0
    in_food_desert: bool = False
    hvac_proxy_score: float = 0
    estimated_peak_kw: float = 0
    aggregation_grid_id: str = ""
    score: float = 0
    score_structural: float = 0
    score_area: float = 0
    score_solar: float = 0
    score_zoning: float = 0
    score_food_desert: float = 0
    score_aggregation: float = 0
    subsidy_summary: SubsidySummary = Field(default_factory=SubsidySummary)


class BuildingFeature(BaseModel):
    type: str = "Feature"
    geometry: dict[str, Any] = Field(default_factory=dict)
    properties: BuildingProperties


class BuildingCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[BuildingFeature] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Building stats
# ---------------------------------------------------------------------------


class BuildingStats(BaseModel):
    total_buildings: int = 0
    avg_score: float = 0
    high_potential: int = 0  # score >= 70
    total_roof_sqft: float = 0
    total_units: int = 0
    by_zoning: dict[str, int] = Field(default_factory=dict)
    by_score_tier: dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Subsidy detail response
# ---------------------------------------------------------------------------


class BuildingSubsidyDetail(BaseModel):
    building_id: str
    energy_profile: EnergyProfile = Field(default_factory=EnergyProfile)
    threshold_indicator: ThresholdIndicator = Field(default_factory=ThresholdIndicator)
    demand_response_programs: DemandResponsePrograms = Field(default_factory=DemandResponsePrograms)
    efficiency_rebates: EfficiencyRebates = Field(default_factory=EfficiencyRebates)
    aggregation_bonus: AggregationBonus = Field(default_factory=AggregationBonus)


class SubsidyCustomRequest(BaseModel):
    """Custom assumptions for POST /buildings/{id}/subsidies."""
    estimated_peak_kw: float | None = None
    estimated_annual_kwh: float | None = None
    num_units: int | None = None
    is_lmi: bool = False


# ---------------------------------------------------------------------------
# Revenue / Developer projections
# ---------------------------------------------------------------------------


class CropMix(BaseModel):
    # Default leafy-greens-dominant, because at-scale CEA operating data only
    # exists for leafy greens (BrightFarms/Gotham Greens). Herbs/microgreens
    # carry premium prices but the addressable volume saturates fast in a small
    # market, so they default to a minority share. User-adjustable via POST.
    leafy_greens_pct: float = Field(60.0, ge=0, le=100)
    herbs_pct: float = Field(25.0, ge=0, le=100)
    microgreens_pct: float = Field(15.0, ge=0, le=100)


# Revenue assumptions calibrated to published greenhouse-CEA operating data,
# NOT vertical-farm or boutique-retail figures. Primary source: AgFunder's
# greenhouse-vs-vertical economics breakdown of BrightFarms' actual operations
# (https://agfundernews.com/the-economics-of-local-vertical-and-greenhouse-farming-are-getting-competitive):
#   - BrightFarms greenhouse: 2.0M lb/yr over 280,000 sqft  -> ~7.1 lb/sqft/yr
#   - Capex $65.48/sqft; all-in delivered cost $2.33/lb
#     (growing $1.52/lb incl. labor $1.10/lb, delivery $0.20/lb, depr. $0.61/lb)
#   - Greenhouse-grown retail ceiling ~$4/lb (operators sell wholesale below that)
# Herb price from fresh-basil wholesale $13-22/kg (~$6-10/lb, FrutPlanet/Accio);
# microgreens from wholesale-at-volume ~$12-16/lb (boutique $25-50/lb does not
# hold at this production volume). The old defaults (8/5/12 lb yields at
# $4.50/$18/$30 retail prices) implied an indefensible ~81% margin / 7-mo payback;
# real greenhouse CEA runs thin contribution margins before SG&A and financing.
class RevenueAssumptions(BaseModel):
    crop_mix: CropMix = Field(default_factory=CropMix)
    # $/sq ft/year
    lease_rate: float = 8.0
    construction_cost_per_sqft: float = 55.0   # BrightFarms ~$65/sqft, less rooftop structural carve-out below
    structural_cost_per_sqft: float = 12.0     # rooftop load reinforcement (separate PE scope)
    electricity_cost_per_sqft: float = 2.50    # greenhouse (daylight + supplemental), well below vertical-farm lighting load
    water_cost_per_sqft: float = 0.60
    gas_cost_per_sqft: float = 1.00            # winter heating, Atlanta climate
    labor_cost_per_sqft: float = 8.00          # ~$1.10/lb x ~7 lb/sqft (AgFunder labor share)
    supplies_cost_per_sqft: float = 2.50       # seed/media/nutrients + insurance + overhead proxy
    # Crop prices $/lb (wholesale, not retail)
    leafy_greens_price: float = 2.75           # operator wholesale below ~$4/lb retail ceiling
    herbs_price: float = 6.00                  # fresh basil wholesale at foodservice volume
    microgreens_price: float = 12.00           # wholesale-at-volume, not boutique retail
    # Crop yields lbs/sq ft/year (whole-footprint basis, matching BrightFarms ops data)
    leafy_greens_yield: float = 7.0
    herbs_yield: float = 4.0
    microgreens_yield: float = 7.0


class CropRevenueDetail(BaseModel):
    crop: str
    area_sqft: float
    pct: float
    yield_lbs: float
    price_per_lb: float
    revenue: float


class CostLineItem(BaseModel):
    category: str
    icon: str = ""
    amount: float


class RevenueProjection(BaseModel):
    building_id: str
    roof_area_sqft: float
    # Revenue
    crop_revenues: list[CropRevenueDetail] = Field(default_factory=list)
    total_annual_revenue: float = 0
    # Operating costs
    operating_costs: list[CostLineItem] = Field(default_factory=list)
    total_annual_costs: float = 0
    # Bottom line
    annual_net_profit: float = 0
    margin_pct: float = 0
    # Startup
    startup_greenhouse: float = 0
    startup_structural: float = 0
    startup_total: float = 0
    # ROI
    months_to_breakeven: int = 0
    five_year_cash_flow: list[float] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Owner revenue response
# ---------------------------------------------------------------------------


class OwnerRevenueProjection(BaseModel):
    building_id: str
    roof_area_sqft: float
    lease_rate: float
    annual_lease_income: float = 0
    annual_energy_savings: float = 0
    onetime_tax_incentive: float = 0
    total_annual_revenue: float = 0
    property_value_current: float = 0
    green_roof_premium_pct: float = 3.5
    property_value_new: float = 0
    property_value_increase: float = 0
    ten_year_cumulative: float = 0


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------


class GridProperties(BaseModel):
    grid_id: str
    building_count: int = 0
    total_units: int = 0
    total_roof_sqft: float = 0
    combined_peak_kw: float = 0
    meets_vpp_threshold: bool = False
    meets_cl1_threshold: bool = False
    aggregation_tier: str = "Below Threshold"
    potential_annual_value: float = 0
    buildings_needed_for_cl1: int = 0


class GridFeature(BaseModel):
    type: str = "Feature"
    geometry: dict[str, Any] = Field(default_factory=dict)
    properties: GridProperties


class GridCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GridFeature] = Field(default_factory=list)


class GridDetail(BaseModel):
    grid: GridFeature
    buildings: list[BuildingFeature] = Field(default_factory=list)


class GridSubsidyResponse(BaseModel):
    grid_id: str
    aggregation_tier: str
    combined_peak_kw: float
    building_count: int
    total_annual_subsidy_value: float
    total_onetime_value: float
    programs: dict[str, Any] = Field(default_factory=dict)
