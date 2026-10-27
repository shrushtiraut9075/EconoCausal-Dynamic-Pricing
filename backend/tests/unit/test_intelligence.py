"""Unit tests for the Strategic Intelligence Suite.

Validates:
- Pricing Strategy A/B Testing & statistical hypothesis tests
- Seasonal demand forecasting & elasticity shifts
- Competitor price comparison & cross-price elasticity
- Fair pricing & bias detection under 4/5ths rule
- Sales drop causal counterfactual decomposition
- Customer pricing explainability & what-if counterfactuals
- Automated executive PDF/HTML report generation
"""

from __future__ import annotations

from econocausal.intelligence.ab_testing import run_pricing_ab_test
from econocausal.intelligence.competitor import evaluate_competitor_pricing
from econocausal.intelligence.explainability import explain_customer_pricing
from econocausal.intelligence.fairness import audit_pricing_fairness
from econocausal.intelligence.report import generate_executive_report
from econocausal.intelligence.root_cause import analyze_sales_drop_root_cause
from econocausal.intelligence.schemas import (
    ABTestRequest,
    CompetitorComparisonRequest,
    ExplainabilityRequest,
    FairnessAuditRequest,
    GenerateReportRequest,
    SalesDropAnalysisRequest,
)
from econocausal.intelligence.seasonality import get_seasonal_pricing_forecast


def test_ab_testing_statistical_properties() -> None:
    """Validate A/B test simulation, metrics, and statistical significance."""
    req = ABTestRequest(sample_size=10000, confidence_level=0.95)
    res = run_pricing_ab_test(req)

    assert len(res.variants) == 5
    assert res.baseline_strategy == "control_zero"
    assert res.statistical_power >= 0.70
    assert res.min_detectable_effect > 0

    # DML variant should outperform blanket and control in net profit
    dml = next(v for v in res.variants if v.strategy_id == "dml_causal_optimal")
    ctrl = next(v for v in res.variants if v.strategy_id == "control_zero")
    blanket = next(v for v in res.variants if v.strategy_id == "blanket_10")

    assert dml.net_profit > ctrl.net_profit
    assert dml.net_profit > blanket.net_profit
    assert dml.is_statistically_significant is True
    assert dml.bayes_prob_better_than_control > 0.95
    assert len(res.segment_breakdown) == 4


def test_seasonal_pricing_forecast() -> None:
    """Validate seasonal demand prediction and elasticity shifts."""
    res = get_seasonal_pricing_forecast()

    assert len(res.periods) >= 6
    assert res.overall_seasonal_lift_pct > 0
    assert res.peak_demand_period != ""
    assert res.peak_elasticity_period != ""

    # Black Friday should have higher demand index than standard weekday
    bf = next(p for p in res.periods if "black_friday" in p.period_id)
    weekday = next(p for p in res.periods if "normal_weekday" in p.period_id)

    assert bf.seasonal_demand_index > weekday.seasonal_demand_index
    assert bf.price_elasticity < weekday.price_elasticity  # more negative elasticity
    assert len(res.executive_advice) >= 3


def test_competitor_price_comparison() -> None:
    """Validate competitor benchmarking and cross-price elasticity assessment."""
    req = CompetitorComparisonRequest(
        category="Consumer Electronics",
        our_base_price=150.0,
    )
    res = evaluate_competitor_pricing(req)

    assert res.our_base_price == 150.0
    assert len(res.competitors) == 5
    assert res.price_index_vs_median > 0

    # Ensure critical/high vulnerabilities have defensive actions
    for comp in res.competitors:
        assert comp.cross_price_elasticity > 0
        assert comp.defensive_pricing_strategy != ""


def test_fair_pricing_and_bias_audit() -> None:
    """Validate 4/5ths rule disparate impact evaluation."""
    req = FairnessAuditRequest(protected_attribute="age_bracket")
    res = audit_pricing_fairness(req)

    assert res.protected_attribute == "age_bracket"
    assert len(res.groups) >= 3
    assert 0 <= res.overall_fairness_score <= 100
    assert res.overall_compliance_status in ["COMPLIANT", "BORDERLINE", "DISPARATE_IMPACT_DETECTED"]

    # Check that Disparate Impact Ratio (DIR) is calculated for each group
    for g in res.groups:
        assert g.disparate_impact_ratio > 0
        assert g.discount_allocation_rate > 0
        assert g.fairness_status in ["PASS", "WARNING", "FAIL"]


def test_sales_drop_root_cause_analysis() -> None:
    """Validate causal counterfactual decomposition of revenue drop."""
    req = SalesDropAnalysisRequest(
        prior_period_revenue=150000.0,
        current_period_revenue=110000.0,
        drop_horizon_days=30,
    )
    res = analyze_sales_drop_root_cause(req)

    assert res.total_revenue_drop_usd == 40000.0
    assert res.drop_pct > 20.0
    assert res.severity in ["low", "moderate", "severe", "critical"]
    assert len(res.drivers) == 5

    # Sum of dollar impacts should equal total drop
    total_decomposed = sum(d.impact_amount_usd for d in res.drivers)
    assert abs(total_decomposed - res.total_revenue_drop_usd) < 1.0

    # Sum of share percentages should be approx 100%
    total_shares = sum(d.impact_pct_of_drop for d in res.drivers)
    assert abs(total_shares - 100.0) < 1.0

    assert len(res.immediate_recovery_playbook) >= 3


def test_pricing_explainability_and_counterfactuals() -> None:
    """Validate customer pricing explainability and counterfactual what-ifs."""
    req = ExplainabilityRequest(
        customer_id="TEST-USER-1",
        features={
            "days_since_last_order": 42.0,
            "discount_usage_rate": 0.70,
            "avg_order_value": 125.0,
            "tenure_days": 180.0,
            "order_frequency_90d": 4.0,
        },
    )
    res = explain_customer_pricing(req)

    assert res.customer_id == "TEST-USER-1"
    assert res.segment == "Persuadables"
    assert res.assigned_discount in [10, 20]
    assert len(res.feature_attributions) == 5
    assert len(res.counterfactual_options) >= 2


def test_automated_executive_report_generation() -> None:
    """Validate automated PDF/HTML report compilation."""
    req = GenerateReportRequest(
        report_title="Quarterly Causal Pricing & Strategic Intelligence Audit",
    )
    res = generate_executive_report(req)

    assert res.report_id.startswith("rpt_")
    assert "Quarterly Causal Pricing" in res.html_content
    assert "Pricing Strategy A/B Testing Scorecard" in res.html_content
    assert "Seasonal Pricing & Demand Elasticity Forecast" in res.html_content
    assert "Competitor Pricing & Cross-Price Elasticity Benchmark" in res.html_content
    assert "Fair Pricing & Demographic Bias Audit" in res.html_content
    assert "Sales Drop Causal Counterfactual Decomposition" in res.html_content
    assert len(res.summary_metrics) >= 6
