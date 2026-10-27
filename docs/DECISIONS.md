# Architectural & Technical Decisions Log: Strategic Intelligence Suite

## Decision 001: Strategic Intelligence Architecture
- **Date**: 2026-10-18
- **Context**: The user requested an advanced Strategic Intelligence Suite encompassing:
  1. Automated Pricing Strategy Evaluation & Explainability
  2. Pricing Strategy A/B Testing
  3. Seasonal Pricing & Demand Prediction
  4. Competitor Price Comparison & Cross-Price Elasticity
  5. Automated PDF Report Generation
  6. Fair Pricing & Bias Detection (4/5ths Rule)
  7. Sales Drop Causal Counterfactual Root-Cause Analysis
- **Decision**: Created dedicated subpackage `econocausal.intelligence` containing modular engines:
  - `ab_testing.py`: Two-sample Z-test, Welch's t-test, confidence intervals, power, MDE, Bayesian win prob.
  - `seasonality.py`: Event calendar (Black Friday, Diwali, Christmas, Weekends, Weekdays), demand index vs elasticity.
  - `competitor.py`: Price Index (PI), cross-price elasticity, vulnerability rating, defensive recommendations.
  - `fairness.py`: Demographic parity, Disparate Impact Ratio (DIR) under 4/5ths rule, compliance rating, causal sensitivity vs discrimination.
  - `root_cause.py`: Causal counterfactual decomposition of revenue loss (competitor, macro, elasticity fatigue, seasonal dip, misallocation).
  - `explainability.py`: Feature attribution for treatment effect heterogeneity (ITE) and counterfactual what-ifs.
  - `report.py`: Automated executive PDF/HTML report generator with `@media print` support and KPI scorecard.
- **API**: Exposed via `/intelligence/*` endpoints with Pydantic v2 schemas.
- **Frontend**: Integrated interactive tab `Strategic Intelligence` in React + Plotly frontend with live charts, parameter sliders, what-if simulators, and one-click PDF printing.
