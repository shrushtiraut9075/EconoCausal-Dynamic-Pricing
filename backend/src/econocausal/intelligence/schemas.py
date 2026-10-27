"""Pydantic v2 schemas for EconoCausal Strategic Intelligence Suite.

Covers:
- Strategy A/B testing
- Seasonal pricing & demand forecasting
- Competitor price comparison & cross-price elasticity
- Fair pricing & bias detection
- Sales drop root-cause decomposition
- Pricing explainability & counterfactuals
- Executive PDF report generation
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Strategy A/B Testing ───────────────────────────────────────────────────────
class ABVariantMetric(BaseModel):
    strategy_id: str
    strategy_name: str
    sample_size: int
    treated_count: int
    treatment_rate: float
    conversion_rate: float
    avg_order_value: float
    revenue_per_user: float
    total_revenue: float
    total_spend: float
    net_profit: float
    profit_margin_pct: float
    # Lift vs Control
    conv_lift_abs: float
    conv_lift_pct: float
    profit_lift_abs: float
    profit_lift_pct: float
    # Statistics
    z_statistic: float
    p_value: float
    ci_lower: float
    ci_upper: float
    is_statistically_significant: bool
    bayes_prob_better_than_control: float


class SegmentABLift(BaseModel):
    segment: str
    variant_conv_rates: dict[str, float]
    variant_net_profits: dict[str, float]


class ABTestResponse(BaseModel):
    test_id: str
    baseline_strategy: str
    winning_strategy: str
    winner_recommendation: str
    variants: list[ABVariantMetric]
    segment_breakdown: list[SegmentABLift]
    statistical_power: float
    min_detectable_effect: float
    confidence_level: float


class ABTestRequest(BaseModel):
    dataset_id: str | None = None
    sample_size: int = Field(default=5000, ge=500, le=50000)
    confidence_level: float = Field(default=0.95, ge=0.80, le=0.999)
    baseline_budget: float = Field(default=5000.0, ge=500.0)


# ── Seasonal Pricing & Demand ─────────────────────────────────────────────────
class SeasonalityPeriod(BaseModel):
    period_id: str
    period_name: str
    date_label: str
    period_type: Literal["regular", "weekend", "festival", "holiday_peak"]
    seasonal_demand_index: float
    price_elasticity: float
    optimal_base_discount: int
    predicted_conversion_rate: float
    projected_revenue: float
    projected_net_profit: float
    pricing_action: str


class SeasonalForecastResponse(BaseModel):
    baseline_demand: float
    avg_elasticity: float
    peak_demand_period: str
    peak_elasticity_period: str
    overall_seasonal_lift_pct: float
    periods: list[SeasonalityPeriod]
    executive_advice: list[str]


# ── Competitor Price Comparison ───────────────────────────────────────────────
class CompetitorProductPrice(BaseModel):
    competitor_id: str
    competitor_name: str
    competitor_price: float
    price_difference_pct: float
    position: Literal["undercut", "parity", "premium"]
    cross_price_elasticity: float
    vulnerability_tier: Literal["low", "medium", "high", "critical"]
    recommended_our_discount: int
    defensive_pricing_strategy: str


class CompetitorComparisonResponse(BaseModel):
    product_category: str
    our_base_price: float
    market_median_price: float
    price_index_vs_median: float
    our_current_position: str
    competitors: list[CompetitorProductPrice]
    pricing_recommendations: list[str]


class CompetitorComparisonRequest(BaseModel):
    category: str = "Electronics & Audio"
    our_base_price: float = Field(default=120.0, ge=10.0, le=10000.0)
    competitors_override: list[dict[str, Any]] | None = None


# ── Fair Pricing & Bias Detection ─────────────────────────────────────────────
class DemographicGroupFairness(BaseModel):
    group_name: str
    sample_size: int
    group_share_pct: float
    avg_discount_received: float
    discount_allocation_rate: float  # Prob of receiving any discount > 0
    mean_causal_ite: float
    disparate_impact_ratio: float  # vs privileged group (4/5ths rule: 0.8 - 1.25)
    statistical_parity_diff: float  # diff in treatment rate vs privileged
    fairness_status: Literal["PASS", "WARNING", "FAIL"]


class FairnessAuditResponse(BaseModel):
    protected_attribute: str
    privileged_group: str
    overall_fairness_score: float  # 0 to 100
    overall_compliance_status: Literal["COMPLIANT", "BORDERLINE", "DISPARATE_IMPACT_DETECTED"]
    four_fifths_rule_passed: bool
    groups: list[DemographicGroupFairness]
    audit_findings: list[str]
    mitigation_recommendation: str


class FairnessAuditRequest(BaseModel):
    dataset_id: str | None = None
    protected_attribute: Literal["age_bracket", "customer_tenure_tier", "loyalty_tier"] = (
        "age_bracket"
    )
    discount_threshold: int = Field(default=0, ge=0, le=20)


# ── Sales Drop Root-Cause Analysis ────────────────────────────────────────────
class SalesDropDriver(BaseModel):
    driver_name: str
    driver_category: Literal["macro", "competitor", "elasticity", "seasonality", "targeting"]
    impact_amount_usd: float
    impact_pct_of_drop: float
    causal_confidence: float
    description: str
    counterfactual_recovery_potential_usd: float


class SalesDropAnalysisResponse(BaseModel):
    prior_period_revenue: float
    current_period_revenue: float
    total_revenue_drop_usd: float
    drop_pct: float
    severity: Literal["low", "moderate", "severe", "critical"]
    primary_root_cause: str
    drivers: list[SalesDropDriver]
    immediate_recovery_playbook: list[str]


class SalesDropAnalysisRequest(BaseModel):
    prior_period_revenue: float = Field(default=125000.0, ge=1000.0)
    current_period_revenue: float = Field(default=96000.0, ge=1000.0)
    drop_horizon_days: int = Field(default=30, ge=7, le=180)


# ── Explainability & What-If ──────────────────────────────────────────────────
class FeatureAttribution(BaseModel):
    feature_name: str
    feature_value: float | str
    attribution_weight: float
    direction: Literal["positive", "negative", "neutral"]
    insight: str


class ExplainabilityResponse(BaseModel):
    customer_id: str
    segment: str
    baseline_purchase_prob: float
    assigned_discount: int
    predicted_ite: float
    expected_profit: float
    explanation_summary: str
    feature_attributions: list[FeatureAttribution]
    counterfactual_options: list[dict[str, Any]]


class ExplainabilityRequest(BaseModel):
    customer_id: str | None = "CUST-84920"
    features: dict[str, float] | None = None


# ── Automated PDF / Executive Report ──────────────────────────────────────────
class GenerateReportRequest(BaseModel):
    report_title: str = "EconoCausal Executive Pricing & Strategic Intelligence Report"
    dataset_id: str | None = None
    include_ab_testing: bool = True
    include_seasonality: bool = True
    include_competitor: bool = True
    include_fairness: bool = True
    include_root_cause: bool = True


class GenerateReportResponse(BaseModel):
    report_id: str
    generated_at: str
    title: str
    summary_metrics: dict[str, Any]
    html_content: str
    executive_recommendations: list[str]
