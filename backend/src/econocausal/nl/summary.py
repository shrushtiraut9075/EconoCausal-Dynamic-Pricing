"""Natural-language summary engine for allocation results.

Template-based ONLY — all numbers come from computed data.
No LLM is used for numbers. Golden-file unit tests guard wording.

Implements PROJECT.md §11 and PRD US-9.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from econocausal.causal.segments import segment_summary
from econocausal.logging import get_logger

logger = get_logger(__name__)


def generate_summary(
    allocation_df: pd.DataFrame,
    budget: float,
    total_spend: float,
    total_delta_pi: float,
    n_treated: int,
    blanket_delta_pi: float | None = None,
    predictive_delta_pi: float | None = None,
) -> dict[str, Any]:
    """Generate a natural-language summary of the discount allocation.

    All text is templated from computed numbers only.

    Args:
        allocation_df: Full allocation DataFrame (all customers).
        budget: Total budget in USD.
        total_spend: Actual spend from allocation.
        total_delta_pi: Total incremental profit.
        n_treated: Number of customers allocated a discount.
        blanket_delta_pi: Incremental profit of blanket strategy at same budget (optional).
        predictive_delta_pi: Incremental profit of predictive targeting (optional).

    Returns:
        Dict with headline (str) and bullets (list[str]).
    """
    n_total = len(allocation_df)
    treat_pct = 100 * n_treated / n_total if n_total > 0 else 0.0
    spend_pct = 100 * total_spend / budget if budget > 0 else 0.0
    budget_remaining = budget - total_spend

    # Segment mix of treated customers
    treated_df = (
        allocation_df[allocation_df.get("allocated_discount", 0) > 0]
        if "allocated_discount" in allocation_df.columns
        else allocation_df.head(0)
    )
    if len(treated_df) > 0 and "segment" in treated_df.columns:
        seg_mix = segment_summary(treated_df["segment"].values)
        persuadable_pct = 100 * seg_mix.get("persuadable", 0.0)
    else:
        persuadable_pct = float("nan")

    # Headline
    headline = (
        f"Targeting {n_treated:,} of {n_total:,} customers ({treat_pct:.0f}%) with discounts "
        f"uses ${total_spend:,.0f} of your ${budget:,.0f} budget "
        f"and is expected to add ${total_delta_pi:,.0f} in incremental profit."
    )

    bullets: list[str] = [
        f"💰 Budget used: ${total_spend:,.0f} ({spend_pct:.0f}% of ${budget:,.0f}). "
        f"${budget_remaining:,.0f} remaining.",
        f"🎯 {n_treated:,} customers targeted out of {n_total:,} ({treat_pct:.0f}%).",
        f"📈 Expected incremental profit: ${total_delta_pi:,.0f}.",
    ]

    if not np.isnan(persuadable_pct):
        bullets.append(
            f"✅ {persuadable_pct:.0f}% of treated customers are Persuadables "
            f"(buy only because of the discount)."
        )

    if blanket_delta_pi is not None and blanket_delta_pi > 0:
        lift_vs_blanket = total_delta_pi - blanket_delta_pi
        bullets.append(
            f"⚡ ${lift_vs_blanket:,.0f} more profit than a blanket discount campaign "
            f"at the same budget ({100 * lift_vs_blanket / blanket_delta_pi:.0f}% lift)."
        )

    if predictive_delta_pi is not None and predictive_delta_pi > 0:
        lift_vs_pred = total_delta_pi - predictive_delta_pi
        bullets.append(
            f"🔬 ${lift_vs_pred:,.0f} more profit than predictive-propensity targeting "
            f"({100 * lift_vs_pred / predictive_delta_pi:.0f}% lift)."
        )

    # Assumptions caveat
    bullets.append(
        "⚠️ Assumptions: unconfoundedness (all confounders observed), SUTVA (no spillover), "
        "and consistent treatment definition."
    )

    logger.info("NL summary generated", n_treated=n_treated, total_delta_pi=total_delta_pi)

    return {
        "headline": headline,
        "bullets": bullets,
        "computed_at": str(pd.Timestamp.now()),
    }


generate_allocation_summary = generate_summary
