export interface HealthResponse {
  status: string;
  version: string;
}

export interface DatasetProfile {
  dataset_id: string;
  rows: number;
  columns: string[];
  treatment_distribution: Record<string, number>;
  purchase_rate: number;
  missing_fractions: Record<string, number>;
  validation_warnings: string[];
}

export interface DemoDataRequest {
  n?: number;
  seed?: number;
  hidden_confounder_strength?: number;
}

export interface GraphNode {
  id: string;
  role: 'treatment' | 'outcome' | 'confounder' | 'unobserved';
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  dashed?: boolean;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  estimand: string;
  adjustment_set: string[];
  estimand_text: string;
}

export interface ModelSummary {
  model_id: string;
  estimator_type: string;
  dataset_id: string;
  trained_at: string;
  cv: number;
  n_estimators: number | null;
  seed: number;
  metrics: Record<string, any>;
  nuisance_scores: Record<string, number>;
}

export interface AuditTest {
  test: string;
  status: 'PASS' | 'WARN' | 'FAIL';
  effect_before: number | null;
  effect_after: number | null;
  p_value: number | null;
  ci: number[] | null;
  note: string;
}

export interface AuditResponse {
  model_id: string;
  tests: AuditTest[];
  overall_status: 'PASS' | 'WARN' | 'FAIL';
}

export interface QiniCurveData {
  fractions: number[];
  uplift_values: number[];
  qini_coefficient: number;
  auuc: number;
  uplift_at_10: number;
  uplift_at_20: number;
  uplift_at_30: number;
  discount_level: number;
  estimator: string;
}

export interface UpliftResponse {
  model_id: string;
  curves: QiniCurveData[];
  decile_data: Array<{
    decile: number;
    targeted_uplift: number;
    baseline_uplift: number;
  }>;
  metrics_vs_targets: Record<
    string,
    {
      achieved: number;
      target: number;
      status: string;
    }
  >;
}

export interface CATEDistribution {
  model_id: string;
  level: number;
  histogram: {
    bins: number[];
    counts: number[];
  };
  mean_ite: number;
  std_ite: number;
}

export interface OptimiseRequest {
  model_id: string;
  dataset_id: string;
  budget: number;
  levels?: number[];
  objective?: string;
  mode?: 'standard' | 'conservative';
  margin_rate?: number;
  max_treat_fraction?: number;
  min_uplift?: number | null;
}

export interface AllocationSummary {
  allocation_id: string;
  model_id: string;
  dataset_id: string;
  budget: number;
  total_spend: number;
  total_delta_pi: number;
  n_treated: number;
  n_total: number;
  lp_obj_value: number;
  optimality_gap: number;
  budget_compliant: boolean;
  segment_mix: Record<string, number>;
}

export interface AllocationRow {
  customer_id: string;
  segment: string;
  p0: number;
  allocated_discount: number;
  expected_spend: number;
  expected_delta_pi: number;
  expected_uplift: number;
  ite_lower: number;
  ite_upper: number;
}

export interface AllocationPage {
  data: AllocationRow[];
  total: number;
  page: number;
  size: number;
}

export interface FeatureDriftResult {
  name: string;
  psi: number;
  ks_statistic: number | null;
  chi2_statistic: number | null;
  flag: 'GREEN' | 'AMBER' | 'RED';
}

export interface DriftRequest {
  model_id: string;
  new_data: Record<string, any>[];
}

export interface DriftResponse {
  status: 'GREEN' | 'AMBER' | 'RED';
  features: FeatureDriftResult[];
  residual_drift: number | null;
  ate_shift: number | null;
  note: string;
}

// ── Strategic Intelligence Suite ──────────────────────────────────────────────
export interface ABVariantMetric {
  strategy_id: string;
  strategy_name: string;
  sample_size: number;
  treated_count: number;
  treatment_rate: number;
  conversion_rate: number;
  avg_order_value: number;
  revenue_per_user: number;
  total_revenue: number;
  total_spend: number;
  net_profit: number;
  profit_margin_pct: number;
  conv_lift_abs: number;
  conv_lift_pct: number;
  profit_lift_abs: number;
  profit_lift_pct: number;
  z_statistic: number;
  p_value: number;
  ci_lower: number;
  ci_upper: number;
  is_statistically_significant: boolean;
  bayes_prob_better_than_control: number;
}

export interface SegmentABLift {
  segment: string;
  variant_conv_rates: Record<string, number>;
  variant_net_profits: Record<string, number>;
}

export interface ABTestResponse {
  test_id: string;
  baseline_strategy: string;
  winning_strategy: string;
  winner_recommendation: string;
  variants: ABVariantMetric[];
  segment_breakdown: SegmentABLift[];
  statistical_power: number;
  min_detectable_effect: number;
  confidence_level: number;
}

export interface ABTestRequest {
  dataset_id?: string;
  sample_size?: number;
  confidence_level?: number;
  baseline_budget?: number;
}

export interface SeasonalityPeriod {
  period_id: string;
  period_name: string;
  date_label: string;
  period_type: 'regular' | 'weekend' | 'festival' | 'holiday_peak';
  seasonal_demand_index: number;
  price_elasticity: number;
  optimal_base_discount: number;
  predicted_conversion_rate: number;
  projected_revenue: number;
  projected_net_profit: number;
  pricing_action: string;
}

export interface SeasonalForecastResponse {
  baseline_demand: number;
  avg_elasticity: number;
  peak_demand_period: string;
  peak_elasticity_period: string;
  overall_seasonal_lift_pct: number;
  periods: SeasonalityPeriod[];
  executive_advice: string[];
}

export interface CompetitorProductPrice {
  competitor_id: string;
  competitor_name: string;
  competitor_price: number;
  price_difference_pct: number;
  position: 'undercut' | 'parity' | 'premium';
  cross_price_elasticity: number;
  vulnerability_tier: 'low' | 'medium' | 'high' | 'critical';
  recommended_our_discount: number;
  defensive_pricing_strategy: string;
}

export interface CompetitorComparisonResponse {
  product_category: string;
  our_base_price: number;
  market_median_price: number;
  price_index_vs_median: number;
  our_current_position: string;
  competitors: CompetitorProductPrice[];
  pricing_recommendations: string[];
}

export interface CompetitorComparisonRequest {
  category?: string;
  our_base_price?: number;
  competitors_override?: any[];
}

export interface DemographicGroupFairness {
  group_name: string;
  sample_size: number;
  group_share_pct: number;
  avg_discount_received: number;
  discount_allocation_rate: number;
  mean_causal_ite: number;
  disparate_impact_ratio: number;
  statistical_parity_diff: number;
  fairness_status: 'PASS' | 'WARNING' | 'FAIL';
}

export interface FairnessAuditResponse {
  protected_attribute: string;
  privileged_group: string;
  overall_fairness_score: number;
  overall_compliance_status: 'COMPLIANT' | 'BORDERLINE' | 'DISPARATE_IMPACT_DETECTED';
  four_fifths_rule_passed: boolean;
  groups: DemographicGroupFairness[];
  audit_findings: string[];
  mitigation_recommendation: string;
}

export interface FairnessAuditRequest {
  dataset_id?: string;
  protected_attribute?: 'age_bracket' | 'customer_tenure_tier' | 'loyalty_tier';
  discount_threshold?: number;
}

export interface SalesDropDriver {
  driver_name: string;
  driver_category: 'macro' | 'competitor' | 'elasticity' | 'seasonality' | 'targeting';
  impact_amount_usd: number;
  impact_pct_of_drop: number;
  causal_confidence: number;
  description: string;
  counterfactual_recovery_potential_usd: number;
}

export interface SalesDropAnalysisResponse {
  prior_period_revenue: number;
  current_period_revenue: number;
  total_revenue_drop_usd: number;
  drop_pct: number;
  severity: 'low' | 'moderate' | 'severe' | 'critical';
  primary_root_cause: string;
  drivers: SalesDropDriver[];
  immediate_recovery_playbook: string[];
}

export interface SalesDropAnalysisRequest {
  prior_period_revenue?: number;
  current_period_revenue?: number;
  drop_horizon_days?: number;
}

export interface FeatureAttribution {
  feature_name: string;
  feature_value: number | string;
  attribution_weight: number;
  direction: 'positive' | 'negative' | 'neutral';
  insight: string;
}

export interface ExplainabilityResponse {
  customer_id: string;
  segment: string;
  baseline_purchase_prob: number;
  assigned_discount: number;
  predicted_ite: number;
  expected_profit: number;
  explanation_summary: string;
  feature_attributions: FeatureAttribution[];
  counterfactual_options: any[];
}

export interface ExplainabilityRequest {
  customer_id?: string;
  features?: Record<string, number>;
}

export interface GenerateReportResponse {
  report_id: string;
  generated_at: string;
  title: string;
  summary_metrics: Record<string, any>;
  html_content: string;
  executive_recommendations: string[];
}

export interface GenerateReportRequest {
  report_title?: string;
  dataset_id?: string;
  include_ab_testing?: boolean;
  include_seasonality?: boolean;
  include_competitor?: boolean;
  include_fairness?: boolean;
  include_root_cause?: boolean;
}
