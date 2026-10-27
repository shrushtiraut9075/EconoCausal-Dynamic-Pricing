"""EconoCausal Strategic Intelligence Suite.

Exports:
- A/B Testing Engine
- Seasonal Pricing & Elasticity Engine
- Competitor Price & Cross-Elasticity Engine
- Fair Pricing & Bias Audit Engine
- Sales Drop Root-Cause Analysis Engine
- Customer Pricing Explainability Engine
- Executive PDF / HTML Report Generator
"""

from econocausal.intelligence.ab_testing import run_pricing_ab_test
from econocausal.intelligence.competitor import evaluate_competitor_pricing
from econocausal.intelligence.explainability import explain_customer_pricing
from econocausal.intelligence.fairness import audit_pricing_fairness
from econocausal.intelligence.report import generate_executive_report
from econocausal.intelligence.root_cause import analyze_sales_drop_root_cause
from econocausal.intelligence.seasonality import get_seasonal_pricing_forecast

__all__ = [
    "analyze_sales_drop_root_cause",
    "audit_pricing_fairness",
    "evaluate_competitor_pricing",
    "explain_customer_pricing",
    "generate_executive_report",
    "get_seasonal_pricing_forecast",
    "run_pricing_ab_test",
]
