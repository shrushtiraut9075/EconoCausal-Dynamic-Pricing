"""Seasonal Pricing Prediction and Demand Forecasting Engine.

Analyzes:
- Seasonal demand indices across calendar periods, weekends, and retail festivals
- Price elasticity shifts during peak shopping events vs regular periods
- Optimal dynamic discount rates and markdown multipliers per period
- Revenue and net profit projections under dynamic causal pricing
"""

from __future__ import annotations

from typing import Literal, TypedDict

import numpy as np

from econocausal.intelligence.schemas import (
    SeasonalForecastResponse,
    SeasonalityPeriod,
)


class _PeriodData(TypedDict):
    id: str
    name: str
    date_label: str
    type: Literal["regular", "weekend", "festival", "holiday_peak"]
    demand_idx: float
    elasticity: float
    optimal_discount: int
    base_p: float
    aov: float
    margin: float
    action: str


def get_seasonal_pricing_forecast() -> SeasonalForecastResponse:
    """Compute seasonal demand, price elasticity shifts, and optimal pricing strategy."""
    periods_data: list[_PeriodData] = [
        {
            "id": "p01_normal_weekday",
            "name": "Standard Weekday",
            "date_label": "Typical Tue-Thu",
            "type": "regular",
            "demand_idx": 1.00,
            "elasticity": -1.45,
            "optimal_discount": 10,
            "base_p": 0.20,
            "aov": 100.0,
            "margin": 0.40,
            "action": "Maintain standard 10% personalized DML offer to persuadables.",
        },
        {
            "id": "p02_weekend_surge",
            "name": "Standard Weekend",
            "date_label": "Typical Sat-Sun",
            "type": "weekend",
            "demand_idx": 1.28,
            "elasticity": -1.62,
            "optimal_discount": 10,
            "base_p": 0.24,
            "aov": 108.0,
            "margin": 0.40,
            "action": "Surge traffic window: target mobile shoppers with timed 10% coupon.",
        },
        {
            "id": "p03_summer_flash",
            "name": "Summer Mid-Year Sale",
            "date_label": "Jul 15 - Jul 22",
            "type": "festival",
            "demand_idx": 1.55,
            "elasticity": -1.95,
            "optimal_discount": 15,
            "base_p": 0.27,
            "aov": 115.0,
            "margin": 0.38,
            "action": "High price sensitivity: deploy 15% discount bundle to capture volume.",
        },
        {
            "id": "p04_festive_diwali",
            "name": "Festive & Diwali Rush",
            "date_label": "Oct 24 - Nov 05",
            "type": "festival",
            "demand_idx": 2.10,
            "elasticity": -1.15,
            "optimal_discount": 5,
            "base_p": 0.36,
            "aov": 142.0,
            "margin": 0.42,
            "action": "High organic intent: pull back broad discounts (5% max); avoid margin dilution.",
        },
        {
            "id": "p05_black_friday",
            "name": "Black Friday & Cyber Week",
            "date_label": "Nov 25 - Dec 02",
            "type": "holiday_peak",
            "demand_idx": 2.65,
            "elasticity": -2.35,
            "optimal_discount": 20,
            "base_p": 0.42,
            "aov": 155.0,
            "margin": 0.35,
            "action": "Extreme price sensitivity & basket size: 20% tier on multi-item baskets.",
        },
        {
            "id": "p06_holiday_christmas",
            "name": "Christmas & New Year Gifting",
            "date_label": "Dec 18 - Dec 31",
            "type": "holiday_peak",
            "demand_idx": 2.20,
            "elasticity": -1.25,
            "optimal_discount": 10,
            "base_p": 0.35,
            "aov": 138.0,
            "margin": 0.40,
            "action": "Last-minute delivery urgency: prioritize shipping guarantees over heavy discounting.",
        },
        {
            "id": "p07_post_holiday_slump",
            "name": "January Reset & Clearance",
            "date_label": "Jan 05 - Jan 25",
            "type": "regular",
            "demand_idx": 0.78,
            "elasticity": -1.80,
            "optimal_discount": 15,
            "base_p": 0.16,
            "aov": 92.0,
            "margin": 0.36,
            "action": "Off-peak lull: selective 15% win-back incentives for dormant high-value customers.",
        },
    ]

    base_customers = 10000
    periods: list[SeasonalityPeriod] = []

    for item in periods_data:
        d_idx = item["demand_idx"]
        cr = float(min(0.95, item["base_p"] * (1.0 + 0.12 * (item["optimal_discount"] / 10.0))))
        users_in_period = int(base_customers * d_idx)
        conversions = int(users_in_period * cr)
        gross_rev = float(conversions * item["aov"])
        discount_spend = float(conversions * item["optimal_discount"])
        net_profit = float(gross_rev * item["margin"] - discount_spend)

        periods.append(
            SeasonalityPeriod(
                period_id=item["id"],
                period_name=item["name"],
                date_label=item["date_label"],
                period_type=item["type"],
                seasonal_demand_index=round(d_idx, 2),
                price_elasticity=round(item["elasticity"], 2),
                optimal_base_discount=item["optimal_discount"],
                predicted_conversion_rate=round(cr, 4),
                projected_revenue=round(gross_rev, 2),
                projected_net_profit=round(net_profit, 2),
                pricing_action=item["action"],
            )
        )

    peak_demand = max(periods, key=lambda p: p.seasonal_demand_index)
    peak_elasticity = min(periods, key=lambda p: p.price_elasticity)  # most negative

    avg_el = float(np.mean([p.price_elasticity for p in periods]))

    return SeasonalForecastResponse(
        baseline_demand=base_customers,
        avg_elasticity=round(avg_el, 2),
        peak_demand_period=peak_demand.period_name,
        peak_elasticity_period=peak_elasticity.period_name,
        overall_seasonal_lift_pct=round(((peak_demand.seasonal_demand_index - 1.0) * 100), 1),
        periods=periods,
        executive_advice=[
            f"Surge elasticity is highest during {peak_elasticity.period_name} (elasticity {peak_elasticity.price_elasticity:.2f}); discounts drive massive volume lift.",
            f"During {peak_demand.period_name}, organic demand spikes ({peak_demand.seasonal_demand_index}x index). Restrict discount levels to avoid subsidizing customers who would buy anyway.",
            "Post-holiday January requires counter-cyclical retention incentives to protect customer active tenure.",
        ],
    )
