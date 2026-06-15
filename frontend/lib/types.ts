/**
 * TypeScript interfaces mirroring the Roofus backend Pydantic models.
 */

// ---------------------------------------------------------------------------
// Score helpers
// ---------------------------------------------------------------------------

export type ScoreTier = "Excellent" | "Good" | "Moderate" | "Below Average" | "Poor";

export function getScoreTier(score: number): ScoreTier {
  if (score >= 85) return "Excellent";
  if (score >= 70) return "Good";
  if (score >= 50) return "Moderate";
  if (score >= 30) return "Below Average";
  return "Poor";
}

export function getScoreColor(score: number): string {
  if (score >= 85) return "#10B981";
  if (score >= 70) return "#84CC16";
  if (score >= 50) return "#F59E0B";
  if (score >= 30) return "#F97316";
  return "#EF4444";
}

export function getScoreLabel(score: number): string {
  if (score >= 85) return "Excellent Viability";
  if (score >= 70) return "Good Viability";
  if (score >= 50) return "Moderate Viability";
  if (score >= 30) return "Below Average";
  return "Poor Viability";
}

// ---------------------------------------------------------------------------
// Building types
// ---------------------------------------------------------------------------

export interface SubsidySummary {
  eligible_programs: string[];
  total_annual_value: number;
  total_onetime_value: number;
  aggregation_tier: string;
  grid_combined_kw: number;
  grid_building_count: number;
}

export interface BuildingProperties {
  id: string;
  address: string;
  roof_area_sqft: number;
  year_built: number;
  num_units: number;
  num_floors: number;
  zoning: string;
  owner_name: string;
  owner_address: string;
  owner_phone: string;
  owner_email: string;
  avg_ghi: number;
  in_food_desert: boolean;
  hvac_proxy_score: number;
  estimated_peak_kw: number;
  aggregation_grid_id: string;
  score: number;
  score_structural: number;
  score_area: number;
  score_solar: number;
  score_zoning: number;
  score_food_desert: number;
  score_aggregation: number;
  subsidy_summary: SubsidySummary;
}

export interface BuildingFeature {
  type: "Feature";
  geometry: GeoJSON.Geometry;
  properties: BuildingProperties;
}

export interface BuildingCollection {
  type: "FeatureCollection";
  features: BuildingFeature[];
}

// ---------------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------------

export interface BuildingStats {
  total_buildings: number;
  avg_score: number;
  high_potential: number;
  total_roof_sqft: number;
  total_units: number;
  by_zoning: Record<string, number>;
  by_score_tier: Record<string, number>;
}

// ---------------------------------------------------------------------------
// Grid types
// ---------------------------------------------------------------------------

export interface GridProperties {
  grid_id: string;
  building_count: number;
  total_units: number;
  total_roof_sqft: number;
  combined_peak_kw: number;
  meets_vpp_threshold: boolean;
  meets_cl1_threshold: boolean;
  aggregation_tier: string;
  potential_annual_value: number;
  buildings_needed_for_cl1: number;
}

export interface GridFeature {
  type: "Feature";
  geometry: GeoJSON.Geometry;
  properties: GridProperties;
}

export interface GridCollection {
  type: "FeatureCollection";
  features: GridFeature[];
}

// ---------------------------------------------------------------------------
// Score breakdown factor definition
// ---------------------------------------------------------------------------

export interface ScoreFactor {
  key: string;
  label: string;
  score: number;
  rawValue: string;
}

// ---------------------------------------------------------------------------
// Persona
// ---------------------------------------------------------------------------

export type Persona = "developer" | "owner";

// ---------------------------------------------------------------------------
// Revenue types
// ---------------------------------------------------------------------------

export interface CropMix {
  leafy_greens_pct: number;
  herbs_pct: number;
  microgreens_pct: number;
}

export interface RevenueAssumptions {
  crop_mix: CropMix;
  lease_rate?: number;
  construction_cost_per_sqft?: number;
  structural_cost_per_sqft?: number;
  electricity_cost_per_sqft?: number;
  water_cost_per_sqft?: number;
  gas_cost_per_sqft?: number;
  labor_cost_per_sqft?: number;
  supplies_cost_per_sqft?: number;
  leafy_greens_price?: number;
  herbs_price?: number;
  microgreens_price?: number;
  leafy_greens_yield?: number;
  herbs_yield?: number;
  microgreens_yield?: number;
}

export interface CropRevenueDetail {
  crop: string;
  area_sqft: number;
  pct: number;
  yield_lbs: number;
  price_per_lb: number;
  revenue: number;
}

export interface CostLineItem {
  category: string;
  icon: string;
  amount: number;
}

export interface RevenueProjection {
  building_id: string;
  roof_area_sqft: number;
  crop_revenues: CropRevenueDetail[];
  total_annual_revenue: number;
  operating_costs: CostLineItem[];
  total_annual_costs: number;
  annual_net_profit: number;
  margin_pct: number;
  startup_greenhouse: number;
  startup_structural: number;
  startup_total: number;
  months_to_breakeven: number;
  five_year_cash_flow: number[];
}

export interface OwnerRevenueProjection {
  building_id: string;
  roof_area_sqft: number;
  lease_rate: number;
  annual_lease_income: number;
  annual_energy_savings: number;
  onetime_tax_incentive: number;
  total_annual_revenue: number;
  property_value_current: number;
  green_roof_premium_pct: number;
  property_value_new: number;
  property_value_increase: number;
  ten_year_cumulative: number;
}

// ---------------------------------------------------------------------------
// Subsidy types
// ---------------------------------------------------------------------------

export interface EnergyProfile {
  estimated_peak_kw: number;
  estimated_annual_kwh: number;
  current_rate_schedule: string;
  summer_rate_tier: string;
  annual_energy_cost_estimate: number;
}

export interface ThresholdIndicator {
  current_tier: string;
  target_tier: string;
  kwh_reduction_needed: number;
  pct_reduction_needed: number;
  greenhouse_demand_shed_potential_kw: number;
}

export interface ProgramDetail {
  eligible: boolean | string;
  description: string;
  upfront_incentive_per_kw?: number;
  performance_incentive_per_kwh?: number;
  estimated_annual_value?: number;
  estimated_onetime_value?: number;
  lmi_incentive_per_kw?: number;
  enrollment_bonus?: number;
  annual_incentive?: number;
  per_unit_value?: number;
  total_property_value?: number;
  max_per_unit?: number;
  total_property_max?: number;
  max_per_household?: number;
  measures?: string[];
  savings_tier?: string;
  per_unit_rebate?: number;
  lmi_per_unit_rebate?: number;
  total_property_estimate?: number;
  reason?: string;
  kw_shortfall?: number;
  buildings_needed?: number;
  potential_value_if_eligible?: string;
  summer_credit_months?: string;
}

export interface DemandResponsePrograms {
  vpp_consumer: ProgramDetail;
  vpp_utility: ProgramDetail;
  tempcheck: ProgramDetail;
  cl1_aggregated: ProgramDetail;
  dpec5_aggregated: ProgramDetail;
}

export interface EfficiencyRebates {
  gp_multifamily: ProgramDetail;
  gefa_her: ProgramDetail;
  gefa_hear: ProgramDetail;
}

export interface AggregationBonus {
  grid_id: string;
  grid_combined_kw: number;
  current_tier: string;
  next_tier: string;
  kw_to_next_tier: number;
  buildings_to_next_tier: number;
  current_grid_annual_value: number;
  next_tier_annual_value: number;
  uplift_if_threshold_met: number;
}

export interface BuildingSubsidyDetail {
  building_id: string;
  energy_profile: EnergyProfile;
  threshold_indicator: ThresholdIndicator;
  demand_response_programs: DemandResponsePrograms;
  efficiency_rebates: EfficiencyRebates;
  aggregation_bonus: AggregationBonus;
}

// ---------------------------------------------------------------------------
// Score breakdown factor definition
// ---------------------------------------------------------------------------

export function getBuildingScoreFactors(props: BuildingProperties): ScoreFactor[] {
  return [
    {
      key: "structural",
      label: "Structural Readiness",
      score: props.score_structural,
      rawValue: `HVAC ${props.hvac_proxy_score}`,
    },
    {
      key: "area",
      label: "Roof Area",
      score: props.score_area,
      rawValue: `${props.roof_area_sqft.toLocaleString()} sq ft`,
    },
    {
      key: "solar",
      label: "Solar Exposure",
      score: props.score_solar,
      rawValue: `${props.avg_ghi} GHI`,
    },
    {
      key: "zoning",
      label: "Zoning",
      score: props.score_zoning,
      rawValue: props.zoning,
    },
    {
      key: "food_desert",
      label: "Food Desert Impact",
      score: props.score_food_desert,
      rawValue: props.in_food_desert ? "Yes" : "No",
    },
    {
      key: "aggregation",
      label: "Aggregation Bonus",
      score: props.score_aggregation,
      rawValue: props.aggregation_grid_id || "N/A",
    },
  ];
}
