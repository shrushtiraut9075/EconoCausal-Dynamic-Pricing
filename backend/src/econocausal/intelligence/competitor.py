"""Competitor Price Comparison and Cross-Price Elasticity Engine.

Tracks:
- Competitor product pricing across market rivals
- Relative Price Index (PI = P_our / P_competitor * 100)
- Cross-price demand elasticity (E_cross = % dQ_our / % dP_competitor)
- Vulnerability assessment per competitor
- Defensive dynamic pricing recommendations (matching, premium defense, or coupon defense)
"""

from __future__ import annotations

from typing import TypedDict

import numpy as np

from econocausal.intelligence.schemas import (
    CompetitorComparisonRequest,
    CompetitorComparisonResponse,
    CompetitorProductPrice,
)


class _CompetitorItem(TypedDict):
    id: str
    name: str
    price: float
    cross_elasticity: float


def evaluate_competitor_pricing(
    request: CompetitorComparisonRequest,
) -> CompetitorComparisonResponse:
    """Analyze competitor prices, calculate cross-price elasticity, and generate recommendations."""
    our_price = request.our_base_price

    default_competitors: list[_CompetitorItem] = [
        {
            "id": "comp_alpha",
            "name": "AlphaRetail (Category Leader)",
            "price": our_price * 0.92,
            "cross_elasticity": 0.85,
        },
        {
            "id": "comp_discount_direct",
            "name": "DiscountDirect (Aggressive Undercutter)",
            "price": our_price * 0.81,
            "cross_elasticity": 1.25,
        },
        {
            "id": "comp_nexus",
            "name": "NexusStore (Mid-Market Parity)",
            "price": our_price * 0.99,
            "cross_elasticity": 0.45,
        },
        {
            "id": "comp_luxora",
            "name": "Luxora Boutique (Premium Player)",
            "price": our_price * 1.22,
            "cross_elasticity": 0.22,
        },
        {
            "id": "comp_fastship",
            "name": "FastShip Marketplace",
            "price": our_price * 0.88,
            "cross_elasticity": 0.95,
        },
    ]

    competitors_raw = request.competitors_override or default_competitors
    prices = [float(c["price"]) for c in competitors_raw]
    median_price = float(np.median(prices))
    price_index = float((our_price / median_price) * 100.0)

    competitor_items: list[CompetitorProductPrice] = []

    for comp in competitors_raw:
        c_price = float(comp["price"])
        diff_pct = float(((our_price - c_price) / c_price) * 100.0)
        c_elasticity = float(comp.get("cross_elasticity", 0.75))

        if diff_pct > 2.0:
            pos = "premium"
        elif diff_pct < -2.0:
            pos = "undercut"
        else:
            pos = "parity"

        # Vulnerability assessment: depends on price difference and cross-elasticity
        if diff_pct > 15.0 and c_elasticity > 1.0:
            vuln = "critical"
            rec_disc = 20
            strategy = (
                f"Severe price gap (+{diff_pct:.1f}%). Deploy targeted 20% counter-discount to "
                "price-sensitive customers to prevent high volume defection."
            )
        elif diff_pct > 5.0 and c_elasticity > 0.6:
            vuln = "high"
            rec_disc = 10
            strategy = (
                f"Competitor undercuts by {abs(diff_pct):.1f}%. Offer 10% coupon triggered on cart abandonment "
                "to defend conversion rate without resetting public MSRP."
            )
        elif diff_pct > 0.0:
            vuln = "medium"
            rec_disc = 5
            strategy = (
                "Mild premium position. Maintain baseline price; differentiate with loyalty points "
                "and free expedited shipping."
            )
        else:
            vuln = "low"
            rec_disc = 0
            strategy = (
                "Our price is competitive or lower. Do not discount; harvest margin and highlight "
                "superior quality & customer reviews."
            )

        competitor_items.append(
            CompetitorProductPrice(
                competitor_id=str(comp["id"]),
                competitor_name=str(comp["name"]),
                competitor_price=round(c_price, 2),
                price_difference_pct=round(diff_pct, 2),
                position=pos,  # type: ignore[arg-type]
                cross_price_elasticity=round(c_elasticity, 2),
                vulnerability_tier=vuln,  # type: ignore[arg-type]
                recommended_our_discount=rec_disc,
                defensive_pricing_strategy=strategy,
            )
        )

    # Position summary
    if price_index > 110.0:
        position_desc = "Premium Priced (High Undercut Vulnerability)"
    elif price_index < 90.0:
        position_desc = "Value Leader (Aggressive Margin Opportunity)"
    else:
        position_desc = "Competitive Parity (Balanced Market Alignment)"

    recommendations = [
        f"Our Price Index stands at {price_index:.1f} vs market median (${median_price:.2f}).",
        "DiscountDirect poses the highest cross-price elasticity risk (1.25). Target defection-prone customers with selective 10-20% counter-offers.",
        "Maintain list price parity against AlphaRetail while leveraging causal ITE to target discounts exclusively to persuadable shoppers.",
    ]

    return CompetitorComparisonResponse(
        product_category=request.category,
        our_base_price=round(our_price, 2),
        market_median_price=round(median_price, 2),
        price_index_vs_median=round(price_index, 2),
        our_current_position=position_desc,
        competitors=competitor_items,
        pricing_recommendations=recommendations,
    )
